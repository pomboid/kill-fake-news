# 🌀 VORTEX — Sistema de Combate a Fake News com IA

> **Detecte, analise e verifique notícias falsas automaticamente usando Inteligência Artificial**

VORTEX é um sistema inteligente que coleta notícias de fontes confiáveis, analisa padrões de desinformação e permite verificar afirmações em tempo real. Usando Google Gemini AI e busca híbrida avançada, o sistema identifica características de fake news e fornece análises detalhadas com evidências.

---

## 🎯 O Que Este Projeto Faz?

### **1. Coleta Automática de Notícias** 📰
- Busca notícias em fontes confiáveis (G1, Folha, UOL, BBC Brasil, CNN Brasil, Estadão)
- Coleta automática a cada 6 horas
- Monitora a saúde das fontes de notícias

### **2. Análise Inteligente com IA** 🤖
- Usa **Google Gemini** para identificar marcadores de fake news
- Detecta linguagem sensacionalista, clickbait e manipulação emocional
- Identifica ausência de fontes e dados verificáveis
- Classifica notícias como confiáveis ou suspeitas

### **3. Verificação de Afirmações (Fact-Checking)** ✅
- Você cola uma afirmação → O sistema busca evidências
- **Busca híbrida**: vetorial (semântica) + BM25 (keywords)
- Retorna veredito: VERDADEIRO, FALSO ou INCONCLUSIVO
- Mostra evidências encontradas e nível de confiança

### **4. Dashboard Web** 🖥️
- Interface escura moderna e intuitiva
- Estatísticas em tempo real
- Histórico de verificações
- Qualidade da base de dados
- Status das fontes monitoradas

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────┐
│                   VORTEX SYSTEM                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📥 COLETA (RSS + Scraping)                        │
│      ↓                                             │
│  🤖 ANÁLISE IA (Gemini 2.0 Flash)                  │
│      ↓                                             │
│  📊 INDEXAÇÃO (ChromaDB + BM25)                    │
│      ↓                                             │
│  🔍 VERIFICAÇÃO (RAG Híbrido)                      │
│      ↓                                             │
│  🌐 API REST + Dashboard Web                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Tecnologias Utilizadas

| Componente | Tecnologia |
|------------|------------|
| **Backend** | Python 3.11, FastAPI |
| **IA** | Google Gemini 2.0 Flash |
| **Busca Vetorial** | ChromaDB (embeddings) |
| **Busca por Palavras** | BM25 (Rank-BM25) |
| **Scraping** | BeautifulSoup4, Feedparser |
| **Agendamento** | APScheduler |
| **Containerização** | Docker + Docker Compose |
| **Segurança** | API Key Auth, Rate Limiting, CORS |

---

## 🚀 Como Instalar e Usar

### **Opção 1: Deploy com Docker (Recomendado)** 🐳

