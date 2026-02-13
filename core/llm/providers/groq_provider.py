"""Groq Provider - FREE unlimited tier with Llama, Gemma, Mixtral models"""

import json
import logging
from typing import Optional, Dict, Any
from groq import AsyncGroq

from ..base import LLMProvider

logger = logging.getLogger("VORTEX.LLM.Groq")


class GroqProvider(LLMProvider):
    """
    Groq provider with ultra-fast inference.
    FREE tier: Unlimited requests (beta)
    Models: Llama 3.3 70B, Llama 3.1 8B, Gemma 2 9B, Mixtral 8x7B
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if api_key:
            self.client = AsyncGroq(api_key=api_key)

    @property
    def name(self) -> str:
        return "groq"

    @property
    def display_name(self) -> str:
        return "Groq (FREE)"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def default_model(self) -> str:
        return "llama-3.3-70b-versatile"  # Best free model

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Groq"""
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
            logger.error(f"Groq text generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON using Groq"""
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
            logger.error(f"Groq JSON generation failed: {e}")
            raise
