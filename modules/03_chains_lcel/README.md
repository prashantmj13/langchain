# 03 — Chains with LCEL

## Theory

LCEL (LangChain Expression Language) is the `|` pipe syntax for composing `Runnable`s: `prompt | llm | parser`. Each stage's output becomes the next stage's input. Key pieces:

- **`Runnable`** — the base interface (`.invoke`, `.batch`, `.stream`, `.ainvoke`) implemented by prompts, models, parsers, and retrievers alike.
- **`RunnableLambda`** — wrap any plain Python function as a Runnable so it can slot into a pipe.
- **Output parsers** — `StrOutputParser` extracts `.content` as a plain string; `PydanticOutputParser`/`.with_structured_output()` coerce the model's output into a typed schema.
- **Automatic parallelism & streaming** — because every stage shares the same interface, LCEL chains get `.batch()` (parallel calls) and `.stream()` (token streaming through the whole pipeline) for free, without you writing any threading code.

This is the modern replacement for the older `LLMChain` class, which is deprecated — `prompt | llm | parser` *is* the chain.

## Use Case

Any multi-step LLM workflow: "template the input, call the model, parse the output" is the single most common pattern in LangChain apps, from a one-shot classifier to the first stage of a RAG pipeline.

## Execution Internals: the Runnable protocol

Module 01 explained what `.invoke()` does on a single chat model; this is where the pieces that make *chains* of them possible get explained mechanically. Every other module that uses `RunnableLambda`/`RunnableParallel`/`RunnablePassthrough`/`RunnableBranch` links back here instead of repeating this.

**What `prompt | llm | parser` actually does when that line runs.** Python lets a class override the `|` operator by defining `__or__`. `Runnable.__or__` does *not* run anything — it just builds and returns a `RunnableSequence` object that remembers the steps in order. So the line `chain = prompt | llm | parser` executes instantly and does zero LLM calls; it only wires three objects together into one. Nothing runs until you later call `chain.invoke(...)`, `.batch(...)`, or `.stream(...)`.

**What `chain.invoke(input)` does on that `RunnableSequence`.** It's a plain loop: call `step.invoke(current_value)` for the first step, take its return value, pass that as the input to the next step's `.invoke()`, and so on. So `chain.invoke({"topic": "x"})` runs as:
```python
formatted = prompt.invoke({"topic": "x"})   # -> a list of messages
response  = llm.invoke(formatted)           # -> an AIMessage (see module 01)
result    = parser.invoke(response)         # -> a plain string
return result
```
Each `step.invoke()` call is exactly the kind of call module 01 walks through in detail for the `llm` step; `prompt.invoke()` and `parser.invoke()` are just much cheaper, pure-Python transformations with no network call.

**What `RunnableLambda` does.** It's a thin wrapper class whose entire `.invoke(x)` implementation is `return self.func(x)`. It exists only so a plain Python function — which has no `.invoke()`/`.batch()`/`.stream()` methods of its own — can be dropped into a `|` pipe and satisfy the `Runnable` interface the rest of the chain expects. You usually don't even have to write `RunnableLambda(...)` explicitly: when LangChain sees a raw function on either side of a `|`, it auto-wraps it in a `RunnableLambda` for you (this "coercion" is why `chain | (lambda text: text.upper())` works even though a bare lambda isn't a `Runnable`).

**What a `{...}` dict inside a chain does (`RunnableParallel`).** Writing `{"context": retriever, "question": RunnablePassthrough()}` as a pipe stage gets auto-coerced into a `RunnableParallel`. Its `.invoke(input)` calls `.invoke(input)` on *every value in the dict*, dispatching them to a thread pool so they run concurrently rather than one after another, then returns a new dict with the same keys holding each branch's result. This is exactly why the parallel-branch pipeline in [module 05](../05_sequential_chain) and the RAG pipelines in [modules 16](../16_rag)/[17](../17_history_aware_rag_bot) can be faster than calling each branch with a separate `.invoke()`.

**What `RunnablePassthrough` does.** Its `.invoke(input)` is just `return input` — it exists so that inside a `RunnableParallel`, you can forward the *original* input unchanged into one output key while other keys compute something new from that same input (e.g. keeping `question` around alongside a computed `context`).

**What `RunnableBranch` does** (used in [module 06](../06_multiple_llms)). It's a list of `(condition, runnable)` pairs plus a default; `.invoke(input)` checks each condition function against the input in order and calls `.invoke(input)` on the first `runnable` whose condition returns `True` (falling back to the default if none match) — a routing `if/elif/else` expressed as data instead of code.

**What `.batch([x1, x2, x3])` does differently from a `for` loop of `.invoke()` calls.** For I/O-bound steps (an HTTP call to Claude, for instance), the default `Runnable.batch()` implementation dispatches all the `.invoke()` calls concurrently via a thread pool, so wall-clock time is close to the *slowest single call*, not the sum of all of them — as long as the provider doesn't rate-limit you into serializing anyway.

**What `.stream()` does on a `RunnableSequence`.** It doesn't wait for the whole chain to finish before producing anything: steps that support real streaming (a chat model) yield partial chunks as soon as they exist; steps that don't support streaming (most prompt templates, parsers) just run once via `.invoke()` and hand their single result onward. That's why `(prompt | llm | StrOutputParser()).stream(...)` still shows token-by-token output — the streaming happens at the `llm` step, and `StrOutputParser` passes each chunk's text through as it arrives rather than buffering the whole response.

## How to Run

```bash
python modules/03_chains_lcel/example.py
python modules/03_chains_lcel/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY` in `.env`. Each function builds a small `prompt | llm | parser` chain and calls `.invoke()`/`.batch()` on it; the script runs all four demo functions back to back and prints each result under its own header.

## Walkthrough

`example.py`:
1. Builds a 3-stage chain: `ChatPromptTemplate | ChatAnthropic | StrOutputParser`.
2. Adds a `RunnableLambda` stage that post-processes the string output (e.g. uppercasing a keyword).
3. Uses `.with_structured_output(PydanticModel)` to get back a typed, validated object instead of raw text.
4. Calls `.batch()` on three inputs at once.

## Using a different model

Only the middle stage of the pipe changes — everything else (`prompt`, `parser`, `RunnableLambda`) is provider-agnostic:
```python
chain = prompt | get_chat_model(provider="openai") | StrOutputParser()
```

## Reference Docs

- LCEL concept guide: https://python.langchain.com/docs/concepts/lcel/
- `Runnable` interface: https://python.langchain.com/docs/concepts/runnables/
- Structured output: https://python.langchain.com/docs/how_to/structured_output/

## Exercises

1. Add a fourth stage to the chain that counts words in the final string and prints `"{n} words: {text}"`.
2. Define a Pydantic model `MovieReview(title: str, rating: int, summary: str)` and use `.with_structured_output()` to extract it from a free-text review.
3. Call `.batch()` with 5 different questions and time it against calling `.invoke()` in a plain Python `for` loop — compare wall-clock time.
4. Use `.stream()` on the full 3-stage chain and print output as it arrives, not just at the end.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
