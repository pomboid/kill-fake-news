"""
Script para popular banco de dados com URLs RSS de todas as fontes

Este script adiciona:
- 6 Sources (organizações de notícias)
- ~165 RSS Feeds (URLs RSS válidas)

Formatos suportados:
- RSS 2.0 (UOL, G1, Estadão)
- RSS 0.91 (Folha)
- Atom (BBC Brasil)
- News Sitemap (CNN Brasil)

Uso:
    python scripts/seed_rss_feeds.py
"""
import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import AsyncSession, engine
from core.sql_models import Source, RSSFeed
from sqlmodel import select

# ─── Dados de Sources ────────────────────────────────────────────
SOURCES = [
    {"name": "UOL", "display_name": "UOL Notícias", "website_url": "https://www.uol.com.br"},
    {"name": "G1", "display_name": "G1", "website_url": "https://g1.globo.com"},
    {"name": "Folha", "display_name": "Folha de S.Paulo", "website_url": "https://www.folha.uol.com.br"},
    {"name": "BBC Brasil", "display_name": "BBC Brasil", "website_url": "https://www.bbc.com/portuguese"},
    {"name": "CNN Brasil", "display_name": "CNN Brasil", "website_url": "https://www.cnnbrasil.com.br"},
    {"name": "Estadão", "display_name": "Estadão", "website_url": "https://www.estadao.com.br"},
]

