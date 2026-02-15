"""
Script para popular banco de dados com URLs RSS de todas as fontes

Este script adiciona:
- 19 Sources (organizacoes de noticias + Google News)
- ~200+ RSS Feeds (URLs RSS validas)

Formatos suportados:
- RSS 2.0 (maioria das fontes)
- RSS 0.91 (Folha)
- Atom (BBC Brasil)

Uso:
    python scripts/seed_rss_feeds.py
"""
import asyncio
import sys
from pathlib import Path

# Adicionar diretorio raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import AsyncSession, engine
from core.sql_models import Source, RSSFeed
from sqlmodel import select

# ─── Dados de Sources ────────────────────────────────────────────
SOURCES = [
    # --- Fontes originais ---
    {"name": "UOL", "display_name": "UOL Noticias", "website_url": "https://www.uol.com.br"},
    {"name": "G1", "display_name": "G1", "website_url": "https://g1.globo.com"},
    {"name": "Folha", "display_name": "Folha de S.Paulo", "website_url": "https://www.folha.uol.com.br"},
    {"name": "BBC Brasil", "display_name": "BBC Brasil", "website_url": "https://www.bbc.com/portuguese"},
    {"name": "CNN Brasil", "display_name": "CNN Brasil", "website_url": "https://www.cnnbrasil.com.br"},
    {"name": "Estadao", "display_name": "Estadao", "website_url": "https://www.estadao.com.br"},
    # --- Novas fontes brasileiras ---
    {"name": "Agencia Brasil", "display_name": "Agencia Brasil (EBC)", "website_url": "https://agenciabrasil.ebc.com.br"},
    {"name": "R7", "display_name": "R7 Noticias", "website_url": "https://noticias.r7.com"},
    {"name": "Gazeta do Povo", "display_name": "Gazeta do Povo", "website_url": "https://www.gazetadopovo.com.br"},
    {"name": "Carta Capital", "display_name": "Carta Capital", "website_url": "https://www.cartacapital.com.br"},
    {"name": "The Intercept", "display_name": "The Intercept Brasil", "website_url": "https://www.intercept.com.br"},
    {"name": "Poder360", "display_name": "Poder360", "website_url": "https://www.poder360.com.br"},
    {"name": "Terra", "display_name": "Terra Noticias", "website_url": "https://www.terra.com.br"},
    {"name": "InfoMoney", "display_name": "InfoMoney", "website_url": "https://www.infomoney.com.br"},
    {"name": "Metropoles", "display_name": "Metropoles", "website_url": "https://www.metropoles.com"},
    {"name": "Correio Braziliense", "display_name": "Correio Braziliense", "website_url": "https://www.correiobraziliense.com.br"},
    {"name": "Brasil de Fato", "display_name": "Brasil de Fato", "website_url": "https://www.brasildefato.com.br"},
    {"name": "Nexo Jornal", "display_name": "Nexo Jornal", "website_url": "https://www.nexojornal.com.br"},
    # --- Google News (feeds dinamicos, sempre frescos) ---
    {"name": "Google News BR", "display_name": "Google News Brasil", "website_url": "https://news.google.com"},
]

