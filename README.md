<p align="center">
  <img src="https://img.shields.io/badge/VORTEX-Cognitive_Defense_System-00FFB2?style=for-the-badge&labelColor=0A0A0A" alt="VORTEX Badge"/>
</p>

<h1 align="center">🌀 VORTEX</h1>

<p align="center">
  <strong>Sistema Inteligente de Combate a Fake News com Múltiplos Provedores de IA</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/AI_Providers-8-FF6B6B?logo=openai&logoColor=white" alt="8 AI Providers"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
</p>

<p align="center">
  <em>Detecte, analise e verifique notícias falsas automaticamente usando 8 provedores de IA com failover automático</em>
</p>

---

## 📖 O Que é o VORTEX?

O **VORTEX** (Verification & Observation of Real-Time EXploits) é um sistema completo de defesa cognitiva contra desinformação baseado em **RAG (Retrieval-Augmented Generation)**. Em termos simples:

1. 🤖 O sistema **coleta notícias** automaticamente de portais confiáveis via RSS/scraping
2. 🧠 Usa **8 provedores de IA diferentes** (Groq, Gemini, OpenAI, Claude, etc.) com failover automático
3. 🔍 Permite que **você cole qualquer texto ou afirmação** e o sistema verifica se é verdadeiro, falso ou inconclusivo
4. 📊 Mostra tudo em um **painel visual moderno** com estatísticas em tempo real

> **Pense no VORTEX como um "detector de mentiras digital"** — ele cruza informações de fontes confiáveis para te dizer se aquela notícia do WhatsApp é verdadeira ou não.

---

## 🤖 8 Provedores de IA com Failover Automático

O VORTEX suporta **8 provedores diferentes de IA**, proporcionando **máxima resiliência e flexibilidade**:

### 🟢 FREE

