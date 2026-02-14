#!/usr/bin/env python3
"""
Test script to discover which Gemini embedding model works
"""

import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Models to test
MODELS_TO_TEST = [
    "models/text-embedding-004",
    "text-embedding-004",
    "models/embedding-001",
    "embedding-001",
    "models/text-multilingual-embedding-002",
    "text-multilingual-embedding-002",
]

TEST_TEXT = "This is a test sentence for embedding generation."


async def test_model(model_name: str) -> dict:
    """Test a specific embedding model"""
    try:
        print(f"\n🔍 Testing: {model_name}")

        result = await genai.embed_content_async(
            model=model_name,
            content=TEST_TEXT,
            task_type="retrieval_document"
        )

        embedding = result['embedding']
        dimensions = len(embedding)

        print(f"   ✅ SUCCESS!")
        print(f"   📏 Dimensions: {dimensions}")
        print(f"   📊 First 5 values: {embedding[:5]}")

        return {
            "model": model_name,
            "status": "success",
            "dimensions": dimensions,
            "sample": embedding[:5]
        }

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ FAILED: {error_msg}")

        return {
            "model": model_name,
            "status": "failed",
            "error": error_msg
        }


async def main():
    """Test all models and report results"""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return

    print(f"🔑 API Key found: {api_key[:20]}...")
    print(f"📝 Testing {len(MODELS_TO_TEST)} models...")

    genai.configure(api_key=api_key)

    # Test all models
    results = []
    for model in MODELS_TO_TEST:
        result = await test_model(model)
        results.append(result)
        await asyncio.sleep(1)  # Rate limit protection

    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)

    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    if successful:
        print(f"\n✅ {len(successful)} model(s) working:")
        for r in successful:
            print(f"   • {r['model']} ({r['dimensions']} dims)")

        # Recommend the first working model
        best = successful[0]
        print(f"\n🎯 RECOMMENDED MODEL:")
        print(f"   Update gemini_provider.py line 51:")
        print(f'   return "{best["model"]}"')
    else:
        print(f"\n❌ No models working! All {len(failed)} failed.")
        print("\n💡 Possible issues:")
        print("   1. Rate limit exceeded (wait until midnight Pacific Time)")
        print("   2. API key invalid")
        print("   3. Billing not configured (upgrade from free tier)")
        print("\n🔧 RECOMMENDATION: Implement Opção 2 (Gemini + Local) for resilience")

    if failed:
        print(f"\n❌ {len(failed)} model(s) failed:")
        for r in failed:
            print(f"   • {r['model']}: {r['error'][:80]}")


if __name__ == "__main__":
    asyncio.run(main())