# ─── URLs RSS por Fonte ──────────────────────────────────────────
RSS_FEEDS = {
    "UOL": [
        # Notícias gerais
        {"url": "https://rss.uol.com.br/feed/noticias.xml", "type": "rss2", "category": "Notícias"},
        {"url": "https://rss.uol.com.br/feed/tecnologia.xml", "type": "rss2", "category": "Tecnologia"},
        {"url": "https://rss.uol.com.br/feed/economia.xml", "type": "rss2", "category": "Economia"},
        {"url": "https://rss.uol.com.br/feed/jogos.xml", "type": "rss2", "category": "Jogos"},
        {"url": "http://rss.uol.com.br/feed/cinema.xml", "type": "rss2", "category": "Cinema"},
        {"url": "https://rss.uol.com.br/feed/vestibular.xml", "type": "rss2", "category": "Vestibular"},
        {"url": "https://rss.uol.com.br/feed/eleicoes2022.xml", "type": "rss2", "category": "Eleições"},
        {"url": "https://rss.uol.com.br/feed/comecar-o-dia.xml", "type": "rss2", "category": "Começar o Dia"},

        # Futebol por time
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/atleticomg.xml", "type": "rss2", "category": "Futebol - Atlético-MG"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/atleticopr.xml", "type": "rss2", "category": "Futebol - Atlético-PR"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/bahia.xml", "type": "rss2", "category": "Futebol - Bahia"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/ceara.xml", "type": "rss2", "category": "Futebol - Ceará"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/corinthians.xml", "type": "rss2", "category": "Futebol - Corinthians"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/coritiba.xml", "type": "rss2", "category": "Futebol - Coritiba"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/cruzeiro.xml", "type": "rss2", "category": "Futebol - Cruzeiro"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/flamengo.xml", "type": "rss2", "category": "Futebol - Flamengo"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/fluminense.xml", "type": "rss2", "category": "Futebol - Fluminense"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/fortaleza.xml", "type": "rss2", "category": "Futebol - Fortaleza"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/gremio.xml", "type": "rss2", "category": "Futebol - Grêmio"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/internacional.xml", "type": "rss2", "category": "Futebol - Internacional"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/nautico.xml", "type": "rss2", "category": "Futebol - Náutico"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/palmeiras.xml", "type": "rss2", "category": "Futebol - Palmeiras"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/santacruz.xml", "type": "rss2", "category": "Futebol - Santa Cruz"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/santos.xml", "type": "rss2", "category": "Futebol - Santos"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/saopaulo.xml", "type": "rss2", "category": "Futebol - São Paulo"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/sport.xml", "type": "rss2", "category": "Futebol - Sport"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/vasco.xml", "type": "rss2", "category": "Futebol - Vasco"},
        {"url": "https://www.uol.com.br/esporte/futebol/clubes/vitoria.xml", "type": "rss2", "category": "Futebol - Vitória"},
    ],

    "G1": [
        # Categorias nacionais
        {"url": "https://g1.globo.com/rss/g1/brasil/", "type": "rss2", "category": "Brasil"},
        {"url": "https://g1.globo.com/rss/g1/carros/", "type": "rss2", "category": "Carros"},
        {"url": "https://g1.globo.com/rss/g1/ciencia-e-saude/", "type": "rss2", "category": "Ciência e Saúde"},
        {"url": "https://g1.globo.com/rss/g1/concursos-e-emprego/", "type": "rss2", "category": "Concursos e Emprego"},
        {"url": "https://g1.globo.com/rss/g1/economia/", "type": "rss2", "category": "Economia"},
        {"url": "https://g1.globo.com/rss/g1/educacao/", "type": "rss2", "category": "Educação"},
        {"url": "https://g1.globo.com/rss/g1/loterias/", "type": "rss2", "category": "Loterias"},
        {"url": "https://g1.globo.com/rss/g1/mundo/", "type": "rss2", "category": "Mundo"},
        {"url": "https://g1.globo.com/rss/g1/musica/", "type": "rss2", "category": "Música"},
        {"url": "https://g1.globo.com/rss/g1/natureza/", "type": "rss2", "category": "Natureza"},
        {"url": "https://g1.globo.com/rss/g1/planeta-bizarro/", "type": "rss2", "category": "Planeta Bizarro"},
        {"url": "https://g1.globo.com/rss/g1/politica/mensalao/", "type": "rss2", "category": "Política - Mensalão"},
        {"url": "https://g1.globo.com/rss/g1/pop-arte/", "type": "rss2", "category": "Pop & Arte"},
        {"url": "https://g1.globo.com/rss/g1/tecnologia/", "type": "rss2", "category": "Tecnologia"},
        {"url": "https://g1.globo.com/rss/g1/turismo-e-viagem/", "type": "rss2", "category": "Turismo e Viagem"},

        # Estados
        {"url": "https://g1.globo.com/rss/g1/ac/acre/", "type": "rss2", "category": "Acre"},
        {"url": "https://g1.globo.com/rss/g1/al/alagoas/", "type": "rss2", "category": "Alagoas"},
        {"url": "https://g1.globo.com/rss/g1/ap/amapa/", "type": "rss2", "category": "Amapá"},
        {"url": "https://g1.globo.com/rss/g1/am/amazonas/", "type": "rss2", "category": "Amazonas"},
        {"url": "https://g1.globo.com/rss/g1/bahia/", "type": "rss2", "category": "Bahia"},
        {"url": "https://g1.globo.com/rss/g1/ceara/", "type": "rss2", "category": "Ceará"},
        {"url": "https://g1.globo.com/rss/g1/distrito-federal/", "type": "rss2", "category": "Distrito Federal"},
        {"url": "https://g1.globo.com/rss/g1/espirito-santo/", "type": "rss2", "category": "Espírito Santo"},
        {"url": "https://g1.globo.com/rss/g1/goias/", "type": "rss2", "category": "Goiás"},
        {"url": "https://g1.globo.com/rss/g1/ma/maranhao/", "type": "rss2", "category": "Maranhão"},
        {"url": "https://g1.globo.com/rss/g1/mato-grosso/", "type": "rss2", "category": "Mato Grosso"},
        {"url": "https://g1.globo.com/rss/g1/mato-grosso-do-sul/", "type": "rss2", "category": "Mato Grosso do Sul"},
        {"url": "https://g1.globo.com/rss/g1/minas-gerais/", "type": "rss2", "category": "Minas Gerais"},
        {"url": "https://g1.globo.com/rss/g1/mg/centro-oeste/", "type": "rss2", "category": "MG - Centro-Oeste"},
        {"url": "https://g1.globo.com/rss/g1/mg/grande-minas/", "type": "rss2", "category": "MG - Grande Minas"},
        {"url": "https://g1.globo.com/rss/g1/mg/sul-de-minas/", "type": "rss2", "category": "MG - Sul de Minas"},
        {"url": "https://g1.globo.com/rss/g1/minas-gerais/triangulo-mineiro/", "type": "rss2", "category": "MG - Triângulo Mineiro"},
        {"url": "https://g1.globo.com/rss/g1/mg/vales-mg/", "type": "rss2", "category": "MG - Vales MG"},
        {"url": "https://g1.globo.com/rss/g1/mg/zona-da-mata/", "type": "rss2", "category": "MG - Zona da Mata"},
        {"url": "https://g1.globo.com/rss/g1/pa/para/", "type": "rss2", "category": "Pará"},
        {"url": "https://g1.globo.com/rss/g1/pb/paraiba/", "type": "rss2", "category": "Paraíba"},
        {"url": "https://g1.globo.com/rss/g1/pr/parana/", "type": "rss2", "category": "Paraná"},
        {"url": "https://g1.globo.com/rss/g1/pr/campos-gerais-sul/", "type": "rss2", "category": "PR - Campos Gerais e Sul"},
        {"url": "https://g1.globo.com/rss/g1/pr/oeste-sudoeste/", "type": "rss2", "category": "PR - Oeste e Sudoeste"},
        {"url": "https://g1.globo.com/rss/g1/pr/norte-noroeste/", "type": "rss2", "category": "PR - Norte e Noroeste"},
        {"url": "https://g1.globo.com/rss/g1/pernambuco/", "type": "rss2", "category": "Pernambuco"},
        {"url": "https://g1.globo.com/rss/g1/pe/caruaru-regiao/", "type": "rss2", "category": "PE - Caruaru e Região"},
        {"url": "https://g1.globo.com/rss/g1/pe/petrolina-regiao/", "type": "rss2", "category": "PE - Petrolina e Região"},
        {"url": "https://g1.globo.com/rss/g1/rio-de-janeiro/", "type": "rss2", "category": "Rio de Janeiro"},
        {"url": "https://g1.globo.com/rss/g1/rj/regiao-serrana/", "type": "rss2", "category": "RJ - Região Serrana"},
        {"url": "https://g1.globo.com/rss/g1/rj/regiao-dos-lagos/", "type": "rss2", "category": "RJ - Região dos Lagos"},
        {"url": "https://g1.globo.com/rss/g1/rj/norte-fluminense/", "type": "rss2", "category": "RJ - Norte Fluminense"},
        {"url": "https://g1.globo.com/rss/g1/rj/sul-do-rio-costa-verde/", "type": "rss2", "category": "RJ - Sul do Rio e Costa Verde"},
        {"url": "https://g1.globo.com/rss/g1/rn/rio-grande-do-norte/", "type": "rss2", "category": "Rio Grande do Norte"},
        {"url": "https://g1.globo.com/rss/g1/rs/rio-grande-do-sul/", "type": "rss2", "category": "Rio Grande do Sul"},
        {"url": "https://g1.globo.com/rss/g1/ro/rondonia/", "type": "rss2", "category": "Rondônia"},
        {"url": "https://g1.globo.com/rss/g1/rr/roraima/", "type": "rss2", "category": "Roraima"},
        {"url": "https://g1.globo.com/rss/g1/sc/santa-catarina/", "type": "rss2", "category": "Santa Catarina"},
        {"url": "https://g1.globo.com/rss/g1/sao-paulo/", "type": "rss2", "category": "São Paulo"},
        {"url": "https://g1.globo.com/rss/g1/sp/bauru-marilia/", "type": "rss2", "category": "SP - Bauru e Marília"},
        {"url": "https://g1.globo.com/rss/g1/sp/campinas-regiao/", "type": "rss2", "category": "SP - Campinas e Região"},
        {"url": "https://g1.globo.com/rss/g1/sao-paulo/itapetininga-regiao/", "type": "rss2", "category": "SP - Itapetininga e Região"},
        {"url": "https://g1.globo.com/rss/g1/sp/mogi-das-cruzes-suzano/", "type": "rss2", "category": "SP - Mogi das Cruzes e Suzano"},
        {"url": "https://g1.globo.com/rss/g1/sp/piracicaba-regiao/", "type": "rss2", "category": "SP - Piracicaba e Região"},
        {"url": "https://g1.globo.com/rss/g1/sp/presidente-prudente-regiao/", "type": "rss2", "category": "SP - Presidente Prudente e Região"},
        {"url": "https://g1.globo.com/rss/g1/sp/ribeirao-preto-franca/", "type": "rss2", "category": "SP - Ribeirão Preto e Franca"},
        {"url": "https://g1.globo.com/rss/g1/sao-paulo/sao-jose-do-rio-preto-aracatuba/", "type": "rss2", "category": "SP - São José do Rio Preto e Araçatuba"},
        {"url": "https://g1.globo.com/rss/g1/sp/santos-regiao/", "type": "rss2", "category": "SP - Santos e Região"},
        {"url": "https://g1.globo.com/rss/g1/sp/sao-carlos-regiao/", "type": "rss2", "category": "SP - São Carlos e Região"},
        {"url": "https://g1.globo.com/rss/g1/sao-paulo/sorocaba-jundiai/", "type": "rss2", "category": "SP - Sorocaba e Jundiaí"},
        {"url": "https://g1.globo.com/rss/g1/sp/vale-do-paraiba-regiao/", "type": "rss2", "category": "SP - Vale do Paraíba e Região"},
        {"url": "https://g1.globo.com/rss/g1/se/sergipe/", "type": "rss2", "category": "Sergipe"},
        {"url": "https://g1.globo.com/rss/g1/to/tocantins/", "type": "rss2", "category": "Tocantins"},
        {"url": "https://g1.globo.com/rss/g1/vc-no-g1/", "type": "rss2", "category": "Você no G1"},
    ],

    "Folha": [
        {"url": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml", "type": "rss091", "category": "Em Cima da Hora"},
        {"url": "https://feeds.folha.uol.com.br/opiniao/rss091.xml", "type": "rss091", "category": "Opinião"},
        {"url": "https://feeds.folha.uol.com.br/mundo/rss091.xml", "type": "rss091", "category": "Mundo"},
        {"url": "https://feeds.folha.uol.com.br/mercado/rss091.xml", "type": "rss091", "category": "Mercado"},
        {"url": "https://feeds.folha.uol.com.br/cotidiano/rss091.xml", "type": "rss091", "category": "Cotidiano"},
        {"url": "https://feeds.folha.uol.com.br/educacao/rss091.xml", "type": "rss091", "category": "Educação"},
        {"url": "https://feeds.folha.uol.com.br/equilibrio/rss091.xml", "type": "rss091", "category": "Equilíbrio"},
        {"url": "https://feeds.folha.uol.com.br/esporte/rss091.xml", "type": "rss091", "category": "Esporte"},
        {"url": "https://feeds.folha.uol.com.br/ilustrada/rss091.xml", "type": "rss091", "category": "Ilustrada"},
        {"url": "https://feeds.folha.uol.com.br/ilustrissima/rss091.xml", "type": "rss091", "category": "Ilustríssima"},
        {"url": "https://feeds.folha.uol.com.br/ciencia/rss091.xml", "type": "rss091", "category": "Ciência"},
        {"url": "https://feeds.folha.uol.com.br/ambiente/rss091.xml", "type": "rss091", "category": "Ambiente"},
        {"url": "https://feeds.folha.uol.com.br/tec/rss091.xml", "type": "rss091", "category": "Tecnologia"},
        {"url": "https://feeds.folha.uol.com.br/comida/rss091.xml", "type": "rss091", "category": "Comida"},
        {"url": "https://feeds.folha.uol.com.br/equilibrioesaude/rss091.xml", "type": "rss091", "category": "Equilíbrio e Saúde"},
        {"url": "https://feeds.folha.uol.com.br/folhinha/rss091.xml", "type": "rss091", "category": "Folhinha"},
        {"url": "https://feeds.folha.uol.com.br/turismo/rss091.xml", "type": "rss091", "category": "Turismo"},
        {"url": "https://feeds.folha.uol.com.br/paineldoleitor/rss091.xml", "type": "rss091", "category": "Painel do Leitor"},

        # F5
        {"url": "https://feeds.folha.uol.com.br/f5/tudo/rss091.xml", "type": "rss091", "category": "F5 - Tudo"},
        {"url": "https://feeds.folha.uol.com.br/f5/celebridades/rss091.xml", "type": "rss091", "category": "F5 - Celebridades"},
        {"url": "https://feeds.folha.uol.com.br/f5/celebridades/carnaval/rss091.xml", "type": "rss091", "category": "F5 - Carnaval"},
        {"url": "https://feeds.folha.uol.com.br/f5/televisao/rss091.xml", "type": "rss091", "category": "F5 - Televisão"},
        {"url": "https://feeds.folha.uol.com.br/f5/multitela/rss091.xml", "type": "rss091", "category": "F5 - Multitela"},
        {"url": "https://feeds.folha.uol.com.br/f5/televisao/novelas/rss091.xml", "type": "rss091", "category": "F5 - Novelas"},
        {"url": "https://feeds.folha.uol.com.br/f5/astrologia/rss091.xml", "type": "rss091", "category": "F5 - Astrologia"},
        {"url": "https://feeds.folha.uol.com.br/f5/nerdices/rss091.xml", "type": "rss091", "category": "F5 - Nerdices"},
        {"url": "https://feeds.folha.uol.com.br/f5/musica/rss091.xml", "type": "rss091", "category": "F5 - Música"},
        {"url": "https://feeds.folha.uol.com.br/f5/cinema-e-series/rss091.xml", "type": "rss091", "category": "F5 - Cinema e Séries"},
        {"url": "https://feeds.folha.uol.com.br/f5/diversao/rss091.xml", "type": "rss091", "category": "F5 - Diversão"},
        {"url": "https://feeds.folha.uol.com.br/f5/estilo/rss091.xml", "type": "rss091", "category": "F5 - Estilo"},
        {"url": "https://feeds.folha.uol.com.br/f5/estilo/spfw/rss091.xml", "type": "rss091", "category": "F5 - SPFW"},
        {"url": "https://feeds.folha.uol.com.br/f5/viva-bem/rss091.xml", "type": "rss091", "category": "F5 - Viva Bem"},
        {"url": "https://feeds.folha.uol.com.br/f5/bichos/rss091.xml", "type": "rss091", "category": "F5 - Bichos"},
        {"url": "https://feeds.folha.uol.com.br/f5/fofices/rss091.xml", "type": "rss091", "category": "F5 - Fofices"},
        {"url": "https://feeds.folha.uol.com.br/f5/voceviu/rss091.xml", "type": "rss091", "category": "F5 - Você Viu"},
        {"url": "https://feeds.folha.uol.com.br/f5/top5/rss091.xml", "type": "rss091", "category": "F5 - Top 5"},
        {"url": "https://feeds.folha.uol.com.br/f5/colunistas/rss091.xml", "type": "rss091", "category": "F5 - Colunistas"},
        {"url": "https://feeds.folha.uol.com.br/f5/colunistas/aventura-na-cozinha/rss091.xml", "type": "rss091", "category": "F5 - Aventura na Cozinha"},
        {"url": "https://feeds.folha.uol.com.br/f5/colunistas/biblioteca-da-vivi/rss091.xml", "type": "rss091", "category": "F5 - Biblioteca da Vivi"},
        {"url": "https://feeds.folha.uol.com.br/f5/colunistas/bom-de-garfo/rss091.xml", "type": "rss091", "category": "F5 - Bom de Garfo"},
        {"url": "https://feeds.folha.uol.com.br/f5/colunistas/colo-de-mae/rss091.xml", "type": "rss091", "category": "F5 - Colo de Mãe"},
        {"url": "https://feeds.folha.uol.com.br/f5/colunistas/cabelo-make-mais/rss091.xml", "type": "rss091", "category": "F5 - Cabelo, Make e Mais"},
        {"url": "https://feeds.folha.uol.com.br/f5/colunistas/tonygoes/rss091.xml", "type": "rss091", "category": "F5 - Tony Goes"},
        {"url": "http://feeds.folha.uol.com.br/f5/colunistas/cristina-padiglione/rss091.xml", "type": "rss091", "category": "F5 - Cristina Padiglione"},
    ],

    "BBC Brasil": [
        {"url": "http://www.bbc.co.uk/portuguese/index.xml", "type": "rss2", "category": "Principal"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/brasil/index.xml", "type": "atom", "category": "Brasil"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/america_latina/index.xml", "type": "atom", "category": "América Latina"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/internacional/index.xml", "type": "atom", "category": "Internacional"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/economia/", "type": "atom", "category": "Economia"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/saude/", "type": "atom", "category": "Saúde"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/ciencia_e_tecnologia/", "type": "atom", "category": "Ciência e Tecnologia"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/cultura/", "type": "atom", "category": "Cultura"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/video/index.xml", "type": "atom", "category": "Vídeo"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/fotos/index.xml", "type": "atom", "category": "Fotos"},
        {"url": "http://www.bbc.co.uk/portuguese/especiais/index.xml", "type": "atom", "category": "Especiais"},
        {"url": "http://www.bbc.co.uk/portuguese/topicos/aprenda_ingles/index.xml", "type": "atom", "category": "Aprenda Inglês"},
    ],

    "CNN Brasil": [
        {"url": "https://admin.cnnbrasil.com.br/sitemap-news.xml", "type": "sitemap", "category": "Todas as Notícias"},
    ],

    "Estadão": [
        {"url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/politica/", "type": "rss2", "category": "Política"},
    ],
}

async def seed_sources_and_feeds():
    """Popula banco com sources e RSS feeds"""
    print("🌱 Iniciando seed do banco de dados...")
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
            # Verificar se source já existe
            result = await session.execute(
                select(Source).where(Source.name == source_data["name"])
            )
            source = result.scalar_one_or_none()

            if not source:
                source = Source(**source_data)
                session.add(source)
                await session.commit()
                await session.refresh(source)
                print(f"✅ Source criada: {source.name} ({source.display_name})")
                sources_created += 1
            else:
                print(f"⏭️  Source já existe: {source.name}")
                sources_existing += 1

            # Criar feeds RSS
            feeds_data = RSS_FEEDS.get(source.name, [])
            if feeds_data:
                print(f"   Adicionando {len(feeds_data)} feeds...")

                for feed_data in feeds_data:
                    # Verificar se feed já existe
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
                    else:
                        feeds_existing += 1

                await session.commit()
                print(f"   ✅ {feeds_created - (feeds_created - len([f for f in feeds_data if f]))} feeds adicionados")
            print()

        print("\n" + "="*60)
        print("🎉 Seed concluído com sucesso!")
        print("="*60)
        print(f"\n📊 Estatísticas:")
        print(f"   Sources criadas:     {sources_created}")
        print(f"   Sources existentes:  {sources_existing}")
        print(f"   Total sources:       {sources_created + sources_existing}")
        print()
        print(f"   Feeds criados:       {feeds_created}")
        print(f"   Feeds existentes:    {feeds_existing}")
        print(f"   Total feeds:         {feeds_created + feeds_existing}")
        print()
        print("📝 Próximos passos:")
        print("   1. Execute: python main.py collect")
        print("   2. Execute: python main.py analyze")
        print("   3. Execute: python main.py index")

if __name__ == "__main__":
    try:
        asyncio.run(seed_sources_and_feeds())
    except Exception as e:
        print(f"\n❌ Erro durante seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
