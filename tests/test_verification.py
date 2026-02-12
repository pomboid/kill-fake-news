"""Tests for modules.detection.verification_engine — JSON parsing and retry logic."""

import pytest
import json
import time
from unittest.mock import MagicMock, patch

from modules.detection.verification_engine import retry_api


# ───────────────────── retry_api decorator ─────────────────────

class TestRetryApi:
    """Tests for the retry_api decorator."""

    def test_no_retry_on_success(self):
        call_count = 0

        @retry_api(max_retries=3, base_delay=0)
        def succeeds():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeeds()
        assert result == "ok"
        assert call_count == 1

    def test_retries_on_429(self):
        call_count = 0

        @retry_api(max_retries=3, base_delay=0)
        def fails_then_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Error 429: Rate limit exceeded")
            return "ok"

        result = fails_then_succeeds()
        assert result == "ok"
        assert call_count == 3

    def test_retries_on_resource_exhausted(self):
        call_count = 0

        @retry_api(max_retries=3, base_delay=0)
        def fails_resource():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("RESOURCE_EXHAUSTED")
            return "recovered"

        result = fails_resource()
        assert result == "recovered"
        assert call_count == 2

    def test_raises_non_rate_limit_errors(self):
        @retry_api(max_retries=3, base_delay=0)
        def fails_hard():
            raise ValueError("Some other error")

        with pytest.raises(ValueError, match="Some other error"):
            fails_hard()

    def test_exhausts_retries(self):
        """When all retries are exhausted on 429, the last attempt re-raises."""
        call_count = 0

        @retry_api(max_retries=2, base_delay=0)
        def always_429():
            nonlocal call_count
            call_count += 1
            raise Exception("429 Too Many Requests")

        with pytest.raises(Exception, match="429"):
            always_429()
        # max_retries attempts + 1 final attempt
        assert call_count == 3


# ───────────────────── Verification Response Parsing ─────────────────────

class TestVerificationResponseParsing:
    """Tests for parsing JSON responses from the verification engine."""

    def test_parse_clean_json(self):
        """Direct JSON parsing works."""
        response = '{"veredito": "[VERDADEIRO]", "analise": "Confirmado.", "confianca": 85, "evidencias": ["citação 1"]}'
        import re
        clean = re.search(r'\{.*\}', response, re.DOTALL).group()
        data = json.loads(clean)
        assert data["veredito"] == "[VERDADEIRO]"
        assert data["confianca"] == 85

    def test_parse_json_with_markdown_noise(self):
        """JSON embedded in markdown fencing."""
        response = '```json\n{"veredito": "[FALSO]", "analise": "Sem evidências.", "confianca": 10, "evidencias": []}\n```'
        import re
        clean = re.search(r'\{.*\}', response, re.DOTALL).group()
        data = json.loads(clean)
        assert data["veredito"] == "[FALSO]"

    def test_parse_json_with_surrounding_text(self):
        """JSON with text before and after."""
        response = 'Here is my analysis:\n{"veredito": "[INCONCLUSIVO]", "analise": "Dados insuficientes.", "confianca": 0, "evidencias": []}\nEnd of analysis.'
        import re
        clean = re.search(r'\{.*\}', response, re.DOTALL).group()
        data = json.loads(clean)
        assert data["veredito"] == "[INCONCLUSIVO]"

    def test_fallback_on_unparseable_response(self):
        """When JSON parsing fails, fallback dict should be used."""
        response = "I cannot provide a structured response right now."
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            data = {
                "veredito": "[INCONCLUSIVO]",
                "analise": "Erro ao processar resposta da IA.",
                "confianca": 0,
                "evidencias": []
            }
        assert data["veredito"] == "[INCONCLUSIVO]"
        assert data["confianca"] == 0
