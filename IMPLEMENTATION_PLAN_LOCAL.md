# Plano de Implementação: Gemini + Local Embeddings (Opção 2)

## 🎯 Objetivo

Implementar um **provider de embeddings local** usando SentenceTransformers que:
- ✅ Roda no próprio servidor (sem API externa)
- ✅ Gera embeddings de 768 dimensões (compatível com PostgreSQL Vector(768))
- ✅ Serve como backup quando Gemini falha/está bloqueado
- ✅ É 100% gratuito e sem rate limits
- ✅ Funciona offline

---

## 📋 Etapas de Implementação

### **FASE 1: Criar Provider Local** ⏱️ ~30min

#### 1.1. Criar arquivo do provider
**Arquivo:** `core/llm/providers/local_provider.py`

```python
"""Local Embedding Provider - Uses SentenceTransformers (offline, free)"""

import logging
from typing import Optional, List
from sentence_transformers import SentenceTransformer
import torch

from ..base import EmbeddingProvider

logger = logging.getLogger("VORTEX.LLM.Local")


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local embedding provider using SentenceTransformers.

    Model: sentence-transformers/all-mpnet-base-v2
    - 768 dimensions (compatible with PostgreSQL Vector(768))
    - ~420MB model size
    - Quality: Very good for Portuguese and multilingual
    - Speed: ~100-200ms per text on CPU
    - Cost: FREE (no API calls)
    """

    def __init__(self, api_key: Optional[str] = None):
        # Local provider doesn't need API key, always available
        super().__init__(api_key="local-always-available")
        self.model = None
        self._model_name = "sentence-transformers/all-mpnet-base-v2"

    def _load_model(self):
        """Lazy load model on first use"""
        if self.model is None:
            logger.info(f"Loading local embedding model: {self._model_name}")
            logger.info("This may take 1-2 minutes on first run (downloading ~420MB)...")

            # Use CPU (works on any server)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = SentenceTransformer(self._model_name, device=device)

            logger.info(f"Model loaded successfully on {device}")

    @property
    def name(self) -> str:
        return "local"

    @property
    def display_name(self) -> str:
        return "Local SentenceTransformers"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def embedding_dimensions(self) -> int:
        return 768

    @property
    def default_embedding_model(self) -> str:
        return self._model_name

    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embedding locally"""
        try:
            # Lazy load model
            self._load_model()

            # Truncate text to avoid memory issues
            text = text[:8000]

            # Generate embedding (synchronous operation)
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            self.mark_success()
            return embedding.tolist()

        except Exception as e:
            self.mark_failure(e)
            logger.error(f"Local embedding failed: {e}")
            raise
```

#### 1.2. Registrar provider no `__init__.py`
**Arquivo:** `core/llm/providers/__init__.py`

Adicionar:
```python
from .local_provider import LocalEmbeddingProvider

__all__ = [
    # ... outros providers ...
    "LocalEmbeddingProvider",
]
```

#### 1.3. Adicionar ao LLM Manager
**Arquivo:** `core/llm/manager.py` (linha ~57-69)

Adicionar LocalProvider como **ÚLTIMO da lista** (fallback final):

```python
provider_classes = [
    # FREE providers (priority 1-2)
    (GroqProvider, 'groq'),
    (GeminiProvider, 'gemini'),
    # Freemium providers (priority 3-4)
    (OpenAIProvider, 'openai'),
    (AnthropicProvider, 'anthropic'),
    # Paid providers (priority 5-8)
    (DeepSeekProvider, 'deepseek'),
    (MistralProvider, 'mistral'),
    (TogetherProvider, 'together'),
    (CohereProvider, 'cohere'),
    # LOCAL provider (priority 9 - always available, last resort)
    (LocalEmbeddingProvider, 'local'),  # ← ADICIONAR AQUI
]
```

**IMPORTANTE:** Modificar a lógica de inicialização (linha ~76-88):

