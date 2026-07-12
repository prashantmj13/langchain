# 27 — LangSmith

## Theory

LangSmith is LangChain's observability/evaluation platform: it traces every step of a chain or agent run (each prompt, each LLM call with full input/output and token counts, each tool call) so you can debug *why* an answer came out the way it did, not just see the final output. Core pieces:

- **Tracing** — turned on globally with two env vars, no code changes to your chains required:
  ```bash
  LANGSMITH_TRACING=true
  LANGSMITH_API_KEY=...
  LANGSMITH_PROJECT=my-project
  ```
  Every `Runnable.invoke()` call anywhere in the process gets traced automatically once these are set.
- **`@traceable`** — a decorator for tracing plain Python functions that aren't LangChain `Runnable`s (e.g. custom pre/post-processing logic) so they show up in the same trace tree.
- **Evaluation** — LangSmith lets you define a small dataset of `(input, expected_output)` pairs and run a chain against it, scoring each output (exact match, an LLM-as-judge grader, or a custom Python function), to catch regressions before shipping a prompt change.

## Use Case

Debugging why a RAG chain ([module 16](../16_rag)) retrieved the wrong chunk, understanding an agent's ([module 19](../19_agents)) tool-calling decisions step by step, and regression-testing a prompt change against a fixed dataset before deploying it.

## How to Run

```bash
python modules/27_langsmith/example.py
python modules/27_langsmith/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY`. `LANGSMITH_TRACING`/`LANGSMITH_API_KEY` are optional — `check_tracing_configured()` runs first and prints a clear message if they're unset, then the script continues untraced rather than failing.

## Walkthrough

`example.py`:
1. Loads `LANGSMITH_*` env vars (tracing is opt-in; the script checks whether a key is set and explains what to do if not).
2. Runs the module 03-style `prompt | llm | StrOutputParser()` chain a few times — each call is automatically traced if `LANGSMITH_TRACING=true`.
3. Wraps a custom Python post-processing function with `@traceable` so it appears in the same trace.
4. Defines a tiny 3-example evaluation dataset and runs a lightweight local evaluation (exact-substring check) over the chain's outputs, printing a pass/fail summary — a minimal stand-in for `langsmith.evaluate()` against a hosted dataset.

## Using a different model

Tracing/evaluation are provider-agnostic — they capture whatever `get_chat_model(...)` you're using. Comparing providers on the same evaluation dataset (Claude vs GPT-4o-mini) is itself a common LangSmith use case.

## Reference Docs

- LangSmith docs: https://docs.smith.langchain.com/
- Tracing quickstart: https://docs.smith.langchain.com/observability
- Evaluation quickstart: https://docs.smith.langchain.com/evaluation

## Exercises

1. Set `LANGSMITH_TRACING=true` with a real API key, run `example.py`, and find the resulting trace in the LangSmith UI.
2. Add a second `@traceable` function and confirm it nests correctly under the parent chain's trace in the UI.
3. Expand the evaluation dataset to 10 examples and add a second grading function that also checks response length.
4. Compare two prompt variants (e.g. different system messages) against the same evaluation dataset and decide which performs better.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
