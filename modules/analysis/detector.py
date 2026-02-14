import asyncio
import logging
import json
from typing import List, Optional
from sqlmodel import select, col
from core.config import Config
from core.database import get_session
from core.sql_models import Article, Analysis
from core.models import FakeNewsDetection, DetectionScores
from core.ui import UI
from core.llm import LLMManager

logger = logging.getLogger("VORTEX.Detector")

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
            # Note: response_schema is Gemini-specific, other providers rely on prompt engineering
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
            # Left join Analysis, filter where Analysis.id is NULL
            stmt = select(Article).outerjoin(Analysis, Article.id == Analysis.article_id).where(Analysis.id == None)
            if limit:
                stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            articles = result.scalars().all()
            
            if not articles:
                UI.info("No unanalyzed articles found.")
                return

            UI.info(f"Found {len(articles)} articles to analyze.")
            
            for article in articles:
                UI.info(f"Analyzing: {article.title[:40]}...")
                
                # Analyze
                detection = await self.analyze_article(article)
                
                # Save to DB
                analysis = Analysis(
                    article_id=article.id,
                    is_fake=detection.is_fake,
                    confidence=detection.confidence_score,
                    reasoning=detection.reasoning,
                    markers=detection.detected_markers,
                    scores=detection.scores.model_dump()
                )
                session.add(analysis)
                await session.commit()
                
                UI.info(f"Saved analysis for article {article.id}")
                
                # Rate limit (2s delay)
                await asyncio.sleep(2.0)

if __name__ == "__main__":
    detector = NewsDetector()
    asyncio.run(detector.run_batch_analysis())
