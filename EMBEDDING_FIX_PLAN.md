# Plano de Correção: Embeddings e Failover Multi-Provider

## 🔴 Problemas Identificados

### 1. Rate Limit do Gemini (BLOQUEADO)
- **Status**: Gemini está bloqueado por exceder TPM (36.03K/30K)
- **Modelo atual**: `models/embedding-001` retorna 404 (modelo incorreto ou deprecado)
- **Impacto**: Não pode gerar embeddings mesmo com modelo correto até resetar o rate limit

### 2. Incompatibilidade de Dimensionalidade (CRÍTICO)
```python
# sql_models.py linha 58
embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(768)))
```

**Dimensões dos providers disponíveis:**
- ❌ Gemini: 768 dims (COMPATÍVEL, mas bloqueado por rate limit)
- ❌ OpenAI: 1536 dims (INCOMPATÍVEL - falhará ao inserir no banco)
- ❌ Cohere: 1024 dims (INCOMPATÍVEL - falhará ao inserir no banco)
- ❌ Together: 1024 dims (INCOMPATÍVEL - falhará ao inserir no banco)
- ❌ Groq: Não tem embeddings
- ❌ DeepSeek: Não verificado

### 3. Failover Não Funcional
- O failover está implementado no código mas **bloqueado pela restrição de dimensionalidade**
- Mesmo que tente OpenAI/Cohere/Together, o PostgreSQL rejeitará vetores com dimensões diferentes de 768
- Logs mostram apenas tentativas do Gemini (10x) - outros providers não foram tentados

---

## ✅ SOLUÇÕES PROPOSTAS

### 🎯 **OPÇÃO 1: Migrar para OpenAI (1536 dims) [RECOMENDADO]**

**Vantagens:**
- ✅ OpenAI é o mais estável e confiável
- ✅ Você já tem a API key configurada
- ✅ 1536 dims = melhor qualidade de embeddings
- ✅ Suporte a failover para Cohere/Together (com truncation)

**Passos de implementação:**

1. **Criar migração do banco de dados**
   ```sql
   -- Arquivo: migrations/002_upgrade_embedding_dimensions.sql

   -- 1. Criar nova coluna temporária com 1536 dims
   ALTER TABLE article ADD COLUMN embedding_new vector(1536);

   -- 2. Migrar embeddings existentes (padding com zeros)
   UPDATE article
   SET embedding_new = array_cat(embedding::float[], array_fill(0.0::float, ARRAY[768])::float[])
   WHERE embedding IS NOT NULL;

   -- 3. Remover coluna antiga e renomear
   ALTER TABLE article DROP COLUMN embedding;
   ALTER TABLE article RENAME COLUMN embedding_new TO embedding;

   -- 4. Recriar índice para busca vetorial
   CREATE INDEX ON article USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
   ```

2. **Atualizar sql_models.py**
   ```python
   # Linha 58
   embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(1536)))
   ```

3. **Implementar adaptador de dimensionalidade**
   ```python
   # core/llm/embedding_adapter.py (NOVO)

   def adapt_embedding(embedding: List[float], target_dims: int = 1536) -> List[float]:
       """Adapta embedding para dimensionalidade alvo"""
       current_dims = len(embedding)

       if current_dims == target_dims:
           return embedding
       elif current_dims < target_dims:
           # Padding com zeros
           return embedding + [0.0] * (target_dims - current_dims)
       else:
           # Truncation (primeiros N valores)
           return embedding[:target_dims]
   ```

4. **Atualizar manager.py para usar adaptador**
   ```python
   # Linha 231 - get_embedding()
   result = await provider.get_embedding(text, model)
   result = adapt_embedding(result, target_dims=1536)  # Normalizar para 1536
   return result
   ```

5. **Re-indexar artigos existentes**
   ```bash
   # Limpar embeddings antigos e re-gerar com OpenAI
   docker compose exec backend python -c "
   from core.database import get_session
   from core.sql_models import Article
   from sqlmodel import select
   import asyncio

   async def clear_embeddings():
       async for session in get_session():
           stmt = select(Article)
           result = await session.execute(stmt)
           articles = result.scalars().all()
           for article in articles:
               article.embedding = None
           await session.commit()

   asyncio.run(clear_embeddings())
   print('Embeddings cleared. Run: python main.py index')
   "

   # Re-indexar com OpenAI
   docker compose exec backend python main.py index
   ```

**Custo estimado:** ~$0.10 por 1M tokens (muito barato)

**Tempo de implementação:** 2-3 horas
**Risco:** Médio (requer migração de banco)

---

### 🎯 **OPÇÃO 2: Corrigir Gemini + Provider Local de Backup**

**Vantagens:**
- ✅ Mantém 768 dims (sem migração de banco)
- ✅ Usa Gemini quando disponível (GRATUITO)
- ✅ Fallback local quando Gemini está bloqueado
- ✅ Sem custos de API

**Passos de implementação:**

