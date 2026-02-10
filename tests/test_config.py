"""Tests for core.config — API key validation logic."""

import pytest
from unittest.mock import patch


class TestRequireApiKey:
    """Tests that require_api_key raises SystemExit when key is missing."""

    def test_raises_when_no_key(self):
        with patch("core.config.Config.GEMINI_API_KEY", None):
            from core.config import Config
            with pytest.raises(SystemExit) as exc_info:
                Config.require_api_key()
            assert "ERRO FATAL" in str(exc_info.value)
            assert "GEMINI_API_KEY" in str(exc_info.value)

    def test_passes_when_key_exists(self):
        with patch("core.config.Config.GEMINI_API_KEY", "test-key-12345"):
            from core.config import Config
            # Should not raise
            Config.require_api_key()

    def test_error_message_includes_instructions(self):
        with patch("core.config.Config.GEMINI_API_KEY", None):
            from core.config import Config
            with pytest.raises(SystemExit) as exc_info:
                Config.require_api_key()
            msg = str(exc_info.value)
            assert ".env" in msg
            assert "GEMINI_API_KEY" in msg
