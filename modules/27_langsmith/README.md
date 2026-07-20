# 27 — LangSmith

## Theory

When a chain gives a weird answer, "what actually happened inside there?" is a hard question to answer just by staring at the final output. LangSmith is a tool that records every single step along the way — every prompt that got built, every call to the model with its exact input and output, every tool that got called — so you can go back afterward and see exactly what happened and why.

- **Turning it on needs no code changes.** Just set a couple of settings (an on/off switch and your LangSmith account key), and every chain/model call in your program starts getting recorded automatically — you don't have to add any tracking code yourself.
- **Recording your own custom functions too.** If you have a plain Python function (not a LangChain chain) that's part of your pipeline, adding one line above it lets LangSmith record it alongside everything else, so you get the complete picture in one place.
- **Testing your chain against known examples.** You can build a small set of "here's a question, here's what a good answer looks like" pairs, run your chain against all of them, and get a score — a fast way to check whether a prompt change made things better or worse before you actually ship it.

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

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `os.getenv("LANGSMITH_TRACING")` / `os.getenv("LANGSMITH_API_KEY")` (Python standard library) | Reads environment variables, returning `None` if unset. | Used in `check_tracing_configured()` to detect whether tracing is actually turned on, so the script can explain what's missing instead of just silently not tracing. |
| `@traceable(name="shorten_for_display")` | Marks a plain Python function so LangSmith records its inputs/outputs as part of the trace, the same way it automatically records `Runnable.invoke()` calls. | Applied to `shorten_for_display()` — a plain post-processing function, not a LangChain `Runnable` — so it shows up in the same trace as the model call before it. |
| `prompt \| llm | StrOutputParser()` | The same chain-building pattern from module 03. | Used as the thing actually being traced/evaluated — LangSmith needs something to observe, and this is a realistic, simple example of it. |
| A plain Python loop calling `chain.invoke(...)` and checking `expected_substring in output` | Ordinary Python control flow, not a LangSmith-specific API. | Used in `run_mini_evaluation()` as a minimal, dependency-free stand-in for LangSmith's real dataset-based evaluation feature — enough to demonstrate the *idea* of evaluation without needing a hosted dataset. |

For how setting an env var causes *every* `Runnable.invoke()` in your program to start being traced with zero code changes, and how `@traceable` extends that to plain functions — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

Tracing/evaluation are provider-agnostic — they capture whatever `get_chat_model(...)` you're using. Comparing providers on the same evaluation dataset (Claude vs GPT-4o-mini) is itself a common LangSmith use case.

## Reference Docs

- LangSmith docs: https://docs.smith.langchain.com/
- Tracing quickstart: https://docs.smith.langchain.com/observability
- Evaluation quickstart: https://docs.smith.langchain.com/evaluation

## Exercises

1. **Seeing a real trace, not just reading about tracing.** Sign up for a free LangSmith account, get an API key, and set `LANGSMITH_TRACING=true` plus `LANGSMITH_API_KEY=...` in your `.env`. Run `example.py` again (no code changes needed — that's the point of env-var-based tracing) and go to smith.langchain.com to find the trace it just generated. Click into it and identify: which step took the longest, and how many tokens the LLM call used.
2. **Confirming nested traces actually nest.** Write a second `@traceable`-decorated function that calls the first one (`shorten_for_display`) internally — e.g. a function that first fetches some text, then calls `shorten_for_display` on it. Run it with tracing enabled and check the LangSmith UI: does the inner function's trace appear nested *under* the outer one, showing the call hierarchy?
3. **A bigger, more rigorous evaluation.** Expand `EVAL_DATASET` from 3 examples to 10, covering more varied topics. Add a second grading function alongside the existing substring check — e.g. one that checks the response is under some word count (a proxy for "did it actually follow the 'one sentence' instruction"). Run both checks over all 10 examples and print a pass/fail summary for each.
4. **A/B testing two different prompts.** Build two versions of `build_chain()`'s prompt with different system messages (e.g. one terse, one explaining things "for a beginner"). Run both against the same evaluation dataset from exercise 3, and compare pass rates — which system message actually produces more consistently correct/well-formatted answers?

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