# ─── URLs RSS por Fonte ──────────────────────────────────────────
RSS_FEEDS = {
    "UOL": [
        {"url": "https://rss.uol.com.br/feed/noticias.xml", "type": "rss2", "category": "Noticias"},
        {"url": "https://rss.uol.com.br/feed/tecnologia.xml", "type": "rss2", "category": "Tecnologia"},
        {"url": "https://rss.uol.com.br/feed/economia.xml", "type": "rss2", "category": "Economia"},
        {"url": "https://rss.uol.com.br/feed/jogos.xml", "type": "rss2", "category": "Jogos"},
        {"url": "https://rss.uol.com.br/feed/cinema.xml", "type": "rss2", "category": "Cinema"},
        {"url": "https://rss.uol.com.br/feed/vestibular.xml", "type": "rss2", "category": "Vestibular"},
        {"url": "https://rss.uol.com.br/feed/comecar-o-dia.xml", "type": "rss2", "category": "Comecar o Dia"},
    ],

    "G1": [
        # Categorias nacionais
        {"url": "https://g1.globo.com/rss/g1/", "type": "rss2", "category": "Principal"},
        {"url": "https://g1.globo.com/rss/g1/brasil/", "type": "rss2", "category": "Brasil"},
        {"url": "https://g1.globo.com/rss/g1/ciencia-e-saude/", "type": "rss2", "category": "Ciencia e Saude"},
        {"url": "https://g1.globo.com/rss/g1/economia/", "type": "rss2", "category": "Economia"},
        {"url": "https://g1.globo.com/rss/g1/educacao/", "type": "rss2", "category": "Educacao"},
        {"url": "https://g1.globo.com/rss/g1/mundo/", "type": "rss2", "category": "Mundo"},
        {"url": "https://g1.globo.com/rss/g1/natureza/", "type": "rss2", "category": "Natureza"},
        {"url": "https://g1.globo.com/rss/g1/pop-arte/", "type": "rss2", "category": "Pop & Arte"},
        {"url": "https://g1.globo.com/rss/g1/tecnologia/", "type": "rss2", "category": "Tecnologia"},
        {"url": "https://g1.globo.com/rss/g1/politica/", "type": "rss2", "category": "Politica"},
        # Estados principais (maior populacao)
        {"url": "https://g1.globo.com/rss/g1/sao-paulo/", "type": "rss2", "category": "Sao Paulo"},
        {"url": "https://g1.globo.com/rss/g1/rio-de-janeiro/", "type": "rss2", "category": "Rio de Janeiro"},
        {"url": "https://g1.globo.com/rss/g1/minas-gerais/", "type": "rss2", "category": "Minas Gerais"},
        {"url": "https://g1.globo.com/rss/g1/bahia/", "type": "rss2", "category": "Bahia"},
        {"url": "https://g1.globo.com/rss/g1/rs/rio-grande-do-sul/", "type": "rss2", "category": "Rio Grande do Sul"},
        {"url": "https://g1.globo.com/rss/g1/pr/parana/", "type": "rss2", "category": "Parana"},
        {"url": "https://g1.globo.com/rss/g1/pernambuco/", "type": "rss2", "category": "Pernambuco"},
        {"url": "https://g1.globo.com/rss/g1/ceara/", "type": "rss2", "category": "Ceara"},
        {"url": "https://g1.globo.com/rss/g1/distrito-federal/", "type": "rss2", "category": "Distrito Federal"},
        {"url": "https://g1.globo.com/rss/g1/goias/", "type": "rss2", "category": "Goias"},
        {"url": "https://g1.globo.com/rss/g1/pa/para/", "type": "rss2", "category": "Para"},
        {"url": "https://g1.globo.com/rss/g1/sc/santa-catarina/", "type": "rss2", "category": "Santa Catarina"},
        {"url": "https://g1.globo.com/rss/g1/am/amazonas/", "type": "rss2", "category": "Amazonas"},
        {"url": "https://g1.globo.com/rss/g1/espirito-santo/", "type": "rss2", "category": "Espirito Santo"},
    ],

    "Folha": [
        {"url": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml", "type": "rss091", "category": "Em Cima da Hora"},
        {"url": "https://feeds.folha.uol.com.br/opiniao/rss091.xml", "type": "rss091", "category": "Opiniao"},
        {"url": "https://feeds.folha.uol.com.br/mundo/rss091.xml", "type": "rss091", "category": "Mundo"},
        {"url": "https://feeds.folha.uol.com.br/mercado/rss091.xml", "type": "rss091", "category": "Mercado"},
        {"url": "https://feeds.folha.uol.com.br/cotidiano/rss091.xml", "type": "rss091", "category": "Cotidiano"},
        {"url": "https://feeds.folha.uol.com.br/educacao/rss091.xml", "type": "rss091", "category": "Educacao"},
        {"url": "https://feeds.folha.uol.com.br/esporte/rss091.xml", "type": "rss091", "category": "Esporte"},
        {"url": "https://feeds.folha.uol.com.br/ilustrada/rss091.xml", "type": "rss091", "category": "Ilustrada"},
        {"url": "https://feeds.folha.uol.com.br/ciencia/rss091.xml", "type": "rss091", "category": "Ciencia"},
        {"url": "https://feeds.folha.uol.com.br/ambiente/rss091.xml", "type": "rss091", "category": "Ambiente"},
        {"url": "https://feeds.folha.uol.com.br/tec/rss091.xml", "type": "rss091", "category": "Tecnologia"},
        {"url": "https://feeds.folha.uol.com.br/equilibrioesaude/rss091.xml", "type": "rss091", "category": "Equilibrio e Saude"},
    ],

    "BBC Brasil": [
        # Apenas feeds que funcionam (principal + topicos com index.xml)
        {"url": "https://www.bbc.com/portuguese/articles/c0weg2we0gpo.rss", "type": "rss2", "category": "Principal"},
    ],

    "CNN Brasil": [
        # Feed RSS alternativo (sitemap-news.xml retornava 404)
        {"url": "https://www.cnnbrasil.com.br/feed/", "type": "rss2", "category": "Principal"},
    ],

    "Estadao": [
        {"url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/politica/", "type": "rss2", "category": "Politica"},
        {"url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/economia/", "type": "rss2", "category": "Economia"},
        {"url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/internacional/", "type": "rss2", "category": "Internacional"},
        {"url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/esportes/", "type": "rss2", "category": "Esportes"},
        {"url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/cultura/", "type": "rss2", "category": "Cultura"},
        {"url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/saude/", "type": "rss2", "category": "Saude"},
    ],

    # ─── NOVAS FONTES ──────────────────────────────────────────────

    "Agencia Brasil": [
        {"url": "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml", "type": "rss2", "category": "Ultimas Noticias"},
        {"url": "https://agenciabrasil.ebc.com.br/rss/economia/feed.xml", "type": "rss2", "category": "Economia"},
        {"url": "https://agenciabrasil.ebc.com.br/rss/politica/feed.xml", "type": "rss2", "category": "Politica"},
        {"url": "https://agenciabrasil.ebc.com.br/rss/geral/feed.xml", "type": "rss2", "category": "Geral"},
        {"url": "https://agenciabrasil.ebc.com.br/rss/educacao/feed.xml", "type": "rss2", "category": "Educacao"},
        {"url": "https://agenciabrasil.ebc.com.br/rss/saude/feed.xml", "type": "rss2", "category": "Saude"},
        {"url": "https://agenciabrasil.ebc.com.br/rss/internacional/feed.xml", "type": "rss2", "category": "Internacional"},
    ],

    "R7": [
        {"url": "https://noticias.r7.com/feed.xml", "type": "rss2", "category": "Noticias"},
        {"url": "https://noticias.r7.com/brasil/feed.xml", "type": "rss2", "category": "Brasil"},
        {"url": "https://noticias.r7.com/economia/feed.xml", "type": "rss2", "category": "Economia"},
        {"url": "https://noticias.r7.com/tecnologia-e-ciencia/feed.xml", "type": "rss2", "category": "Tecnologia e Ciencia"},
        {"url": "https://noticias.r7.com/saude/feed.xml", "type": "rss2", "category": "Saude"},
        {"url": "https://noticias.r7.com/internacional/feed.xml", "type": "rss2", "category": "Internacional"},
    ],

    "Gazeta do Povo": [
        {"url": "https://www.gazetadopovo.com.br/feed/rss/", "type": "rss2", "category": "Principal"},
        {"url": "https://www.gazetadopovo.com.br/republica/feed/rss/", "type": "rss2", "category": "Republica"},
        {"url": "https://www.gazetadopovo.com.br/economia/feed/rss/", "type": "rss2", "category": "Economia"},
        {"url": "https://www.gazetadopovo.com.br/vida-e-cidadania/feed/rss/", "type": "rss2", "category": "Vida e Cidadania"},
        {"url": "https://www.gazetadopovo.com.br/educacao/feed/rss/", "type": "rss2", "category": "Educacao"},
    ],

    "Carta Capital": [
        {"url": "https://www.cartacapital.com.br/feed/", "type": "rss2", "category": "Principal"},
        {"url": "https://www.cartacapital.com.br/politica/feed/", "type": "rss2", "category": "Politica"},
        {"url": "https://www.cartacapital.com.br/economia/feed/", "type": "rss2", "category": "Economia"},
        {"url": "https://www.cartacapital.com.br/sociedade/feed/", "type": "rss2", "category": "Sociedade"},
    ],

    "The Intercept": [
        {"url": "https://www.intercept.com.br/feed/", "type": "rss2", "category": "Principal"},
    ],

    "Poder360": [
        {"url": "https://www.poder360.com.br/feed/", "type": "rss2", "category": "Principal"},
    ],

    "Terra": [
        {"url": "https://www.terra.com.br/rss/controller.htm?path=/noticias/", "type": "rss2", "category": "Noticias"},
        {"url": "https://www.terra.com.br/rss/controller.htm?path=/economia/", "type": "rss2", "category": "Economia"},
        {"url": "https://www.terra.com.br/rss/controller.htm?path=/noticias/tecnologia/", "type": "rss2", "category": "Tecnologia"},
        {"url": "https://www.terra.com.br/rss/controller.htm?path=/noticias/ciencia/", "type": "rss2", "category": "Ciencia"},
    ],

    "InfoMoney": [
        {"url": "https://www.infomoney.com.br/feed/", "type": "rss2", "category": "Principal"},
    ],

    "Metropoles": [
        {"url": "https://www.metropoles.com/feed", "type": "rss2", "category": "Principal"},
        {"url": "https://www.metropoles.com/brasil/feed", "type": "rss2", "category": "Brasil"},
        {"url": "https://www.metropoles.com/distrito-federal/feed", "type": "rss2", "category": "Distrito Federal"},
    ],

    "Correio Braziliense": [
        {"url": "https://www.correiobraziliense.com.br/rss/", "type": "rss2", "category": "Principal"},
        {"url": "https://www.correiobraziliense.com.br/politica/rss/", "type": "rss2", "category": "Politica"},
        {"url": "https://www.correiobraziliense.com.br/economia/rss/", "type": "rss2", "category": "Economia"},
    ],

    "Brasil de Fato": [
        {"url": "https://www.brasildefato.com.br/rss2.xml", "type": "rss2", "category": "Principal"},
    ],

    "Nexo Jornal": [
        {"url": "https://www.nexojornal.com.br/feed/", "type": "rss2", "category": "Principal"},
    ],

    # ─── GOOGLE NEWS (feeds dinamicos, SEMPRE frescos) ──────────
    # Vantagem: RSS padrao, conteudo sempre atualizado, sem limites de API
    # Os links redirecionam para o artigo original (httpx follow_redirects=True)
    "Google News BR": [
        # Topicos gerais
        {"url": "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Destaques"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Brasil"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Mundo"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Negocios"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Tecnologia"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREp0Y0RjU0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Saude"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Ciencia"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Entretenimento"},
        {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp4WkRNU0FuQjBHZ0pDVWlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Esportes"},
        # Buscas especificas por temas relevantes para fact-checking
        {"url": "https://news.google.com/rss/search?q=politica+brasil+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Politica Brasil"},
        {"url": "https://news.google.com/rss/search?q=economia+brasil+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Economia Brasil"},
        {"url": "https://news.google.com/rss/search?q=fake+news+brasil+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Fake News"},
        {"url": "https://news.google.com/rss/search?q=desinformacao+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Desinformacao"},
        {"url": "https://news.google.com/rss/search?q=congresso+nacional+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Congresso"},
        {"url": "https://news.google.com/rss/search?q=stf+supremo+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: STF"},
        {"url": "https://news.google.com/rss/search?q=saude+publica+brasil+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Saude Publica"},
        {"url": "https://news.google.com/rss/search?q=meio+ambiente+brasil+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Meio Ambiente"},
        {"url": "https://news.google.com/rss/search?q=educacao+brasil+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Educacao"},
        {"url": "https://news.google.com/rss/search?q=seguranca+publica+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419", "type": "rss2", "category": "Busca: Seguranca"},
    ],
}

async def seed_sources_and_feeds():
    """Popula banco com sources e RSS feeds"""
    print("Iniciando seed do banco de dados...")
    print(f"   Sources: {len(SOURCES)}")
    total_feeds = sum(len(feeds) for feeds in RSS_FEEDS.values())
    print(f"   RSS Feeds: {total_feeds}")
    print()

    async with AsyncSession(engine) as session:
        sources_created = 0
        sources_existing = 0
        feeds_created = 0
        feeds_existing = 0

        # Criar sources
        for source_data in SOURCES:
            # Verificar se source ja existe
            result = await session.execute(
                select(Source).where(Source.name == source_data["name"])
            )
            source = result.scalar_one_or_none()

            if not source:
                source = Source(**source_data)
                session.add(source)
                await session.commit()
                await session.refresh(source)
                print(f"[+] Source criada: {source.name} ({source.display_name})")
                sources_created += 1
            else:
                print(f"[=] Source ja existe: {source.name}")
                sources_existing += 1

            # Criar feeds RSS
            feeds_data = RSS_FEEDS.get(source.name, [])
            if feeds_data:
                new_in_source = 0
                for feed_data in feeds_data:
                    # Verificar se feed ja existe
                    result = await session.execute(
                        select(RSSFeed).where(RSSFeed.feed_url == feed_data["url"])
                    )
                    existing_feed = result.scalar_one_or_none()

                    if not existing_feed:
                        feed = RSSFeed(
                            source_id=source.id,
                            feed_url=feed_data["url"],
                            feed_type=feed_data["type"],
                            category=feed_data.get("category")
                        )
                        session.add(feed)
                        feeds_created += 1
                        new_in_source += 1
                    else:
                        feeds_existing += 1

                await session.commit()
                if new_in_source > 0:
                    print(f"   [+] {new_in_source} novos feeds adicionados")
                else:
                    print(f"   [=] Todos os {len(feeds_data)} feeds ja existem")
            print()

        print("\n" + "="*60)
        print("Seed concluido!")
        print("="*60)
        print(f"\nEstatisticas:")
        print(f"   Sources criadas:     {sources_created}")
        print(f"   Sources existentes:  {sources_existing}")
        print(f"   Total sources:       {sources_created + sources_existing}")
        print()
        print(f"   Feeds criados:       {feeds_created}")
        print(f"   Feeds existentes:    {feeds_existing}")
        print(f"   Total feeds:         {feeds_created + feeds_existing}")
        print()
        print("Proximos passos:")
        print("   1. Execute: python main.py collect")
        print("   2. Execute: python main.py analyze")
        print("   3. Execute: python main.py index")

if __name__ == "__main__":
    try:
        asyncio.run(seed_sources_and_feeds())
    except Exception as e:
        print(f"\nErro durante seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