```python
for provider_class, provider_name in provider_classes:
    # Skip if not in enabled list (if list is specified)
    if enabled_providers and provider_name not in enabled_providers:
        continue

    # LOCAL provider SEMPRE é inicializado (não precisa de API key)
    if provider_name == 'local':
        try:
            provider = provider_class()  # Sem API key
            self.llm_providers.append(provider)
            if isinstance(provider, EmbeddingProvider):
                self.embedding_providers.append(provider)
            logger.info(f"Initialized {provider.display_name} (always available)")
        except Exception as e:
            logger.warning(f"Failed to initialize local provider: {e}")
        continue

    # Para outros providers, precisa de API key
    api_key = self.api_keys.get(provider_name)
    if api_key:
        try:
            provider = provider_class(api_key)
            self.llm_providers.append(provider)
            if isinstance(provider, EmbeddingProvider):
                self.embedding_providers.append(provider)
            logger.info(f"Initialized {provider.display_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize {provider_name}: {e}")
```

---

### **FASE 2: Atualizar Dependências** ⏱️ ~10min

#### 2.1. Atualizar `requirements.txt`

Adicionar:
```txt
# Local embedding support (Opção 2)
sentence-transformers==2.3.1
torch==2.1.2+cpu  # CPU-only version (lighter, works on any server)
```

**Nota:** Se o servidor tiver GPU NVIDIA, usar `torch==2.1.2` (sem +cpu) para melhor performance.

#### 2.2. Atualizar `Dockerfile`

Adicionar antes do `COPY requirements.txt`:

```dockerfile
# Install dependencies for sentence-transformers (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

---

### **FASE 3: Configuração** ⏱️ ~5min

#### 3.1. Atualizar `.env.example`

Adicionar seção:
```bash
# ==========================================
# LOCAL EMBEDDING PROVIDER (Always Available)
# ==========================================
# The local provider uses SentenceTransformers and runs on your server.
# - No API key needed
# - No rate limits
# - 768 dimensions (compatible with PostgreSQL)
# - ~420MB model downloaded on first use
# - Serves as automatic backup when Gemini/OpenAI fail
#
# This provider is AUTOMATICALLY enabled and requires no configuration.
```

#### 3.2. Atualizar `config.py`

Adicionar à lista de providers habilitados:
```python
# Linha 21
ENABLED_PROVIDERS = os.getenv(
    "ENABLED_PROVIDERS",
    "groq,gemini,openai,anthropic,deepseek,mistral,together,cohere,local"  # ← adicionar ,local
).split(",")
```

---

### **FASE 4: Build e Deploy** ⏱️ ~15min

#### 4.1. Rebuild do container

```bash
cd /opt/kill-fake-news

# Parar containers
docker compose down

# Rebuild com novas dependências
docker compose build backend

# Subir novamente
docker compose up -d

# Verificar logs
docker compose logs -f backend
```

#### 4.2. Teste inicial

```bash
# Testar se o local provider foi inicializado
docker compose exec backend python -c "
from core.llm import LLMManager
from core.config import Config
import asyncio

async def test():
    manager = LLMManager(
        enabled_providers=Config.ENABLED_PROVIDERS,
        api_keys=Config.get_provider_api_keys()
    )

    print(f'Total providers: {len(manager.llm_providers)}')
    print(f'Embedding providers: {len(manager.embedding_providers)}')

    for p in manager.embedding_providers:
        print(f'  - {p.display_name} ({p.embedding_dimensions} dims)')

    # Testar embedding local
    print('\nTesting local embedding...')
    text = 'Este é um teste de embedding local.'
    embedding = await manager.get_embedding(text)
    print(f'Success! Generated {len(embedding)} dimensions')

asyncio.run(test())
"
```

**Resultado esperado:**
```
Total providers: 9
Embedding providers: 2
  - Google Gemini (768 dims)
  - Local SentenceTransformers (768 dims)