| # | Provider | Modelos | Embeddings | API Key |
|---|----------|---------|------------|---------|
| 1 | **Groq** ⭐ | Llama 3.3 70B, Gemma 2 9B, Mixtral 8x7B, Qwen 2.5 7B | ❌ | [Obter Key](https://console.groq.com/keys) |
| 2 | **Gemini** | Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash | ✅ 768d | [Obter Key](https://aistudio.google.com/apikey) |

### 🟡 Freemium

| # | Provider | Modelos | Embeddings | API Key |
|---|----------|---------|------------|---------|
| 3 | **OpenAI** | GPT-4o, GPT-4o-mini ($0.15/1M tokens) | ✅ 1536d | [Obter Key](https://platform.openai.com/api-keys) |
| 4 | **Anthropic** | Claude 3.5 Sonnet, Claude 3.5 Haiku ($0.25/1M tokens) | ❌ | [Obter Key](https://console.anthropic.com/account/keys) |

### 🔴 Paid

| # | Provider | Modelos | Embeddings | API Key |
|---|----------|---------|------------|---------|
| 5 | **DeepSeek** | DeepSeek-V3, DeepSeek-R1 (~$0.14/1M tokens) | ❌ | [Obter Key](https://platform.deepseek.com/api_keys) |
| 6 | **Mistral** | Mistral Large 2, Mistral Small, Mixtral 8x7B | ✅ 1024d | [Obter Key](https://console.mistral.ai/api-keys) |
| 7 | **Together** | Llama 3.1 405B, Mixtral 8x22B, Qwen 2.5 | ✅ 1024d | [Obter Key](https://api.together.xyz/settings/api-keys) |
| 8 | **Cohere** | Command R+, Command R | ✅ 1024d | [Obter Key](https://dashboard.cohere.com/api-keys) |

### ✨ Benefícios do Sistema Multi-Provider

- ✅ **Failover Automático**: Se um provedor falhar, tenta automaticamente o próximo
- ✅ **100% Gratuito**: Funciona completamente com Groq + Gemini (ambos FREE)
- ✅ **Load Balancing**: Opcional para distribuir requisições (round-robin)
- ✅ **Máxima Resiliência**: 8 opções de backup
- ✅ **Flexibilidade Total**: Escolha por custo, qualidade, compliance regional
- ✅ **5 Opções de Embeddings**: Gemini, OpenAI, Mistral, Together, Cohere

---

## 🚀 Começando em 5 Minutos

### 1️⃣ Obter API Keys (Escolha pelo menos 1)

**Recomendado para começar (100% GRÁTIS):**

1. **Groq** (FREE, ilimitado): https://console.groq.com/keys
   - Cadastro instantâneo com email
   - Modelos ultra-rápidos (Llama 3.3 70B)

2. **Gemini** (FREE, 1M tokens/min): https://aistudio.google.com/apikey
   - Login com conta Google
   - Inclui embeddings (768 dimensões)

### 2️⃣ Configurar o .env

Crie um arquivo `.env` na raiz do projeto:

```bash
# Opção 1: APENAS Groq (mais simples, FREE)
GROQ_API_KEY=gsk_sua_chave_aqui

# Opção 2: Groq + Gemini (FREE com embeddings)
GROQ_API_KEY=gsk_sua_chave_aqui
GEMINI_API_KEY=AIzaSy_sua_chave_aqui

# Opção 3: Todos os 8 provedores (máxima resiliência)
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIzaSy_...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
MISTRAL_API_KEY=...
TOGETHER_API_KEY=...
COHERE_API_KEY=...

# Ordem de prioridade (opcional - padrão abaixo)
ENABLED_PROVIDERS=groq,gemini,openai,anthropic,deepseek,mistral,together,cohere

# Database (padrão do docker-compose)
DB_HOST=vortex-db
DB_PORT=5432
DB_USER=vortex
DB_PASSWORD=vortex_password
DB_NAME=vortex_db

# Coleta automática (em horas)
COLLECT_INTERVAL_HOURS=1
```

### 3️⃣ Rodar com Docker

```bash
# Clone o repositório
git clone https://github.com/pomboid/kill-fake-news.git
cd kill-fake-news

# Configure o .env (veja passo anterior)
nano .env

# Suba os containers
docker compose up -d

# Aguarde ~30s para o PostgreSQL inicializar

# Popule os feeds RSS (155 feeds de 6 fontes)
docker compose exec backend python scripts/seed_rss_feeds.py

# Colete as primeiras notícias
docker compose exec backend python main.py collect

# Analise com IA (Phase 2)
docker compose exec backend python main.py analyze --limit 100

# Indexe para busca semântica (Phase 3)
docker compose exec backend python main.py index
```

### 4️⃣ Verificar uma Afirmação

```bash
docker compose exec backend python main.py verify "O governo vai taxar o PIX"
```

**Resultado:**
```
🔍 AFIRMAÇÃO ANALISADA: O governo vai taxar o PIX

🟢 [FALSO]
Confiança: 85%

Análise:
A afirmação é falsa. O governo federal esclareceu publicamente que não há
proposta de taxação do PIX. A confusão surgiu de medidas de fiscalização
da Receita Federal sobre movimentações financeiras acima de R$ 5.000/mês,
que já existiam antes e não afetam transações PIX normais.

Evidências:
- "Governo nega taxação do PIX e esclarece fiscalização"
- "Receita Federal: monitoramento não significa imposto"
```

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

Cada artigo coletado é analisado por **um dos 8 provedores de IA** (com failover automático):

**Marcadores detectados:**
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

- 📊 **Embeddings**: Vetores de 768 a 1536 dimensões (depende do provider)
- 🔎 **Busca semântica**: Cosine distance search no PostgreSQL
- ⚡ **Performance**: Índice HNSW para buscas rápidas
- 🎯 **Precisão**: Encontra artigos relevantes mesmo sem palavras exatas
- 🔄 **Failover**: Se um provider de embedding falhar, tenta o próximo

### 4. ✅ Verificação de Fatos (Phase 4 - RAG)

Você pode verificar **qualquer afirmação** ou **artigo completo**:

**Fluxo de verificação:**
1. Usuário submete afirmação: *"O governo vai taxar o PIX"*
2. Sistema gera embedding da afirmação (usa provider disponível)
3. Busca semântica retorna top 5 artigos mais similares (pgvector)
4. IA compara afirmação com evidências (usa provider disponível)
5. Retorna veredicto estruturado:

```
🟢 [VERDADEIRO]               - Confirmado por evidências
🔴 [FALSO]                    - Contradiz evidências
🟡 [PARCIALMENTE VERDADEIRO]  - Parcialmente correto
⚪ [INCONCLUSIVO]              - Sem evidências suficientes
```

### 5. 🖥️ Dashboard Interativo

Interface web moderna construída com **React 18 + TypeScript**, tema escuro e responsiva:

- 📊 **Estatísticas em tempo real** — Artigos coletados, analisados, verificações
- 📜 **Histórico de verificações** — Todas as verificações anteriores
- 🟢 **Status das fontes** — Monitoramento de saúde (HTTP 200)
- 🤖 **Status dos Provedores de IA** — Qual está ativo, taxa de sucesso
- ⏰ **Automação** — Próxima execução do scheduler
- 🔐 **Login seguro** — Autenticação via Google (Clerk)

---

## 🏗️ Arquitetura do Sistema

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           VORTEX SYSTEM                                    │
├──────────────────────┬─────────────────────────────────────────────────────┤
│                      │                                                     │
│  🌐 FRONTEND         │  ⚙️ BACKEND                                         │
│  React + TypeScript  │  Python 3.11 + FastAPI                              │
│  Porta 80 (nginx)    │  Porta 8420                                         │
│                      │                                                     │
│  ┌────────────────┐  │  ┌───────────────────────────────────────────────┐ │
│  │  Dashboard     │─────▶│  API REST                                     │ │
│  │  Login/Auth    │  │  │  /api/verify  (fact-check with failover)      │ │
│  │  Estatísticas  │  │  │  /api/analyze (run phase 2)                   │ │
│  │  Histórico     │  │  │  /api/status  (system + AI providers)         │ │
│  │  AI Status     │  │  │  /api/history (past verifications)            │ │
│  └────────────────┘  │  │  /api/sources (source health)                 │ │
│                      │  │  /api/quality (data quality)                  │ │
│                      │  └───────────┬───────────────────────────────────┘ │
│                      │              │                                      │
│                      │  ┌───────────▼──────────────────────────────────┐  │
│                      │  │  🤖 Multi-Provider AI Engine                 │  │
│                      │  │                                              │  │
│                      │  │  🟢 FREE: Groq, Gemini                       │  │
│                      │  │  🟡 Freemium: OpenAI, Anthropic              │  │
│                      │  │  🔴 Paid: DeepSeek, Mistral, Together, Cohere│  │
│                      │  │                                              │  │
│                      │  │  ✅ Automatic Failover                       │  │
│                      │  │  ✅ Load Balancing (optional)                │  │
│                      │  │  ✅ Health Tracking                          │  │
│                      │  └──────────────────────────────────────────────┘  │
│                      │              │                                      │
│                      │  ┌───────────▼──────────────────────────────────┐  │
│                      │  │  📋 4-Phase Pipeline                         │  │
│                      │  │                                              │  │
│                      │  │  Phase 1: Collector (RSS/Scraping)          │  │
│                      │  │  • 155 RSS feeds from PostgreSQL            │  │
│                      │  │  • Parallel scraping (5 async)              │  │
│                      │  │  • Batch commits                            │  │
│                      │  │                                              │  │
│                      │  │  Phase 2: Analyzer (AI with failover)       │  │
│                      │  │  • Fake news markers detection              │  │
│                      │  │  • Quality scores (0-10)                    │  │
│                      │  │  • Tries providers in priority order        │  │
│                      │  │                                              │  │
│                      │  │  Phase 3: Indexer (pgvector + embeddings)   │  │
│                      │  │  • Generate embeddings (5 provider options) │  │
│                      │  │  • Store in PostgreSQL                      │  │
│                      │  │  • HNSW index for fast search               │  │
│                      │  │                                              │  │
│                      │  │  Phase 4: Verifier (RAG with failover)      │  │
│                      │  │  • Semantic search (cosine distance)        │  │
│                      │  │  • LLM cross-referencing (8 providers)      │  │
│                      │  │  • Structured verdict                       │  │
│                      │  └──────────────────────────────────────────────┘  │
│                      │              │                                      │
│                      │  ┌───────────▼──────────────────────────────────┐  │
│                      │  │  📊 PostgreSQL 16 + pgvector                 │  │
│                      │  │  • Articles (title, content, url)            │  │
│                      │  │  • Embeddings (768-1536 dim vectors)         │  │
│                      │  │  • Analysis (AI verdicts)                    │  │
│                      │  │  • Verifications (fact-checks)               │  │
│                      │  │  • RSS Feeds (155 URLs)                      │  │
│                      │  │  • Sources (6 news outlets)                  │  │
│                      │  └──────────────────────────────────────────────┘  │
│                      │                                                     │
│                      │  ⏰ APScheduler (Background Jobs)                   │
│                      │  • Collect every 1h (configurable)                 │
│                      │  • Source monitoring every 1h                      │
│                      │                                                     │
├──────────────────────┴─────────────────────────────────────────────────────┤
│  🐳 Docker Compose (3 containers: backend, frontend, vortex-db)           │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Para Quê? |
|--------|-----------|-----------|
| **Backend** | Python 3.11 | Linguagem principal |
| | FastAPI | API REST moderna e assíncrona |
| | SQLModel | ORM (Object-Relational Mapping) |
| | AsyncPG | Driver PostgreSQL assíncrono |
| | APScheduler | Jobs agendados (coleta automática) |
| **Frontend** | React 18 + TypeScript | Interface web moderna |
| | Vite | Build tool ultra-rápido |
| | TailwindCSS | Estilização responsiva |
| | Clerk | Autenticação (Google OAuth) |
| **Database** | PostgreSQL 16 | Banco de dados relacional |
| | pgvector | Busca vetorial (embeddings) |
| **AI Providers** | Groq (FREE) | Llama 3.3 70B, Gemma 2 9B |
| | Gemini (FREE) | Gemini 2.0 Flash + embeddings |
| | OpenAI | GPT-4o, embeddings |
| | Anthropic | Claude 3.5 Sonnet/Haiku |
| | DeepSeek | DeepSeek-V3 (custo-benefício) |
| | Mistral | Mistral Large 2 (GDPR) |
| | Together AI | Llama 3.1 405B |
| | Cohere | Command R+ (RAG specialist) |
| **DevOps** | Docker + Docker Compose | Containerização |
| | GitHub Actions | CI/CD (futuro) |

---

## 📊 Schema do Banco de Dados

```sql
-- Fontes de notícias
CREATE TABLE source (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    display_name VARCHAR,
    website_url VARCHAR,
    status VARCHAR DEFAULT 'online',
    last_checked TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Feeds RSS por fonte
CREATE TABLE rss_feed (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES source(id),
    feed_url VARCHAR UNIQUE,
    feed_type VARCHAR DEFAULT 'rss2',  -- rss2, atom, sitemap
    category VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    last_fetched TIMESTAMP,
    fetch_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_error VARCHAR
);

-- Artigos coletados
CREATE TABLE article (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES source(id),
    title VARCHAR,
    subtitle VARCHAR,
    author VARCHAR,
    published_at TIMESTAMP,
    url VARCHAR UNIQUE,
    content TEXT,
    embedding vector(768),  -- ou 1536 dependendo do provider
    created_at TIMESTAMP
);

-- Análises de IA
CREATE TABLE analysis (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES article(id) UNIQUE,
    is_fake BOOLEAN,
    confidence_score FLOAT,
    reasoning TEXT,
    detected_markers JSON,
    scores JSON,  -- {factual_consistency, linguistic_bias, sensationalism, source_credibility}
    analyzed_at TIMESTAMP
);

-- Verificações de fatos
CREATE TABLE verification (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR,
    claim TEXT,
    verdict VARCHAR,
    confidence FLOAT,
    evidence JSON,  -- Array de IDs de artigos usados como evidência
    created_at TIMESTAMP
);

-- Índice HNSW para busca vetorial rápida
CREATE INDEX ON article USING hnsw (embedding vector_cosine_ops);
```

---

## 🔧 Comandos Úteis

### Gerenciamento de Containers

```bash
# Ver logs em tempo real
docker compose logs -f backend

# Reiniciar backend
docker compose restart backend

# Rebuild completo
docker compose down
docker compose up -d --build

# Ver uso de recursos
docker stats
```

### Pipeline de Dados

```bash
# Phase 1: Coletar notícias (todas disponíveis)
docker compose exec backend python main.py collect

# Phase 1: Coletar apenas 50 artigos
docker compose exec backend python main.py collect --limit 50

# Phase 2: Analisar artigos não analisados (máx 100)
docker compose exec backend python main.py analyze --limit 100

# Phase 3: Indexar artigos analisados (gerar embeddings)
docker compose exec backend python main.py index

# Phase 4: Verificar uma afirmação
docker compose exec backend python main.py verify "texto da afirmação"

# Ver estatísticas do sistema
docker compose exec backend python main.py status
```

### Database

```bash
# Conectar ao PostgreSQL
docker compose exec vortex-db psql -U vortex -d vortex_db

# Ver total de artigos
docker compose exec -T vortex-db psql -U vortex -d vortex_db -c "SELECT COUNT(*) FROM article;"

# Ver distribuição por fonte
docker compose exec -T vortex-db psql -U vortex -d vortex_db -c \
  "SELECT s.name, COUNT(a.id) FROM source s LEFT JOIN article a ON a.source_id = s.id GROUP BY s.name ORDER BY count DESC;"

# Ver feeds com mais erros
docker compose exec -T vortex-db psql -U vortex -d vortex_db -c \
  "SELECT feed_url, error_count, last_error FROM rss_feed WHERE error_count > 0 ORDER BY error_count DESC LIMIT 10;"
```

### Monitoramento de Provedores de IA

```bash
# Ver status de todos os provedores (em Python)
docker compose exec backend python -c "
from core.llm import LLMManager
from core.config import Config
import asyncio

async def main():
    manager = LLMManager(
        enabled_providers=Config.ENABLED_PROVIDERS,
        api_keys=Config.get_provider_api_keys()
    )
    status = manager.get_status()
    print('=== LLM Providers ===')
    for p in status['llm_providers']:
        print(f'{p[\"name\"]}: {p[\"status\"]} (success: {p[\"success_count\"]}, errors: {p[\"error_count\"]})')

asyncio.run(main())
"
```

---

## 🌐 Configuração Avançada

### Selecionar Apenas Provedores FREE

```env
ENABLED_PROVIDERS=groq,gemini
```

### Ativar Load Balancing (Round-Robin)

```env
LOAD_BALANCE=true
```

### Usar Apenas Provedores Pagos de Alta Qualidade

```env
ENABLED_PROVIDERS=openai,anthropic
```

### Ajustar Intervalo de Coleta

```env
COLLECT_INTERVAL_HOURS=6  # Coletar a cada 6 horas
```

---

## 📈 Métricas de Performance (Exemplo Real)

**Coleta:**
- 📰 8.673 artigos coletados
- ⏱️ Tempo médio: ~1 hora (155 feeds)
- 🎯 Taxa de sucesso: 76%
- 💾 Tamanho do banco: ~35 MB

**Análise:**
- 🤖 100 artigos analisados em ~5 minutos (Groq)
- 📊 Velocidade: ~20 artigos/minuto
- 💰 Custo: $0 (usando Groq FREE)

**Verificação:**
- 🔍 Tempo médio de resposta: 2-5 segundos
- 🎯 Top 5 artigos similares recuperados
- ✅ Veredicto estruturado com evidências

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- **Groq** por fornecer acesso FREE ilimitado aos modelos Llama
- **Google** pelo Gemini com tier FREE generoso
- **OpenAI, Anthropic, DeepSeek, Mistral, Together AI, Cohere** pelas APIs de qualidade
- Comunidade Python e ecossistema FastAPI
- Contribuidores do projeto pgvector

---

## 📞 Suporte

- 📧 **Issues**: [GitHub Issues](https://github.com/pomboid/kill-fake-news/issues)
- 💼 **LinkedIn**: [Weversson Vital](https://www.linkedin.com/in/weversson-vital/) | [Vitor Benedett Caldas](https://www.linkedin.com/in/vitorbenedettcaldas/)

---

<p align="center">
  Feito com ❤️ por <strong>VORTEX Team</strong>
</p>

<p align="center">
  <sub>Combatendo desinformação, uma verificação de cada vez 🛡️</sub>
</p>
