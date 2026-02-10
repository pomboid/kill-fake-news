"""Tests for the VORTEX API server endpoints."""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Mock the scheduler BEFORE importing server
import scheduler as _sched_module
_sched_module.start_scheduler = MagicMock(return_value=MagicMock(running=False))

from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Headers with valid API key."""
    return {"X-API-Key": "test-secret-key"}


class TestHealthCheck:
    """Health endpoint — no auth required."""

    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert data["version"] == "1.0.0"


class TestAuthentication:
    """API key authentication tests."""

    def test_no_auth_when_key_empty(self, client):
        """When VORTEX_API_KEY is empty, API is open."""
        with patch("server.VORTEX_API_KEY", ""):
            r = client.get("/api/status")
            assert r.status_code == 200

    def test_401_when_key_required_but_missing(self, client):
        """When key is set but not provided, should get 401."""
        with patch("server.VORTEX_API_KEY", "test-secret-key"):
            r = client.get("/api/status")
            assert r.status_code == 401

    def test_valid_key_passes(self, client, auth_headers):
        """Valid API key returns 200."""
        with patch("server.VORTEX_API_KEY", "test-secret-key"):
            r = client.get("/api/status", headers=auth_headers)
            assert r.status_code == 200

    def test_invalid_key_rejected(self, client):
        """Wrong key returns 401."""
        with patch("server.VORTEX_API_KEY", "test-secret-key"):
            r = client.get("/api/status", headers={"X-API-Key": "wrong"})
            assert r.status_code == 401


class TestStatusEndpoint:
    """GET /api/status"""

    def test_returns_system_info(self, client):
        with patch("server.VORTEX_API_KEY", ""):
            r = client.get("/api/status")
            data = r.json()
            assert "reference_articles" in data
            assert "analyzed_articles" in data
            assert "uptime_seconds" in data
            assert "model" in data


class TestVerifyEndpoint:
    """POST /api/verify — input validation."""

    def test_rejects_short_claim(self, client):
        with patch("server.VORTEX_API_KEY", ""):
            r = client.post("/api/verify", json={"claim": "short"})
            assert r.status_code == 422

    def test_rejects_long_claim(self, client):
        with patch("server.VORTEX_API_KEY", ""):
            r = client.post("/api/verify", json={"claim": "x" * 2001})
            assert r.status_code == 422


class TestQualityEndpoint:
    """GET /api/quality"""

    def test_returns_score_structure(self, client):
        with patch("server.VORTEX_API_KEY", ""):
            r = client.get("/api/quality")
            data = r.json()
            assert "total" in data
            assert "valid" in data
            assert "score" in data


class TestDashboard:
    """GET / — HTML dashboard."""

    def test_serves_html(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "VORTEX" in r.text
        assert "text/html" in r.headers["content-type"]
