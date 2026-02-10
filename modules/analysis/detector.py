
import json
import os
import asyncio
import logging
from typing import List, Optional, Set
import google.generativeai as genai
from core.config import Config
from core.models import NewsArticle, FakeNewsDetection, DetectionScores
from core.ui import UI

logger = logging.getLogger("VORTEX.Detector")

class NewsDetector:
    """Analyzes news articles for signs of misinformation using LLM."""
    
    # Max concurrent API calls
    MAX_CONCURRENCY = 3

    def __init__(self):
        Config.require_api_key()
        self.input_path = Config.REFERENCE_FILE_PATH
        self.output_path = Config.ANALYSIS_FILE_PATH
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.LLM_MODEL_NAME)

    def _load_data(self) -> List[NewsArticle]:
        if not os.path.exists(self.input_path):
            UI.error(f"Input file missing: {self.input_path}")
            return []
        
        articles = []
        with open(self.input_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    articles.append(NewsArticle.model_validate_json(line))
                except Exception as e:
                    logger.warning(f"Skipping invalid record: {e}")
        return articles

    def _load_analyzed_urls(self) -> Set[str]:
        """Load URLs that have already been analyzed (cache)."""
        analyzed = set()
        if not os.path.exists(self.output_path):
            return analyzed
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        url = data.get("article", {}).get("url", "")
                        if url:
                            analyzed.add(url)
                    except Exception:
                        continue
        except Exception:
            pass
        return analyzed

    async def analyze_article(self, article: NewsArticle) -> FakeNewsDetection:
        prompt = f"""
        Analyze the following news article for potential misinformation, fake news markers, and bias.
        
        TITLE: {article.title}
        CONTENT: {article.content}
        
        Evaluate and return:
        - is_fake: whether the article is fake news
        - confidence_score: your confidence (0.0 to 1.0)
        - reasoning: brief explanation
        - detected_markers: list of markers found (e.g., "sensationalist headline", "lack of sources")
        - scores: factual_consistency, linguistic_bias, sensationalism, source_credibility (each 0-10)
        """
        
        # Structured output schema for Gemini
        response_schema = {
            "type": "object",
            "properties": {
                "is_fake": {"type": "boolean"},
                "confidence_score": {"type": "number"},
                "reasoning": {"type": "string"},
                "detected_markers": {"type": "array", "items": {"type": "string"}},
                "scores": {
                    "type": "object",
                    "properties": {
                        "factual_consistency": {"type": "integer"},
                        "linguistic_bias": {"type": "integer"},
                        "sensationalism": {"type": "integer"},
                        "source_credibility": {"type": "integer"}
                    },
                    "required": ["factual_consistency", "linguistic_bias", "sensationalism", "source_credibility"]
                }
            },
            "required": ["is_fake", "confidence_score", "reasoning", "detected_markers", "scores"]
        }
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )
            data = json.loads(response.text)
            return FakeNewsDetection(**data)
        except Exception as e:
            logger.error(f"Analysis failed for {article.title[:20]}: {e}")
            # Return a default "safe" but flagged as error record
            return FakeNewsDetection(
                is_fake=False,
                confidence_score=0.0,
                reasoning=f"Error during analysis: {str(e)}",
                detected_markers=[],
                scores=DetectionScores(factual_consistency=5, linguistic_bias=5, sensationalism=5, source_credibility=5)
            )

    async def _analyze_with_semaphore(self, sem: asyncio.Semaphore, article: NewsArticle) -> dict:
        """Analyze a single article respecting concurrency limits."""
        async with sem:
            UI.info(f"Checking: {article.title[:40]}...")
            detection = await self.analyze_article(article)
            return {
                "article": json.loads(article.model_dump_json(by_alias=True)),
                "detection": json.loads(detection.model_dump_json())
            }

    async def run_batch_analysis(self, limit: int = 5):
        articles = self._load_data()
        if not articles: return

        # Cache: skip already analyzed articles
        analyzed_urls = self._load_analyzed_urls()
        new_articles = [a for a in articles if str(a.url) not in analyzed_urls]
        
        if not new_articles:
            UI.info("All articles have already been analyzed. Nothing to do.")
            return

        skipped = len(articles) - len(new_articles)
        if skipped > 0:
            UI.info(f"Cache: skipping {skipped} already analyzed articles.")

        # Limit to avoid huge costs/time
        targets = new_articles[:limit]
        UI.info(f"Analyzing {len(targets)} articles (concurrency: {self.MAX_CONCURRENCY})...")

        # Parallel analysis with semaphore
        sem = asyncio.Semaphore(self.MAX_CONCURRENCY)
        tasks = [self._analyze_with_semaphore(sem, art) for art in targets]
        results = await asyncio.gather(*tasks)

        self._save(list(results))
        UI.info(f"Analysis complete. {len(results)} new results saved to {self.output_path}")

    def _save(self, results: List[dict]):
        """Append results to existing file (instead of overwriting)."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'a', encoding='utf-8') as f:
            for res in results:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    import asyncio
    detector = NewsDetector()
    asyncio.run(detector.run_batch_analysis())

