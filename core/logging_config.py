"""Structured JSON logging with rotation for production use."""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = None, log_dir: str = "logs"):
    """Configure structured logging with console + file output with rotation."""
    level = getattr(logging, (log_level or os.getenv("LOG_LEVEL", "INFO")).upper(), logging.INFO)
    
    # Format: timestamp | level | logger | message
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root = logging.getLogger()
    root.setLevel(level)
    
    # Clear existing handlers
    root.handlers.clear()

    # Console handler (stdout for Docker)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    console.setLevel(level)
    root.addHandler(console)

    # File handler with rotation (5MB x 3 backups)
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "vortex.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(level)
        root.addHandler(file_handler)
    except (PermissionError, OSError):
        # In read-only containers, file logging may not be available
        root.warning("File logging disabled (permission denied or read-only filesystem)")

    # Silence noisy libraries
    for lib in ["httpx", "chromadb", "google", "google_genai", "httpcore", "urllib3"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return root
