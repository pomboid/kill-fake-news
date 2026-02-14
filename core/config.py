
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- AI Provider Configuration ---
    # API Keys (OpenAI primary + Gemini backup)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")                              # Paid embeddings (1536 dims) + text
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")  # FREE embeddings (768 dims) + text

    # Enabled providers (in priority order for failover)
    ENABLED_PROVIDERS = os.getenv("ENABLED_PROVIDERS", "openai,gemini").split(",")

    # Load balancing: if True, distributes requests round-robin; if False, always tries in priority order
    LOAD_BALANCE = os.getenv("LOAD_BALANCE", "false").lower() == "true"

    @classmethod
    def get_provider_api_keys(cls) -> dict:
        """Get all configured API keys"""
        return {
            "openai": cls.OPENAI_API_KEY,    # Paid embeddings (1536d, primary) + text
            "gemini": cls.GEMINI_API_KEY,    # FREE embeddings (768d→1536d, backup) + text
        }

    @classmethod
    def require_api_key(cls):
        """Validates that at least one API key is present"""
        api_keys = cls.get_provider_api_keys()
        if not any(api_keys.values()):
            raise SystemExit(
                "\n[ERRO FATAL] Nenhuma chave de API configurada.\n"
                "Configure pelo menos uma das variáveis de ambiente:\n"
                "  - OPENAI_API_KEY (Recomendado, embeddings 1536d)\n"
                "  - GEMINI_API_KEY ou GOOGLE_API_KEY (FREE tier)\n\n"
                "Crie um arquivo .env na raiz do projeto com:\n"
                "  OPENAI_API_KEY=sk-...\n"
                "  GEMINI_API_KEY=AIzaSy...\n"
            )

    # --- Paths ---
    DATA_RAW_DIR = os.path.join("data", "raw")
    DATA_ANALYSIS_DIR = os.path.join("data", "analysis")

    # --- Files ---
    # Reference news (known to be true)
    REFERENCE_FILE_NAME = "base_veridica_news.jsonl"
    REFERENCE_FILE_PATH = os.path.join(DATA_RAW_DIR, REFERENCE_FILE_NAME)

    # News to be analyzed
    ANALYSIS_FILE_NAME = "analysis_report.jsonl"
    ANALYSIS_FILE_PATH = os.path.join(DATA_ANALYSIS_DIR, ANALYSIS_FILE_NAME)

    # --- Legacy Model Names (for backward compatibility) ---
    LLM_MODEL_NAME = "gemini-2.0-flash"
    EMBEDDING_MODEL_NAME = "models/embedding-001"

    # --- Detection Configuration ---
    # Threshold for flagging a news as suspicious (0.0 to 1.0)
    SUSPICIOUS_THRESHOLD = 0.75
