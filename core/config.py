
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- Multi-Provider AI Configuration ---
    # API Keys for different providers
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

    # Enabled providers (in priority order: free first, then paid)
    # Providers are tried in this order for failover
    ENABLED_PROVIDERS = os.getenv("ENABLED_PROVIDERS", "groq,gemini,openai,anthropic,deepseek,mistral,together,cohere").split(",")

    # Load balancing: if True, distributes requests round-robin; if False, always tries in priority order
    LOAD_BALANCE = os.getenv("LOAD_BALANCE", "false").lower() == "true"

    @classmethod
    def get_provider_api_keys(cls) -> dict:
        """Get all configured API keys"""
        return {
            "groq": cls.GROQ_API_KEY,
            "gemini": cls.GEMINI_API_KEY,
            "openai": cls.OPENAI_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "deepseek": cls.DEEPSEEK_API_KEY,
            "mistral": cls.MISTRAL_API_KEY,
            "together": cls.TOGETHER_API_KEY,
            "cohere": cls.COHERE_API_KEY,
        }

    @classmethod
    def require_api_key(cls):
        """Validates that at least one API key is present"""
        api_keys = cls.get_provider_api_keys()
        if not any(api_keys.values()):
            raise SystemExit(
                "\n[ERRO FATAL] Nenhuma chave de API configurada.\n"
                "Configure pelo menos uma das variáveis de ambiente:\n"
                "  - GROQ_API_KEY (GRATUITO, recomendado)\n"
                "  - GEMINI_API_KEY ou GOOGLE_API_KEY (FREE tier)\n"
                "  - OPENAI_API_KEY (Freemium)\n"
                "  - ANTHROPIC_API_KEY (Freemium)\n\n"
                "Crie um arquivo .env na raiz do projeto com:\n"
                "  GROQ_API_KEY=sua_chave_aqui\n"
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
