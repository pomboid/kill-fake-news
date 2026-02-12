"""Tests for modules.analysis.detector — LLM response parsing and fallback logic."""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

from core.models import NewsArticle, FakeNewsDetection, DetectionScores


# ───────────────────── JSON Response Parsing ─────────────────────

class TestLLMResponseParsing:
    """Tests that the detector correctly parses various LLM response formats."""

    def _make_article(self):
        return NewsArticle(
            titulo="Test Article",
            corpo_do_texto="This is a test article with enough content to pass validation.",
            url="https://example.com/test"
        )

    @pytest.mark.asyncio
    async def test_parse_clean_json_response(self):
        """LLM returns clean JSON without markdown fencing."""
        response_text = json.dumps({
            "is_fake": False,
            "confidence_score": 0.2,
            "reasoning": "Article is factually consistent.",
            "detected_markers": [],
            "scores": {
                "factual_consistency": 9,
                "linguistic_bias": 1,
                "sensationalism": 1,
                "source_credibility": 9
            }
        })

        mock_response = MagicMock()
        mock_response.text = response_text

        with patch("modules.analysis.detector.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            mock_genai.configure = MagicMock()

            from modules.analysis.detector import NewsDetector
            detector = NewsDetector.__new__(NewsDetector)
            detector.model = mock_model

            article = self._make_article()
            result = await detector.analyze_article(article)

            assert isinstance(result, FakeNewsDetection)
            assert result.is_fake is False
            assert result.confidence_score == 0.2

    @pytest.mark.asyncio
    async def test_parse_high_confidence_fake(self):
        """LLM returns high-confidence fake detection (structured output returns clean JSON)."""
        response_text = json.dumps({
            "is_fake": True,
            "confidence_score": 0.9,
            "reasoning": "Sensationalist headline.",
            "detected_markers": ["sensationalist headline"],
            "scores": {
                "factual_consistency": 3,
                "linguistic_bias": 7,
                "sensationalism": 9,
                "source_credibility": 4
            }
        })

        mock_response = MagicMock()
        mock_response.text = response_text

        with patch("modules.analysis.detector.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            mock_genai.configure = MagicMock()

            from modules.analysis.detector import NewsDetector
            detector = NewsDetector.__new__(NewsDetector)
            detector.model = mock_model

            article = self._make_article()
            result = await detector.analyze_article(article)

            assert result.is_fake is True
            assert result.confidence_score == 0.9
            assert "sensationalist headline" in result.detected_markers

    @pytest.mark.asyncio
    async def test_fallback_on_error(self):
        """When LLM fails, detector should return safe default."""
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON at all"

        with patch("modules.analysis.detector.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            mock_genai.configure = MagicMock()

            from modules.analysis.detector import NewsDetector
            detector = NewsDetector.__new__(NewsDetector)
            detector.model = mock_model

            article = self._make_article()
            result = await detector.analyze_article(article)

            assert result.is_fake is False
            assert result.confidence_score == 0.0
            assert "Error" in result.reasoning
