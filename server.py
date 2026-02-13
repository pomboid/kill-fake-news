"""
VORTEX API Server — FastAPI application with security middleware.
Run with: uvicorn server:app --host 0.0.0.0 --port 8420
"""

import os
import sys
import json
import asyncio
import logging
import warnings
import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List

# Silence noisy libs
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["GRPC_VERBOSITY"] = "ERROR"
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import select, func, col

from core.logging_config import setup_logging
from core.config import Config
from core.ui import UI
from core.database import init_db, get_session
from core.sql_models import Article, Analysis, Verification, Source
import core.sql_models  # Register models

setup_logging()
logger = logging.getLogger("VORTEX.API")

# ─── Configuration ───────────────────────────────────────────────

ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")
]
START_TIME = time.time()

# ─── Rate Limiter ────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)

# ─── Request/Response Models ─────────────────────────────────────

class VerifyRequest(BaseModel):
    claim: str = Field(..., min_length=10, max_length=2000, description="The claim to verify")

class AnalyzeRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=50, description="Number of articles to analyze")

class VerifyResponse(BaseModel):
    veredito: str
    analise: str
    confianca: float
    evidencias: list

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    version: str = "1.0.0"

# ─── Lifespan (startup/shutdown) ─────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("VORTEX API starting up...")
    logger.info(f"CORS origins: {ALLOWED_ORIGINS}")
    
    # Initialize Database
    await init_db()
    
    # Start scheduler
    from scheduler import start_scheduler
    scheduler = start_scheduler()
    
    yield
    
    # Shutdown
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
    logger.info("VORTEX API shutting down.")

# ─── App ─────────────────────────────────────────────────────────

app = FastAPI(
    title="VORTEX API",
    description="Fake News Detection & Verification System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan
)

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Reject requests larger than 1MB."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1_048_576:
        return JSONResponse(status_code=413, content={"detail": "Request too large"})
    return await call_next(request)

# ─── Public Endpoints ────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check — no auth required. Use in Uptime Kuma."""
    return HealthResponse(
        status="healthy",
        uptime_seconds=round(time.time() - START_TIME, 1)
    )

# ─── Protected Endpoints ─────────────────────────────────────────

@app.get("/api/status")
@limiter.limit("30/minute")
async def get_status(request: Request):
    """System status: article counts, DB info."""
    async for session in get_session():
        article_count = (await session.execute(select(func.count(Article.id)))).one()[0]
        analysis_count = (await session.execute(select(func.count(Analysis.id)))).one()[0]
        verification_count = (await session.execute(select(func.count(Verification.id)))).one()[0]

    from scheduler import get_scheduler_info
    
    return {
        "reference_articles": article_count,
        "analyzed_articles": analysis_count,
        "verifications": verification_count,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "auth_enabled": False,
        "model": Config.LLM_MODEL_NAME,
        "scheduler": get_scheduler_info()
    }


@app.post("/api/verify", response_model=VerifyResponse)
@limiter.limit("10/minute")
async def verify_claim(request: Request, body: VerifyRequest):
    """Verify a claim against the reference database."""
    user_id = request.headers.get("X-User-ID", "default")
    try:
        from modules.detection.verification_engine import FactVerificationEngine
        engine = FactVerificationEngine()
        result = await engine.verify_claim(body.claim, user_id=user_id)
        return VerifyResponse(
            veredito=result.get("veredito", "[INCONCLUSIVO]"),
            analise=result.get("analise", ""),
            confianca=float(result.get("confianca", 0)),
            evidencias=result.get("evidencias", [])
        )
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            logger.warning(f"Gemini Rate Limit Hit: {error_msg}")
            raise HTTPException(
                status_code=429,
                detail="Google Gemini API Quota Exceeded. Try again later."
            )
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/analyze")
@limiter.limit("5/minute")
async def run_analysis(request: Request, body: AnalyzeRequest):
    """Run batch analysis on collected articles."""
    try:
        from modules.analysis.detector import NewsDetector
        detector = NewsDetector()
        await detector.run_batch_analysis(limit=body.limit)
        return {"status": "completed", "limit": body.limit}
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            logger.warning(f"Gemini Rate Limit Hit during analysis: {error_msg}")
            raise HTTPException(
                status_code=429,
                detail="Google Gemini API Quota Exceeded. Try again later."
            )
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/history")
@limiter.limit("30/minute")
async def get_history(request: Request, limit: int = 20):
    """Retrieve verification history."""
    user_id = request.headers.get("X-User-ID", "default")
    from modules.detection.verification_engine import FactVerificationEngine
    engine = FactVerificationEngine()
    entries = await engine.get_history(limit=limit, user_id=user_id)
    return {"count": len(entries), "entries": entries}


@app.get("/api/quality")
@limiter.limit("30/minute")
async def get_quality(request: Request):
    """Data quality assessment."""
    async for session in get_session():
        total = (await session.execute(select(func.count(Article.id)))).one()[0]
        
        # Count issues (simple heuristic)
        short_content_count = (await session.execute(select(func.count(Article.id)).where(func.length(Article.content) < 50))).one()[0]
        missing_title = (await session.execute(select(func.count(Article.id)).where(Article.title == None))).one()[0]
    
    issues = []
    if short_content_count > 0:
        issues.append(f"{short_content_count} articles have content shorter than 50 chars")
    if missing_title > 0:
        issues.append(f"{missing_title} articles missing title")
        
    valid = total - short_content_count - missing_title
    score = (valid / total * 100) if total > 0 else 0
    
    return {"total": total, "valid": valid, "score": round(score, 1), "issues": issues[:20]}


@app.get("/api/sources")
@limiter.limit("30/minute")
async def get_sources(request: Request):
    """Check status of monitored news sources."""
    from scheduler import check_sources_status
    if asyncio.iscoroutinefunction(check_sources_status):
        return await check_sources_status()
    return check_sources_status()


@app.get("/api/news")
@limiter.limit("20/minute")
async def get_news(request: Request, limit: int = 50):
    """Retrieve scraped news articles from the reference database."""
    async for session in get_session():
        stmt = select(Article).order_by(Article.published_at.desc()).limit(limit)
        result = await session.execute(stmt)
        articles = result.scalars().all()
        return {"count": len(articles), "articles": articles}


# ─── Dashboard ────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def dashboard(request: Request):
    """Serve the web dashboard."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    if not os.path.exists(template_path):
        return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)
    with open(template_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(f.read())
