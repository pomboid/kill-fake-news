"""OpenAI Provider - GPT models"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI, RateLimitError

from ..base import LLMProvider, EmbeddingProvider

logger = logging.getLogger("VORTEX.LLM.OpenAI")


class OpenAIProvider(LLMProvider, EmbeddingProvider):
    """
    OpenAI provider with GPT models and embeddings.
    Models: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
    Embeddings: text-embedding-3-small (1536 dims), text-embedding-3-large (3072 dims)
    Pricing: $0.15/1M tokens (gpt-4o-mini)
    """

    def __init__(self, api_key: Optional[str] = None):
        LLMProvider.__init__(self, api_key)
        EmbeddingProvider.__init__(self, api_key)
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)

    @property
    def name(self) -> str:
        return "openai"

    @property
    def display_name(self) -> str:
        return "OpenAI"

    @property
    def is_free(self) -> bool:
        return False  # Freemium (has free trial)

    @property
    def default_model(self) -> str:
        return "gpt-4o-mini"  # Cheapest, still very good

    @property
    def embedding_dimensions(self) -> int:
        return 1536  # text-embedding-3-small

    @property
    def default_embedding_model(self) -> str:
        return "text-embedding-3-small"

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using OpenAI with retry on rate limits"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.default_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                self.mark_success()
                return response.choices[0].message.content

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait = min(2 ** attempt * 0.5, 30)
                    logger.debug(f"Rate limited, waiting {wait}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    self.mark_failure(e)
                    logger.error(f"OpenAI text generation failed after {max_retries} retries: {e}")
                    raise

            except Exception as e:
                self.mark_failure(e)
                logger.error(f"OpenAI text generation failed: {e}")
                raise

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON using OpenAI with retry on rate limits"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model or self.default_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )

                self.mark_success()
                return json.loads(response.choices[0].message.content)

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait = min(2 ** attempt * 0.5, 30)
                    logger.debug(f"Rate limited, waiting {wait}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    self.mark_failure(e)
                    logger.error(f"OpenAI JSON generation failed after {max_retries} retries: {e}")
                    raise

            except Exception as e:
                self.mark_failure(e)
                logger.error(f"OpenAI JSON generation failed: {e}")
                raise

    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embedding using OpenAI with retry on rate limits"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = await self.client.embeddings.create(
                    model=model or self.default_embedding_model,
                    input=text[:8000]
                )

                self.mark_success()
                return response.data[0].embedding

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait = min(2 ** attempt * 0.5, 30)  # 0.5s, 1s, 2s, 4s, 8s
                    logger.debug(f"Rate limited, waiting {wait}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    self.mark_failure(e)
                    logger.error(f"OpenAI embedding failed after {max_retries} retries: {e}")
                    raise

            except Exception as e:
                self.mark_failure(e)
                logger.error(f"OpenAI embedding failed: {e}")
                raise
