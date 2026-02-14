"""DeepSeek Provider - Cost-effective Chinese AI models"""

import json
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

from ..base import LLMProvider

logger = logging.getLogger("VORTEX.LLM.DeepSeek")


class DeepSeekProvider(LLMProvider):
    """
    DeepSeek provider - very cost-effective alternative to GPT-4.
    Models: DeepSeek-V3, DeepSeek-R1 (reasoning specialist)
    Pricing: Significantly cheaper than GPT-4 (~$0.14/1M tokens)
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if api_key:
            # DeepSeek uses OpenAI-compatible API
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )

    @property
    def name(self) -> str:
        return "deepseek"

    @property
    def display_name(self) -> str:
        return "DeepSeek"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def default_model(self) -> str:
        return "deepseek-chat"  # DeepSeek-V3

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using DeepSeek"""
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
            logger.error(f"DeepSeek text generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON using DeepSeek"""
        try:
            # Add JSON instruction to prompt
            json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON."

            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": json_prompt}],
                temperature=temperature,
                response_format={"type": "json_object"}
            )

            self.mark_success()
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"DeepSeek JSON generation failed: {e}")
            raise
