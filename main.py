import argparse
import sys
import warnings
import asyncio
import logging
import os

# Silence noisy libraries and telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["GRPC_VERBOSITY"] = "ERROR"
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)

# Silence warnings before importing local modules
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*Chroma.*")

from core.config import Config
from core.ui import UI
from modules.intelligence.collector import run_collector
from modules.analysis.detector import NewsDetector
from modules.detection.verification_engine import FactVerificationEngine

def main():
    UI.setup_terminal()
    UI.print_banner()

    parser = argparse.ArgumentParser(
        description="VORTEX: Fake News Detection & Verification System",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Operation Phases")

    # 1. Collect
    subparsers.add_parser("collect", help="Phase 1: Scraping reference news (Gold Standard)")
    
    # 2. Analyze
    parser_analyze = subparsers.add_parser("analyze", help="Phase 2: Deep analysis of news for fake markers")
    parser_analyze.add_argument("--limit", type=int, default=5, help="Number of articles to analyze")

    # 3. Index
    subparsers.add_parser("index", help="Phase 3: Indexing reference news for fact-checking")

    # 4. Verify
    parser_verify = subparsers.add_parser("verify", help="Phase 4: Verify a claim against reference news")
    parser_verify.add_argument("claim", help="The claim or news snippet to verify")

    # 5. Status
    subparsers.add_parser("status", help="Check system status and database health")

    args = parser.parse_args()

    try:
        if args.command == "status":
            UI.info("VORTEX SYSTEM STATUS")
            
            # Check JSONL rows
            count = 0
            if os.path.exists(Config.REFERENCE_FILE_PATH):
                with open(Config.REFERENCE_FILE_PATH, 'r', encoding='utf-8') as f:
                    count = sum(1 for line in f if line.strip())
            
            UI.highlight("Reference Articles (JSONL)", count)
            
            # Check Vector DB
            engine = FactVerificationEngine()
            try:
                # Get approximate count from collection
                store = engine.db.get_store()
                v_count = store._collection.count()
                UI.highlight("Vector Database (Items)", v_count)
            except Exception:
                UI.warning("Vector Database: Not initialized or empty.")

        elif args.command == "collect":
            UI.info("PHASE 1: COLLECTING REFERENCE NEWS")
            run_collector()

        elif args.command == "analyze":
            UI.info("PHASE 2: PERFORMING LINGUISTIC & FACTUAL ANALYSIS")
            detector = NewsDetector()
            asyncio.run(detector.run_batch_analysis(limit=args.limit))

        elif args.command == "index":
            UI.info("PHASE 3: INDEXING DATA FOR VERIFICATION")
            engine = FactVerificationEngine()
            engine.index_documents()

        elif args.command == "verify":
            UI.info("PHASE 4: CROSS-REFERENCING CLAIM")
            engine = FactVerificationEngine()
            report = engine.verify_claim(args.claim)
            
            print(f"\n{UI.C}AFIRMAÇÃO ANALISADA:{UI.RESET} {args.claim}")
            
            UI.print_audit_report(
                veredito=report.get("veredito", "[INCONCLUSIVO]"),
                analise=report.get("analise", "Nenhuma análise disponível."),
                confiança=report.get("confianca", 0),
                trechos=report.get("evidencias", [])
            )

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n{UI.Y}[!] Operation aborted by user.{UI.RESET}")
        sys.exit(0)
    except Exception as e:
        UI.error(f"Critical failure: {e}")
        # import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
