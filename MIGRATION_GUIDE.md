# Guia de Migração: OpenAI (1536 dims) + Gemini Backup

## 📋 Resumo

Esta migração permite usar **OpenAI como primário** (1536 dims, pago, confiável) e **Gemini como backup** (768 dims, grátis).

**Tempo total:** ~45 minutos
**Downtime:** ~5 minutos (durante migração do banco)
**Custo:** ~$0.50/mês na OpenAI

---

## ✅ Pré-requisitos

- [x] $10 adicionados na conta OpenAI
- [x] OPENAI_API_KEY configurada no `.env`
- [x] Backup do banco de dados criado
- [x] Acesso SSH ao servidor

---

## 🚀 Passo a Passo no Servidor

### **FASE 1: Preparação (5min)**

```bash
# 1. Conectar ao servidor
ssh root@vortex

# 2. Ir para o diretório do projeto
cd /opt/kill-fake-news

# 3. Criar backup do banco ANTES de qualquer mudança
docker compose exec postgres pg_dump -U postgres vortex > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

# Verificar backup foi criado
ls -lh backup_*.sql

# 4. Parar o backend (para evitar conflitos durante migração)
docker compose stop backend
```

---

### **FASE 2: Atualizar Código (2min)**

```bash
# 1. Pull das mudanças do GitHub
git pull origin main

# 2. Verificar novos arquivos
git log --oneline -5

# Você deve ver commits sobre:
# - Embedding adapter
# - SQL migration script
# - Config updates
```

---

### **FASE 3: Migrar Banco de Dados (10min)**

```bash
# 1. Entrar no container PostgreSQL
docker compose exec postgres psql -U postgres vortex

# 2. Dentro do psql, rodar o script de migração
\i /opt/kill-fake-news/scripts/migrate_embeddings_to_1536.sql

# OU copiar e colar o conteúdo do script manualmente

# 3. Verificar migração
SELECT
    COUNT(*) as total_articles,
    COUNT(embedding) as with_embeddings,
    ROUND(100.0 * COUNT(embedding) / NULLIF(COUNT(*), 0), 2) as percentage
FROM article;

# 4. Verificar dimensões (deve mostrar 1536)
SELECT array_length(embedding::float[], 1) as dimensions
FROM article WHERE embedding IS NOT NULL LIMIT 1;

# Resultado esperado: dimensions = 1536

# 5. Sair do psql
\q
```

---

### **FASE 4: Rebuild Backend (5min)**

```bash
# 1. Rebuild com novas dependências
docker compose build backend

# 2. Iniciar backend
docker compose start backend

# 3. Verificar logs
docker compose logs -f backend --tail=50

# Deve mostrar:
# - "LLM Manager initialized with 4 providers"
# - "Initialized OpenAI"
# - "Initialized Google Gemini"
```

---

### **FASE 5: Testar Sistema (10min)**

#### Teste 1: Verificar Providers

```bash
docker compose exec backend python -c "
from core.llm import LLMManager
from core.config import Config
import asyncio

async def test():
    manager = LLMManager(
        enabled_providers=Config.ENABLED_PROVIDERS,
        api_keys=Config.get_provider_api_keys()
    )

    print(f'✅ Total providers: {len(manager.llm_providers)}')
    print(f'✅ Embedding providers: {len(manager.embedding_providers)}')

    for p in manager.embedding_providers:
        print(f'   - {p.display_name} ({p.embedding_dimensions} dims)')

asyncio.run(test())
"
```

**Resultado esperado:**
```
✅ Total providers: 4
✅ Embedding providers: 2
   - OpenAI (1536 dims)
   - Google Gemini (768 dims)
```

#### Teste 2: Gerar Embedding de Teste

```bash
docker compose exec backend python -c "
from core.llm import LLMManager
from core.config import Config
import asyncio

async def test():
    manager = LLMManager(
        enabled_providers=Config.ENABLED_PROVIDERS,
        api_keys=Config.get_provider_api_keys()
    )

    text = 'Este é um teste de embedding com OpenAI.'
    embedding = await manager.get_embedding(text)

    print(f'✅ Generated embedding with {len(embedding)} dimensions')
    print(f'✅ First 5 values: {embedding[:5]}')

asyncio.run(test())
"
```

**Resultado esperado:**
```
INFO:VORTEX.LLM.Manager:Using OpenAI for embedding
✅ Generated embedding with 1536 dimensions
✅ First 5 values: [0.0123, -0.0456, 0.0789, ...]
```

#### Teste 3: Testar Failover (Gemini como Backup)

```bash
# Temporariamente remover OpenAI key
docker compose exec backend bash -c "
export OPENAI_API_KEY=''
python -c \"
from core.llm import LLMManager
from core.config import Config
import asyncio
import os

async def test():
    # Remove OpenAI key
    api_keys = Config.get_provider_api_keys()
    api_keys['openai'] = None

    manager = LLMManager(
        enabled_providers=Config.ENABLED_PROVIDERS,
        api_keys=api_keys
    )

    text = 'Teste de failover para Gemini.'
    embedding = await manager.get_embedding(text)

    print(f'✅ Failover successful! Generated {len(embedding)} dimensions')

asyncio.run(test())
\"
"
```