Testing local embedding...
Loading local embedding model: sentence-transformers/all-mpnet-base-v2
This may take 1-2 minutes on first run (downloading ~420MB)...
Model loaded successfully on cpu
Success! Generated 768 dimensions
```

#### 4.3. Indexar artigos

```bash
docker compose exec backend python main.py index
```

**Resultado esperado:**
```
[+] PHASE 3: INDEXING DATA FOR VERIFICATION
[+] Checking for unindexed articles...
[+] Indexing 10 articles...
INFO:VORTEX.LLM.Manager:Using Google Gemini for embedding
ERROR:VORTEX.LLM.Gemini:Gemini embedding failed: 404 models/...
INFO:VORTEX.LLM.Manager:Google Gemini failed: 404...
INFO:VORTEX.LLM.Manager:Using Local SentenceTransformers for embedding  ← AQUI!
[+] Indexed: Título do artigo...
[+] Indexed: Outro artigo...
```

---

### **FASE 5: Limpeza e Otimização** ⏱️ ~30min

#### 5.1. Remover providers incompatíveis

**Problema:** OpenAI, Cohere, Together, Mistral geram embeddings com dimensões incompatíveis (1024/1536 vs 768 necessário).

**Arquivos a remover:**
```bash
rm core/llm/providers/openai_provider.py
rm core/llm/providers/cohere_provider.py
rm core/llm/providers/together_provider.py
rm core/llm/providers/mistral_provider.py
rm core/llm/providers/deepseek_provider.py  # Não tem embeddings
```

**Atualizar `core/llm/providers/__init__.py`:**
```python
"""
LLM Providers Package

Available providers:
- GroqProvider: FREE, text generation only (no embeddings)
- GeminiProvider: FREE, text + embeddings (768 dims, rate limited)
- AnthropicProvider: Paid, text generation only (no embeddings)
- LocalEmbeddingProvider: FREE, embeddings only (768 dims, always available)
"""

from .groq_provider import GroqProvider
from .gemini_provider import GeminiProvider
from .anthropic_provider import AnthropicProvider
from .local_provider import LocalEmbeddingProvider

__all__ = [
    "GroqProvider",
    "GeminiProvider",
    "AnthropicProvider",
    "LocalEmbeddingProvider",
]
```

**Atualizar `core/llm/manager.py`:**
```python
# Importações (linha ~10-17)
from .providers.groq_provider import GroqProvider
from .providers.gemini_provider import GeminiProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.local_provider import LocalEmbeddingProvider

# Provider classes (linha ~57-69)
provider_classes = [
    # Text generation
    (GroqProvider, 'groq'),           # FREE, no embeddings
    (GeminiProvider, 'gemini'),       # FREE, 768-dim embeddings
    (AnthropicProvider, 'anthropic'), # Paid, no embeddings
    # Embeddings only
    (LocalEmbeddingProvider, 'local'), # FREE, 768-dim embeddings, always available
]
```

**Atualizar `core/config.py`:**
```python
# Linha 10-17: Remover API keys não usadas
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Linha 21
ENABLED_PROVIDERS = os.getenv("ENABLED_PROVIDERS", "groq,gemini,anthropic,local").split(",")

# Linha 27-38
@classmethod
def get_provider_api_keys(cls) -> dict:
    """Get all configured API keys"""
    return {
        "groq": cls.GROQ_API_KEY,
        "gemini": cls.GEMINI_API_KEY,
        "anthropic": cls.ANTHROPIC_API_KEY,
        "local": "local-always-available",  # Local não precisa de key
    }
```

**Atualizar `requirements.txt`:**
```txt
# Remove linhas não necessárias:
# - openai
# - cohere
# - mistral
# - deepseek

# Manter apenas:
google-generativeai==0.8.3  # Gemini
groq==0.11.0                # Groq
anthropic==0.39.0           # Claude
sentence-transformers==2.3.1 # Local embeddings
torch==2.1.2+cpu            # PyTorch (CPU-only)
```

#### 5.2. Atualizar README.md

**Seção a modificar:** "Supported AI Providers"

```markdown
## 🤖 Supported AI Providers

The system supports multiple AI providers with automatic failover:

