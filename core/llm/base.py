"""
Abstract base classes for LLM providers.
Defines the interface that all providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum


class ProviderStatus(Enum):
    """Status of a provider"""
    ACTIVE = "active"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    DISABLED = "disabled"


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.status = ProviderStatus.DISABLED if not api_key else ProviderStatus.ACTIVE
        self.error_count = 0
        self.success_count = 0
        self.last_error = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'groq', 'gemini', 'openai')"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name"""
        pass

    @property
    @abstractmethod
    def is_free(self) -> bool:
        """Whether this provider has a free tier"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model to use for this provider"""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text completion"""
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate JSON response"""
        pass

    def mark_success(self):
        """Mark a successful request"""
        self.success_count += 1
        self.error_count = 0
        self.status = ProviderStatus.ACTIVE

    def mark_failure(self, error: Exception):
        """Mark a failed request"""
        self.error_count += 1
        self.last_error = str(error)

        # Disable after 3 consecutive failures
        if self.error_count >= 3:
            self.status = ProviderStatus.FAILED

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.status == ProviderStatus.ACTIVE and self.api_key is not None


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.status = ProviderStatus.DISABLED if not api_key else ProviderStatus.ACTIVE
        self.error_count = 0
        self.success_count = 0
        self.last_error = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass

    @property
    @abstractmethod
    def embedding_dimensions(self) -> int:
        """Number of dimensions in the embedding vector"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default embedding model"""
        pass

    @abstractmethod
    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embedding vector"""
        pass

    def mark_success(self):
        """Mark a successful request"""
        self.success_count += 1
        self.error_count = 0
        self.status = ProviderStatus.ACTIVE

    def mark_failure(self, error: Exception):
        """Mark a failed request"""
        self.error_count += 1
        self.last_error = str(error)

        if self.error_count >= 3:
            self.status = ProviderStatus.FAILED

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.status == ProviderStatus.ACTIVE and self.api_key is not None
