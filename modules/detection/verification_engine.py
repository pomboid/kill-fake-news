import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional

from sqlmodel import select
from sqlalchemy import func

from core.config import Config
from core.database import get_session
from core.sql_models import Article, Verification
from core.ui import UI
from core.llm import LLMManager

logger = logging.getLogger("VORTEX.Verification")

# Process 50 articles per batch to avoid memory/task overload
INDEX_BATCH_SIZE = 50
# 3 concurrent embedding requests per batch
INDEX_CONCURRENCY = 3


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
            embedding = await self.llm_manager.get_embedding(text[:9000])
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    async def index_documents(self, limit: Optional[int] = None):
        """Generates embeddings for articles that don't have them, in batches."""
        limit_msg = f"limit={limit}" if limit else "all"
        UI.info(f"Checking for unindexed articles ({limit_msg})...")

        # Count total unindexed articles
        async for session in get_session():
            count_stmt = select(func.count(Article.id)).where(Article.embedding == None)
            total = (await session.execute(count_stmt)).scalar()

        if limit:
            total = min(total, limit)

        if total == 0:
            UI.info("All articles are indexed.")
            return

        UI.info(f"Found {total} articles to index (batches of {INDEX_BATCH_SIZE}, concurrency={INDEX_CONCURRENCY}).")

        completed = 0
        errors = 0
        start_time = time.time()

        while completed < total:
            # Fetch next batch of unindexed articles
            fetch_size = min(INDEX_BATCH_SIZE, total - completed)
            async for session in get_session():
                stmt = select(Article).where(Article.embedding == None).limit(fetch_size)
                result = await session.execute(stmt)
                batch = result.scalars().all()

            if not batch:
                break

            semaphore = asyncio.Semaphore(INDEX_CONCURRENCY)

            async def index_one(art: Article):
                nonlocal completed, errors
                async with semaphore:
                    text_content = f"Title: {art.title}\nSubtitle: {art.subtitle or ''}\nContent: {art.content}"
                    embedding = await self._generate_embedding(text_content)

                    if embedding:
                        async for save_session in get_session():
                            art.embedding = embedding
                            await save_session.merge(art)
                            await save_session.commit()
                    else:
                        errors += 1

                    completed += 1
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    remaining = (total - completed) / rate if rate > 0 else 0

                    UI.info(
                        f"[{completed}/{total}] "
                        f"({100 * completed // total}%) "
                        f"{art.title[:35]}... "
                        f"| {rate:.1f}/s | ETA: {remaining / 60:.1f}min"
                    )

                    await asyncio.sleep(0.5)

            tasks = [index_one(a) for a in batch]
            await asyncio.gather(*tasks, return_exceptions=True)

            batch_num = (completed // INDEX_BATCH_SIZE) + 1
            UI.info(f"Batch {batch_num} complete ({completed}/{total} total)")

        elapsed_total = time.time() - start_time
        if completed > 0:
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
