import asyncio
import logging
import time
from typing import Optional
from sqlmodel import select
from core.config import Config
from core.database import get_session
from core.sql_models import Article, Analysis
from core.models import FakeNewsDetection, DetectionScores
from core.ui import UI
from core.llm import LLMManager

logger = logging.getLogger("VORTEX.Detector")

# Concurrency: 5 simultaneous requests (OpenAI gpt-4o-mini: 500 RPM, 200K TPM)
ANALYZE_CONCURRENCY = 5


class NewsDetector:
    """Analyzes news articles for signs of misinformation using LLM."""

    def __init__(self):
        Config.require_api_key()

        # Initialize multi-provider LLM manager
        self.llm_manager = LLMManager(
            enabled_providers=Config.ENABLED_PROVIDERS,
            api_keys=Config.get_provider_api_keys(),
            load_balance=Config.LOAD_BALANCE
        )

    async def analyze_article(self, article: Article) -> FakeNewsDetection:
        prompt = f"""
        Analyze the following news article for potential misinformation, fake news markers, and bias.

        TITLE: {article.title}
        CONTENT: {article.content[:5000]}

        Respond ONLY with valid JSON in this exact format:
        {{
            "is_fake": boolean,
            "confidence_score": number (0.0 to 1.0),
            "reasoning": "brief explanation",
            "detected_markers": ["marker1", "marker2"],
            "scores": {{
                "factual_consistency": integer (0-10),
                "linguistic_bias": integer (0-10),
                "sensationalism": integer (0-10),
                "source_credibility": integer (0-10)
            }}
        }}
        """

        try:
            # Use LLMManager with automatic failover
            data = await self.llm_manager.generate_json(prompt)
            return FakeNewsDetection(**data)
        except Exception as e:
            logger.error(f"Analysis failed for article {article.id}: {e}")
            return FakeNewsDetection(
                is_fake=False,
                confidence_score=0.0,
                reasoning=f"Error during analysis: {str(e)}",
                detected_markers=[],
                scores=DetectionScores(factual_consistency=5, linguistic_bias=5, sensationalism=5, source_credibility=5)
            )

    async def run_batch_analysis(self, limit: Optional[int] = None):
        limit_msg = f"limit={limit}" if limit else "all"
        UI.info(f"Checking for unanalyzed articles ({limit_msg})...")

        async for session in get_session():
            # Fetch unanalyzed articles
            stmt = select(Article).outerjoin(Analysis, Article.id == Analysis.article_id).where(Analysis.id == None)
            if limit:
                stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            articles = result.scalars().all()

            if not articles:
                UI.info("No unanalyzed articles found.")
                return

            total = len(articles)
            UI.info(f"Found {total} articles to analyze (concurrency={ANALYZE_CONCURRENCY}).")

            # Progress tracking
            completed = 0
            errors = 0
            start_time = time.time()
            semaphore = asyncio.Semaphore(ANALYZE_CONCURRENCY)

            async def analyze_one(article: Article):
                nonlocal completed, errors
                async with semaphore:
                    detection = await self.analyze_article(article)

                    # Save to DB using a new session for thread safety
                    async for save_session in get_session():
                        analysis = Analysis(
                            article_id=article.id,
                            is_fake=detection.is_fake,
                            confidence=detection.confidence_score,
                            reasoning=detection.reasoning,
                            markers=detection.detected_markers,
                            scores=detection.scores.model_dump()
                        )
                        save_session.add(analysis)
                        await save_session.commit()

                    completed += 1
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    remaining = (total - completed) / rate if rate > 0 else 0
                    remaining_min = remaining / 60

                    if detection.reasoning and "Error" in detection.reasoning:
                        errors += 1

                    UI.info(
                        f"[{completed}/{total}] "
                        f"({100 * completed // total}%) "
                        f"{article.title[:35]}... "
                        f"| {rate:.1f}/s | ETA: {remaining_min:.1f}min"
                    )

                    # Small delay to respect rate limits
                    await asyncio.sleep(0.3)

            # Process all articles concurrently with semaphore
            tasks = [analyze_one(article) for article in articles]
            await asyncio.gather(*tasks, return_exceptions=True)

            elapsed_total = time.time() - start_time
            UI.info(
                f"Analysis complete: {completed}/{total} articles "
                f"({errors} errors) in {elapsed_total / 60:.1f} minutes "
                f"({completed / elapsed_total:.1f} articles/sec)"
            )


if __name__ == "__main__":
    detector = NewsDetector()
    asyncio.run(detector.run_batch_analysis())
