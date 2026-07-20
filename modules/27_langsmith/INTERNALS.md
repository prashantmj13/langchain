# Module 27 — Internals

## How env-var tracing turns on with zero code changes

**What it is:** Not a class you call directly — this is the more interesting (and more "magic-feeling") mechanism in this module: setting `LANGSMITH_TRACING=true` causes *every* `Runnable.invoke()` call anywhere in your program to start being recorded, without you touching any of your chain-building code.

**How it works internally:**
1. Every `Runnable`'s `.invoke()` (module 03's Execution Internals) is actually wrapped with a callback system under the hood — LangChain has always had this "callback manager" infrastructure, originally built for things like streaming and logging, and LangSmith tracing is implemented as one more callback handler plugged into it.
2. When `langsmith`'s tracing is active (which the `langsmith` package detects by checking the `LANGSMITH_TRACING` environment variable at call time), a tracing callback gets automatically attached to every `Runnable` invocation happening anywhere in the process — this is why `common/model_factory.py` and your chain code never need to import anything LangSmith-specific to get traced.
3. Each callback captures the inputs, outputs, timing, and (for LLM calls specifically) token usage of the step it's attached to, and — because `Runnable`s nest (a `RunnableSequence` contains steps, module 03) — the callback system naturally builds a *tree* of these recordings, mirroring your chain's actual structure.
4. That tree gets sent (asynchronously, in the background, so it doesn't slow down your actual chain execution) to LangSmith's servers, tagged with your `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT`, where it becomes the trace you view in the UI.

**Real source:** The callback infrastructure is in [`langchain_core/callbacks/`](https://github.com/langchain-ai/langchain/tree/master/libs/core/langchain_core/callbacks); the LangSmith-specific tracer is in the separate [`langchain-ai/langsmith-sdk`](https://github.com/langchain-ai/langsmith-sdk) repo (the `langsmith` package), specifically its `run_helpers.py` and tracing client code.

**How to validate tracing is genuinely active, without needing to open the LangSmith UI:**
```python
import os
print(os.getenv("LANGSMITH_TRACING"))   # should print "true" if you've set it correctly
print(os.getenv("LANGSMITH_API_KEY") is not None)  # True if a key is set (don't print the key itself)
```
The definitive check is still the UI — run a chain, then look for a new run under your `LANGSMITH_PROJECT` at smith.langchain.com. If nothing shows up despite the env vars being set correctly, double-check `load_dotenv()` actually ran *before* your first `.invoke()` call (env vars set after a `Runnable` has already started executing won't retroactively enable tracing for that call).

## `@traceable`

**How it works internally:** Unlike `Runnable.invoke()`, a plain Python function has no built-in callback system to hook into — `@traceable` adds one. It wraps your function so that, on each call, it manually starts a trace span (recording inputs), calls your original function, records the output (or the exception, if one was raised), and closes the span — then attaches that span to the current trace context, so if a `@traceable` function is called from *inside* a chain's execution (or from inside another `@traceable` function), it correctly nests under the parent, matching the tree structure described above.

**Real source:** [`langsmith/run_helpers.py`](https://github.com/langchain-ai/langsmith-sdk/blob/main/python/langsmith/run_helpers.py) in the `langchain-ai/langsmith-sdk` repo — look for the `traceable` decorator.

**How to validate nesting works correctly:** See this module's exercise 2 — build a `@traceable` function that calls another `@traceable` function internally, run it with tracing enabled, and check the LangSmith UI: the inner function's span should appear nested under the outer one's, not as a sibling trace.
