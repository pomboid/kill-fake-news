"""Cohere Provider - Enterprise-grade NLP models"""

import json
import logging
from typing import Optional, Dict, Any, List
import cohere

from ..base import LLMProvider, EmbeddingProvider

logger = logging.getLogger("VORTEX.LLM.Cohere")


class CohereProvider(LLMProvider, EmbeddingProvider):
    """
    Cohere provider - excellent for RAG and enterprise use.
    Models: Command R+, Command R
    Embeddings: embed-multilingual-v3.0 (1024 dims)
    Pricing: Pay-per-use, enterprise-focused
    """

    def __init__(self, api_key: Optional[str] = None):
        LLMProvider.__init__(self, api_key)
        EmbeddingProvider.__init__(self, api_key)
        if api_key:
            self.client = cohere.AsyncClient(api_key)

    @property
    def name(self) -> str:
        return "cohere"

    @property
    def display_name(self) -> str:
        return "Cohere"

    @property
    def is_free(self) -> bool:
        return False  # Has trial credits

    @property
    def default_model(self) -> str:
        return "command-r-plus"

    @property
    def embedding_dimensions(self) -> int:
        return 1024

    @property
    def default_embedding_model(self) -> str:
        return "embed-multilingual-v3.0"

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Cohere"""
        try:
            response = await self.client.chat(
                model=model or self.default_model,
                message=prompt,
                temperature=temperature,
                max_tokens=max_tokens or 8000
            )

            self.mark_success()
            return response.text

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Cohere text generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON using Cohere"""
        try:
            json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON, no explanations."

            response = await self.client.chat(
                model=model or self.default_model,
                message=json_prompt,
                temperature=temperature
            )

            self.mark_success()
            text = response.text

            # Extract JSON if wrapped in markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            return json.loads(text)

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Cohere JSON generation failed: {e}")
            raise

    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embedding using Cohere"""
        try:
            response = await self.client.embed(
                model=model or self.default_embedding_model,
                texts=[text[:8000]],
                input_type="search_document"
            )

            self.mark_success()
            return response.embeddings[0]

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Cohere embedding failed: {e}")
            raise
