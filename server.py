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
from typing import Optional

# Silence noisy libs
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["GRPC_VERBOSITY"] = "ERROR"
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*Chroma.*")

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.logging_config import setup_logging
from core.config import Config
from core.ui import UI

setup_logging()
logger = logging.getLogger("VORTEX.API")

# ─── Configuration ───────────────────────────────────────────────

VORTEX_API_KEY = os.getenv("VORTEX_API_KEY", "")
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1,http://localhost:5173").split(",")
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
    confianca: int
    evidencias: list

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    version: str = "1.0.0"

# ─── Auth Dependency ─────────────────────────────────────────────

async def verify_api_key(x_api_key: str = Header(None)):
    """Validate API key for protected endpoints."""
    if not VORTEX_API_KEY:
        # No key configured = no auth required (dev mode)
        return True
    if x_api_key != VORTEX_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Set X-API-Key header."
        )
    return True

# ─── Lifespan (startup/shutdown) ─────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("VORTEX API starting up...")
    logger.info(f"Auth: {'ENABLED' if VORTEX_API_KEY else 'DISABLED (dev mode)'}")
    logger.info(f"CORS origins: {ALLOWED_ORIGINS}")
    
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
    docs_url="/docs" if not VORTEX_API_KEY else None,  # Hide docs in production
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
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "X-User-ID", "Content-Type"],
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
async def get_status(request: Request, auth=Depends(verify_api_key)):
    """System status: article counts, DB info."""
    count = 0
    if os.path.exists(Config.REFERENCE_FILE_PATH):
        with open(Config.REFERENCE_FILE_PATH, 'r', encoding='utf-8') as f:
            count = sum(1 for line in f if line.strip())

    analysis_count = 0
    if os.path.exists(Config.ANALYSIS_FILE_PATH):
        with open(Config.ANALYSIS_FILE_PATH, 'r', encoding='utf-8') as f:
            analysis_count = sum(1 for line in f if line.strip())

    from scheduler import get_scheduler_info
    
    return {
        "reference_articles": count,
        "analyzed_articles": analysis_count,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "auth_enabled": bool(VORTEX_API_KEY),
        "model": Config.LLM_MODEL_NAME,
        "scheduler": get_scheduler_info()
    }


@app.post("/api/verify", response_model=VerifyResponse)
@limiter.limit("10/minute")
async def verify_claim(request: Request, body: VerifyRequest, auth=Depends(verify_api_key)):
    """Verify a claim against the reference database."""
    user_id = request.headers.get("X-User-ID", "default")
    try:
        from modules.detection.verification_engine import FactVerificationEngine
        engine = FactVerificationEngine()
        result = engine.verify_claim(body.claim, user_id=user_id)
        return VerifyResponse(
            veredito=result.get("veredito", "[INCONCLUSIVO]"),
            analise=result.get("analise", ""),
            confianca=result.get("confianca", 0),
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
async def run_analysis(request: Request, body: AnalyzeRequest, auth=Depends(verify_api_key)):
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
async def get_history(request: Request, limit: int = 20, auth=Depends(verify_api_key)):
    """Retrieve verification history."""
    user_id = request.headers.get("X-User-ID", "default")
    from modules.detection.verification_engine import FactVerificationEngine
    entries = FactVerificationEngine.get_history(limit=limit, user_id=user_id)
    return {"count": len(entries), "entries": entries}


@app.get("/api/quality")
@limiter.limit("30/minute")
async def get_quality(request: Request, auth=Depends(verify_api_key)):
    """Data quality assessment."""
    ref_path = Config.REFERENCE_FILE_PATH
    if not os.path.exists(ref_path):
        return {"total": 0, "valid": 0, "score": 0.0, "issues": ["Reference file missing"]}

    total = valid = 0
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
    return {"total": total, "valid": valid, "score": round(score, 1), "issues": issues[:20]}


@app.get("/api/sources")
@limiter.limit("30/minute")
async def get_sources(request: Request, auth=Depends(verify_api_key)):
    """Check status of monitored news sources."""
    from scheduler import check_sources_status
    return await check_sources_status()


@app.get("/api/news")
@limiter.limit("20/minute")
async def get_news(request: Request, limit: int = 50, auth=Depends(verify_api_key)):
    """Retrieve scraped news articles from the reference database."""
    if not os.path.exists(Config.REFERENCE_FILE_PATH):
        return {"count": 0, "articles": []}
    
    articles = []
    try:
        with open(Config.REFERENCE_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        articles.append(json.loads(line))
                    except:
                        continue
    except Exception as e:
        logger.error(f"Error reading reference file: {e}")
        return {"count": 0, "articles": [], "error": str(e)}
    
    # Return latest first
    return {"count": len(articles), "articles": articles[::-1][:limit]}


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
