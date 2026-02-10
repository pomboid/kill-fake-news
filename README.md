# 🌀 VORTEX — Fake News Detection & Verification System

Sistema de detecção e verificação de fake news utilizando IA (Google Gemini), busca híbrida (ChromaDB + BM25) e RAG (Retrieval-Augmented Generation).

## ⚡ Features

| Feature | Descrição |
|---------|-----------|
| **Coleta automática** | Scrapping de fontes de notícias confiáveis |
| **Análise com IA** | Detecção de marcadores de fake news via Gemini |
| **Verificação de claims** | RAG com busca híbrida (vetorial + BM25) |
| **API REST** | FastAPI com autenticação, rate limiting, CORS |
| **Dashboard web** | Interface dark theme para monitoramento |
| **Scheduler** | Coleta automática a cada 6h |
| **Docker** | Container hardened para produção |

## 🚀 Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/pomboid/kill-fake-news.git
cd kill-fake-news

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure API key
cp .env.production.example .env
# Edite .env e adicione sua GEMINI_API_KEY

# 4. Use via CLI
python main.py collect          # Coleta notícias
python main.py analyze          # Análise com IA
python main.py index            # Indexa para verificação
python main.py verify "claim"   # Verifica uma afirmação
python main.py full-pipeline    # Roda tudo em sequência

# 5. Ou via API
uvicorn server:app --port 8420
# Acesse http://localhost:8420
```

## 🐳 Deploy com Docker

```bash
cp .env.production.example .env.production
# Configure suas chaves no .env.production
docker-compose up -d
# Acesse http://localhost:8420
```

## 🔒 Segurança

- Usuário non-root no container
- Filesystem read-only
- Rate limiting (30 req/min)
- Autenticação por API key
- CORS whitelist
- Resource limits (512MB RAM)

## 📊 Testes

```bash
python -m pytest tests/ -v
# 67 tests passing
```

## 📝 Licença

MIT
