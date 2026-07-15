# 06 — Multiple LLMs

## Theory

Real apps usually don't rely on just one AI model for everything — different jobs call for different models. A few common ways to mix models:

- **Comparing them.** Ask the same question to several different models, and look at the answers side by side, to see which one is better, faster, or cheaper for your use case.
- **Sending different requests to different models.** A quick, cheap model can handle simple lookups; a stronger model like Claude can handle anything that needs careful reasoning. You decide which request goes where.
- **Asking several models and taking a vote.** If you're unsure which model to trust, ask more than one the same question and go with whatever answer most of them agree on.
- **Draft, then polish.** Use a cheap, fast model to write a rough first version, then have a stronger model clean it up — cheaper overall than having the strong model write everything from scratch.

This is easy in LangChain because every model, no matter the provider, is used the exact same way (from module 01) — so switching which model handles a given step is as simple as swapping which model object you pass in. That's exactly what `get_chat_model(provider=...)` in [`common/model_factory.py`](../../common/model_factory.py) does.

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
2. Builds a `RunnableBranch` that routes a request to Claude for anything tagged "reasoning" and to a cheaper model for anything tagged "simple lookup." For exactly how `RunnableBranch` decides which chain to call, see [module 03's Execution Internals](../03_chains_lcel#execution-internals-the-runnable-protocol).
3. Demonstrates a draft-and-polish pipeline: a fast/cheap model drafts, Claude edits.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `get_chat_model(provider="openai", model="gpt-4o-mini", temperature=0.9)` | This repo's factory function — returns a chat model instance for whichever provider/model/temperature you ask for. | Used repeatedly to get several *different* model instances in the same script (Claude, GPT-4o-mini, Ollama), instead of always getting the default. |
| `RunnableBranch((condition, chain), default_chain)` | Checks each condition against the input in order, and runs the first chain whose condition is `True` (falling back to the default). | Used in `routing_example()` to send "reasoning" questions to Claude and everything else to a cheaper model, based on a `task_type` field in the input. |
| `try` / `except Exception` around each provider call | Standard Python error handling — catches a failure instead of crashing. | Used around every non-Anthropic provider call so the script still runs and demonstrates the pattern even if you haven't configured `OPENAI_API_KEY` or a local Ollama install. |

## Using a different model

This entire module *is* the "different model" note — it directly instantiates `ChatAnthropic`, `ChatOpenAI`, and `ChatOllama` side by side via `get_chat_model(provider=...)` rather than relying on a single global `LLM_PROVIDER`.

## Reference Docs

- Chat models concept: https://python.langchain.com/docs/concepts/chat_models/
- `RunnableBranch`: https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.branch.RunnableBranch.html
- Anthropic model comparison: https://docs.anthropic.com/en/docs/about-claude/models

## Exercises

1. **Add a 4th provider to `compare_providers()`.** The example already loops over `("anthropic", "openai", "ollama")`; add `"google"` to that tuple (needs `GOOGLE_API_KEY` set). For each provider, also time the call with `time.perf_counter()` and print the latency alongside the answer, so you end up comparing both *what* each model says and *how long* it took.
2. **Adding a condition that overrides the existing routing logic.** `routing_example()`'s `RunnableBranch` currently routes purely on the `task_type` field. Add a *second* condition, checked before the existing one, that routes to Claude whenever the word `"code"` appears anywhere in the question — regardless of what `task_type` says. Test it with a question tagged `"simple lookup"` that also happens to ask for code, and confirm it still goes to Claude.
3. **A minimal "ask 3 models, take the majority" pattern.** Pick a factual yes/no question (e.g. "Is Python a compiled language? Answer with exactly one word: yes or no."). Ask it to 3 different providers, collect the 3 one-word answers into a list, and use Python's `collections.Counter` to find and print whichever answer appears most often.
4. **Comparing real costs, not just latency.** Run `draft_and_polish()` and sum up the token usage (`response.usage_metadata`) across both the draft and polish calls. Separately, ask Claude the same underlying question directly in one call, and note its token usage. Compare the two totals — is a "cheap draft + Claude polish" pipeline actually cheaper than just asking Claude directly for this particular question?

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
