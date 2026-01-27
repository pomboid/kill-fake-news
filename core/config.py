
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- System Configuration ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        # Fallback check if user used GOOGLE_API_KEY
        GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
        
    if not GEMINI_API_KEY:
        # We don't raise error immediately to allow localized checks, but main flows will need it.
        print("WARNING: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")

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
    EMBEDDING_MODEL_NAME = "models/embedding-001"

    # --- Detection Configuration ---
    # Threshold for flagging a news as suspicious (0.0 to 1.0)
    SUSPICIOUS_THRESHOLD = 0.75

    # --- Constants ---
    COLLECTION_NAME_REFERENCE = "news_reference"
    COLLECTION_NAME_SUSPICIOUS = "news_suspicious"
