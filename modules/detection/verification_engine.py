
import os
import json
import time
import logging
import re
from typing import List, Tuple, Optional
from functools import wraps

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from core.config import Config
from core.models import NewsArticle
from core.ui import UI

logger = logging.getLogger("VORTEX.Verification")

def retry_api(max_retries=3, delay=5):
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
                        UI.warning(f"Rate limit hit. Retrying in {delay}s... ({retries}/{max_retries})")
                        time.sleep(delay)
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
            time.sleep(4) 

class FactVerificationEngine:
    """Uses RAG to verify claims against a reference dataset."""
    
    def __init__(self, mode: str = "reference"):
        self.mode = mode
        self.db = VerificationDatabase(mode)
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL_NAME,
            temperature=0,
            google_api_key=Config.GEMINI_API_KEY
        )

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
        """Cross-references a claim against the reference database."""
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
        
        retriever = self.db.get_store().as_retriever(search_kwargs={"k": 5})
        
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
            return json.loads(clean_response)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {response}")
            return {
                "veredito": "[INCONCLUSIVO]",
                "analise": f"Erro ao processar resposta da IA: {str(e)}",
                "confianca": 0,
                "evidencias": []
            }
