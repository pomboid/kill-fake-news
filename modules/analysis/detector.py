import asyncio
import logging
import time
from typing import Optional
from sqlmodel import select
from sqlalchemy import func
from core.config import Config
from core.database import get_session
from core.sql_models import Article, Analysis
from core.models import FakeNewsDetection, DetectionScores
from core.ui import UI
from core.llm import LLMManager

logger = logging.getLogger("VORTEX.Detector")

# Process 50 articles per batch to avoid memory/task overload
ANALYZE_BATCH_SIZE = 50
# 3 concurrent LLM requests per batch (gpt-4o-mini: 500 RPM, 200K TPM)
ANALYZE_CONCURRENCY = 3


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

        # Count total unanalyzed articles
        async for session in get_session():
            count_stmt = (
                select(func.count(Article.id))
                .outerjoin(Analysis, Article.id == Analysis.article_id)
                .where(Analysis.id == None)
            )
            total = (await session.execute(count_stmt)).scalar()

        if limit:
            total = min(total, limit)

        if total == 0:
            UI.info("No unanalyzed articles found.")
            return

        UI.info(f"Found {total} articles to analyze (batches of {ANALYZE_BATCH_SIZE}, concurrency={ANALYZE_CONCURRENCY}).")

        completed = 0
        errors = 0
        start_time = time.time()

        while completed < total:
            # Fetch next batch of unanalyzed articles
            fetch_size = min(ANALYZE_BATCH_SIZE, total - completed)
            async for session in get_session():
                stmt = (
                    select(Article)
                    .outerjoin(Analysis, Article.id == Analysis.article_id)
                    .where(Analysis.id == None)
                    .limit(fetch_size)
                )
                result = await session.execute(stmt)
                batch = result.scalars().all()

            if not batch:
                break

            semaphore = asyncio.Semaphore(ANALYZE_CONCURRENCY)

            async def analyze_one(art: Article):
                nonlocal completed, errors
                async with semaphore:
                    detection = await self.analyze_article(art)

                    async for save_session in get_session():
                        analysis = Analysis(
                            article_id=art.id,
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

                    if detection.reasoning and "Error" in detection.reasoning:
                        errors += 1

                    UI.info(
                        f"[{completed}/{total}] "
                        f"({100 * completed // total}%) "
                        f"{art.title[:35]}... "
                        f"| {rate:.1f}/s | ETA: {remaining / 60:.1f}min"
                    )

                    await asyncio.sleep(0.5)

            tasks = [analyze_one(a) for a in batch]
            await asyncio.gather(*tasks, return_exceptions=True)

            batch_num = (completed // ANALYZE_BATCH_SIZE) + 1
            UI.info(f"Batch {batch_num} complete ({completed}/{total} total)")

        elapsed_total = time.time() - start_time
        if completed > 0:
            UI.info(
                f"Analysis complete: {completed}/{total} articles "
                f"({errors} errors) in {elapsed_total / 60:.1f} minutes "
                f"({completed / elapsed_total:.1f} articles/sec)"
            )


if __name__ == "__main__":
    detector = NewsDetector()
    asyncio.run(detector.run_batch_analysis())
