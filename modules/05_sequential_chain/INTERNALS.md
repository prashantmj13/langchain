# Module 05 — Internals

## `RunnablePassthrough.assign(sentiment=..., summary=...)`

**What it is:** A class method that builds a `Runnable` which takes an incoming dict, keeps every key already in it, and adds new keys computed by running the given sub-chains against that same incoming dict.

**How it works internally:**
1. `RunnablePassthrough.assign(sentiment=sentiment_chain, summary=summary_chain)` internally builds something equivalent to `RunnableParallel({"sentiment": sentiment_chain, "summary": summary_chain, **{k: RunnablePassthrough() for k in "keep existing keys"}})` — conceptually, it merges a "keep what's already there" pass with a "compute these new things" pass.
2. On `.invoke({"review": "..."})`, it runs `sentiment_chain.invoke({"review": "..."})` and `summary_chain.invoke({"review": "..."})` concurrently (via a thread pool — the same mechanism as `RunnableParallel`, covered in module 03's Execution Internals), while also just keeping `"review"` unchanged.
3. It merges all of that into one new dict: `{"review": "...", "sentiment": "...", "summary": "..."}` and returns it — ready to be the input to the next stage.

**Real source:** [`langchain_core/runnables/passthrough.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/runnables/passthrough.py) — look for `RunnablePassthrough.assign`.

**How to validate it's working:**
```python
enrich = RunnablePassthrough.assign(sentiment=sentiment_chain, summary=summary_chain)
result = enrich.invoke({"review": "Great product!"})
print(result.keys())   # dict_keys(['review', 'sentiment', 'summary']) -- original key preserved, 2 new ones added
print(result["review"])  # unchanged -- exactly what you passed in
```

## `RunnableParallel(review=..., sentiment=..., reply=...)`

**What it is:** The explicit class form of the `{...}` dict auto-coercion covered in module 03's Execution Internals — used here at the very end of the pipeline to assemble the final output shape.

**How it works internally:** Each keyword argument is itself a `Runnable`. On `.invoke(input)`, `RunnableParallel` submits every one of them to a thread pool at once (via Python's `concurrent.futures.ThreadPoolExecutor`, under the hood), waits for all of them to finish, and returns a dict pairing each key with its corresponding `Runnable`'s result. A plain `lambda x: x["review"]` counts as a `Runnable` here too (auto-coerced into a `RunnableLambda`) — it just does essentially no work, picking one key back out of the dict it's handed.

**Real source:** [`langchain_core/runnables/base.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/runnables/base.py) — look for the `RunnableParallel` class and its `invoke`/`_invoke` methods.

**How to validate the concurrency is real:**
```python
import time

def slow_chain_call(x):
    time.sleep(1)
    return "done"

parallel = RunnableParallel(a=slow_chain_call, b=slow_chain_call, c=slow_chain_call)
start = time.perf_counter()
parallel.invoke({})
print(time.perf_counter() - start)   # ~1 second, not ~3 -- proof all 3 ran concurrently, not sequentially
```
