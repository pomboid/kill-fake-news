import argparse
import sys
import warnings
import asyncio
import logging
import os
import json
from datetime import datetime

# Silence noisy libraries and telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["GRPC_VERBOSITY"] = "ERROR"
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)

# Silence warnings before importing local modules
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from core.config import Config
from core.ui import UI
from modules.intelligence.collector import run_collector
from modules.analysis.detector import NewsDetector
from modules.detection.verification_engine import FactVerificationEngine


def _quality_score() -> dict:
    """Calculate data quality score for the reference base (#13)."""
    ref_path = Config.REFERENCE_FILE_PATH
    if not os.path.exists(ref_path):
        return {"total": 0, "valid": 0, "score": 0.0, "issues": ["Reference file missing"]}
    
    total = 0
    valid = 0
    issues = []
    
    with open(ref_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            total += 1
            try:
                data = json.loads(line)
                has_title = bool(data.get("titulo", "").strip())
                has_content = bool(data.get("corpo_do_texto", "").strip())
                has_url = bool(data.get("url", "").strip())
                content_len = len(data.get("corpo_do_texto", ""))
                
                if not has_title:
                    issues.append(f"Line {i}: missing title")
                elif not has_content:
                    issues.append(f"Line {i}: missing content")
                elif not has_url:
                    issues.append(f"Line {i}: missing URL")
                elif content_len < 50:
                    issues.append(f"Line {i}: content too short ({content_len} chars)")
                else:
                    valid += 1
            except Exception:
                issues.append(f"Line {i}: malformed JSON")
    
    score = (valid / total * 100) if total > 0 else 0
    return {"total": total, "valid": valid, "score": round(score, 1), "issues": issues[:10]}


def _export_html(output_path: str = "data/report.html"):
    """Export analysis + verification results as an HTML report (#19)."""
    analysis_path = Config.ANALYSIS_FILE_PATH
    history_path = FactVerificationEngine.HISTORY_FILE
    
    analyses = []
    if os.path.exists(analysis_path):
        with open(analysis_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        analyses.append(json.loads(line))
                    except Exception:
                        pass
    
    history = FactVerificationEngine.get_history(limit=50)
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VORTEX Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
<style>
  :root {{ --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #c9d1d9; --green: #3fb950; --red: #f85149; --yellow: #d29922; --cyan: #58a6ff; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }}
  h1 {{ color: var(--cyan); font-size: 1.8rem; margin-bottom: 0.5rem; }}
  .subtitle {{ color: #8b949e; margin-bottom: 2rem; }}
  h2 {{ color: var(--cyan); font-size: 1.3rem; margin: 2rem 0 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; }}
  .card-title {{ font-weight: 600; margin-bottom: 0.5rem; }}
  .verdict {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }}
  .verdict-true {{ background: #1a3a2a; color: var(--green); }}
  .verdict-fake {{ background: #3a1a1a; color: var(--red); }}
  .verdict-partial {{ background: #3a2a1a; color: var(--yellow); }}
  .verdict-unknown {{ background: #1a2a3a; color: var(--cyan); }}
  .score-bar {{ height: 6px; background: var(--border); border-radius: 3px; margin: 4px 0; }}
  .score-fill {{ height: 100%; border-radius: 3px; }}
  .meta {{ color: #8b949e; font-size: 0.85rem; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--cyan); font-size: 0.85rem; text-transform: uppercase; }}
  .markers {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }}
  .marker {{ background: #1a2a3a; color: var(--cyan); padding: 2px 6px; border-radius: 3px; font-size: 0.75rem; }}
</style>
</head>
<body>
<h1>🌀 VORTEX Report</h1>
<p class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — {len(analyses)} analyses, {len(history)} verifications</p>
"""

    if analyses:
        html += "<h2>📊 Analysis Results</h2>\n"
        for a in analyses:
            art = a.get("article", {})
            det = a.get("detection", {})
            title = art.get("titulo", "Unknown")
            is_fake = det.get("is_fake", False)
            conf = det.get("confidence_score", 0)
            reasoning = det.get("reasoning", "")
            markers = det.get("detected_markers", [])
            scores = det.get("scores", {})
            
            v_class = "verdict-fake" if is_fake else "verdict-true"
            v_label = "FAKE" if is_fake else "LEGIT"
            
            markers_html = "".join(f'<span class="marker">{m}</span>' for m in markers)
            
            html += f"""<div class="card">
  <div class="card-title">{title}</div>
  <span class="verdict {v_class}">{v_label}</span> <span class="meta">Confidence: {conf:.0%}</span>
  <p style="margin-top:8px">{reasoning}</p>
  <div class="markers">{markers_html}</div>
  <table style="margin-top:8px">
    <tr><th>Factual</th><th>Bias</th><th>Sensationalism</th><th>Credibility</th></tr>
    <tr>
      <td>{scores.get('factual_consistency', '?')}/10</td>
      <td>{scores.get('linguistic_bias', '?')}/10</td>
      <td>{scores.get('sensationalism', '?')}/10</td>
      <td>{scores.get('source_credibility', '?')}/10</td>
    </tr>
  </table>
</div>\n"""

    if history:
        html += "<h2>🔍 Verification History</h2>\n"
        for h in history:
            ts = h.get("timestamp", "")[:19]
            claim = h.get("claim", "")
            result = h.get("result", {})
            veredito = result.get("veredito", "?")
            analise = result.get("analise", "")
            confianca = result.get("confianca", 0)
            
            if "FALSO" in veredito.upper():
                v_class = "verdict-fake"
            elif "VERDADEIRO" in veredito.upper() and "PARCIALMENTE" not in veredito.upper():
                v_class = "verdict-true"
            elif "PARCIALMENTE" in veredito.upper():
                v_class = "verdict-partial"
            else:
                v_class = "verdict-unknown"
            
            html += f"""<div class="card">
  <div class="card-title">{claim}</div>
  <span class="verdict {v_class}">{veredito}</span> <span class="meta">{ts} — Confidence: {confianca}%</span>
  <p style="margin-top:8px">{analise}</p>
</div>\n"""

    html += "</body></html>"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return output_path


def main():
    UI.setup_terminal()
    UI.print_banner()

    parser = argparse.ArgumentParser(
        description="VORTEX: Fake News Detection & Verification System",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Operation Phases")

    # 1. Collect
    parser_collect = subparsers.add_parser("collect", help="Phase 1: Scraping reference news (Gold Standard)")
    parser_collect.add_argument("--limit", type=int, default=None, help="Max articles to collect (default: all)")
    
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

    # 6. History
    parser_history = subparsers.add_parser("history", help="View past verification results")
    parser_history.add_argument("--limit", type=int, default=10, help="Number of entries to show")

    # 7. Full Pipeline (#2)
    parser_pipeline = subparsers.add_parser("full-pipeline", help="Run collect → analyze → index in sequence")
    parser_pipeline.add_argument("--limit", type=int, default=5, help="Analyze limit")

    # 8. Batch Verify (#14)
    parser_batch = subparsers.add_parser("batch-verify", help="Verify multiple claims from a file")
    parser_batch.add_argument("file", help="Text file with one claim per line")

    # 9. Quality (#13)
    subparsers.add_parser("quality", help="Check data quality score of the reference base")

    # 10. Export (#19)
    parser_export = subparsers.add_parser("export", help="Export analysis results as HTML report")
    parser_export.add_argument("--output", default="data/report.html", help="Output HTML path")

    # 11. Seed RSS Feeds
    subparsers.add_parser("seed-feeds", help="Populate database with RSS feed URLs from all sources")

    args = parser.parse_args()

    try:
        if args.command == "status":
            async def show_status():
                UI.info("VORTEX SYSTEM STATUS")
                from core.database import get_session
                from sqlmodel import select, func
                from core.sql_models import Article
                
                async for session in get_session():
                    # Count Articles
                    res = await session.execute(select(func.count(Article.id)))
                    count = res.one()[0]
                    UI.highlight("Reference Articles (PostgreSQL)", count)
                    
                    # Count Vector Embeddings (approx via Articles with embedding)
                    # res_vec = await session.execute(select(func.count(Article.id)).where(Article.embedding != None))
                    # vec_count = res_vec.one()[0]
                    # UI.highlight("Articles with Embeddings", vec_count)

            asyncio.run(show_status())

        elif args.command == "collect":
            UI.info("PHASE 1: COLLECTING REFERENCE NEWS")
            asyncio.run(run_collector(limit=args.limit))

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

        elif args.command == "history":
            UI.info("VERIFICATION HISTORY")
            entries = FactVerificationEngine.get_history(limit=args.limit)
            if not entries:
                UI.warning("No verification history found.")
            else:
                for entry in entries:
                    ts = entry.get("timestamp", "?")[:19]
                    claim = entry.get("claim", "?")[:60]
                    veredito = entry.get("result", {}).get("veredito", "?")
                    confianca = entry.get("result", {}).get("confianca", 0)
                    print(f"  {UI.C}{ts}{UI.RESET} | {veredito} ({confianca}%) | {claim}")

        elif args.command == "full-pipeline":
            # #2 — Unified pipeline
            steps = [
                ("Phase 1: Collecting Reference News", lambda: run_collector()),
                ("Phase 2: Analyzing Articles", lambda: asyncio.run(NewsDetector().run_batch_analysis(limit=args.limit))),
                ("Phase 3: Indexing for Verification", lambda: FactVerificationEngine().index_documents()),
            ]
            
            try:
                from rich.progress import Progress, SpinnerColumn, TextColumn
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    for desc, fn in steps:
                        task = progress.add_task(desc, total=None)
                        fn()
                        progress.update(task, completed=True)
            except ImportError:
                for i, (desc, fn) in enumerate(steps, 1):
                    UI.info(f"[{i}/{len(steps)}] {desc}")
                    fn()
            
            UI.info("Full pipeline complete!")

        elif args.command == "batch-verify":
            # #14 — Batch verification
            if not os.path.exists(args.file):
                UI.error(f"Claims file not found: {args.file}")
                sys.exit(1)
            
            with open(args.file, 'r', encoding='utf-8') as f:
                claims = [line.strip() for line in f if line.strip()]
            
            if not claims:
                UI.warning("No claims found in file.")
                sys.exit(0)
            
            UI.info(f"Verifying {len(claims)} claims...")
            engine = FactVerificationEngine()
            
            try:
                from rich.progress import track
                iterator = track(claims, description="Verifying claims...")
            except ImportError:
                iterator = claims
            
            for claim in iterator:
                report = engine.verify_claim(claim)
                veredito = report.get("veredito", "?")
                confianca = report.get("confianca", 0)
                UI.highlight(f"  {veredito} ({confianca}%)", claim[:70])

        elif args.command == "quality":
            # #13 — Data quality score
            UI.info("DATA QUALITY ASSESSMENT")
            q = _quality_score()
            
            UI.highlight("Total Articles", q["total"])
            UI.highlight("Valid Articles", q["valid"])
            
            score = q["score"]
            if score >= 90:
                color = UI.G
            elif score >= 70:
                color = UI.Y
            else:
                color = UI.R
            print(f"  {color}Quality Score: {score}%{UI.RESET}")
            
            if q["issues"]:
                UI.warning(f"Issues found ({len(q['issues'])} shown):")
                for issue in q["issues"]:
                    print(f"    {UI.Y}•{UI.RESET} {issue}")

        elif args.command == "export":
            # #19 — HTML export
            UI.info("EXPORTING HTML REPORT")
            path = _export_html(args.output)
            UI.info(f"Report saved to: {path}")

        elif args.command == "seed-feeds":
            # Populate database with RSS feeds
            UI.info("POPULATING DATABASE WITH RSS FEEDS")
            from scripts.seed_rss_feeds import seed_sources_and_feeds
            asyncio.run(seed_sources_and_feeds())
            UI.info("RSS feeds populated successfully!")

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n{UI.Y}[!] Operation aborted by user.{UI.RESET}")
        sys.exit(0)
    except Exception as e:
        UI.error(f"Critical failure: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
