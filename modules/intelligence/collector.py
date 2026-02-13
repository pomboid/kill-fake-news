import asyncio
import re
import logging
import json
from typing import List, Optional, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import httpx
from datetime import datetime

from sqlmodel import select
from core.database import get_session
from core.sql_models import Article, Source, RSSFeed
from core.ui import UI

# Logging Setup
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("VORTEX.Collector")

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
        "bbc.com": {"t": "h1", "s": None, "b": "main", "p": "p"},
        "folha.uol.com.br": {"t": "h1.c-content-head__title", "s": "h2.c-content-head__subtitle", "b": "div.c-news__body", "p": "p"},
        "noticias.uol.com.br": {"t": "h1.pg-title", "s": "p.pg-subtitle", "b": "div.text", "p": "p"},
        "cnnbrasil.com.br": {"t": "h1.post__title", "s": "p.post__excerpt", "b": "div.post__content", "p": "p"},
        "estadao.com.br": {"t": "h1.n-title", "s": "h2.n-subtitle", "b": "div.n-content", "p": "p"}
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

    async def scrape(self, client: httpx.AsyncClient, url: str) -> Optional[Article]:
        try:
            domain = urlparse(url).netloc.replace("www.", "")
            resp = await client.get(url, timeout=20)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            json_ld = self._extract_json_ld(soup)
            config = self._get_config(domain)

            title = self._clean_text(json_ld.get('headline') or self._select(soup, config.get("t")))
            if not title or len(title) < 10: return None

            content = self._extract_body(soup, config)
            if not content or len(content) < 300: return None
            
            # Parse date
            pub_date = None
            date_str = json_ld.get('datePublished', '')
            if date_str:
                try:
                    pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except: pass

            return Article(
                title=title,
                subtitle=self._clean_text(self._select(soup, config.get("s"))),
                author=self._extract_author(json_ld),
                published_at=pub_date,
                url=url,
                content=content,
                created_at=datetime.utcnow()
            )
        except Exception as e:
            # logger.warning(f"Scrape failed for {url}: {e}")
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
    """Robust RSS Engine with DB storage and multi-format support."""

    def __init__(self):
        self.scraper = ContentScraper()

    def _parse_rss(self, content: str) -> List[str]:
        """Parser para RSS 2.0 e RSS 0.91"""
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        urls = []
        for item in items:
            link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
            if link_match:
                url = link_match.group(1).strip()
                # Remove CDATA tags if present
                url = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', url)
                urls.append(url.strip())
        return urls

    def _parse_atom(self, content: str) -> List[str]:
        """Parser para Atom feeds"""
        entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)
        urls = []
        for entry in entries:
            # Atom uses <link href="..."/>
            link_match = re.search(r'<link[^>]*href=["\']([^"\']+)["\']', entry)
            if link_match:
                urls.append(link_match.group(1).strip())
        return urls

    def _parse_sitemap(self, content: str) -> List[str]:
        """Parser para News Sitemap XML (CNN Brasil)"""
        urls_blocks = re.findall(r'<url>(.*?)</url>', content, re.DOTALL)
        urls = []
        for url_block in urls_blocks:
            loc_match = re.search(r'<loc>(.*?)</loc>', url_block)
            if loc_match:
                urls.append(loc_match.group(1).strip())
        return urls

    async def run(self, limit: int = None):
        """Coleta notícias de todos os feeds ativos no banco de dados"""
        UI.info(f"Connecting to database...")

        async for session in get_session():
            # Buscar todos os feeds ativos do banco de dados
            statement = select(RSSFeed).join(Source).where(
                RSSFeed.is_active == True,
                Source.is_active == True
            )
            result = await session.execute(statement)
            feeds = result.scalars().all()

            if not feeds:
                UI.warning("⚠️  Nenhum feed ativo encontrado no banco de dados")
                UI.warning("   Execute: python scripts/seed_rss_feeds.py")
                return

            UI.info(f"🔍 Coletando de {len(feeds)} feeds RSS ativos")

            async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=self.scraper.headers) as client:
                total_collected = 0

                for feed in feeds:
                    source_name = feed.source.name
                    feed_category = feed.category or "Principal"

                    UI.info(f"📡 [{source_name}] {feed_category}")

                    try:
                        # Fetch feed content
                        resp = await client.get(feed.feed_url, timeout=30)
                        resp.raise_for_status()
                        content = resp.text

                        # Parse baseado no tipo de feed
                        if feed.feed_type == "sitemap":
                            article_urls = self._parse_sitemap(content)
                        elif feed.feed_type == "atom":
                            article_urls = self._parse_atom(content)
                        else:  # rss2, rss091
                            article_urls = self._parse_rss(content)

                        UI.info(f"   Encontrados {len(article_urls)} artigos")

                        # Processar artigos
                        feed_collected_count = 0
                        for article_url in article_urls:
                            if limit and total_collected >= limit:
                                break

                            # Verificar se artigo já existe
                            stmt = select(Article).where(Article.url == article_url)
                            existing = (await session.execute(stmt)).scalars().first()
                            if existing:
                                continue

                            # Fazer scraping do artigo completo
                            article = await self.scraper.scrape(client, article_url)
                            if article:
                                article.source_id = feed.source_id
                                session.add(article)
                                await session.commit()
                                UI.info(f"   ✅ {article.title[:50]}...")
                                feed_collected_count += 1
                                total_collected += 1
                            else:
                                # Artigo rejeitado (conteúdo curto ou erro de parse)
                                pass

                        # Atualizar estatísticas do feed
                        feed.last_fetched = datetime.utcnow()
                        feed.fetch_count += 1
                        feed.error_count = 0
                        feed.last_error = None
                        await session.commit()

                        if feed_collected_count > 0:
                            UI.info(f"   📰 Coletados: {feed_collected_count} novos artigos")

                    except Exception as e:
                        logger.error(f"Erro ao coletar feed {feed.feed_url}: {e}")
                        UI.error(f"   ❌ Erro: {str(e)[:80]}")

                        # Atualizar contador de erros
                        feed.error_count += 1
                        feed.last_error = str(e)[:500]
                        await session.commit()

                UI.info(f"\n🎉 Coleta concluída! Total de artigos coletados: {total_collected}")

async def run_collector(limit: int = None):
    engine = RSSCollectorEngine()
    await engine.run(limit=limit)

if __name__ == "__main__":
    asyncio.run(run_collector())
