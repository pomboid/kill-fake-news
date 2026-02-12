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
  <img src="https://img.shields.io/badge/Gemini_AI-2.0_Flash-4285F4?logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
</p>

<p align="center">
  <em>Detecte, analise e verifique notícias falsas automaticamente usando Inteligência Artificial</em>
</p>

---

## 📖 O Que é o VORTEX?

O **VORTEX** (Verification & Observation of Real-Time EXploits) é um sistema completo de defesa cognitiva contra desinformação. Em termos simples:

1. 🤖 O sistema **coleta notícias** automaticamente de portais confiáveis como G1, Folha, UOL, BBC Brasil, CNN Brasil e Estadão
2. 🧠 Usa **Inteligência Artificial (Google Gemini)** para analisar cada notícia e identificar padrões de fake news
3. 🔍 Permite que **você cole qualquer texto ou afirmação** e o sistema verifica se é verdadeiro, falso ou inconclusivo
4. 📊 Mostra tudo em um **painel visual moderno** com estatísticas em tempo real

> **Pense no VORTEX como um "detector de mentiras digital"** — ele cruza informações de fontes confiáveis para te dizer se aquela notícia do WhatsApp é verdadeira ou não.

---

## 🖥️ Screenshots

### Dashboard Principal
Interface moderna com tema escuro, estatísticas em tempo real e motor de verificação integrado.

### Funcionalidades do Dashboard:
- **Reference Base** — Quantidade de artigos indexados na base de dados
- **AI Analyzed** — Total de artigos analisados pela IA
- **Quality Index** — Percentual de qualidade da base de dados
- **Live Sources** — Status das fontes de notícias monitoradas (ex: 6/6 online)
- **Cortex Verification Engine** — Motor de verificação onde você cola textos para analisar
- **Automation Ops** — Status do crawler e monitoramento automático
- **Media Intelligence Sources** — Saúde de cada fonte (G1, Folha, UOL, etc.)

---

## 🎯 Funcionalidades Principais

### 1. 📰 Coleta Automática de Notícias
O sistema busca notícias automaticamente em **6 fontes confiáveis** brasileiras:

| Fonte | Tipo | Frequência |
|-------|------|------------|
| G1 (Globo) | RSS + Scraping | A cada 12 horas |
| Folha de S.Paulo | RSS + Scraping | A cada 12 horas |
| UOL | RSS + Scraping | A cada 12 horas |
| BBC Brasil | RSS + Scraping | A cada 12 horas |
| CNN Brasil | RSS + Scraping | A cada 12 horas |
| Estadão | RSS + Scraping | A cada 12 horas |

> 💡 As fontes são monitoradas a cada **1 hora** para verificar se estão online.

### 2. 🤖 Análise com Inteligência Artificial
Cada artigo coletado é analisado pelo **Google Gemini 2.0 Flash**, que identifica:

- ⚠️ **Linguagem sensacionalista** (títulos exagerados, alarmistas)
- 🎣 **Clickbait** (títulos enganosos para gerar cliques)
- 😡 **Manipulação emocional** (apelar para medo, raiva, indignação)
- 📉 **Ausência de fontes** (afirmações sem dados ou referências)
- 🔄 **Inconsistências** (informações que se contradizem)

O resultado é uma classificação: **Confiável** ou **Suspeito**, com um score de confiança.

### 3. ✅ Verificação de Fatos (Fact-Checking)
Você pode verificar **qualquer afirmação** ou **artigo completo** (até 10.000 caracteres):

```
Exemplo: "O governo vai taxar todas as transações do PIX"
```

O sistema usa **busca híbrida** para encontrar evidências:
- 🧮 **Busca Vetorial (Semântica)** — Encontra artigos com significado similar usando embeddings (ChromaDB)
- 📝 **Busca por Palavras-chave (BM25)** — Encontra artigos com palavras exatas

O resultado mostra:
- 🟢 **VERDADEIRO** — A afirmação é confirmada por evidências
- 🔴 **FALSO** — A afirmação contradiz as evidências encontradas
- 🟡 **INCONCLUSIVO** — Não há evidências suficientes para confirmar ou negar

### 4. 🖥️ Dashboard Interativo
Interface web moderna construída com **React + TypeScript**, tema escuro e responsiva:

