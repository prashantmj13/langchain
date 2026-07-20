# Module 03 — Internals

This module's README already has a deep [Execution Internals](README.md#execution-internals-the-runnable-protocol) section covering the `Runnable` protocol itself — what `|` builds, what `RunnableLambda`/`RunnableParallel`/`RunnablePassthrough`/`RunnableBranch` do, and how `.batch()`/`.stream()` differ from a plain loop. This page covers the two pieces that section doesn't: `StrOutputParser` and `.with_structured_output()`.

## `StrOutputParser`

**What it is:** The simplest possible output parser — a `Runnable` whose entire job is `AIMessage` in, plain string out.

**How it works internally:** Its `.invoke(message)` implementation is close to `return message.content` — it just reads the `.content` attribute off whatever `BaseMessage` it receives and returns that. As the last stage of a chain (`prompt | llm | StrOutputParser()`), it's the thing that turns `chain.invoke(...)`'s return value from an `AIMessage` object into a plain `str`.

**Real source:** [`langchain_core/output_parsers/string.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/output_parsers/string.py).

**How to validate it's working:**
```python
from langchain_core.messages import AIMessage
parser = StrOutputParser()
print(parser.invoke(AIMessage(content="hello")))   # "hello" -- a plain str, not an AIMessage
print(type(parser.invoke(AIMessage(content="hello"))))  # <class 'str'>
```

## `.with_structured_output(PydanticModel)`

**What it is:** A method on chat models that returns a *new*, wrapped version of the model — one that always replies with an instance of your Pydantic model instead of an `AIMessage` with free text.

**How it works internally (this is worth understanding, since it looks like magic at first):**
1. It converts your Pydantic model's fields into a JSON Schema description — the same kind of schema module 21 shows you being auto-generated for MCP tools from Python type hints.
2. It passes that schema to Claude as a special "tool" the model can call (Anthropic's API supports forcing a response through a structured tool-call rather than free text) — this reuses the exact same tool-calling mechanism module 19's agents use to call `add`/`get_word_length`, just aimed at *output formatting* instead of taking an action.
3. Claude's response comes back as a structured tool-call matching your schema (arguments filled in) rather than prose.
4. LangChain parses those arguments and constructs a real instance of your Pydantic class from them, validating the types along the way (so if Claude returns `"rating": "nine"` instead of a number, Pydantic validation will catch that as an error rather than silently accepting a string where an int was expected).

**Real source:** The `with_structured_output` method is defined on `BaseChatModel` in [`langchain_core/language_models/chat_models.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/language_models/chat_models.py); Anthropic's specific implementation of the underlying tool-calling is in [`langchain_anthropic/chat_models.py`](https://github.com/langchain-ai/langchain/blob/master/libs/partners/anthropic/langchain_anthropic/chat_models.py).

**How to validate it's working:**
```python
structured_llm = llm.with_structured_output(MovieReview)
result = structured_llm.invoke("Extract data from: Dune was great, 9/10.")
print(type(result))       # <class '__main__.MovieReview'> -- a real Pydantic instance, not AIMessage
print(result.rating)      # 9 -- a real int, already validated
```
If you pass text with no extractable data at all, watch what happens — depending on your Pydantic model's field constraints, it may raise a validation error or fill in a best guess. Testing that edge case is a good way to understand how strict your schema actually is.
