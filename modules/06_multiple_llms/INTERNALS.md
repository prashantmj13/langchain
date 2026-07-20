# Module 06 — Internals

## `RunnableBranch((condition, chain), default_chain)`

**What it is:** A `Runnable` that behaves like an `if`/`elif`/`else` chain expressed as data instead of code — a list of `(condition_function, runnable)` pairs plus a fallback.

**How it works internally:**
1. `RunnableBranch` stores its list of `(condition, runnable)` pairs exactly as you passed them, plus the final positional argument as its `default`.
2. On `.invoke(input)`, it loops through the pairs *in order* and calls `condition(input)` for each one — the condition is a plain Python function (often a `lambda`) that returns `True`/`False`.
3. The moment a condition returns `True`, it stops checking further conditions and calls `.invoke(input)` on that pair's `runnable`, returning its result immediately.
4. If none of the conditions match, it falls through to the `default` runnable.

This means **order matters** — if two conditions could both be `True` for the same input, the first one listed wins, exactly like `if`/`elif` in plain Python.

**Real source:** [`langchain_core/runnables/branch.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/runnables/branch.py) — look for the `RunnableBranch` class and its `invoke` method.

**How to validate it's working:**
```python
router = RunnableBranch(
    (lambda x: x["task_type"] == "reasoning", reasoning_chain),
    simple_chain,
)
# Confirm routing by checking which branch actually gets called, not just the final answer --
# e.g. temporarily replace reasoning_chain/simple_chain with functions that print their own name:
router_test = RunnableBranch(
    (lambda x: x["task_type"] == "reasoning", lambda x: "WENT TO REASONING BRANCH"),
    lambda x: "WENT TO DEFAULT BRANCH",
)
print(router_test.invoke({"task_type": "reasoning"}))     # "WENT TO REASONING BRANCH"
print(router_test.invoke({"task_type": "simple lookup"})) # "WENT TO DEFAULT BRANCH"
```
Swapping in these print-based stand-ins temporarily is a genuinely useful debugging technique any time you're not sure which branch of a `RunnableBranch` is actually firing.