**Resultado esperado:**
```
INFO:VORTEX.LLM.Manager:Using Google Gemini for embedding
DEBUG:VORTEX.LLM.Adapter:Padded Google Gemini embedding: 768 → 1536 dims (added 768 zeros)
✅ Failover successful! Generated 1536 dimensions
```

---

### **FASE 6: Re-indexar Artigos (15min)**

```bash
# Limpar embeddings antigos (768 dims padded com zeros não são ideais)
docker compose exec backend python -c "
from core.database import get_session
from core.sql_models import Article
from sqlmodel import select
import asyncio

async def clear():
    async for session in get_session():
        result = await session.execute(select(Article))
        for article in result.scalars().all():
            article.embedding = None
        await session.commit()
        print('✅ Cleared all embeddings')

asyncio.run(clear())
"

# Re-indexar com OpenAI (gerará embeddings 1536 nativos)
docker compose exec backend python main.py index
```

**Resultado esperado:**
```
[+] PHASE 3: INDEXING DATA FOR VERIFICATION
[+] Checking for unindexed articles...
[+] Indexing 10 articles...
INFO:VORTEX.LLM.Manager:Using OpenAI for embedding
[+] Indexed: Título do artigo 1...
[+] Indexed: Título do artigo 2...
...
```

---

### **FASE 7: Teste Final (5min)**

```bash
# Testar busca semântica com claim
docker compose exec backend python main.py verify "Teste de verificação de claim"
```

**Resultado esperado:**
```
[+] PHASE 4: CLAIM VERIFICATION
[+] Claim: Teste de verificação de claim
[+] Generating embedding...
INFO:VORTEX.LLM.Manager:Using OpenAI for embedding
[+] Searching similar articles...
[+] Found 5 similar articles
[+] Analyzing with LLM...
INFO:VORTEX.LLM.Manager:Using Groq for JSON generation

╔════════════════════════════════════╗
║       ANÁLISE DE VERACIDADE        ║
╚════════════════════════════════════╝

🎯 Veredito: INCONCLUSIVO
📊 Confiança: 45.00%
...
```

---

## ✅ Verificação de Sucesso

Marque ✅ quando cada item estiver funcionando:

- [ ] OpenAI aparece como primeiro provider de embeddings
- [ ] Gemini aparece como segundo (backup)
- [ ] Embeddings têm 1536 dimensões
- [ ] Indexação funciona sem erros 404
- [ ] Busca semântica retorna resultados
- [ ] Verificação de claims funciona

---

## 🔧 Troubleshooting

### Erro: "404 models/text-embedding-004"

**Problema:** Gemini está sendo usado mas falha

**Solução:**
```bash
# Verificar ordem de providers
docker compose exec backend python -c "
from core.config import Config
print('Enabled providers:', Config.ENABLED_PROVIDERS)
"

# Deve mostrar: ['groq', 'openai', 'gemini', 'anthropic']
# OpenAI deve vir ANTES de Gemini
```

### Erro: "Invalid API key for OpenAI"

**Problema:** API key inválida ou sem crédito

**Solução:**
```bash
# Verificar se key está no .env
grep OPENAI_API_KEY /opt/kill-fake-news/.env

# Verificar créditos em: https://platform.openai.com/usage
# Adicionar $10 se necessário
```

### Erro: "Embedding has 768 dimensions, expected 1536"

**Problema:** Banco ainda tem coluna antiga ou migração falhou

**Solução:**
```bash
# Verificar coluna no banco
docker compose exec postgres psql -U postgres vortex -c "
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'article' AND column_name = 'embedding';
"

# Se ainda mostrar vector(768), rodar migração novamente
```

---

## 💰 Custos Estimados (OpenAI)

### Embeddings (text-embedding-3-small)
- **Preço:** $0.00002 por 1K tokens
- **$10 compra:** 500 milhões de tokens

### Para seu projeto:
- **10.000 artigos** (~5M tokens): $0.10
- **Verificações diárias** (100/dia, 3K/mês): $0.20/mês
- **Re-indexações** (1x/mês): $0.10/mês

**Total mensal:** ~$0.30-0.50/mês
**$10 dura:** ~20-30 meses 🎉

---

## 📊 Monitoring

### Verificar uso da OpenAI:
https://platform.openai.com/usage

### Verificar status dos providers:
```bash
docker compose exec backend python -c "
from core.llm import LLMManager
from core.config import Config
import json

manager = LLMManager(
    enabled_providers=Config.ENABLED_PROVIDERS,
    api_keys=Config.get_provider_api_keys()
)

status = manager.get_status()
print(json.dumps(status, indent=2))
"
```

---

## 🎉 Sucesso!

Parabéns! Seu sistema agora tem:
- ✅ OpenAI como provider primário (confiável, rápido, 1536 dims)
- ✅ Gemini como backup grátis (failover automático)
- ✅ Melhor qualidade de busca semântica (1536 vs 768)
- ✅ Custo muito baixo (~$0.50/mês)

**Próximos passos:**
1. Monitorar uso na OpenAI durante 1 semana
2. Ajustar batch_size se necessário
3. Configurar alertas de custo (se ultrapassar $5/mês)

---

**Dúvidas?** Revise os logs em: `docker compose logs backend`