**Requisitos:**
- Docker e Docker Compose instalados
- Porta 8420 disponível
- Chave de API do Google Gemini ([obtenha aqui](https://aistudio.google.com/app/apikey))

**Passo a passo:**

```bash
# 1. Clone o repositório
git clone https://github.com/pomboid/kill-fake-news.git
cd kill-fake-news

# 2. Configure as variáveis de ambiente
cp .env.production.example .env.production
nano .env.production  # Edite e adicione suas chaves

# 3. Suba o container
docker compose up -d

# 4. Acesse o dashboard
# http://SEU_IP:8420
```

**Variáveis obrigatórias no `.env.production`:**
```env
GEMINI_API_KEY=sua_chave_aqui
API_KEY=uma_chave_secreta_aleatoria
ADMIN_USERNAME=admin
ADMIN_PASSWORD=SenhaSegura123!
```

---

### **Opção 2: Instalação Local (Desenvolvimento)** 💻

**Requisitos:**
- Python 3.11+
- pip

```bash
# 1. Clone e entre no diretório
git clone https://github.com/pomboid/kill-fake-news.git
cd kill-fake-news

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis
cp .env.production.example .env
nano .env  # Adicione suas chaves

# 5. Rode o sistema
python main.py full-pipeline  # Pipeline completo
# ou
uvicorn server:app --host 0.0.0.0 --port 8420  # Servidor web
```

---

## 📖 Guia de Uso

### **Via CLI (Terminal)**

```bash
# Coletar notícias
python main.py collect

# Analisar com IA
python main.py analyze

# Indexar no banco vetorial
python main.py index

# Verificar uma afirmação
python main.py verify "O governo vai taxar o PIX"

# Pipeline completo (tudo acima de uma vez)
python main.py full-pipeline
```

### **Via Dashboard Web**

1. Acesse `http://localhost:8420` (ou `http://IP_DO_SERVIDOR:8420`)
2. Use a seção "🔍 Verify Claim" para verificar afirmações
3. Veja estatísticas, histórico e qualidade dos dados
4. Monitore o status das fontes de notícias

### **Via API REST**

**Autenticação:** Adicione header `X-API-Key: SUA_CHAVE_AQUI`

```bash
# Verificar claim
curl -X POST http://localhost:8420/api/verify \
  -H "X-API-Key: sua_chave" \
  -H "Content-Type: application/json" \
  -d '{"claim": "Vacinas causam autismo"}'

# Obter status do sistema
curl -H "X-API-Key: sua_chave" http://localhost:8420/api/status

# Ver histórico
curl -H "X-API-Key: sua_chave" http://localhost:8420/api/history

# Qualidade dos dados
curl -H "X-API-Key: sua_chave" http://localhost:8420/api/quality
```

---

## 🔒 Segurança

O VORTEX foi desenvolvido com segurança em mente:

- ✅ **Autenticação obrigatória** via API Key
- ✅ **Rate Limiting** (30 requisições/minuto)
- ✅ **CORS configurável** (whitelist de origens)
- ✅ **Container hardened** (non-root user, read-only filesystem)
- ✅ **Resource limits** (512MB RAM máximo)
- ✅ **Logs estruturados** para auditoria
- ✅ **Input validation** em todas as requisições

---

## 📊 Comandos Úteis (Docker)

```bash
# Ver logs em tempo real
docker logs vortex -f

# Ver últimas 50 linhas
docker logs vortex --tail 50

# Reiniciar container
docker compose restart

# Parar tudo
docker compose down

# Reconstruir após mudanças no código
docker compose build --no-cache
docker compose up -d

# Ver status
docker compose ps

# Limpar volumes (⚠️ apaga dados)
docker compose down -v
```

---

## 🧪 Testes

O projeto possui 67 testes automatizados cobrindo todas as funcionalidades:

```bash
# Rodar todos os testes
python -m pytest tests/ -v

# Rodar apenas testes de análise
python -m pytest tests/test_detector.py -v

# Ver cobertura
python -m pytest --cov=. tests/
```

---

## 📁 Estrutura do Projeto

```
kill-fake-news/
├── core/
│   ├── collector.py          # Coleta de notícias (RSS/Scraping)
│   ├── detector.py           # Análise com IA (Gemini)
│   ├── indexer.py            # Indexação (ChromaDB)
│   └── verifier.py           # Verificação (RAG)
├── templates/
│   └── dashboard.html        # Interface web
├── tests/                    # Testes automatizados
├── data/                     # Dados persistentes (não versionado)
├── scheduler.py              # Automação de coleta
├── server.py                 # API FastAPI
├── main.py                   # CLI principal
├── Dockerfile                # Imagem Docker
├── docker-compose.yml        # Orquestração
├── requirements.txt          # Dependências Python
└── README.md                 # Este arquivo
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## ⚠️ Limitações e Avisos

- **Free Tier do Gemini**: Limite de requisições/dia. Para produção, considere upgrade.
- **Precisão da IA**: Não é 100%. Sempre verifique fontes primárias.
- **Idioma**: Otimizado para português brasileiro.
- **Fontes**: Limitado às fontes configuradas em `scheduler.py`.

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/pomboid/kill-fake-news/issues)
- **LinkedIn**: [Weversson Vital](https://www.linkedin.com/in/weversson-vital/) | [Vitor Benedett Caldas](https://www.linkedin.com/in/vitorbenedettcaldas/)

---

## 🌟 Roadmap Futuro

- [ ] Suporte a múltiplos idiomas
- [ ] Integração com Telegram/WhatsApp
- [ ] Sistema de reputação de fontes
- [ ] Dashboard analytics avançado
- [ ] API REST v2 com GraphQL
- [ ] Extensão para navegadores

---

**Desenvolvido por Weversson Vital e Vitor Benedett Caldas** | 2026
