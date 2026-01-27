import asyncio
import requests
import json
import re
import os
import logging
import xml.etree.ElementTree as ET
from typing import Set, List, Optional, Dict
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from core.config import Config
from core.models import NewsArticle
from core.ui import UI

# Logging Setup
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("VORTEX.Collector")

class URLRegistry:
    """Manages crawled URLs and titles with persistent storage for deduplication."""
    def __init__(self, persistent_file: str):
        self.file_path = persistent_file
        self.urls: Set[str] = set()
        self.titles: Set[str] = set()
        self._load()

    def _load(self):
        if not os.path.exists(self.file_path): return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        if 'url' in data: self.urls.add(data['url'])
                        if 'titulo' in data: self.titles.add(self._normalize(data['titulo']))
                    except: continue
        except Exception as e:
            UI.error(f"Registry load error: {e}")

    def _normalize(self, text: str) -> str:
        return re.sub(r'[^\w\s]', '', text.lower()).strip()

    def exists(self, url: str, title: str) -> bool:
        return url in self.urls or self._normalize(title) in self.titles

    def add(self, url: str, title: str):
        self.urls.add(url)
        self.titles.add(self._normalize(title))

class ContentScraper:
    """Handles site-specific extraction for high-quality news content."""
    
    DOMAIN_MAP = {
        "g1.globo.com": {"t": "h1.content-head__title", "s": "h2.content-head__subtitle", "b": "div.mc-article-body", "p": "p.content-text__container"},
        "tecnoblog.net": {"t": "h1", "s": "p.excerpt", "b": "div.texts", "p": "p"},
        "tecmundo.com.br": {"t": "h1.tec--article__header__title", "s": "div.tec--article__header__description", "b": "div.tec--article__body", "p": "p"},
        "olhardigital.com.br": {"t": "h1.post-title", "s": "p.post-excerpt", "b": "div.post-content", "p": "p"},
        "tudocelular.com": {"t": "h2.title_main", "s": "p.subtitle", "b": "div.text_content", "p": "p"},
        "canaltech.com.br": {"t": "h1", "s": "div.c-card__title", "b": "div.c-body", "p": "p"},
        "inovacaotecnologica.com.br": {"t": "h1", "s": None, "b": "div#texto", "p": "p"},
        "bbc.com": {"t": "h1", "s": None, "b": "main", "p": "p"}
    }

    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        }

    def _clean_text(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r'[^\x00-\x7F\u00C0-\u017F\s,.?!()\-:;\"\'\/]', '', text)
        patterns = [r'\(ver mais\)', r'\(veja mais\)', r'leia também', r'veja também', r'baixe o app', r'Esta reportagem foi produzida.*', r'Caso o leitor opte.*', r'A Globo poderá.*', r'Esclarecemos que a Globo.*']
        for p in patterns: text = re.sub(p, '', text, flags=re.IGNORECASE | re.DOTALL)
        return re.sub(r'\s+', ' ', text).strip()

    def scrape(self, url: str) -> Optional[NewsArticle]:
        try:
            domain = urlparse(url).netloc.replace("www.", "")
            resp = requests.get(url, headers=self.headers, timeout=20)
            resp.raise_for_status()
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            json_ld = self._extract_json_ld(soup)
            config = self._get_config(domain)

            title = self._clean_text(json_ld.get('headline') or self._select(soup, config.get("t")))
            if not title or len(title) < 10: return None

            content = self._extract_body(soup, config)
            if not content or len(content) < 300: return None

            return NewsArticle(
                titulo=title,
                subtitulo=self._clean_text(self._select(soup, config.get("s"))),
                autor=self._extract_author(json_ld),
                data_publicacao=json_ld.get('datePublished', ''),
                url=url,
                corpo_do_texto=content
            )
        except Exception as e:
            return None

    def _get_config(self, domain: str) -> dict:
        for key, val in self.DOMAIN_MAP.items():
            if key in domain: return val
        return {"t": "h1", "s": None, "b": "article", "p": "p"}

    def _select(self, soup, selector) -> str:
        if not selector: return ""
        tag = soup.select_one(selector)
        return tag.get_text(strip=True) if tag else ""

    def _extract_json_ld(self, soup) -> dict:
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            if not script.string: continue
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']: return item
                    return data[0]
                if data.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']: return data
            except: continue
        return {}

    def _extract_author(self, json_ld) -> str:
        auth = json_ld.get('author')
        if isinstance(auth, list) and auth: auth = auth[0]
        if isinstance(auth, dict): return auth.get('name', "Redação")
        return "Redação"

    def _extract_body(self, soup, config) -> str:
        container = soup.select_one(config["b"]) if config["b"] else None
        if not container: return ""
        
        for noise in container.select('script, style, iframe, ul.post-tags, div.social-buttons, div.advertisement, aside'):
            noise.decompose()

        paragraphs = container.select(config["p"]) if config["p"] else container.find_all('p')
        text_blocks = []
        for p in paragraphs:
            txt = self._clean_text(p.get_text(separator=' ', strip=True))
            if len(txt) > 60:
                if txt not in text_blocks: text_blocks.append(txt)
        return "\n\n".join(text_blocks)

