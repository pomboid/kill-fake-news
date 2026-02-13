<p align="center">
  <img src="https://img.shields.io/badge/VORTEX-Cognitive_Defense_System-00FFB2?style=for-the-badge&labelColor=0A0A0A" alt="VORTEX Badge"/>
</p>

<h1 align="center">🌀 VORTEX</h1>

<p align="center">
  <strong>Sistema Inteligente de Combate a Fake News com Inteligência Artificial</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Gemini_AI-2.0_Flash-4285F4?logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
</p>

<p align="center">
  <em>Detecte, analise e verifique notícias falsas automaticamente usando Inteligência Artificial</em>
</p>

---

## 📖 O Que é o VORTEX?

O **VORTEX** (Verification & Observation of Real-Time EXploits) é um sistema completo de defesa cognitiva contra desinformação baseado em **RAG (Retrieval-Augmented Generation)**. Em termos simples:

1. 🤖 O sistema **coleta notícias** automaticamente de portais confiáveis via RSS/scraping
2. 🧠 Usa **Inteligência Artificial (Google Gemini 2.0 Flash)** para analisar cada notícia e identificar padrões de fake news
3. 🔍 Permite que **você cole qualquer texto ou afirmação** e o sistema verifica se é verdadeiro, falso ou inconclusivo
4. 📊 Mostra tudo em um **painel visual moderno** com estatísticas em tempo real

> **Pense no VORTEX como um "detector de mentiras digital"** — ele cruza informações de fontes confiáveis para te dizer se aquela notícia do WhatsApp é verdadeira ou não.

---

## 🎯 Funcionalidades Principais

### 1. 📰 Coleta Automática de Notícias (Database-Driven)

O sistema busca notícias automaticamente em **6 fontes confiáveis** brasileiras usando **155 feeds RSS** armazenados no PostgreSQL:

| Fonte | Feeds | Exemplos |
|-------|-------|----------|
| **G1** (Globo) | 69 feeds | Brasil, Mundo, Tecnologia, Estados, Cidades |
| **Folha de S.Paulo** | 44 feeds | Política, Mercado, Cotidiano, F5, Ilustrada |
| **UOL** | 28 feeds | Notícias, Tecnologia, Esportes, Vestibular |
| **BBC Brasil** | 12 feeds | Brasil, Internacional, Economia, Ciência |
| **CNN Brasil** | 1 feed | News Sitemap |
| **Estadão** | 1 feed | Política |

**Arquitetura de Coleta:**
- ✅ **Database-driven**: URLs armazenadas em PostgreSQL (`rss_feed` table)
- ✅ **Parallel scraping**: Processa 5 URLs simultaneamente (asyncio.gather)
- ✅ **Batch commits**: Salva múltiplos artigos por transação
- ✅ **Deduplicação automática**: URL com constraint `UNIQUE` no banco
- ✅ **Filtro de qualidade**: Título ≥10 chars, conteúdo ≥300 chars
- ✅ **Rate limiting**: 0.5s delay entre batches para não sobrecarregar servidores

**Capacidade atual:**
- 🔢 **8.673+ artigos** coletados (exemplo de coleta real)
- 📡 **155 feeds RSS** ativos
- 🔄 **Coleta automática** a cada 1 hora (configurável via `COLLECT_INTERVAL_HOURS`)
- ⚡ **Processamento paralelo** - 5 URLs simultâneas
- 🎯 **Taxa de sucesso** ~76% (23% rejeitados por qualidade)

### 2. 🤖 Análise com Inteligência Artificial (Phase 2)

Cada artigo coletado é analisado pelo **Google Gemini 2.0 Flash**, que identifica:

- ⚠️ **Linguagem sensacionalista** (títulos exagerados, alarmistas)
- 🎣 **Clickbait** (títulos enganosos para gerar cliques)
- 😡 **Manipulação emocional** (apelar para medo, raiva, indignação)
- 📉 **Ausência de fontes** (afirmações sem dados ou referências)
- 🔄 **Inconsistências** (informações que se contradizem)

