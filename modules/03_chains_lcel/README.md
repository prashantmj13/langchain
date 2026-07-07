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
