"""Mistral AI Provider - European AI leader"""

import json
import logging
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI

from ..base import LLMProvider, EmbeddingProvider

logger = logging.getLogger("VORTEX.LLM.Mistral")


class MistralProvider(LLMProvider, EmbeddingProvider):
    """
    Mistral AI provider - European AI company, GDPR compliant.
    Models: Mistral Large 2, Mistral Small, Mixtral 8x7B
    Embeddings: mistral-embed (1024 dims)
    Pricing: Competitive European alternative
    """

    def __init__(self, api_key: Optional[str] = None):
        LLMProvider.__init__(self, api_key)
        EmbeddingProvider.__init__(self, api_key)
        if api_key:
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.mistral.ai/v1"
            )

    @property
    def name(self) -> str:
        return "mistral"

    @property
    def display_name(self) -> str:
        return "Mistral AI"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def default_model(self) -> str:
        return "mistral-small-latest"  # Cost-effective

    @property
    def embedding_dimensions(self) -> int:
        return 1024

    @property
    def default_embedding_model(self) -> str:
        return "mistral-embed"

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Mistral"""
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens or 8000
            )

            self.mark_success()
            return response.choices[0].message.content

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Mistral text generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON using Mistral"""
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                response_format={"type": "json_object"}
            )

            self.mark_success()
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Mistral JSON generation failed: {e}")
            raise

    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embedding using Mistral"""
        try:
            response = await self.client.embeddings.create(
                model=model or self.default_embedding_model,
                input=text[:8000]
            )

            self.mark_success()
            return response.data[0].embedding

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Mistral embedding failed: {e}")
            raise
