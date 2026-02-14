"""Gemini Provider - Google's generative AI models"""

import json
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai

from ..base import LLMProvider, EmbeddingProvider

logger = logging.getLogger("VORTEX.LLM.Gemini")


class GeminiProvider(LLMProvider, EmbeddingProvider):
    """
    Google Gemini provider with both LLM and embedding capabilities.
    FREE tier: 1M tokens/min for Flash, 15 RPM for Pro
    Models: Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash
    Embeddings: models/embedding-001 (768 dimensions)
    """

    def __init__(self, api_key: Optional[str] = None):
        LLMProvider.__init__(self, api_key)
        EmbeddingProvider.__init__(self, api_key)
        if api_key:
            genai.configure(api_key=api_key)

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def display_name(self) -> str:
        return "Google Gemini"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def default_model(self) -> str:
        return "gemini-2.0-flash-exp"  # Fastest, FREE

    @property
    def embedding_dimensions(self) -> int:
        return 768

    @property
    def default_embedding_model(self) -> str:
        # Try different model names - Gemini API changed model naming
        # Options: "models/text-embedding-004", "text-embedding-004", "models/embedding-001"
        return "models/text-embedding-004"  # Try this first

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using Gemini"""
        try:
            model_instance = genai.GenerativeModel(model or self.default_model)
            response = await model_instance.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )

            self.mark_success()
            return response.text

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Gemini text generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON using Gemini"""
        try:
            model_instance = genai.GenerativeModel(model or self.default_model)
            response = await model_instance.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json"
                )
            )

            self.mark_success()
            return json.loads(response.text)

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Gemini JSON generation failed: {e}")
            raise

    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embedding using Gemini"""
        try:
            result = await genai.embed_content_async(
                model=model or self.default_embedding_model,
                content=text[:9000],
                task_type="retrieval_document"
            )

            self.mark_success()
            return result['embedding']

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Gemini embedding failed: {e}")
            raise
