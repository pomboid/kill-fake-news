# API Rate Limiting Configuration for Gemini Free Tier
#
# Free Tier Limits (per minute):
# - RPM: 100 requests/minute
# - TPM: 30,000 tokens/minute  ← CRITICAL LIMIT
# - RPD: 1,000 requests/day
#
# See: https://ai.google.dev/gemini-api/docs/rate-limits

import time
import asyncio
from functools import wraps

# Free tier safe limits (80% of max to leave margin)
SAFE_RPM = 80  # 80% of 100
SAFE_TPM = 24000  # 80% of 30,000
SAFE_RPD = 800  # 80% of 1,000

# Delays between API calls (in seconds)
DELAY_BETWEEN_ANALYSIS = 2.0  # 2 seconds between each article analysis
DELAY_BETWEEN_EMBEDDINGS = 1.5  # 1.5 seconds between embeddings
DELAY_AFTER_BATCH = 5.0  # 5 seconds after processing a batch

# Batch sizes (reduce to avoid token spikes)
MAX_ARTICLES_PER_BATCH = 5  # Process max 5 articles at once
MAX_CONCURRENT_REQUESTS = 2  # Only 2 parallel requests

# Collection interval (hours) - increased from 6h to reduce daily usage
COLLECTION_INTERVAL_HOURS = 12  # Changed from 6h to 12h


def rate_limit_delay(delay_seconds: float = DELAY_BETWEEN_ANALYSIS):
    """Decorator to add delay after function execution."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await asyncio.sleep(delay_seconds)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            time.sleep(delay_seconds)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def chunk_list(lst, chunk_size):
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
