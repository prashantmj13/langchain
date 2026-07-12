# 06 — Multiple LLMs

## Theory

Real applications rarely use just one model for everything. Common multi-model patterns:

- **Comparison** — run the same prompt against several providers to compare quality/cost/latency.
- **Routing** — send different *kinds* of requests to different models (a cheap/fast model for simple classification, Claude for anything requiring careful reasoning).
- **Ensembling** — ask multiple models the same question and combine/vote on their answers.
- **Pipeline specialization** — use a cheap model for a rough draft and a stronger model to refine it (draft-and-polish).

LangChain makes this trivial because every chat model is a `Runnable` with the same interface — `get_chat_model(provider=...)` from [`common/model_factory.py`](../../common/model_factory.py) is exactly this pattern formalized.

## Use Case

Cost control (route simple queries away from your most expensive model), redundancy (fail over to a second provider if one is down/rate-limited), and quality benchmarking (which model handles your specific domain best) all require running more than one model in the same app.

## How to Run

```bash
python modules/06_multiple_llms/example.py
python modules/06_multiple_llms/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY`; `OPENAI_API_KEY` and a running local Ollama daemon are optional — each provider call is wrapped in `try/except`, so if a provider isn't configured the script prints `skipped (...)` for it and keeps going instead of crashing.

## Walkthrough

`example.py`:
1. Sends the identical prompt to Claude, GPT-4o-mini, and (optionally) a local Ollama model, printing each response side by side.
2. Builds a `RunnableBranch` that routes a request to Claude for anything tagged "reasoning" and to a cheaper model for anything tagged "simple lookup."
3. Demonstrates a draft-and-polish pipeline: a fast/cheap model drafts, Claude edits.

## Using a different model

This entire module *is* the "different model" note — it directly instantiates `ChatAnthropic`, `ChatOpenAI`, and `ChatOllama` side by side via `get_chat_model(provider=...)` rather than relying on a single global `LLM_PROVIDER`.

## Reference Docs

- Chat models concept: https://python.langchain.com/docs/concepts/chat_models/
- `RunnableBranch`: https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.branch.RunnableBranch.html
- Anthropic model comparison: https://docs.anthropic.com/en/docs/about-claude/models

## Exercises

1. Add a fourth provider (Google Gemini) to the comparison and print all four answers plus each call's latency.
2. Change the routing chain's condition so anything containing the word "code" always goes to Claude, regardless of the "reasoning"/"simple lookup" tag.
3. Build a simple voting ensemble: ask 3 models the same yes/no question and print the majority answer.
4. Measure the actual cost difference between the draft-and-polish pipeline and just asking Claude directly, using each provider's token usage metadata.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
