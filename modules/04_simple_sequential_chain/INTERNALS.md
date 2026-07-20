# Module 04 — Internals

This module doesn't introduce a new class — `ChatPromptTemplate` and `StrOutputParser` are covered in [module 02's](../02_prompt_templates/INTERNALS.md) and [module 03's](../03_chains_lcel/INTERNALS.md) INTERNALS.md pages. What's worth a closer look here specifically is what happens when you compose two *already-built* chains together with a reshaping step in between.

## Composing two chains: `stage_1 | (lambda outline_text: {"outline": outline_text}) | stage_2`

**What it is:** `stage_1` and `stage_2` are each themselves `RunnableSequence`s (built from `prompt | llm | StrOutputParser()`). This line chains a *sequence* into another *sequence*, with a reshaping function in between.

**How it works internally:**
1. `stage_1` is itself a `Runnable` (every `RunnableSequence` is), so piping it with `|` works exactly the same as piping a single prompt or model — LangChain doesn't care whether the left side of `|` is one component or an entire pre-built pipeline.
2. `stage_1.invoke({"topic": "..."})` runs its own internal 3 steps (prompt → llm → parser) and returns a plain string (the outline) — from the outside, you can't tell it was 3 steps; it behaves like any other single `Runnable`.
3. The middle `lambda outline_text: {"outline": outline_text}` gets auto-wrapped into a `RunnableLambda` (module 03's Execution Internals). Its job is purely structural: `stage_1` outputs a plain string, but `stage_2`'s prompt template expects a dict with an `"outline"` key — this lambda bridges that mismatch.
4. `stage_2` then runs its own 3 internal steps on that reshaped dict, same as `stage_1` did.

The key insight: **a `RunnableSequence` composed of `RunnableSequence`s is still just a `RunnableSequence`** — LangChain flattens/handles nested sequences transparently, which is exactly why arbitrarily large pipelines can be built by gluing smaller, already-tested pieces together.

**Real source:** The composition/flattening behavior lives in `RunnableSequence.__or__` and `__ror__` in [`langchain_core/runnables/base.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/runnables/base.py).

**How to validate it's working:**
```python
full_chain = stage_1 | (lambda outline_text: {"outline": outline_text}) | stage_2
print(type(full_chain))   # <class 'langchain_core.runnables.base.RunnableSequence'>

# Confirm the reshaping step actually runs by checking stage_1's raw output type
# vs. what stage_2 needs:
outline = stage_1.invoke({"topic": "test"})
print(type(outline))      # <class 'str'> -- stage_2's prompt needs a dict, hence the lambda
```
