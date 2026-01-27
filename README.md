# VORTEX: Auditoria de Integridade e Verificação Factual

O VORTEX é um framework técnico desenvolvido para a automação da auditoria de informações e combate à desinformação sistêmica. O sistema utiliza uma arquitetura de Recuperação Aumentada por Geração (RAG) para validar alegações através do cruzamento com bases de dados verificadas e fontes de alta credibilidade.

Diferente de modelos de análise puramente linguística, o VORTEX estabelece um nexo causal entre a informação analisada e um corpus de referência (Gold Standard) construído sob demanda pelo operador.

---

## Estrutura Técnica e Camadas Operacionais

O framework é segmentado em quatro camadas distintas de processamento:

1.  **Camada de Inteligência (Intelligence Layer)**: Módulos de extração de dados (scraping) programados para minerar portais de notícias e repositórios oficiais.
2.  **Análise Semântica (Linguistic Analysis)**: Processamento via Google Gemini SDK para identificação de marcadores de viés cognitivo, sensacionalismo e inconsistências lógicas.
3.  **Indexação Vetorial (Vectorial Indexing)**: Conversão de dados brutos em representações vetoriais (embeddings) integradas ao banco de dados ChromaDB.
4.  **Motor de Verificação (Verification Engine)**: Núcleo de auditoria que executa buscas por similaridade e gera pareceres técnicos baseados em evidências documentais.

---

## Configuração do Ambiente

O sistema exige a configuração de credenciais de API para o processamento de linguagem natural.

### 1. Variáveis de Ambiente
Crie um arquivo `.env` no diretório raiz com a seguinte definição:

```env
GEMINI_API_KEY=INSIRA_SUA_CHAVE_AQUI
```

### 2. Dependências do Sistema
A instalação dos pacotes necessários deve ser realizada via gerenciador de pacotes Python:

```bash
pip install -r requirements.txt
```

---

## Interface de Linha de Comando (CLI)

O gerenciamento do VORTEX é centralizado no arquivo `main.py`. A execução segue o fluxo logístico de análise:

### Auditoria de Estado
Verifica a integridade das bases locais e o volume de dados indexados:
```bash
python main.py status
```

### Coleta de Dados (Fase 01)
Inicia a extração de notícias de fontes de referência para a composição da base verídica:
```bash
python main.py collect
```

### Análise de Propagação (Fase 02)
Processa a base coletada em busca de padrões de desinformação:
```bash
python main.py analyze --limit 10
```

### Sincronização de Conhecimento (Fase 03)
Indexa os dados processados na base vetorial, preparando o sistema para consultas:
```bash
python main.py index
```

### Protocolo de Verificação (Fase 04)
Submete uma alegação ou fragmento de texto à auditoria do sistema:
```bash
python main.py verify "Texto ou afirmação a ser auditada"
```

---

## Especificações da Stack

*   **Linguagem**: Python 3.10+
*   **Processamento de Linguagem**: Google Gemini 2.0 Flash
*   **Banco de Dados Vetorial**: ChromaDB
*   **Integração de Dados**: LangChain Framework

---
*Documentação técnica destinada a pesquisadores de integridade de informação e análise de guerra cognitiva.*
