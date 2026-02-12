"""Tests for modules.intelligence.collector — URL registry, scraping logic, text cleaning."""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from modules.intelligence.collector import URLRegistry, ContentScraper


# ───────────────────── URLRegistry ─────────────────────

class TestURLRegistry:
    """Tests for URL and title deduplication."""

    def test_empty_registry(self, tmp_path):
        reg = URLRegistry(str(tmp_path / "nonexistent.jsonl"))
        assert not reg.exists("https://example.com", "Test Title")

    def test_add_and_check(self, tmp_path):
        reg = URLRegistry(str(tmp_path / "test.jsonl"))
        reg.add("https://example.com/1", "First Article")
        assert reg.exists("https://example.com/1", "anything")
        assert reg.exists("https://other.com", "First Article")

    def test_normalize_title_case_insensitive(self, tmp_path):
        reg = URLRegistry(str(tmp_path / "test.jsonl"))
        reg.add("https://ex.com", "Notícia Importante Sobre AI")
        # Same title different case
        assert reg.exists("https://other.com", "notícia importante sobre ai")

    def test_normalize_title_ignores_punctuation(self, tmp_path):
        reg = URLRegistry(str(tmp_path / "test.jsonl"))
        reg.add("https://ex.com", "Breaking: News! About (AI)")
        assert reg.exists("https://other.com", "Breaking News About AI")

    def test_load_from_existing_jsonl(self, tmp_path):
        """Registry should load existing URLs/titles from JSONL file."""
        fpath = str(tmp_path / "existing.jsonl")
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(json.dumps({"titulo": "Existing Title", "url": "https://loaded.com", "corpo_do_texto": "x"}) + "\n")
            f.write(json.dumps({"titulo": "Another", "url": "https://another.com", "corpo_do_texto": "y"}) + "\n")

        reg = URLRegistry(fpath)
        assert reg.exists("https://loaded.com", "whatever")
        assert reg.exists("https://whatever.com", "Existing Title")
        assert reg.exists("https://another.com", "xyz")

    def test_ignores_malformed_lines(self, tmp_path):
        """Registry should skip invalid JSON lines without crashing."""
        fpath = str(tmp_path / "bad.jsonl")
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write("not valid json\n")
            f.write(json.dumps({"titulo": "Good", "url": "https://good.com"}) + "\n")
            f.write("{broken json\n")

        reg = URLRegistry(fpath)
        assert reg.exists("https://good.com", "whatever")

    def test_different_urls_same_title(self, tmp_path):
        reg = URLRegistry(str(tmp_path / "test.jsonl"))
        reg.add("https://site-a.com/news/1", "Same Title")
        # Different URL but same title — should be detected as duplicate
        assert reg.exists("https://site-b.com/news/999", "Same Title")


# ───────────────────── ContentScraper._clean_text ─────────────────────

class TestCleanText:
    """Tests for the text cleaning function."""

    def setup_method(self):
        self.scraper = ContentScraper()

    def test_removes_see_more_patterns(self):
        text = "This is content (ver mais) and more text."
        result = self.scraper._clean_text(text)
        assert "(ver mais)" not in result
        assert "content" in result

    def test_removes_veja_mais(self):
        result = self.scraper._clean_text("Texto (veja mais) aqui.")
        assert "(veja mais)" not in result

    def test_removes_leia_tambem(self):
        result = self.scraper._clean_text("Texto leia também outro artigo.")
        assert "leia também" not in result.lower()

    def test_removes_globo_disclaimers(self):
        text = "Content. A Globo poderá vender os dados conforme política."
        result = self.scraper._clean_text(text)
        assert "Globo" not in result

    def test_collapses_whitespace(self):
        result = self.scraper._clean_text("word1    word2\n\n\nword3")
        assert result == "word1 word2 word3"

    def test_empty_string(self):
        assert self.scraper._clean_text("") == ""

    def test_none_input(self):
        assert self.scraper._clean_text(None) == ""


# ───────────────────── ContentScraper._extract_json_ld ─────────────────────

class TestExtractJsonLD:
    """Tests for JSON-LD structured data extraction."""

    def setup_method(self):
        self.scraper = ContentScraper()

    def test_extract_news_article_type(self):
        html = '''
        <html><head>
        <script type="application/ld+json">
        {"@type": "NewsArticle", "headline": "Test Headline", "datePublished": "2024-01-01"}
        </script>
        </head><body></body></html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = self.scraper._extract_json_ld(soup)
        assert result["headline"] == "Test Headline"
        assert result["@type"] == "NewsArticle"

    def test_extract_article_type(self):
        html = '''
        <html><head>
        <script type="application/ld+json">
        {"@type": "Article", "headline": "Article Headline"}
        </script>
        </head><body></body></html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = self.scraper._extract_json_ld(soup)
        assert result["headline"] == "Article Headline"

    def test_extract_from_array(self):
        html = '''
        <html><head>
        <script type="application/ld+json">
        [{"@type": "WebSite"}, {"@type": "NewsArticle", "headline": "From Array"}]
        </script>
        </head><body></body></html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = self.scraper._extract_json_ld(soup)
        assert result["headline"] == "From Array"

    def test_no_json_ld_returns_empty(self):
        html = '<html><head></head><body></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        result = self.scraper._extract_json_ld(soup)
        assert result == {}

    def test_invalid_json_returns_empty(self):
        html = '''
        <html><head>
        <script type="application/ld+json">{broken json</script>
        </head><body></body></html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = self.scraper._extract_json_ld(soup)
        assert result == {}

    def test_empty_script_tag_returns_empty(self):
        html = '''
        <html><head>
        <script type="application/ld+json"></script>
        </head><body></body></html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = self.scraper._extract_json_ld(soup)
        assert result == {}


# ───────────────────── ContentScraper._extract_author ─────────────────────

class TestExtractAuthor:
    def setup_method(self):
        self.scraper = ContentScraper()

    def test_author_as_dict(self):
        json_ld = {"author": {"name": "João Silva", "@type": "Person"}}
        assert self.scraper._extract_author(json_ld) == "João Silva"

    def test_author_as_list_of_dicts(self):
        json_ld = {"author": [{"name": "Maria"}, {"name": "Pedro"}]}
        assert self.scraper._extract_author(json_ld) == "Maria"

    def test_no_author_returns_default(self):
        json_ld = {}
        assert self.scraper._extract_author(json_ld) == "Redação"

    def test_author_dict_without_name(self):
        json_ld = {"author": {"@type": "Person"}}
        assert self.scraper._extract_author(json_ld) == "Redação"


# ───────────────────── ContentScraper._get_config ─────────────────────

class TestGetConfig:
    def setup_method(self):
        self.scraper = ContentScraper()

    def test_known_domain_g1(self):
        config = self.scraper._get_config("g1.globo.com")
        assert config["t"] == "h1.content-head__title"

    def test_known_domain_tecnoblog(self):
        config = self.scraper._get_config("tecnoblog.net")
        assert config["t"] == "h1"

    def test_unknown_domain_returns_fallback(self):
        config = self.scraper._get_config("unknowndomain.com")
        assert config["t"] == "h1"
        assert config["b"] == "article"