- 📊 **Estatísticas em tempo real** — Artigos coletados, analisados, qualidade
- 📜 **Histórico de verificações** — Todas as verificações anteriores
- 🟢 **Status das fontes** — Quais fontes estão online (HTTP 200)
- ⏰ **Automação** — Próxima execução do crawler e monitor
- 🔐 **Login seguro** — Autenticação via Google (Clerk)

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        VORTEX SYSTEM                            │
├────────────────────────┬────────────────────────────────────────┤
│                        │                                        │
│   🌐 FRONTEND          │   ⚙️ BACKEND                          │
│   (React + TypeScript) │   (Python + FastAPI)                   │
│   Porta 80 (nginx)     │   Porta 8420                          │
│                        │                                        │
│   ┌──────────────┐     │   ┌──────────────────────────────┐    │
│   │  Dashboard   │────────▶│  API REST                    │    │
│   │  Login/Auth  │     │   │  /api/verify                 │    │
│   │  Estatísticas│     │   │  /api/status                 │    │
│   │  Histórico   │     │   │  /api/history                │    │
│   └──────────────┘     │   │  /api/sources                │    │
│                        │   │  /api/quality                │    │
│                        │   └──────────┬───────────────────┘    │
│                        │              │                         │
│                        │   ┌──────────▼───────────────────┐    │
│                        │   │  🤖 Motor de IA              │    │
│                        │   │  • Coleta RSS/Scraping       │    │
│                        │   │  • Análise Gemini AI         │    │
│                        │   │  • Indexação ChromaDB        │    │
│                        │   │  • Verificação RAG Híbrido   │    │
│                        │   └──────────────────────────────┘    │
│                        │                                        │
├────────────────────────┴────────────────────────────────────────┤
│  🐳 Docker Compose (2 containers + rede interna)               │
└─────────────────────────────────────────────────────────────────┘
```

### 🛠️ Stack Tecnológica

| Camada | Tecnologia | Para Quê? |
|--------|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite | Interface do usuário |
| **Estilo** | CSS moderno (tema escuro) | Visual premium |
| **Autenticação** | Clerk (Google OAuth) | Login seguro |
| **Backend** | Python 3.11 + FastAPI | API e lógica do servidor |
| **IA Generativa** | Google Gemini 2.0 Flash | Análise de fake news |
| **Embeddings** | Gemini Embedding Model | Transformar texto em vetores |
| **Banco Vetorial** | ChromaDB | Busca semântica |
| **Busca Textual** | Rank-BM25 | Busca por palavras-chave |
| **Scraping** | BeautifulSoup4 + Feedparser | Coleta de notícias |
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

# Configurações do sistema
COLLECT_INTERVAL_HOURS=12
SOURCE_CHECK_INTERVAL_HOURS=1
LOG_LEVEL=INFO
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

> ⚠️ **IMPORTANTE:** Substitua `SEU_IP` pelo IP do seu servidor (ex: `192.168.1.100`).

#### Passo 3: Suba os Containers

```bash
docker compose up -d --build
```

Aguarde ~60 segundos para o build completar.

#### Passo 4: Verifique

```bash
# Ver se os 2 containers estão rodando
docker ps

# Deve mostrar:
# vortex-backend   (porta 8420)
# vortex-frontend  (porta 80)
```

#### Passo 5: Acesse

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

# Configure variáveis de ambiente
cp .env.production.example .env
nano .env  # Adicione sua GEMINI_API_KEY

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
3. Use o campo **"Cortex Verification Engine"** para verificar afirmações:
   - Cole uma notícia ou afirmação (até 10.000 caracteres)
   - Clique em **"Run Verification"**
   - Veja o resultado: **Verdadeiro**, **Falso** ou **Inconclusivo**
4. Monitore as **estatísticas** e **fontes** na dashboard

### Via CLI (Linha de Comando)

```bash
# Coletar notícias de todas as fontes
python main.py collect

# Analisar artigos com IA
python main.py analyze

# Indexar no banco vetorial
python main.py index

# Verificar uma afirmação
python main.py verify "O governo vai taxar o PIX"

# Pipeline completo (coleta + análise + indexação)
python main.py full-pipeline
```

### Via API REST

```bash
# Verificar uma afirmação
curl -X POST http://SEU_IP:8420/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "Vacinas causam autismo"}'

# Status do sistema
curl http://SEU_IP:8420/api/status

# Histórico de verificações
curl http://SEU_IP:8420/api/history

# Qualidade da base de dados
curl http://SEU_IP:8420/api/quality

# Status das fontes
curl http://SEU_IP:8420/api/sources
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
│   ├── models.py                  # Modelos de dados
│   ├── rate_limits.py             # Limites da API Gemini
│   ├── logging_config.py          # Configuração de logs
│   └── ui.py                      # Interface CLI
│
├── 🧠 modules/                    # Módulos de Processamento
│   ├── intelligence/              # Coleta de notícias
│   ├── analysis/                  # Indexação vetorial
│   └── detection/                 # Análise IA + Verificação
│
├── 🧪 tests/                      # Testes Automatizados
│
├── 📄 server.py                   # API FastAPI (backend)
├── 📄 scheduler.py                # Agendador de tarefas
├── 📄 main.py                     # CLI principal
├── 🐳 Dockerfile                  # Build do backend
├── 🐳 docker-compose.yml          # Orquestração (frontend + backend)
├── 📋 requirements.txt            # Dependências Python
└── 📖 README.md                   # Este arquivo
```

---

## 🐳 Comandos Docker Úteis

```bash
# 📊 Ver containers rodando
docker ps

# 📜 Ver logs do backend
docker logs vortex-backend --tail 50

# 📜 Ver logs do frontend
docker logs vortex-frontend --tail 50

# 🔄 Atualizar após mudanças no código
git pull origin main
docker compose down
docker compose up -d --build

# ⏹️ Parar tudo
docker compose down

# 🗑️ Limpar tudo (⚠️ APAGA DADOS)
docker compose down -v
docker system prune -af
```

---

## ⚠️ Limitações e Avisos

| Limitação | Detalhe |
|-----------|---------|
| **Free Tier Gemini** | ~1.500 requisições/dia no plano gratuito. Suficiente para uso moderado. |
| **Precisão da IA** | Nenhuma IA é 100% precisa. Sempre verifique fontes primárias. |
| **Idioma** | Otimizado para **Português Brasileiro**. |
| **Fontes** | Limitado às 6 fontes configuradas. Novas podem ser adicionadas. |
| **Embeddings** | Qualidade depende da base de dados. Mais artigos = mais precisão. |

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

- [ ] 🌍 Suporte a múltiplos idiomas
- [ ] 💬 Integração com Telegram e WhatsApp
- [ ] ⭐ Sistema de reputação de fontes
- [ ] 📈 Dashboard analytics avançado
- [ ] 🔌 Extensão para navegadores (Chrome/Firefox)
- [ ] 🗄️ Migração para PostgreSQL
- [ ] 📱 Aplicativo mobile (React Native)

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
