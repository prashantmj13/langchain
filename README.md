# LangChain, End to End — with Claude

A comprehensive, hands-on LangChain curriculum: fundamentals → prompt engineering → chains → memory → embeddings & vector search → RAG → multimodal → agents → the Model Context Protocol (MCP) → LangSmith observability.

Every module ships with:
- **Theory** — the core concept, explained plainly
- **Use Case** — when you'd actually reach for this in production
- **Walkthrough** — a runnable `example.py` (or `server.py`/`client.py` pair for MCP)
- **Using a different model** — the 2-3 line diff to swap providers
- **Reference Docs** — links to the primary sources
- **Exercises** — 3-4 tasks to extend what you built

**Anthropic's Claude is the reference model throughout.** Every example also shows exactly how to swap in OpenAI, Google Gemini, or a local Ollama model — see [Model-agnostic design](#model-agnostic-design) below.

## Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/settings/keys)
- Optional, for the "other providers" side-notes: an OpenAI key, a Google AI Studio key, and/or a local [Ollama](https://ollama.com) install
- Optional, for embeddings: a [Voyage AI key](https://dash.voyageai.com/) (Anthropic's recommended embeddings partner — Anthropic does not ship its own embedding model)
- Optional, for tracing: a [LangSmith key](https://smith.langchain.com/)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in your API keys
```

Every example loads `.env` automatically via `python-dotenv`. Run any module from the **repo root**:

```bash
python modules/01_langchain_basics/example.py
```

## Model-agnostic design

[`common/model_factory.py`](common/model_factory.py) and [`common/embedding_factory.py`](common/embedding_factory.py) are the only places that instantiate a model. Every module imports from here instead of hardcoding a provider:

```python
from common.model_factory import get_chat_model

llm = get_chat_model()          # ChatAnthropic("claude-sonnet-4-5") by default
```

Swap providers globally by setting an env var — no code changes needed:

```bash
# .env
LLM_PROVIDER=openai        # anthropic (default) | openai | google | ollama
EMBEDDING_PROVIDER=voyage  # voyage (default) | openai | huggingface
```

Each module's README also has a "Using a different model" section showing the direct code-level diff, for when you want to compare two providers side by side rather than switch globally.

## Learning path

### Foundations
| # | Module | Covers |
|---|--------|--------|
| 01 | [LangChain Basics](modules/01_langchain_basics) | LLMs vs chat models, messages, invoke/stream, temperature |
| 02 | [Prompt Templates](modules/02_prompt_templates) | `PromptTemplate`, `ChatPromptTemplate`, partials, few-shot prompting |
| 03 | [Chains (LCEL)](modules/03_chains_lcel) | The `\|` pipe operator, `Runnable`, `RunnableLambda`, composition |
| 04 | [Simple Sequential Chain](modules/04_simple_sequential_chain) | Single-input/output, step-after-step chains |
| 05 | [Sequential Chain](modules/05_sequential_chain) | Multi-input/output chains with `RunnableParallel`/`RunnablePassthrough` |
| 06 | [Multiple LLMs](modules/06_multiple_llms) | Routing between/combining several models in one pipeline |
| 07 | [Chat History](modules/07_chat_history) | `RunnableWithMessageHistory`, session-scoped memory |
| 08 | [Display History](modules/08_display_history) | Formatting, printing, and exporting a conversation transcript |

### Embeddings & Retrieval
| # | Module | Covers |
|---|--------|--------|
| 09 | [Embeddings Theory](modules/09_embeddings_theory) | What a vector embedding is, cosine similarity, dimensionality |
| 10 | [Embedding Models](modules/10_embedding_models) | Voyage AI, OpenAI, and local HuggingFace embedding models |
| 11 | [Similarity Search](modules/11_similarity_search) | Manual cosine/dot-product ranking, top-k search |
| 12 | [Vector Stores](modules/12_vector_stores) | The vector store abstraction: add, search, delete, persist |
| 13 | [Job Search Helper](modules/13_job_search_helper) | **Capstone**: embed job posts, match a resume, explain the fit with Claude |
| 14 | [Retrieval](modules/14_retrieval) | Retriever interface, similarity vs MMR, `create_retrieval_chain` |
| 15 | [FAISS Vector Store](modules/15_faiss_vector_store) | Building, saving, loading, and querying a FAISS index |
| 16 | [RAG](modules/16_rag) | Full pipeline: load → split → embed → store → retrieve → generate |
| 17 | [History-Aware RAG Bot](modules/17_history_aware_rag_bot) | Conversational RAG that reformulates follow-up questions |

### Multimodal & Agentic
| # | Module | Covers |
|---|--------|--------|
| 18 | [Image Processing](modules/18_image_processing) | Claude's multimodal vision input, base64 image content blocks |
| 19 | [Agents](modules/19_agents) | LangGraph `create_react_agent`, tool calling, reasoning loops |

### Model Context Protocol (MCP)
| # | Module | Covers |
|---|--------|--------|
| 20 | [MCP Fundamentals](modules/20_mcp_fundamentals) | Architecture, transports, primitives (tools/resources/prompts) |
| 21 | [Create MCP Server](modules/21_mcp_create_server) | A minimal `FastMCP` server exposing tools over stdio |
| 22 | [Stdio Client](modules/22_mcp_stdio_client) | Connecting to a local MCP server over stdio |
| 23 | [HTTP Client](modules/23_mcp_http_client) | Streamable-HTTP transport: server + client pair |
| 24 | [Hosting Resources & Prompts](modules/24_mcp_hosting_resources_prompts) | Exposing `@mcp.resource` and `@mcp.prompt`, not just tools |
| 25 | [Implement Server](modules/25_mcp_implement_server) | Production-style server: tools + resources + prompts + HTTP |
| 26 | [Implement Client](modules/26_mcp_implement_client) | A Claude/LangGraph agent consuming MCP tools via `langchain-mcp-adapters` |

### Observability
| # | Module | Covers |
|---|--------|--------|
| 27 | [LangSmith](modules/27_langsmith) | Tracing, `@traceable`, running a lightweight evaluation |

## Repo structure

```
langchain-repo/
├── common/                 # model_factory.py, embedding_factory.py — shared, provider-agnostic helpers
├── modules/                # one folder per topic above, each self-contained
├── requirements.txt
├── .env.example
└── README.md               # you are here
```

## License

[MIT](LICENSE)