**Resultado estruturado:**
```json
{
  "is_fake": boolean,
  "confidence_score": 0.0-1.0,
  "reasoning": "Explicação técnica...",
  "detected_markers": ["sensacionalismo", "falta de fontes"],
  "scores": {
    "factual_consistency": 0-10,
    "linguistic_bias": 0-10,
    "sensationalism": 0-10,
    "source_credibility": 0-10
  }
}
```

### 3. 🔍 Indexação Semântica (Phase 3)

Usa **pgvector** (extensão do PostgreSQL) para busca por similaridade:

- 📊 **Embeddings**: Vetores de 768 dimensões via `text-embedding-004`
- 🔎 **Busca semântica**: Cosine distance search no PostgreSQL
- ⚡ **Performance**: Índice HNSW para buscas rápidas
- 🎯 **Precisão**: Encontra artigos relevantes mesmo sem palavras exatas

### 4. ✅ Verificação de Fatos (Phase 4 - RAG)

Você pode verificar **qualquer afirmação** ou **artigo completo**:

**Fluxo de verificação:**
1. Usuário submete afirmação: *"O governo vai taxar o PIX"*
2. Sistema gera embedding da afirmação (768-dim vector)
3. Busca semântica retorna top 5 artigos mais similares (pgvector)
4. Gemini 2.0 Flash compara afirmação com evidências
5. Retorna veredicto estruturado:

```
🟢 [VERDADEIRO]           - Confirmado por evidências
🔴 [FALSO]                - Contradiz evidências
🟡 [PARCIALMENTE VERDADEIRO] - Parcialmente correto
⚪ [INCONCLUSIVO]         - Sem evidências suficientes
```

### 5. 🖥️ Dashboard Interativo

Interface web moderna construída com **React 18 + TypeScript**, tema escuro e responsiva:

- 📊 **Estatísticas em tempo real** — Artigos coletados, analisados, verificações
- 📜 **Histórico de verificações** — Todas as verificações anteriores
- 🟢 **Status das fontes** — Monitoramento de saúde (HTTP 200)
- ⏰ **Automação** — Próxima execução do scheduler
- 🔐 **Login seguro** — Autenticação via Google (Clerk)

---

## 🏗️ Arquitetura do Sistema

```
┌───────────────────────────────────────────────────────────────────┐
│                         VORTEX SYSTEM                             │
├──────────────────────┬────────────────────────────────────────────┤
│                      │                                            │
│  🌐 FRONTEND         │  ⚙️ BACKEND                               │
│  React + TypeScript  │  Python 3.11 + FastAPI                     │
│  Porta 80 (nginx)    │  Porta 8420                                │
│                      │                                            │
│  ┌────────────────┐  │  ┌──────────────────────────────────────┐ │
│  │  Dashboard     │─────▶│  API REST                            │ │
│  │  Login/Auth    │  │  │  /api/verify  (fact-check)           │ │
│  │  Estatísticas  │  │  │  /api/analyze (run phase 2)          │ │
│  │  Histórico     │  │  │  /api/status  (system stats)         │ │
│  └────────────────┘  │  │  /api/history (past verifications)   │ │
│                      │  │  /api/sources (source health)        │ │
│                      │  │  /api/quality (data quality)         │ │
│                      │  └──────────┬───────────────────────────┘ │
│                      │             │                              │
│                      │  ┌──────────▼───────────────────────────┐ │
│                      │  │  🤖 Motor de IA (4 Phases)          │ │
│                      │  │                                      │ │
│                      │  │  Phase 1: Collector (RSS/Scraping)  │ │
│                      │  │  • 155 RSS feeds from PostgreSQL    │ │
│                      │  │  • Parallel scraping (5 async)      │ │
│                      │  │  • Batch commits                    │ │
│                      │  │                                      │ │
│                      │  │  Phase 2: Analyzer (Gemini AI)      │ │
│                      │  │  • Fake news markers detection      │ │
│                      │  │  • Quality scores (0-10)            │ │
│                      │  │                                      │ │
│                      │  │  Phase 3: Indexer (pgvector)        │ │
│                      │  │  • Generate 768-dim embeddings      │ │
│                      │  │  • Store in PostgreSQL              │ │
│                      │  │                                      │ │
│                      │  │  Phase 4: Verifier (RAG)            │ │
│                      │  │  • Semantic search (cosine dist.)   │ │
│                      │  │  • LLM cross-referencing            │ │
│                      │  └──────────────────────────────────────┘ │
│                      │                                            │
│                      │  ┌──────────────────────────────────────┐ │
│                      │  │  📊 PostgreSQL 16 + pgvector         │ │
│                      │  │  • Articles (title, content, url)    │ │
│                      │  │  • Embeddings (768-dim vectors)      │ │
│                      │  │  • Analysis (AI verdicts)            │ │
│                      │  │  • Verifications (fact-checks)       │ │
│                      │  │  • RSS Feeds (155 URLs)              │ │
│                      │  │  • Sources (6 news outlets)          │ │
│                      │  └──────────────────────────────────────┘ │
│                      │                                            │
│                      │  ⏰ APScheduler (Background Jobs)          │
│                      │  • Collect every 1h (configurable)        │
│                      │  • Source monitoring every 1h             │
│                      │                                            │
├──────────────────────┴────────────────────────────────────────────┤
│  🐳 Docker Compose (3 containers: backend, frontend, vortex-db)  │
└───────────────────────────────────────────────────────────────────┘
```

