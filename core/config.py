
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- System Configuration ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    @classmethod
    def require_api_key(cls):
        """Validates that the API key is present. Call this in modules that need it."""
        if not cls.GEMINI_API_KEY:
            raise SystemExit(
                "\n[ERRO FATAL] Chave de API não encontrada.\n"
                "Configure uma das variáveis de ambiente:\n"
                "  - GEMINI_API_KEY\n"
                "  - GOOGLE_API_KEY\n\n"
                "Crie um arquivo .env na raiz do projeto com:\n"
                "  GEMINI_API_KEY=sua_chave_aqui\n"
            )

    # --- Paths ---
    DATA_RAW_DIR = os.path.join("data", "raw")
    DATA_ANALYSIS_DIR = os.path.join("data", "analysis")
    
    CHROMA_PERSIST_DIR_REFERENCE = os.path.join("data", "chroma_db_reference")
    CHROMA_PERSIST_DIR_SUSPICIOUS = os.path.join("data", "chroma_db_suspicious")

    # --- Files ---
    # Reference news (known to be true)
    REFERENCE_FILE_NAME = "base_veridica_news.jsonl"
    REFERENCE_FILE_PATH = os.path.join(DATA_RAW_DIR, REFERENCE_FILE_NAME)
    
    # News to be analyzed
    ANALYSIS_FILE_NAME = "analysis_report.jsonl"
    ANALYSIS_FILE_PATH = os.path.join(DATA_ANALYSIS_DIR, ANALYSIS_FILE_NAME)

    # --- Models ---
    LLM_MODEL_NAME = "gemini-2.0-flash"
    EMBEDDING_MODEL_NAME = "models/text-embedding-004"

    # --- Detection Configuration ---
    # Threshold for flagging a news as suspicious (0.0 to 1.0)
    SUSPICIOUS_THRESHOLD = 0.75

    # --- Constants ---
    COLLECTION_NAME_REFERENCE = "news_reference"
    COLLECTION_NAME_SUSPICIOUS = "news_suspicious"
