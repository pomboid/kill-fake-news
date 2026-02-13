"""Anthropic Provider - Claude models"""

import json
import logging
from typing import Optional, Dict, Any
from anthropic import AsyncAnthropic

from ..base import LLMProvider

logger = logging.getLogger("VORTEX.LLM.Anthropic")


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude provider.
    Models: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
    Pricing: $0.25/1M tokens (Haiku), $3/1M tokens (Sonnet)
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if api_key:
            self.client = AsyncAnthropic(api_key=api_key)

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def display_name(self) -> str:
        return "Anthropic Claude"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def default_model(self) -> str:
        return "claude-3-5-haiku-20241022"  # Cheapest, fast

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Claude"""
        try:
            response = await self.client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens or 8000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            self.mark_success()
            return response.content[0].text

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Anthropic text generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON using Claude"""
        try:
            # Claude doesn't have native JSON mode, so we rely on prompt engineering
            json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON, no explanations."

            response = await self.client.messages.create(
                model=model or self.default_model,
                max_tokens=8000,
                temperature=temperature,
                messages=[{"role": "user", "content": json_prompt}]
            )

            self.mark_success()
            text = response.content[0].text

            # Extract JSON from response (sometimes Claude wraps it in markdown)
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            return json.loads(text)

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Anthropic JSON generation failed: {e}")
            raise
