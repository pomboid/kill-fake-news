"""
Embedding Dimensionality Adapter

Adapts embeddings from different providers to a common dimensionality.
Supports padding (for smaller embeddings) and truncation (for larger embeddings).
"""

from typing import List
import logging

logger = logging.getLogger("VORTEX.LLM.Adapter")

# Target dimensionality for PostgreSQL Vector column
TARGET_DIMENSIONS = 1536


def adapt_embedding(
    embedding: List[float],
    target_dims: int = TARGET_DIMENSIONS,
    source_provider: str = "unknown"
) -> List[float]:
    """
    Adapt embedding to target dimensionality.

    Args:
        embedding: The embedding vector to adapt
        target_dims: Target number of dimensions (default: 1536 for OpenAI)
        source_provider: Name of the provider for logging

    Returns:
        Adapted embedding with target_dims dimensions

    Strategy:
        - If embedding has correct dimensions: return as-is
        - If embedding is smaller: pad with zeros (common for Gemini 768 → 1536)
        - If embedding is larger: truncate to first N values (rare case)
    """
    current_dims = len(embedding)

    # Already correct size
    if current_dims == target_dims:
        return embedding

    # Need to expand (padding)
    elif current_dims < target_dims:
        padding_size = target_dims - current_dims
        padded = embedding + [0.0] * padding_size

        logger.debug(
            f"Padded {source_provider} embedding: {current_dims} → {target_dims} dims "
            f"(added {padding_size} zeros)"
        )

        return padded

    # Need to reduce (truncation)
    else:
        truncated = embedding[:target_dims]

        logger.warning(
            f"Truncated {source_provider} embedding: {current_dims} → {target_dims} dims "
            f"(lost {current_dims - target_dims} dimensions)"
        )

        return truncated


def get_provider_native_dimensions(provider_name: str) -> int:
    """
    Get native embedding dimensions for a provider.

    Args:
        provider_name: Name of the provider

    Returns:
        Number of dimensions the provider generates
    """
    dimensions_map = {
        "gemini": 768,
        "openai": 1536,
        "cohere": 1024,
        "together": 1024,
        "mistral": 1024,
        "local": 768,  # SentenceTransformers all-mpnet-base-v2
    }

    return dimensions_map.get(provider_name.lower(), 768)


def validate_embedding(embedding: List[float], expected_dims: int = TARGET_DIMENSIONS) -> bool:
    """
    Validate that an embedding has the expected dimensions.

    Args:
        embedding: The embedding to validate
        expected_dims: Expected number of dimensions

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(embedding, list):
        logger.error(f"Embedding must be a list, got {type(embedding)}")
        return False

    if len(embedding) != expected_dims:
        logger.error(
            f"Embedding has {len(embedding)} dimensions, expected {expected_dims}"
        )
        return False

    if not all(isinstance(x, (int, float)) for x in embedding):
        logger.error("Embedding contains non-numeric values")
        return False

    return True


# Example usage and tests
if __name__ == "__main__":
    import asyncio

    # Test padding (Gemini 768 → OpenAI 1536)
    gemini_embedding = [0.1] * 768
    adapted = adapt_embedding(gemini_embedding, target_dims=1536, source_provider="Gemini")
    assert len(adapted) == 1536
    assert adapted[:768] == gemini_embedding  # Original values preserved
    assert all(x == 0.0 for x in adapted[768:])  # Padding is zeros
    print("✅ Padding test passed (Gemini 768 → 1536)")

    # Test no-op (OpenAI 1536 → 1536)
    openai_embedding = [0.2] * 1536
    adapted = adapt_embedding(openai_embedding, target_dims=1536, source_provider="OpenAI")
    assert len(adapted) == 1536
    assert adapted == openai_embedding
    print("✅ No-op test passed (OpenAI 1536 → 1536)")

    # Test truncation (hypothetical 2048 → 1536)
    large_embedding = [0.3] * 2048
    adapted = adapt_embedding(large_embedding, target_dims=1536, source_provider="Custom")
    assert len(adapted) == 1536
    assert adapted == large_embedding[:1536]
    print("✅ Truncation test passed (2048 → 1536)")

    # Test validation
    assert validate_embedding([0.1] * 1536, expected_dims=1536)
    assert not validate_embedding([0.1] * 768, expected_dims=1536)
    print("✅ Validation test passed")

    print("\n🎉 All tests passed!")
