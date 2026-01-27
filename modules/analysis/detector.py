
import json
import os
import logging
from typing import List, Optional
import google.generativeai as genai
from core.config import Config
from core.models import NewsArticle, FakeNewsDetection, DetectionScores
from core.ui import UI

logger = logging.getLogger("VORTEX.Detector")

class NewsDetector:
    """Analyzes news articles for signs of misinformation using LLM."""
    def __init__(self):
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

    async def analyze_article(self, article: NewsArticle) -> FakeNewsDetection:
        prompt = f"""
        Analyze the following news article for potential misinformation, fake news markers, and bias.
        
        TITLE: {article.title}
        CONTENT: {article.content}
        
        Provide your analysis in strict JSON format with the following keys:
        - is_fake: boolean
        - confidence_score: float (0.0 to 1.0)
        - reasoning: string (brief explanation)
        - detected_markers: list of strings (e.g., "sensationalist headline", "lack of sources", "logical fallacy")
        - scores: object with:
            - factual_consistency: int (0-10)
            - linguistic_bias: int (0-10)
            - sensationalism: int (0-10)
            - source_credibility: int (0-10)
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Find JSON in response
            json_match = response.text.strip()
            if "```json" in json_match:
                json_match = json_match.split("```json")[1].split("```")[0].strip()
            
            data = json.loads(json_match)
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

    async def run_batch_analysis(self, limit: int = 5):
        articles = self._load_data()
        if not articles: return

        # Limit to avoid huge costs/time during testing
        targets = articles[:limit]
        UI.info(f"Analyzing {len(targets)} articles...")

        results = []
        for art in targets:
            UI.info(f"Checking: {art.title[:40]}...")
            detection = await self.analyze_article(art)
            results.append({
                "article": json.loads(art.model_dump_json(by_alias=True)),
                "detection": json.loads(detection.model_dump_json())
            })

        self._save(results)
        UI.info(f"Analysis complete. Results saved to {self.output_path}")

    def _save(self, results: List[dict]):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for res in results:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    import asyncio
    detector = NewsDetector()
    asyncio.run(detector.run_batch_analysis())
