"""
VORTEX Scheduler — Background jobs for automatic collection, analysis, and source monitoring.
"""

import os
import logging
import asyncio
import time
from datetime import datetime

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("VORTEX.Scheduler")

# ─── Configuration ───────────────────────────────────────────────

COLLECT_INTERVAL = int(os.getenv("COLLECT_INTERVAL_HOURS", "6"))
SOURCE_CHECK_INTERVAL = int(os.getenv("SOURCE_CHECK_INTERVAL_HOURS", "1"))

# Known news sources to monitor
MONITORED_SOURCES = [
    {"name": "G1", "url": "https://g1.globo.com", "type": "reference"},
    {"name": "Folha", "url": "https://www.folha.uol.com.br", "type": "reference"},
    {"name": "UOL", "url": "https://www.uol.com.br", "type": "reference"},
    {"name": "BBC Brasil", "url": "https://www.bbc.com/portuguese", "type": "reference"},
    {"name": "Reuters Brasil", "url": "https://www.reuters.com/", "type": "reference"},
]

_sources_status = {}

# ─── Jobs ────────────────────────────────────────────────────────

def job_collect_and_analyze():
    """Collect news, analyze, and reindex."""
    logger.info("Scheduled job: Starting collection pipeline...")
    try:
        from modules.intelligence.collector import run_collector
        run_collector()
        logger.info("Collection complete. Starting analysis...")
        
        from modules.analysis.detector import NewsDetector
        detector = NewsDetector()
        asyncio.run(detector.run_batch_analysis(limit=10))
        logger.info("Analysis complete. Starting reindex...")
        
        from modules.detection.verification_engine import FactVerificationEngine
        engine = FactVerificationEngine()
        engine.index_documents()
        logger.info("Reindex complete. Pipeline finished.")
    except Exception as e:
        logger.error(f"Pipeline job failed: {e}")


def job_check_sources():
    """Check if monitored news sources are accessible."""
    global _sources_status
    logger.info("Checking source accessibility...")
    
    for source in MONITORED_SOURCES:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            with httpx.Client(timeout=10, follow_redirects=True, headers=headers) as client:
                resp = client.get(source["url"])  # Changed HEAD to GET as some sites block HEAD
                _sources_status[source["name"]] = {
                    "url": source["url"],
                    "status": "online",
                    "http_code": resp.status_code,
                    "checked_at": datetime.now().isoformat()
                }
        except Exception as e:
            _sources_status[source["name"]] = {
                "url": source["url"],
                "status": "offline",
                "error": str(e)[:100],
                "checked_at": datetime.now().isoformat()
            }
            logger.warning(f"Source {source['name']} is DOWN: {e}")


# ─── Public API ──────────────────────────────────────────────────

async def check_sources_status() -> dict:
    """Get last known status of all monitored sources."""
    if not _sources_status:
        # Do initial check
        job_check_sources()
    
    online = sum(1 for s in _sources_status.values() if s.get("status") == "online")
    total = len(_sources_status)
    return {
        "total": total,
        "online": online,
        "offline": total - online,
        "sources": _sources_status
    }


def start_scheduler() -> BackgroundScheduler:
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler(daemon=True)
    
    # Collection pipeline every N hours
    scheduler.add_job(
        job_collect_and_analyze,
        trigger=IntervalTrigger(hours=COLLECT_INTERVAL),
        id="collect_pipeline",
        name=f"Collect & Analyze (every {COLLECT_INTERVAL}h)",
        replace_existing=True,
        max_instances=1
    )
    
    # Source monitoring every N hours
    scheduler.add_job(
        job_check_sources,
        trigger=IntervalTrigger(hours=SOURCE_CHECK_INTERVAL),
        id="check_sources",
        name=f"Source Monitor (every {SOURCE_CHECK_INTERVAL}h)",
        replace_existing=True,
        max_instances=1
    )
    
    scheduler.start()
    logger.info(f"Scheduler started: collect every {COLLECT_INTERVAL}h, sources every {SOURCE_CHECK_INTERVAL}h")
    
    # Run initial source check
    scheduler.add_job(job_check_sources, id="initial_check", replace_existing=True)
    
    return scheduler
