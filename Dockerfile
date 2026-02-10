# ─── Build Stage ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── Runtime Stage ───────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: create non-root user
RUN groupadd -r vortex && useradd -r -g vortex -d /app -s /sbin/nologin vortex

# Install curl for health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy application code
COPY --chown=vortex:vortex . .

# Create writable directories
RUN mkdir -p /app/data/raw /app/data/analysis /app/data/chroma_db_reference \
    /app/data/chroma_db_suspicious /app/logs \
    && chown -R vortex:vortex /app/data /app/logs

# Switch to non-root user
USER vortex

# Expose port
EXPOSE 8420

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8420/health || exit 1

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8420", "--workers", "1", "--log-level", "info"]