### 🛠️ Stack Tecnológica

| Camada | Tecnologia | Para Quê? |
|--------|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite | Interface do usuário |
| **Estilo** | CSS moderno (tema escuro) | Visual premium |
| **Autenticação** | Clerk (Google OAuth) | Login seguro |
| **Backend** | Python 3.11 + FastAPI | API e lógica do servidor |
| **IA Generativa** | Google Gemini 2.0 Flash | Análise de fake news + RAG |
| **Embeddings** | text-embedding-004 (Gemini) | Transformar texto em vetores (768-dim) |
| **Banco de Dados** | PostgreSQL 16 + pgvector | Armazenamento + busca semântica |
| **Banco Vetorial** | pgvector extension | Cosine distance search (HNSW index) |
| **ORM** | SQLModel + AsyncSession | Queries assíncronas |
| **Scraping** | BeautifulSoup4 + httpx | Coleta de notícias |
| **Agendamento** | APScheduler | Automação de tarefas |
| **Containerização** | Docker + Docker Compose | Deploy simplificado |
| **Servidor Web** | Nginx (Alpine) | Servir frontend em produção |
| **Rate Limiting** | SlowAPI | Proteção contra abuso |

---

## 🚀 Como Instalar

### **Pré-requisitos**

Antes de começar, você vai precisar ter instalado:

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)
- Uma chave de API do **Google Gemini** (grátis): [Obtenha aqui](https://aistudio.google.com/app/apikey)
- Uma conta no **Clerk** para autenticação: [Crie aqui](https://dashboard.clerk.com)

---

### **Deploy com Docker (Recomendado)** 🐳

#### Passo 1: Clone o Repositório

```bash
git clone https://github.com/pomboid/kill-fake-news.git
cd kill-fake-news
```

#### Passo 2: Configure as Variáveis de Ambiente

**Backend** (`.env` na raiz):
```bash
cp .env.production.example .env
nano .env
```

Preencha:
```env
# Obrigatório — Chave da API Gemini
GEMINI_API_KEY=sua_chave_gemini_aqui

# API Key interna (para proteger endpoints)
VORTEX_API_KEY=sua_chave_secreta_aqui

# Configurações do scheduler
COLLECT_INTERVAL_HOURS=1        # Coleta automática a cada 1 hora
SOURCE_CHECK_INTERVAL_HOURS=1   # Monitoramento de fontes a cada 1 hora
LOG_LEVEL=INFO

# PostgreSQL (já configurado no docker-compose.yml)
DATABASE_URL=postgresql+asyncpg://vortex:vortex_password@vortex-db:5432/vortex_db

# CORS
ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,http://SEU_IP

# Chave do Clerk (para Docker Compose build args)
VITE_CLERK_PUBLISHABLE_KEY=pk_test_sua_chave_clerk_aqui
VITE_API_URL=http://SEU_IP:8420
```

**Frontend** (`frontend/.env`):
```bash
nano frontend/.env
```

Preencha:
```env
VITE_CLERK_PUBLISHABLE_KEY=pk_test_sua_chave_clerk_aqui
VITE_API_URL=http://SEU_IP:8420
```

> ⚠️ **IMPORTANTE:** Substitua `SEU_IP` pelo IP do seu servidor (ex: `192.168.1.100` ou `localhost`).

#### Passo 3: Suba os Containers

```bash
docker compose up -d --build
```

Aguarde ~60 segundos para o build completar.

#### Passo 4: Popular o Banco com RSS Feeds

```bash
# Criar tabelas e popular feeds
docker compose exec backend python scripts/seed_rss_feeds.py
```

Isso vai criar 6 fontes e 155 feeds RSS no PostgreSQL.

#### Passo 5: Coletar Primeiros Artigos

```bash
# Coletar artigos de todas as fontes (pode demorar ~30min-1h)
docker compose exec backend python main.py collect

# OU com limite para teste rápido:
docker compose exec backend python main.py collect --limit 50
```

#### Passo 6: Verifique

```bash
# Ver se os 3 containers estão rodando
docker ps

# Deve mostrar:
# vortex-backend   (porta 8420)
# vortex-frontend  (porta 80)
# vortex-db        (porta 5432, interna)

# Ver status do sistema
docker compose exec backend python main.py status
```

#### Passo 7: Acesse

```
Frontend (Interface): http://SEU_IP
Backend (API):        http://SEU_IP:8420
API Docs:             http://SEU_IP:8420/docs
```

---

### **Instalação Local (Desenvolvimento)** 💻

Para quem quer desenvolver e modificar o código:

#### Backend

```bash
# Clone o projeto
git clone https://github.com/pomboid/kill-fake-news.git
cd kill-fake-news

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate     # Linux/Mac
# ou
venv\Scripts\activate        # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure PostgreSQL local
# Instale PostgreSQL 16+ com extensão pgvector
createdb vortex_db
psql vortex_db -c "CREATE EXTENSION vector;"

# Configure variáveis de ambiente
cp .env.production.example .env
nano .env  # Adicione GEMINI_API_KEY e DATABASE_URL

# Popular feeds
python scripts/seed_rss_feeds.py

# Rode o servidor
uvicorn server:app --host 0.0.0.0 --port 8420 --reload
```

#### Frontend

```bash
cd frontend

# Instale as dependências
npm install

# Configure variáveis de ambiente
nano .env
# Adicione:
# VITE_CLERK_PUBLISHABLE_KEY=pk_test_sua_chave
# VITE_API_URL=http://localhost:8420

# Rode o frontend (desenvolvimento)
npm run dev
# Acesse: http://localhost:5173
```

---

## 📖 Como Usar

### Via Dashboard Web (Interface Visual)

1. Acesse `http://SEU_IP` no navegador
2. Faça login com sua conta Google
3. **Aguarde as fases 2 e 3** (primeira vez):
   ```bash
   # Fase 2: Analisar artigos com IA (pode demorar)
   docker compose exec backend python main.py analyze --limit 100

   # Fase 3: Indexar (criar embeddings)
   docker compose exec backend python main.py index
   ```
4. Use o campo **"Cortex Verification Engine"** para verificar afirmações:
   - Cole uma notícia ou afirmação (até 10.000 caracteres)
   - Clique em **"Run Verification"**
   - Veja o resultado: **Verdadeiro**, **Falso** ou **Inconclusivo**
5. Monitore as **estatísticas** e **fontes** na dashboard

### Via CLI (Linha de Comando)

```bash
# 📊 Ver status do sistema
python main.py status

# 📰 FASE 1: Coletar notícias de todas as fontes
python main.py collect                  # Sem limite (coleta tudo)
python main.py collect --limit 100      # Com limite

# 🧠 FASE 2: Analisar artigos com IA (cuidado com cota da API)
python main.py analyze --limit 50       # Analisa 50 artigos não analisados

# 🔍 FASE 3: Indexar no banco vetorial (gerar embeddings)
python main.py index

# ✅ FASE 4: Verificar uma afirmação
python main.py verify "O governo vai taxar o PIX"

# 🔄 Pipeline completo (coleta + análise + indexação)
python main.py full-pipeline

# 📜 Ver histórico de verificações
python main.py history --limit 10

# 📊 Ver qualidade da base de dados
python main.py quality

# 🌱 Popular feeds RSS no banco
python main.py seed-feeds
```

### Via API REST

```bash
# ✅ Verificar uma afirmação (Phase 4)
curl -X POST http://SEU_IP:8420/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "Vacinas causam autismo"}'

# 📊 Status do sistema
curl http://SEU_IP:8420/api/status

# 🧠 Rodar análise em batch (Phase 2)
curl -X POST http://SEU_IP:8420/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"limit": 50}'

# 📜 Histórico de verificações
curl http://SEU_IP:8420/api/history

# 📊 Qualidade da base de dados
curl http://SEU_IP:8420/api/quality

# 🟢 Status das fontes (online/offline)
curl http://SEU_IP:8420/api/sources

# 📰 Últimas notícias coletadas
curl http://SEU_IP:8420/api/news?limit=20
```

> 📚 **Documentação completa da API** disponível em: `http://SEU_IP:8420/docs`

---

## 📁 Estrutura do Projeto

```
kill-fake-news/
│
├── 🌐 frontend/                   # Interface do Usuário (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx         # Barra de navegação
│   │   │   ├── StatsGrid.tsx      # Cards de estatísticas
│   │   │   ├── VerifyForm.tsx     # Motor de verificação
│   │   │   ├── HistoryList.tsx    # Histórico de verificações
│   │   │   ├── SchedulerInfo.tsx  # Info de automação
│   │   │   └── SourcesList.tsx    # Lista de fontes
│   │   ├── pages/                 # Páginas da aplicação
│   │   ├── App.tsx                # Componente principal
│   │   └── main.tsx               # Entry point
│   ├── Dockerfile                 # Build do frontend (Node → Nginx)
│   ├── package.json               # Dependências JavaScript
│   └── .env.example               # Template de variáveis
│
├── ⚙️ core/                       # Configurações do Sistema
│   ├── config.py                  # Configuração centralizada
│   ├── database.py                # Conexão PostgreSQL + AsyncSession
│   ├── sql_models.py              # SQLModel schemas (Article, Source, etc.)
│   ├── rate_limits.py             # Limites da API Gemini
│   ├── logging_config.py          # Configuração de logs
│   └── ui.py                      # Interface CLI
│
├── 🧠 modules/                    # Módulos de Processamento
│   ├── intelligence/              # Coleta de notícias
│   │   └── collector.py           # RSS/Scraping engine (parallel)
│   ├── analysis/                  # Análise IA
│   │   └── detector.py            # Gemini fake news detector
│   └── detection/                 # Verificação RAG
│       └── verification_engine.py # pgvector + Gemini RAG
│
├── 📜 scripts/                    # Scripts utilitários
│   └── seed_rss_feeds.py          # Popular feeds no PostgreSQL
│
├── 🧪 tests/                      # Testes Automatizados
│
├── 📄 server.py                   # API FastAPI (backend)
├── 📄 scheduler.py                # Agendador de tarefas (APScheduler)
├── 📄 main.py                     # CLI principal (argparse)
├── 🐳 Dockerfile                  # Build do backend
├── 🐳 docker-compose.yml          # Orquestração (backend + frontend + db)
├── 📋 requirements.txt            # Dependências Python
└── 📖 README.md                   # Este arquivo
```

---

## 🗄️ Schema do Banco de Dados (PostgreSQL)

```sql
-- Tabela de fontes de notícias
CREATE TABLE source (
  id SERIAL PRIMARY KEY,
  name VARCHAR UNIQUE NOT NULL,        -- Ex: "G1", "Folha"
  display_name VARCHAR NOT NULL,
  website_url VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'online',
  last_checked TIMESTAMP,
  is_active BOOLEAN DEFAULT true
);

-- Tabela de feeds RSS
CREATE TABLE rss_feed (
  id SERIAL PRIMARY KEY,
  source_id INTEGER REFERENCES source(id),
  feed_url VARCHAR UNIQUE NOT NULL,
  feed_type VARCHAR DEFAULT 'rss2',  -- rss2, atom, sitemap
  category VARCHAR,                   -- Ex: "Tecnologia", "Política"
  is_active BOOLEAN DEFAULT true,
  last_fetched TIMESTAMP,
  fetch_count INTEGER DEFAULT 0,
  error_count INTEGER DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de artigos coletados
CREATE TABLE article (
  id SERIAL PRIMARY KEY,
  title VARCHAR NOT NULL,
  subtitle VARCHAR,
  url VARCHAR UNIQUE NOT NULL,       -- Unique constraint (deduplicação)
  content TEXT NOT NULL,
  author VARCHAR NOT NULL,
  published_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL,
  embedding VECTOR(768),             -- pgvector: 768-dimensional
  source_id INTEGER REFERENCES source(id)
);

CREATE INDEX ON article USING HNSW (embedding vector_cosine_ops);

-- Tabela de análises IA (Phase 2)
CREATE TABLE analysis (
  id SERIAL PRIMARY KEY,
  article_id INTEGER REFERENCES article(id) UNIQUE,
  is_fake BOOLEAN NOT NULL,
  confidence FLOAT NOT NULL,
  reasoning TEXT NOT NULL,
  markers JSON,                      -- ["sensacionalismo", "falta de fontes"]
  scores JSON,                       -- {"factual": 7, "bias": 3, ...}
  analyzed_at TIMESTAMP NOT NULL
);

-- Tabela de verificações (Phase 4)
CREATE TABLE verification (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR,
  claim TEXT NOT NULL,
  verdict VARCHAR NOT NULL,          -- [VERDADEIRO], [FALSO], etc.
  confidence FLOAT NOT NULL,
  evidence JSON,                     -- [article_ids]
  created_at TIMESTAMP NOT NULL
);
```

---

## 🐳 Comandos Docker Úteis

```bash
# 📊 Ver containers rodando
docker ps

# 📜 Ver logs do backend
docker compose logs backend --tail 50 -f

# 📜 Ver logs do frontend
docker compose logs frontend --tail 50 -f

# 📜 Ver logs do PostgreSQL
docker compose logs vortex-db --tail 50 -f

# 🔄 Atualizar após mudanças no código
git pull origin main
docker compose down
docker compose up -d --build

# 🔄 Rebuild apenas backend
docker compose up -d --build backend

# ⏹️ Parar tudo
docker compose down

# 🗑️ Limpar tudo (⚠️ APAGA DADOS)
docker compose down -v
docker system prune -af

# 💾 Backup do banco
docker compose exec vortex-db pg_dump -U vortex vortex_db > backup.sql

# 📥 Restaurar backup
cat backup.sql | docker compose exec -T vortex-db psql -U vortex vortex_db

# 🐚 Entrar no container backend (debug)
docker compose exec backend bash

# 🐚 Acessar PostgreSQL
docker compose exec vortex-db psql -U vortex -d vortex_db
```

---

## ⚙️ Configuração Avançada

### Ajustar Intervalo de Coleta

Edite `.env`:
```env
COLLECT_INTERVAL_HOURS=1   # Coletar a cada 1 hora
SOURCE_CHECK_INTERVAL_HOURS=1  # Monitorar fontes a cada 1 hora
```

Reinicie o backend:
```bash
docker compose restart backend
```

### Adicionar Novas Fontes RSS

1. Adicione a fonte em `scripts/seed_rss_feeds.py`
2. Execute:
```bash
docker compose exec backend python scripts/seed_rss_feeds.py
```

### Melhorar Seletores de Scraping

Edite `modules/intelligence/collector.py` → `DOMAIN_MAP`:

```python
DOMAIN_MAP = {
    "exemplo.com.br": {
        "t": "h1.titulo",           # Seletor CSS do título
        "s": "h2.subtitulo",        # Seletor CSS do subtítulo
        "b": "div.corpo-texto",     # Seletor CSS do body
        "p": "p.paragrafo"          # Seletor CSS dos parágrafos
    }
}
```

---

## ⚠️ Limitações e Avisos

| Limitação | Detalhe |
|-----------|---------|
| **Free Tier Gemini** | ~1.500 requisições/dia no plano gratuito. Suficiente para uso moderado. |
| **Precisão da IA** | Nenhuma IA é 100% precisa. Sempre verifique fontes primárias. |
| **Idioma** | Otimizado para **Português Brasileiro**. |
| **Fontes** | Limitado às fontes com RSS feeds públicos. Novas podem ser adicionadas. |
| **Embeddings** | Qualidade depende da base de dados. Mais artigos = mais precisão. |
| **Primeira coleta** | Pode demorar 30min-1h para coletar ~8.000 artigos na primeira vez. |

---

## 📈 Performance e Escalabilidade

| Métrica | Valor |
|---------|-------|
| **Artigos coletados** | 8.673+ (exemplo real) |
| **Taxa de coleta** | ~150-200 artigos/minuto (5 paralelos) |
| **Tamanho do banco** | ~35 MB para 8.673 artigos |
| **Taxa de sucesso** | ~76% (23% rejeitados por qualidade) |
| **Busca semântica** | <100ms (pgvector HNSW index) |
| **API Gemini** | 2s rate limit entre análises (cota gratuita) |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga estes passos:

1. 🍴 Faça um **fork** do projeto
2. 🌿 Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. 💾 Commit suas mudanças (`git commit -m 'feat: adiciona MinhaFeature'`)
4. 📤 Push para a branch (`git push origin feature/MinhaFeature`)
5. 🔀 Abra um **Pull Request**

---

## 🌟 Roadmap Futuro

- [x] ✅ Migração para PostgreSQL + pgvector
- [x] ✅ Database-driven RSS feeds (155 feeds)
- [x] ✅ Parallel scraping com asyncio
- [x] ✅ Batch commits e deduplicação
- [ ] 🌍 Suporte a múltiplos idiomas
- [ ] 💬 Integração com Telegram e WhatsApp
- [ ] ⭐ Sistema de reputação de fontes (consenso multi-fonte)
- [ ] 📈 Dashboard analytics avançado
- [ ] 🔌 Extensão para navegadores (Chrome/Firefox)
- [ ] 📱 Aplicativo mobile (React Native)
- [ ] 🔗 Google Fact Check API integration
- [ ] 🎯 Aumento de fontes (R7, Metrópoles, etc.)

---

## 📝 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🆘 Suporte e Contato

- 📧 **Issues**: [GitHub Issues](https://github.com/pomboid/kill-fake-news/issues)
- 💼 **LinkedIn**: [Weversson Vital](https://www.linkedin.com/in/weversson-vital/) | [Vitor Benedett Caldas](https://www.linkedin.com/in/vitorbenedettcaldas/)

---

<p align="center">
  <strong>Desenvolvido com 💚 por Weversson Vital e Vitor Benedett Caldas</strong>
  <br/>
  <em>© 2026 VORTEX Cognitive Defense System. Combatendo Fake News com Tecnologia.</em>
</p>
