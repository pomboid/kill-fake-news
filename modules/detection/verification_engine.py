import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional

from sqlmodel import select

from core.config import Config
from core.database import get_session
from core.sql_models import Article, Verification
from core.ui import UI
from core.llm import LLMManager

logger = logging.getLogger("VORTEX.Verification")

# Concurrency: 10 simultaneous requests (OpenAI text-embedding-3-small: 3K RPM, 1M TPM)
INDEX_CONCURRENCY = 10

class FactVerificationEngine:
    """Uses RAG with semantic search (pgvector) to verify claims."""

    def __init__(self):
        Config.require_api_key()

        # Initialize multi-provider LLM manager
        self.llm_manager = LLMManager(
            enabled_providers=Config.ENABLED_PROVIDERS,
            api_keys=Config.get_provider_api_keys(),
            load_balance=Config.LOAD_BALANCE
        ) 

    async def _generate_embedding(self, text: str) -> List[float]:
        try:
            # Use LLMManager with automatic failover
            embedding = await self.llm_manager.get_embedding(text[:9000])
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    async def index_documents(self, limit: Optional[int] = None):
        """Generates embeddings for articles that don't have them."""
        limit_msg = f"limit={limit}" if limit else "all"
        UI.info(f"Checking for unindexed articles ({limit_msg})...")

        async for session in get_session():
            # Select articles where embedding is NULL
            stmt = select(Article).where(Article.embedding == None)
            if limit:
                stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            articles = result.scalars().all()

            if not articles:
                UI.info("All articles are indexed.")
                return

            total = len(articles)
            UI.info(f"Found {total} articles to index (concurrency={INDEX_CONCURRENCY}).")

            # Progress tracking
            completed = 0
            errors = 0
            start_time = time.time()
            semaphore = asyncio.Semaphore(INDEX_CONCURRENCY)

            async def index_one(article: Article):
                nonlocal completed, errors
                async with semaphore:
                    text_content = f"Title: {article.title}\nSubtitle: {article.subtitle or ''}\nContent: {article.content}"
                    embedding = await self._generate_embedding(text_content)

                    if embedding:
                        # Save to DB using a new session for thread safety
                        async for save_session in get_session():
                            article.embedding = embedding
                            save_session.add(article)
                            await save_session.commit()
                    else:
                        errors += 1

                    completed += 1
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    remaining = (total - completed) / rate if rate > 0 else 0
                    remaining_min = remaining / 60

                    UI.info(
                        f"[{completed}/{total}] "
                        f"({100 * completed // total}%) "
                        f"{article.title[:35]}... "
                        f"| {rate:.1f}/s | ETA: {remaining_min:.1f}min"
                    )

                    # Small delay to respect rate limits
                    await asyncio.sleep(0.1)

            # Process all articles concurrently with semaphore
            tasks = [index_one(article) for article in articles]
            await asyncio.gather(*tasks, return_exceptions=True)

            elapsed_total = time.time() - start_time
            UI.info(
                f"Indexing complete: {completed}/{total} articles "
                f"({errors} errors) in {elapsed_total / 60:.1f} minutes "
                f"({completed / elapsed_total:.1f} articles/sec)"
            )

    async def verify_claim(self, claim: str, user_id: str = "default") -> dict:
        """Cross-references a claim against the DB using pgvector search."""

        # 1. Generate claim embedding
        try:
            claim_vec = await self.llm_manager.get_embedding(claim)
        except Exception as e:
            return {"veredito": "ERRO", "analise": f"Falha ao gerar embedding: {e}", "confianca": 0, "evidencias": []}

        # 2. Search relevant articles
        context_docs = []
        evidence_ids = []
        
        async for session in get_session():
            # Cosine distance search using pgvector
            stmt = select(Article).order_by(Article.embedding.cosine_distance(claim_vec)).limit(5)
            result = await session.execute(stmt)
            articles = result.scalars().all()
            
            for art in articles:
                context_docs.append(f"NOTÍCIA: {art.title}\nCONTEÚDO: {art.content[:2000]}") # Truncate content for context
                if art.id: evidence_ids.append(art.id)
        
        context_text = "\n\n---\n\n".join(context_docs)
        
        # 3. LLM Verification
        prompt = f"""
        Você é um Auditor Especialista em Integridade de Informação.
        Analise a congruência entre a AFIRMAÇÃO e o CONTEXTO documental fornecido.
        
        REGRAS DE RESPOSTA:
        1. Resposta estritamente em JSON.
        2. Tom clínico, impessoal e direto.
        3. Se o contexto não permitir validação, o veredito deve ser [INCONCLUSIVO].
        
        FORMATO:
        {{
            "veredito": "[VERDADEIRO], [FALSO], [PARCIALMENTE VERDADEIRO] ou [INCONCLUSIVO]",
            "analise": "Descrição técnica da discrepância ou confirmação.",
            "confianca": integer,
            "evidencias": ["citação direta 1", "citação direta 2"]
        }}
        
        CONTEXTO OBTIDO: 
        {context_text}
        
        AFIRMAÇÃO ANALISADA: 
        {claim}
        """
        
        try:
            result = await self.llm_manager.generate_json(prompt)
        except Exception as e:
            logger.error(f"LLM Verification failed: {e}")
            result = {
                "veredito": "[INCONCLUSIVO]",
                "analise": f"Erro na análise LLM: {str(e)}",
                "confianca": 0,
                "evidencias": []
            }
        
        # 4. Save to DB
        await self._save_verification(claim, result, user_id, evidence_ids)
        
        return result

    async def _save_verification(self, claim: str, result: dict, user_id: str, evidence_ids: List[int]):
        async for session in get_session():
            verification = Verification(
                user_id=user_id,
                claim=claim,
                verdict=result.get("veredito", "INCONCLUSIVO"),
                confidence=float(result.get("confianca", 0)),
                evidence=evidence_ids,
                created_at=datetime.utcnow()
            )
            session.add(verification)
            await session.commit()

    async def get_history(self, limit: int = 20, user_id: str = "default") -> List[dict]:
        async for session in get_session():
            stmt = select(Verification).where(Verification.user_id == user_id).order_by(Verification.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            verifications = result.scalars().all()
            
            return [
                {
                    "timestamp": v.created_at.isoformat(),
                    "claim": v.claim,
                    "result": {
                        "veredito": v.verdict,
                        "analise": f"Confiança: {v.confidence}%", # Simplified for history list
                        "confianca": v.confidence
                    }
                } for v in verifications
            ]
        return []

if __name__ == "__main__":
    engine = FactVerificationEngine()
    asyncio.run(engine.index_documents())