### Text Generation (LLM)
| Provider | Cost | Models | Rate Limits | Get API Key |
|----------|------|--------|-------------|-------------|
| **Groq** | 🟢 FREE (Unlimited) | Llama 3.3 70B, Gemma 2 9B | 30 RPM | [Get Key](https://console.groq.com/keys) |
| **Gemini** | 🟢 FREE | Gemini 2.5 Flash, 2.0 Pro | 15 RPM, 1M TPM | [Get Key](https://aistudio.google.com/apikey) |
| **Anthropic** | 🟡 Freemium | Claude Sonnet 4.5 | Paid usage | [Get Key](https://console.anthropic.com/settings/keys) |

### Embeddings (Semantic Search)
| Provider | Cost | Model | Dimensions | Notes |
|----------|------|-------|------------|-------|
| **Gemini** | 🟢 FREE | text-embedding-004 | 768 | Rate limited (1K RPD) |
| **Local** | 🟢 FREE | all-mpnet-base-v2 | 768 | **Always available**, no rate limits, runs on your server |

### 🔄 Automatic Failover Strategy

**For Embeddings:**
1. Try **Gemini** (fast, free, but rate limited)
2. Fallback to **Local** (always works, slightly slower)

**For Text Generation:**
1. Try **Groq** (fastest, unlimited)
2. Fallback to **Gemini** (fast, rate limited)
3. Fallback to **Anthropic** (paid, most reliable)

### 🎯 Recommended Setup

**Minimal (FREE):**
```bash
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
# Local embeddings automatically enabled (no key needed)
```

**Production (Best Quality):**
```bash
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key  # Backup LLM
# Local embeddings always available as fallback
```
```

#### 5.3. Atualizar `.env.example`

Remover seções de providers não usados (OpenAI, Cohere, Together, Mistral, DeepSeek).

**Nova versão simplificada:**
```bash
# ==========================================
# AI PROVIDERS - Get your FREE API keys
# ==========================================

# --- Text Generation (LLM) ---

# Groq (RECOMMENDED - FREE, Unlimited)
# https://console.groq.com/keys
GROQ_API_KEY=

# Gemini (FREE, Rate Limited)
# https://aistudio.google.com/apikey
GEMINI_API_KEY=

# Anthropic Claude (Paid, Optional Backup)
# https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=

# --- Embeddings (Semantic Search) ---
# Local embeddings are AUTOMATICALLY enabled (no API key needed)
# Uses SentenceTransformers running on your server
# - 768 dimensions (compatible with database)
# - No rate limits
# - ~420MB model downloaded on first use

# --- Provider Configuration ---
ENABLED_PROVIDERS=groq,gemini,anthropic,local
LOAD_BALANCE=false

# ==========================================
# DATABASE
# ==========================================
# ... resto do arquivo ...
```

---

### **FASE 6: Documentação Técnica** ⏱️ ~10min

#### 6.1. Criar documentação do Local Provider

**Arquivo:** `core/llm/providers/LOCAL_PROVIDER.md`

```markdown
# Local Embedding Provider

## Overview

The Local Embedding Provider uses [SentenceTransformers](https://www.sbert.net/) to generate embeddings locally on your server, without requiring external API calls.

## Model Details

- **Model:** `sentence-transformers/all-mpnet-base-v2`
- **Dimensions:** 768 (compatible with PostgreSQL Vector(768))
- **Size:** ~420MB (downloaded once, cached)
- **Performance:** ~100-200ms per text on CPU
- **Languages:** Multilingual (excellent for Portuguese)
- **Quality:** Very good for general-purpose embeddings

## Advantages

✅ **100% Free** - No API costs
✅ **Always Available** - No rate limits
✅ **Offline** - Works without internet
✅ **Privacy** - Data never leaves your server
✅ **Reliable** - Cannot be rate-limited or blocked

## Disadvantages

⚠️ **Resource Usage** - Requires ~2GB RAM during processing
⚠️ **Slower** - ~200ms vs ~50ms for API-based embeddings
⚠️ **Quality** - Slightly lower than GPT-4/Gemini embeddings

## Server Requirements

- **CPU:** 2+ cores (recommended 4+)
- **RAM:** 4GB total (2GB free for model)
- **Disk:** 500MB for model cache
- **OS:** Linux (Docker container)

## Automatic Failover

The Local Provider serves as the **last resort** when all API-based providers fail:

```
Gemini (API) → FAIL → Local (Server) → SUCCESS
```

## Configuration

No configuration needed! The provider is automatically enabled and always available.

To disable (not recommended):
```bash
ENABLED_PROVIDERS=groq,gemini,anthropic  # Remove 'local'
```

## Monitoring

Check provider status:
```python
from core.llm import LLMManager

manager = LLMManager()
status = manager.get_status()
print(status['embedding_providers'])
```

## Troubleshooting

**Issue:** Model download fails
**Solution:** Check disk space (needs 500MB) and internet connection

**Issue:** Out of memory
**Solution:** Increase Docker container memory limit to 4GB+

**Issue:** Slow performance
**Solution:** Reduce batch size or upgrade CPU
```

---

## 📊 Resumo de Mudanças

### Arquivos Novos (3)
1. ✅ `core/llm/providers/local_provider.py` - Provider local
2. ✅ `core/llm/providers/LOCAL_PROVIDER.md` - Documentação
3. ✅ `IMPLEMENTATION_PLAN_LOCAL.md` - Este arquivo

### Arquivos Modificados (7)
1. ✅ `core/llm/providers/__init__.py` - Importar LocalProvider
2. ✅ `core/llm/manager.py` - Adicionar LocalProvider à lista
3. ✅ `core/config.py` - Atualizar ENABLED_PROVIDERS
4. ✅ `requirements.txt` - Adicionar sentence-transformers + torch
5. ✅ `Dockerfile` - Adicionar build dependencies (se necessário)
6. ✅ `README.md` - Atualizar documentação de providers
7. ✅ `.env.example` - Simplificar e documentar local provider

### Arquivos Removidos (5)
1. ❌ `core/llm/providers/openai_provider.py` - Incompatível (1536 dims)
2. ❌ `core/llm/providers/cohere_provider.py` - Incompatível (1024 dims)
3. ❌ `core/llm/providers/together_provider.py` - Incompatível (1024 dims)
4. ❌ `core/llm/providers/mistral_provider.py` - Incompatível (1024 dims)
5. ❌ `core/llm/providers/deepseek_provider.py` - Sem embeddings

---

## ⏱️ Tempo Estimado Total

| Fase | Tempo |
|------|-------|
| Criar Local Provider | 30min |
| Atualizar Dependências | 10min |
| Configuração | 5min |
| Build e Deploy | 15min |
| Limpeza e Otimização | 30min |
| Documentação | 10min |
| **TOTAL** | **~1h 40min** |

---

## ✅ Critérios de Sucesso

Após implementação, o sistema deve:

1. ✅ Indexar artigos com sucesso usando Local Provider
2. ✅ Gerar embeddings de 768 dimensões
3. ✅ Fazer failover automaticamente: Gemini → Local
4. ✅ Funcionar sem erros 404 ou rate limit
5. ✅ Verificar claims com busca semântica funcional

---

## 🚀 Próximos Passos (Quando Implementar)

1. **Commit do plano:**
   ```bash
   git add IMPLEMENTATION_PLAN_LOCAL.md
   git commit -m "docs: add detailed implementation plan for local embeddings"
   git push
   ```

2. **Descansar** 😴

3. **Quando voltar:** Seguir o plano fase por fase

4. **Testar em staging primeiro** antes de deploy em produção

---

## 📝 Notas Finais

- ⚠️ **Backup do banco** antes de qualquer mudança
- ⚠️ **Testar localmente** antes de deploy
- ⚠️ **Monitorar recursos** do servidor após deploy
- ✅ **Local Provider** resolve PERMANENTEMENTE o problema de rate limits
- ✅ Sistema ficará **100% independente de APIs externas** para embeddings

---

**Status:** 📋 PLANO PRONTO - AGUARDANDO IMPLEMENTAÇÃO

**Criado em:** 2026-02-14
**Estimativa:** 1h 40min de implementação
**Risco:** ⬜ Baixo
