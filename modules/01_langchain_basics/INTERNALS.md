# Module 01 — Internals

A deeper look at the specific classes this module uses: how each one actually works inside, where to read the real source if you want to go further, and a quick way to confirm each one is behaving correctly on your machine. This is a companion to the [Classes & Methods Used](README.md#classes--methods-used) table and the [Execution Internals](README.md#execution-internals-what-invoke-actually-does) section in the main README — start there first if you haven't already.

## `ChatAnthropic`

**What it is:** The LangChain class that represents Claude as a chat model. Every call in this module goes through an instance of it (returned by `get_chat_model()`).

**How it works internally:**
1. On creation, it reads your `ANTHROPIC_API_KEY` (from the environment, since `common/model_factory.py` calls `load_dotenv()` first) and stores it along with the model name and temperature you passed in.
2. It doesn't make any network call at creation time — building `ChatAnthropic(model="claude-sonnet-4-5")` is cheap and instant, just like building a `RunnableSequence` with `|` is (module 03).
3. When you call `.invoke(messages)`, it delegates to an internal `_generate()` method that converts your list of `HumanMessage`/`SystemMessage`/`AIMessage` objects into the JSON shape Anthropic's API expects (a `system` string plus a `messages` array of role/content pairs).
4. It hands that JSON to the `anthropic` Python package (a separate, lower-level library that just wraps HTTP requests — LangChain doesn't talk to the network directly), which sends the actual `POST` request to `api.anthropic.com`.
5. The response comes back as JSON; `ChatAnthropic` parses it into an `AIMessage`, filling in `.content` (the generated text), `.usage_metadata` (token counts), and `.response_metadata` (everything else Anthropic returned, like the stop reason).

**Real source:** [`langchain_anthropic/chat_models.py`](https://github.com/langchain-ai/langchain/blob/master/libs/partners/anthropic/langchain_anthropic/chat_models.py) in the `langchain-ai/langchain` repo — look for the `ChatAnthropic` class and its `_generate`/`_stream` methods. The underlying HTTP client is the separate [`anthropics/anthropic-sdk-python`](https://github.com/anthropics/anthropic-sdk-python) repo.

**How to validate it's working:**
```python
llm = get_chat_model()
print(type(llm))                  # should print <class 'langchain_anthropic.chat_models.ChatAnthropic'>
print(llm.model)                  # should print the model name, e.g. 'claude-sonnet-4-5'
response = llm.invoke("hello")
print(type(response))             # should print <class 'langchain_core.messages.ai.AIMessage'>
```
If the API key is missing or wrong, `.invoke()` will raise an authentication error from the `anthropic` package — that error, not a silent wrong answer, is your signal something's misconfigured.

## `HumanMessage` / `SystemMessage` / `AIMessage`

**What it is:** Simple data classes (built on Pydantic) — each just holds a `.content` string and a `.type` label (`"human"`, `"system"`, `"ai"`). They carry no logic of their own; they're just structured containers `ChatAnthropic` reads from and writes to.

**How it works internally:** All three inherit from `BaseMessage`, which is itself a Pydantic model. Creating one (`HumanMessage(content="hi")`) just validates that `content` is a string (or a list, for multimodal content — module 18) and stores it. `.type` is a fixed class attribute — `HumanMessage.type` is always `"human"`, hardcoded in the class definition, not something you set per-instance.

**Real source:** [`langchain_core/messages/`](https://github.com/langchain-ai/langchain/tree/master/libs/core/langchain_core/messages) — `human.py`, `system.py`, and `ai.py` each define one of these classes; `base.py` defines the shared `BaseMessage`.

**How to validate it's working:**
```python
msg = HumanMessage(content="test")
print(msg.type)       # "human"
print(msg.content)    # "test"
print(isinstance(msg, BaseMessage))  # True -- every message type shares this parent
```

## `.invoke()` vs `.stream()`

**What it is:** Two different ways of getting a response from the same `ChatAnthropic` object — covered in depth in this module's [Execution Internals](README.md#execution-internals-what-invoke-actually-does) section. The short version: `.invoke()` waits for the complete answer in one blocking call; `.stream()` opens a streaming connection and yields `AIMessageChunk` pieces as they're generated.

**How to validate the difference is real, not just visual:**
```python
import time

start = time.perf_counter()
llm.invoke("Count from 1 to 20.")
print("invoke total time:", time.perf_counter() - start)

start = time.perf_counter()
first_chunk_time = None
for chunk in llm.stream("Count from 1 to 20."):
    if first_chunk_time is None:
        first_chunk_time = time.perf_counter() - start
print("stream: time to first chunk:", first_chunk_time)
```
`.stream()`'s time-to-first-chunk should be noticeably shorter than `.invoke()`'s total time — that's proof it's genuinely returning partial output as it arrives, not just buffering the whole response and doling it out to you afterward.