1. **Descobrir modelo correto do Gemini**
   Testar modelos possíveis:
   - `text-multilingual-embedding-002` (768 dims)
   - `text-embedding-005` (768 dims)
   - `embedding-001` (sem prefixo "models/")

   ```python
   # gemini_provider.py linha 49
   @property
   def default_embedding_model(self) -> str:
       return "text-multilingual-embedding-002"  # Testar este
   ```

2. **Implementar provider local com SentenceTransformers**
   ```python
   # core/llm/providers/local_provider.py (NOVO)

   from sentence_transformers import SentenceTransformer
   from ..base import EmbeddingProvider

   class LocalEmbeddingProvider(EmbeddingProvider):
       """Provider local usando SentenceTransformers (768 dims)"""

       def __init__(self, api_key: Optional[str] = None):
           super().__init__(api_key="local")  # Sempre disponível
           self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

       @property
       def embedding_dimensions(self) -> int:
           return 768

       async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
           try:
               # Modelo local não precisa de API key
               embedding = self.model.encode(text[:8000], convert_to_numpy=True)
               self.mark_success()
               return embedding.tolist()
           except Exception as e:
               self.mark_failure(e)
               raise
   ```

3. **Adicionar LocalProvider ao manager**
   ```python
   # manager.py linha 57-69
   provider_classes = [
       (GroqProvider, 'groq'),
       (GeminiProvider, 'gemini'),
       (OpenAIProvider, 'openai'),
       (AnthropicProvider, 'anthropic'),
       (DeepSeekProvider, 'deepseek'),
       (MistralProvider, 'mistral'),
       (TogetherProvider, 'together'),
       (CohereProvider, 'cohere'),
       (LocalEmbeddingProvider, 'local'),  # SEMPRE DISPONÍVEL (não precisa API key)
   ]
   ```

4. **Atualizar requirements.txt**
   ```
   sentence-transformers==2.3.1
   torch==2.1.2
   ```

5. **Rebuild do container**
   ```bash
   docker compose down
   docker compose build backend
   docker compose up -d
   docker compose exec backend python main.py index
   ```

**Custo:** GRATUITO (modelo local)
**Tempo de implementação:** 1-2 horas
**Risco:** Baixo (sem migração de banco)
**Desvantagem:** Embeddings locais podem ser de qualidade inferior

---

### 🎯 **OPÇÃO 3: Sistema Híbrido (Melhor dos Dois Mundos)**

**Vantagens:**
- ✅ Usa OpenAI quando disponível (melhor qualidade)
- ✅ Fallback para modelo local (sempre disponível)
- ✅ Suporta múltiplas dimensionalidades com adaptador

**Implementação:** Combina Opção 1 + Opção 2
1. Migrar banco para 1536 dims
2. Implementar adaptador de dimensionalidade
3. Adicionar LocalProvider como último fallback
4. Ordem de prioridade: OpenAI → Cohere → Together → Gemini → Local

**Custo:** ~$0.10 por 1M tokens (muito barato, só quando API é usada)
**Tempo de implementação:** 3-4 horas
**Risco:** Médio-Alto (mais complexo)

---

## 🎯 RECOMENDAÇÃO FINAL

### Para Implementar AGORA (Curto Prazo):
**Escolha OPÇÃO 2** - Corrigir Gemini + Provider Local

**Razões:**
1. ✅ **Mais rápido** (1-2 horas vs 2-4 horas)
2. ✅ **Menor risco** (sem migração de banco)
3. ✅ **GRATUITO** (modelo local sem custo de API)
4. ✅ **Sempre disponível** (não depende de rate limits)
5. ✅ **Não perde dados** (mantém embeddings existentes com 768 dims)

### Para Implementar DEPOIS (Longo Prazo):
**Migrar para OPÇÃO 1** quando o projeto crescer

**Razões:**
1. OpenAI tem melhor qualidade de embeddings
2. 1536 dims = busca semântica mais precisa
3. Mais estabilidade (SLA 99.9%)
4. Custo muito baixo ($0.10 por 1M tokens)

---

## 🚀 PRÓXIMOS PASSOS

**Aguardando decisão do usuário:**
1. Qual opção implementar? (Opção 1, 2 ou 3)
2. Após escolha, começar implementação imediatamente
3. Testar em ambiente de desenvolvimento primeiro
4. Deploy em produção após validação

---

## 📊 COMPARAÇÃO RÁPIDA

| Critério | Opção 1 (OpenAI) | Opção 2 (Gemini+Local) | Opção 3 (Híbrido) |
|----------|------------------|------------------------|-------------------|
| Custo | ~$0.10/1M tokens | GRATUITO | ~$0.10/1M tokens |
| Tempo | 2-3h | 1-2h | 3-4h |
| Risco | Médio | Baixo | Médio-Alto |
| Qualidade | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Disponibilidade | 99.9% | 100% | 100% |
| Migração DB | ✅ Sim | ❌ Não | ✅ Sim |

**Recomendação:** OPÇÃO 2 agora → OPÇÃO 1 depois
