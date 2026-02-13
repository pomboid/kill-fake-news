# Multi-Provider LLM System

Sistema de gerenciamento de múltiplos provedores de IA com failover automático e load balancing.

## 🎯 Funcionalidades

- ✅ **Failover Automático**: Se um provedor falhar, automaticamente tenta o próximo
- ✅ **Load Balancing**: Distribui requisições entre provedores (round-robin)
- ✅ **Priorização**: Provedores gratuitos são priorizados
- ✅ **Health Tracking**: Desabilita provedores após 3 falhas consecutivas
- ✅ **Embeddings Multi-Provider**: Suporte a embeddings de múltiplos provedores

## 🤖 Provedores Suportados

### Gratuitos (Prioridade Máxima)
1. **Groq** - FREE, ilimitado
   - Llama 3.3 70B, Gemma 2 9B, Mixtral 8x7B
   - Velocidade: Ultra-rápida

2. **Gemini** - FREE tier generoso
   - Gemini 2.0 Flash, Gemini 1.5 Pro
   - Embeddings: 768 dimensões

### Freemium (Fallback)
3. **OpenAI** - $0.15/1M tokens (gpt-4o-mini)
   - GPT-4o, GPT-4o-mini
   - Embeddings: 1536 dimensões

4. **Anthropic** - $0.25/1M tokens (Haiku)
   - Claude 3.5 Sonnet, Claude 3.5 Haiku
   - Melhor para análise textual

## 📝 Uso

### Configuração Básica

```python
from core.llm import LLMManager

# Inicializar manager
manager = LLMManager(
    enabled_providers=['groq', 'gemini', 'openai'],
    api_keys={
        'groq': 'your_groq_key',
        'gemini': 'your_gemini_key',
        'openai': 'your_openai_key'
    },
    load_balance=False  # False = failover only, True = round-robin
)
```

### Gerar Texto

```python
# Gera texto com failover automático
text = await manager.generate_text(
    prompt="Explique o que é fake news",
    temperature=0.7
)
```

### Gerar JSON

```python
# Gera JSON estruturado
data = await manager.generate_json(
    prompt="Analise este artigo e retorne JSON: {...}",
    temperature=0.5
)
```

### Gerar Embeddings

```python
# Gera embedding com failover
embedding = await manager.get_embedding("texto para vetorizar")
```

### Verificar Status

```python
# Ver status de todos os provedores
status = manager.get_status()
print(status)
```

## 🔧 Variáveis de Ambiente

```env
# API Keys
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Configuração
ENABLED_PROVIDERS=groq,gemini,openai,anthropic
LOAD_BALANCE=false
```

## 🏗️ Arquitetura

```
core/llm/
├── base.py                    # Classes abstratas
├── manager.py                 # Gerenciador principal
└── providers/
    ├── groq_provider.py       # Groq (FREE)
    ├── gemini_provider.py     # Gemini (FREE + embeddings)
    ├── openai_provider.py     # OpenAI (embeddings)
    └── anthropic_provider.py  # Claude
```

## 🎨 Exemplo Completo

```python
from core.llm import LLMManager
from core.config import Config

# Criar manager usando config
manager = LLMManager(
    enabled_providers=Config.ENABLED_PROVIDERS,
    api_keys=Config.get_provider_api_keys(),
    load_balance=Config.LOAD_BALANCE
)

# Análise de notícia com failover
try:
    analysis = await manager.generate_json(
        prompt=f"Analise esta notícia: {article.content}"
    )
    print(f"Resultado: {analysis}")
except Exception as e:
    print(f"Todos os provedores falharam: {e}")

# Verificar qual provedor foi usado
status = manager.get_status()
for provider in status['llm_providers']:
    if provider['success_count'] > 0:
        print(f"✅ {provider['name']}: {provider['success_count']} requests")
```

## 🚀 Vantagens

1. **Resiliência**: Nunca para por falha de um provedor
2. **Economia**: Usa provedores gratuitos primeiro
3. **Flexibilidade**: Fácil adicionar novos provedores
4. **Transparência**: Logs detalhados de cada tentativa
5. **Performance**: Load balancing opcional para distribuir carga

## 📊 Monitoramento

O sistema rastreia automaticamente:
- Número de requisições bem-sucedidas por provedor
- Número de falhas consecutivas
- Último erro registrado
- Status atual (ativo, falhou, rate-limited, desabilitado)

## 🔄 Próximos Provedores

Fácil adicionar novos provedores implementando a interface `LLMProvider`:

```python
class NovoProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "novo_provider"

    async def generate_text(self, prompt: str, **kwargs) -> str:
        # Implementação
        pass

    async def generate_json(self, prompt: str, **kwargs) -> dict:
        # Implementação
        pass
```
