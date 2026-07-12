# LangChain, End to End — with Claude

A comprehensive, hands-on LangChain curriculum: fundamentals → prompt engineering → chains → memory → embeddings & vector search → RAG → multimodal → agents → the Model Context Protocol (MCP) → LangSmith observability.

Every module ships with:
- **Theory** — the core concept, explained plainly
- **Use Case** — when you'd actually reach for this in production
- **Walkthrough** — a runnable `example.py` (or `server.py`/`client.py` pair for MCP)
- **Using a different model** — the 2-3 line diff to swap providers
- **Reference Docs** — links to the primary sources
- **Exercises** — 3-4 tasks to extend what you built, each with a worked solution in `solutions.py`

**New to Python, or new to calling an LLM API at all?** Start with [module 00](modules/00_python_and_llm_basics) — a primer on the Python constructs (functions, dicts, decorators, `async`/`await`) and LLM/API concepts (tokens, API keys, prompts, context windows) every later module assumes you already know.

**Anthropic's Claude is the reference model throughout.** Every example also shows exactly how to swap in OpenAI, Google Gemini, or a local Ollama model — see [Model-agnostic design](#model-agnostic-design) below.

## Prerequisites

- Python 3.10-3.13 (this repo pins to the LangChain 0.3.x API family — see [`requirements.txt`](requirements.txt) — which has a known import-time incompatibility on Python 3.14 due to an upstream typing/pydantic interaction bug, unrelated to this repo's code)
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

## How the examples execute

Every module's README has a **"How to Run"** section with the exact command(s) — but the mechanics are the same across the whole repo, so they're explained once here instead of repeated 28 times.

**1. Every script is run directly, from the repo root, never imported as a package.**
```bash
python modules/07_chat_history/example.py
```
Folder names start with digits (`07_chat_history`), which Python can't import as a module name anyway — that's fine, because you never `import` a module folder, you always run its `.py` file directly with the `python` command above.

**2. Each script finds `common/` via a small `sys.path` bootstrap**, visible at the top of every `example.py`/`solutions.py`:
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))   # adds the repo root to sys.path
from common.model_factory import get_chat_model
```
This is why every command above is written as `python modules/.../example.py` run **from the repo root** — the bootstrap computes the repo root relative to the script's own location, so it works regardless of your current shell directory, but the script itself still needs to be invoked with that full relative (or absolute) path.

**3. API keys load automatically.** `common/model_factory.py` and `common/embedding_factory.py` both call `load_dotenv()` before doing anything else, which reads your `.env` file into environment variables — you never need to `export` or `set` a key manually, just make sure `.env` exists (`cp .env.example .env`) and is filled in.

**4. What actually happens when a script runs:** each `example.py` ends with an `if __name__ == "__main__":` block that calls a handful of top-level functions in sequence (one per concept the module demonstrates), each of which prints its own labeled output section (e.g. `--- Basic invoke ---`) to the console. There's no hidden state between runs — every script is a linear, top-to-bottom script you can read start to finish.

**5. Three execution patterns appear in the repo:**
| Pattern | Modules | How to run |
|---|---|---|
| Single script | Most modules (00-19, 27) | `python modules/NN_xxx/example.py` — one command, runs to completion, prints output |
| Two processes (server + client) | 23, 25+26 | Start the server in one terminal (it blocks, listening), then run the client in a second terminal |
| Client that launches its own server subprocess | 21+22, 24 | One command (the client) — it spawns the server itself over stdio, no second terminal needed |

**6. Files an example may leave behind** (all covered by `.gitignore`, safe to delete anytime): FAISS/Chroma index folders (`faiss_index*/`, `chroma_db*/`), small demo JSON/log files (`*_demo.json`, `server.log`). Nothing in the repo writes outside its own `modules/NN_xxx/` folder.

**7. Nothing calls a real LLM until you provide an API key.** Without `ANTHROPIC_API_KEY` set, any script that reaches `get_chat_model().invoke(...)` will raise an authentication error from the `anthropic` SDK — that's expected, not a bug in the example; it's the point at which the script actually talks to the network.

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

### Start here
| # | Module | Covers |
|---|--------|--------|
| 00 | [Python & LLM Basics](modules/00_python_and_llm_basics) | Python constructs (functions, dicts, decorators, async) and LLM/API concepts (tokens, API keys, prompts) used throughout the repo |

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