class RSSCollectorEngine:
    """Robust RSS Engine with multi-source deduplication and improved XML parsing."""
    def __init__(self, sources: List[Dict]):
        self.sources = sources
        self.registry = URLRegistry(Config.REFERENCE_FILE_PATH)
        self.scraper = ContentScraper()

    def run(self):
        UI.info(f"Global Sync: {len(self.sources)} intelligence sources.")
        total_saved = 0

        for src in self.sources:
            UI.info(f"Target: {src['name']}")
            try:
                resp = requests.get(src['url'], headers=self.scraper.headers, timeout=25)
                resp.raise_for_status()
                
                # Use regex to find links and titles in XML to avoid namespace issues
                content = resp.text
                items = re.findall(r'<(item|entry).*?>(.*?)</\1>', content, re.DOTALL)
                
                for _, item_content in items:
                    link_match = re.search(r'<link.*?>(.*?)</link>', item_content)
                    if not link_match:
                        link_match = re.search(r'<link.*?href="(.*?)"', item_content)
                    
                    title_match = re.search(r'<title.*?>(.*?)</title>', item_content)
                    
                    if not link_match or not title_match: continue
                    
                    link = link_match.group(1).strip()
                    title = title_match.group(1).strip()
                    # Clean title if it contains CDATA
                    title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)

                    if self.registry.exists(link, title): continue
                    
                    article = self.scraper.scrape(link)
                    if article:
                        self._persist(article)
                        self.registry.add(link, article.title)
                        total_saved += 1
                        UI.info(f"[{src['name']}] Caught: {article.title[:45]}...")
                        
            except Exception as e:
                UI.error(f"Source Failure ({src['name']}): {e}")

        UI.info(f"Sync complete. {total_saved} new entries.")

    def _persist(self, article: NewsArticle):
        os.makedirs(os.path.dirname(Config.REFERENCE_FILE_PATH), exist_ok=True)
        with open(Config.REFERENCE_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(article.model_dump_json(by_alias=True) + "\n")

def run_collector():
    sources = [
        {"name": "G1 Tecnologia", "url": "https://g1.globo.com/rss/g1/tecnologia/"},
        {"name": "BBC Brasil", "url": "https://feeds.bbci.co.uk/portuguese/rss.xml"},
        {"name": "Tecnoblog", "url": "https://tecnoblog.net/feed/"},
        {"name": "Tecmundo", "url": "https://rss.tecmundo.com.br/feed"},
        {"name": "Olhar Digital", "url": "https://olhardigital.com.br/rss"},
        {"name": "TudoCelular", "url": "https://www.tudocelular.com/feed/"},
        {"name": "Canaltech", "url": "https://canaltech.com.br/rss/"},
        {"name": "Inovação Tecnológica", "url": "https://www.inovacaotecnologica.com.br/boletim/rss.xml"}
    ]
    engine = RSSCollectorEngine(sources)
    engine.run()

if __name__ == "__main__":
    run_collector()
