"""
LLM Manager - Manages multiple providers with failover and load balancing
"""

import logging
import random
from typing import List, Optional, Dict, Any, Type

from .base import LLMProvider, EmbeddingProvider, ProviderStatus
from .providers.openai_provider import OpenAIProvider
from .providers.gemini_provider import GeminiProvider
from .embedding_adapter import adapt_embedding

logger = logging.getLogger("VORTEX.LLM.Manager")


class LLMManager:
    """
    Manages multiple LLM providers with automatic failover and load balancing.

    Features:
    - Automatic failover: If one provider fails, tries the next one
    - Load balancing: Distributes requests across providers (round-robin)
    - Priority-based: Free providers are tried first
    - Health tracking: Disables providers after consecutive failures
    """

    def __init__(
        self,
        enabled_providers: Optional[List[str]] = None,
        api_keys: Optional[Dict[str, str]] = None,
        load_balance: bool = False
    ):
        """
        Initialize LLM Manager

        Args:
            enabled_providers: List of provider names to enable (e.g., ['groq', 'gemini'])
                             If None, all providers with API keys are enabled
            api_keys: Dict mapping provider name to API key
            load_balance: If True, use round-robin load balancing; if False, always try in priority order
        """
        self.api_keys = api_keys or {}
        self.load_balance = load_balance
        self._current_provider_index = 0

        # Initialize all providers
        self.llm_providers: List[LLMProvider] = []
        self.embedding_providers: List[EmbeddingProvider] = []

        # Initialize providers in priority order
        # OpenAI first (reliable, 1536 dims native)
        # Gemini backup (free, 768 dims adapted to 1536)
        provider_classes = [
            (OpenAIProvider, 'openai'),       # Priority 1: Paid embeddings (1536) + text
            (GeminiProvider, 'gemini'),       # Priority 2: FREE embeddings (768→1536) + text backup
        ]

        for provider_class, provider_name in provider_classes:
            # Skip if not in enabled list (if list is specified)
            if enabled_providers and provider_name not in enabled_providers:
                continue

            api_key = self.api_keys.get(provider_name)
            if api_key:
                try:
                    provider = provider_class(api_key)
                    self.llm_providers.append(provider)

                    # Check if provider also supports embeddings
                    if isinstance(provider, EmbeddingProvider):
                        self.embedding_providers.append(provider)

                    logger.info(f"Initialized {provider.display_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize {provider_name}: {e}")

        if not self.llm_providers:
            logger.error("No LLM providers available! Please configure at least one API key.")

        logger.info(f"LLM Manager initialized with {len(self.llm_providers)} providers")

    def _get_next_provider(self, providers: List, exclude: List = None) -> Optional[Any]:
        """Get next available provider using round-robin or priority"""
        exclude = exclude or []
        available = [p for p in providers if p.is_available() and p not in exclude]

        if not available:
            return None

        if self.load_balance:
            # Round-robin
            provider = available[self._current_provider_index % len(available)]
            self._current_provider_index += 1
            return provider
        else:
            # Priority order (first available)
            return available[0]

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        retry_all: bool = True
    ) -> str:
        """
        Generate text with automatic failover.

        Args:
            prompt: The prompt to send
            model: Optional specific model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            retry_all: If True, tries all providers until one succeeds

        Returns:
            Generated text

        Raises:
            Exception: If all providers fail
        """
        tried_providers = []
        last_error = None

        while True:
            provider = self._get_next_provider(self.llm_providers, tried_providers)

            if not provider:
                error_msg = "All LLM providers are unavailable"
                logger.error(error_msg)
                raise Exception(error_msg)

            tried_providers.append(provider)

            try:
                logger.info(f"Using {provider.display_name} for text generation")
                result = await provider.generate_text(prompt, model, temperature, max_tokens)
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"{provider.display_name} failed: {e}")

                if not retry_all:
                    raise

        # All providers failed
        error_msg = f"All {len(tried_providers)} providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        retry_all: bool = True
    ) -> Dict[str, Any]:
        """Generate JSON with automatic failover"""
        tried_providers = []
        last_error = None

        while True:
            provider = self._get_next_provider(self.llm_providers, tried_providers)

            if not provider:
                error_msg = "All LLM providers are unavailable"
                logger.error(error_msg)
                raise Exception(error_msg)

            tried_providers.append(provider)

            try:
                logger.info(f"Using {provider.display_name} for JSON generation")
                result = await provider.generate_json(prompt, model, temperature)
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"{provider.display_name} failed: {e}")

                if not retry_all:
                    raise

        error_msg = f"All {len(tried_providers)} providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        retry_all: bool = True
    ) -> List[float]:
        """Generate embedding with automatic failover"""
        tried_providers = []
        last_error = None

        while True:
            provider = self._get_next_provider(self.embedding_providers, tried_providers)

            if not provider:
                error_msg = "All embedding providers are unavailable"
                logger.error(error_msg)
                raise Exception(error_msg)

            tried_providers.append(provider)

            try:
                logger.info(f"Using {provider.display_name} for embedding")
                result = await provider.get_embedding(text, model)

                # Adapt embedding to target dimensions (1536 for OpenAI standard)
                adapted = adapt_embedding(
                    result,
                    target_dims=1536,
                    source_provider=provider.display_name
                )

                return adapted

            except Exception as e:
                last_error = e
                logger.warning(f"{provider.display_name} embedding failed: {e}")

                if not retry_all:
                    raise

        error_msg = f"All {len(tried_providers)} embedding providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "llm_providers": [
                {
                    "name": p.display_name,
                    "status": p.status.value,
                    "is_free": p.is_free,
                    "success_count": p.success_count,
                    "error_count": p.error_count,
                    "last_error": p.last_error
                }
                for p in self.llm_providers
            ],
            "embedding_providers": [
                {
                    "name": p.display_name,
                    "status": p.status.value,
                    "dimensions": p.embedding_dimensions,
                    "success_count": p.success_count,
                    "error_count": p.error_count,
                    "last_error": p.last_error
                }
                for p in self.embedding_providers
            ]
        }
