
import os
import json
import time
import logging
import re
from datetime import datetime
from typing import List, Tuple, Optional
from functools import wraps

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from core.config import Config
from core.models import NewsArticle
from core.ui import UI

logger = logging.getLogger("VORTEX.Verification")

def retry_api(max_retries=3, base_delay=2):
    """Retry decorator with exponential backoff for API rate limit errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        wait_time = base_delay * (2 ** (retries - 1))  # Exponential backoff
                        UI.warning(f"Rate limit hit. Retrying in {wait_time}s... ({retries}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        raise e
            return func(*args, **kwargs)
        return wrapper
    return decorator

class VerificationDatabase:
    """Manages the reference vector store for fact-checking."""
    def __init__(self, mode: str = "reference"):
        self.mode = mode
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=Config.EMBEDDING_MODEL_NAME,
            google_api_key=Config.GEMINI_API_KEY
        )
        if mode == "suspicious":
            self.path = Config.CHROMA_PERSIST_DIR_SUSPICIOUS
            self.collection = Config.COLLECTION_NAME_SUSPICIOUS
        else:
            self.path = Config.CHROMA_PERSIST_DIR_REFERENCE
            self.collection = Config.COLLECTION_NAME_REFERENCE

    def clear(self):
        if os.path.exists(self.path):
            import shutil
            shutil.rmtree(self.path)

    def get_store(self) -> Chroma:
        return Chroma(
            persist_directory=self.path,
            embedding_function=self.embeddings,
            collection_name=self.collection
        )

    def add_articles(self, articles: List[NewsArticle], batch_size: int = 5):
        store = self.get_store()
        docs = [
            Document(
                page_content=art.content,
                metadata={
                    "titulo": art.title,
                    "subtitulo": art.subtitle or "",
                    "status_verificacao": art.status,
                    "source": "FactCheckingEngine"
                }
            ) for art in articles
        ]
        
        total = len(docs)
        for i in range(0, total, batch_size):
            batch = docs[i:i + batch_size]
            UI.info(f"Indexing batch {i//batch_size + 1}/{(total+batch_size-1)//batch_size}")
            store.add_documents(batch)
            time.sleep(2)  # Base delay between batches (rate limit protection)

class HybridRetriever(BaseRetriever):
    """Combines vector (semantic) and BM25 (keyword) retrievers for hybrid search."""
    vector_retriever: BaseRetriever
    bm25_retriever: BaseRetriever
    k: int = 5

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        # Get results from both retrievers
        vector_docs = self.vector_retriever.invoke(query)
        bm25_docs = self.bm25_retriever.invoke(query)
        
        # Merge and deduplicate by content hash
        seen = set()
        merged = []
        for doc in vector_docs + bm25_docs:
            key = hash(doc.page_content)
            if key not in seen:
                seen.add(key)
                merged.append(doc)
        return merged[:self.k]

class FactVerificationEngine:
    """Uses RAG with hybrid search to verify claims against a reference dataset."""
    
    HISTORY_FILE = os.path.join("data", "verification_history.jsonl")
    VECTOR_WEIGHT = 0.6  # Weight for vector (semantic) retriever
    BM25_WEIGHT = 0.4    # Weight for BM25 (keyword) retriever

    def __init__(self, mode: str = "reference"):
        Config.require_api_key()
        self.mode = mode
        self.db = VerificationDatabase(mode)
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL_NAME,
            temperature=0,
            google_api_key=Config.GEMINI_API_KEY
        )

    def _load_articles_as_docs(self) -> List[Document]:
        """Load articles from JSONL as LangChain Documents for BM25."""
        input_file = Config.REFERENCE_FILE_PATH
        if not os.path.exists(input_file):
            return []
        docs = []
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    art = NewsArticle.model_validate_json(line)
                    docs.append(Document(
                        page_content=art.content,
                        metadata={"titulo": art.title}
                    ))
                except Exception:
                    continue
        return docs

    def _get_hybrid_retriever(self, k: int = 5):
        """Create a hybrid retriever combining vector search + BM25."""
        vector_retriever = self.db.get_store().as_retriever(search_kwargs={"k": k})
        
        # Try to build BM25 retriever from local docs
        docs = self._load_articles_as_docs()
        if docs:
            bm25_retriever = BM25Retriever.from_documents(docs, k=k)
            return HybridRetriever(
                vector_retriever=vector_retriever,
                bm25_retriever=bm25_retriever,
                k=k
            )
        
        # Fallback to vector-only if no docs available for BM25
        UI.warning("BM25 unavailable (no local documents). Using vector-only retrieval.")
        return vector_retriever

    def index_documents(self):
        input_file = Config.REFERENCE_FILE_PATH
        if not os.path.exists(input_file):
            UI.warning(f"Reference file not found. Creating empty file: {input_file}")
            os.makedirs(os.path.dirname(input_file), exist_ok=True)
            with open(input_file, 'w', encoding='utf-8') as f:
                pass # Create empty file

        articles = []
        with open(input_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if not line.strip(): continue
                try:
                    articles.append(NewsArticle.model_validate_json(line))
                except Exception as e:
                    UI.warning(f"Skipping malformed entry at line {i}: {str(e)[:50]}...")

        if not articles:
            UI.warning("No articles found to index. Base is currently empty.")
            return

        UI.info(f"Indexing {len(articles)} documents for verification reference.")
        self.db.clear()
        self.db.add_articles(articles)

    @retry_api()
    def verify_claim(self, claim: str) -> dict:
        """Cross-references a claim against the reference database using hybrid search."""
        prompt = ChatPromptTemplate.from_template("""
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
        {context}
        
        AFIRMAÇÃO ANALISADA: 
        {question}
        """)
        
        retriever = self._get_hybrid_retriever(k=5)
        
        def format_docs(docs):
            formatted = []
            for d in docs:
                title = d.metadata.get('titulo', 'Fonte Desconhecida')
                content = d.page_content
                formatted.append(f"NOTÍCIA: {title}\nCONTEÚDO: {content}")
            return "\n\n---\n\n".join(formatted)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        response = chain.invoke(claim)
        
        # Parse JSON from response
        try:
            # Clean possible markdown noise (```json ... ```)
            clean_response = re.search(r'\{.*\}', response, re.DOTALL).group()
            result = json.loads(clean_response)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {response}")
            result = {
                "veredito": "[INCONCLUSIVO]",
                "analise": f"Erro ao processar resposta da IA: {str(e)}",
                "confianca": 0,
                "evidencias": []
            }
        
        # Save to history (#12)
        self._save_to_history(claim, result)
        return result

    def _save_to_history(self, claim: str, result: dict):
        """Persist every verification to history file."""
        try:
            os.makedirs(os.path.dirname(self.HISTORY_FILE), exist_ok=True)
            entry = {
                "timestamp": datetime.now().isoformat(),
                "claim": claim,
                "result": result
            }
            with open(self.HISTORY_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"Failed to save verification history: {e}")

    @staticmethod
    def get_history(limit: int = 20) -> List[dict]:
        """Retrieve recent verification history entries."""
        history_file = FactVerificationEngine.HISTORY_FILE
        if not os.path.exists(history_file):
            return []
        entries = []
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            pass
        # Return most recent entries
        return entries[-limit:]

