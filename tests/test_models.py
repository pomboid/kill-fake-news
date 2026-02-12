"""Tests for core.models — Pydantic data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from core.models import NewsArticle, DetectionScores, FakeNewsDetection


# ───────────────────── NewsArticle ─────────────────────

class TestNewsArticle:
    """Validates NewsArticle creation, aliases, and defaults."""

    def test_create_with_aliases(self):
        """Articles can be created using Portuguese aliases."""
        art = NewsArticle(
            titulo="Título da Notícia de Teste",
            corpo_do_texto="Conteúdo longo da notícia para teste de validação.",
            url="https://example.com/noticia"
        )
        assert art.title == "Título da Notícia de Teste"
        assert art.content == "Conteúdo longo da notícia para teste de validação."
        assert art.author == "Redação"  # default
        assert art.status == "UNCHECKED"  # default

    def test_create_with_field_names(self):
        """Articles can also be created using English field names."""
        art = NewsArticle(
            title="Test Title",
            content="Some long enough content for testing purposes.",
            url="https://example.com/test"
        )
        assert art.title == "Test Title"

    def test_optional_fields_default_to_none(self):
        art = NewsArticle(
            titulo="Teste",
            corpo_do_texto="Conteúdo",
            url="https://example.com"
        )
        assert art.subtitle is None
        assert art.publish_date is None
        assert art.credibility_score is None

    def test_serialization_uses_aliases(self):
        """model_dump_json(by_alias=True) should produce Portuguese keys."""
        art = NewsArticle(
            titulo="Título",
            corpo_do_texto="Corpo",
            url="https://example.com"
        )
        import json
        data = json.loads(art.model_dump_json(by_alias=True))
        assert "titulo" in data
        assert "corpo_do_texto" in data
        assert "status_verificacao" in data

    def test_missing_required_title_raises(self):
        with pytest.raises(ValidationError):
            NewsArticle(
                corpo_do_texto="Conteúdo",
                url="https://example.com"
            )

    def test_missing_required_content_raises(self):
        with pytest.raises(ValidationError):
            NewsArticle(
                titulo="Titulo",
                url="https://example.com"
            )

    def test_invalid_url_raises(self):
        with pytest.raises(ValidationError):
            NewsArticle(
                titulo="Titulo",
                corpo_do_texto="Conteúdo",
                url="not-a-url"
            )

    def test_deserialization_from_json(self):
        """model_validate_json should work with aliased JSON."""
        raw = '{"titulo":"T","corpo_do_texto":"C","url":"https://ex.com","autor":"João","status_verificacao":"CHECKED"}'
        art = NewsArticle.model_validate_json(raw)
        assert art.title == "T"
        assert art.author == "João"
        assert art.status == "CHECKED"


# ───────────────────── DetectionScores ─────────────────────

class TestDetectionScores:
    def test_valid_scores(self):
        scores = DetectionScores(
            factual_consistency=8,
            linguistic_bias=3,
            sensationalism=2,
            source_credibility=9
        )
        assert scores.factual_consistency == 8

    def test_score_below_zero_raises(self):
        with pytest.raises(ValidationError):
            DetectionScores(
                factual_consistency=-1,
                linguistic_bias=3,
                sensationalism=2,
                source_credibility=9
            )

    def test_score_above_ten_raises(self):
        with pytest.raises(ValidationError):
            DetectionScores(
                factual_consistency=8,
                linguistic_bias=11,
                sensationalism=2,
                source_credibility=9
            )

    def test_boundary_values(self):
        """0 and 10 are valid boundary values."""
        scores = DetectionScores(
            factual_consistency=0,
            linguistic_bias=10,
            sensationalism=0,
            source_credibility=10
        )
        assert scores.factual_consistency == 0
        assert scores.linguistic_bias == 10


# ───────────────────── FakeNewsDetection ─────────────────────

class TestFakeNewsDetection:
    def test_create_detection(self):
        det = FakeNewsDetection(
            is_fake=True,
            confidence_score=0.85,
            reasoning="Headline exaggerates findings.",
            detected_markers=["sensationalist headline", "lack of sources"],
            scores=DetectionScores(
                factual_consistency=3,
                linguistic_bias=7,
                sensationalism=8,
                source_credibility=4
            )
        )
        assert det.is_fake is True
        assert det.confidence_score == 0.85
        assert len(det.detected_markers) == 2

    def test_timestamp_auto_generated(self):
        det = FakeNewsDetection(
            is_fake=False,
            confidence_score=0.1,
            reasoning="Legit.",
            detected_markers=[],
            scores=DetectionScores(
                factual_consistency=9,
                linguistic_bias=1,
                sensationalism=1,
                source_credibility=9
            )
        )
        assert isinstance(det.timestamp, datetime)

    def test_serialization_roundtrip(self):
        """JSON serialization and deserialization should preserve data."""
        import json
        det = FakeNewsDetection(
            is_fake=True,
            confidence_score=0.5,
            reasoning="Test",
            detected_markers=["marker1"],
            scores=DetectionScores(
                factual_consistency=5,
                linguistic_bias=5,
                sensationalism=5,
                source_credibility=5
            )
        )
        raw = det.model_dump_json()
        data = json.loads(raw)
        assert data["is_fake"] is True
        assert data["confidence_score"] == 0.5
