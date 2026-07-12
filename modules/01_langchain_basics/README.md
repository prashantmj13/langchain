# 01 — LangChain Basics

## Theory

LangChain is a framework for building applications on top of LLMs by composing small, standard building blocks — models, prompts, output parsers, retrievers, tools — into pipelines called **Runnables**. Three ideas matter before anything else:

- **Chat models vs. legacy LLMs.** Modern providers (Claude, GPT-4o, Gemini) are *chat* models: they take a list of role-tagged **messages** (`SystemMessage`, `HumanMessage`, `AIMessage`) and return an `AIMessage`. The old plain-text "LLM" interface (`llm.predict("...")`) still exists for a few completion-style APIs but is not how you should talk to Claude.
- **The Runnable interface.** Every LangChain component — a model, a prompt template, a parser — implements `.invoke()`, `.batch()`, and `.stream()`. This uniform interface is what lets you pipe them together with `|` (covered in [module 03](../03_chains_lcel)).
- **Messages carry the conversation.** A `SystemMessage` sets behavior/persona, `HumanMessage` is user input, `AIMessage` is model output. You build up a `list[BaseMessage]` and pass the whole thing to `.invoke()`.

## Use Case

Every LangChain app — a chatbot, a RAG pipeline, an agent — bottoms out in one of these primitives. Understanding `invoke`/`stream`/messages here means every later module is just "more pipes."

## Execution Internals: what `.invoke()` actually does

This is the one place in the repo that explains this mechanically — every other module just links back here. `llm.invoke([HumanMessage(content="...")])` on a `ChatAnthropic` instance runs through these concrete steps:

1. **`.invoke()` is defined once, on the shared `Runnable` base class.** `ChatAnthropic` (and every other chat model class) inherits it. Under the hood it delegates to a provider-specific `_generate()` method — this is the only part that differs between `ChatAnthropic`, `ChatOpenAI`, etc.
2. **Your `list[BaseMessage]` gets translated into the provider's wire format.** `SystemMessage`/`HumanMessage`/`AIMessage` objects are LangChain's provider-neutral representation; `ChatAnthropic._generate()` converts them into the exact JSON shape Anthropic's API expects (a top-level `system` string plus a `messages` array of `{"role": "user"|"assistant", "content": ...}` objects).
3. **The `anthropic` Python SDK sends a real HTTPS request.** It does a `POST https://api.anthropic.com/v1/messages` with your `ANTHROPIC_API_KEY` in a header, and the model name, messages, temperature, etc. as the JSON body. This is the step that actually leaves your machine and costs money/tokens.
4. **`.invoke()` blocks until the response comes back.** This is a synchronous network round trip — it's why an LLM call takes 1-5+ seconds, unlike a normal Python function call. (The `async`/`await` pattern used in the MCP modules exists specifically so a program *doesn't* have to sit idle during waits like this one.)
5. **The JSON response is parsed back into an `AIMessage`.** The generated text becomes `.content`; token counts become `.usage_metadata`; the raw provider response becomes `.response_metadata`. That `AIMessage` object is what `.invoke()` hands back to you.

**`.stream()` does steps 1-3 the same way**, but opens a streaming connection instead of waiting for the full response: the server sends the answer as a sequence of small chunks as they're generated, and `.stream()` yields one `AIMessageChunk` per chunk, which is why you see text appear token-by-token instead of all at once.

Every other model provider (`ChatOpenAI`, `ChatGoogleGenerativeAI`, `ChatOllama`, ...) follows this exact same 5-step shape — only step 2 (the wire format) and step 3 (which SDK/endpoint) actually differ, which is why swapping providers via `common/model_factory.py` never requires changing any calling code.

## How to Run

```bash
python modules/01_langchain_basics/example.py
python modules/01_langchain_basics/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY` in `.env`. Running `example.py` executes `basic_invoke()`, `system_plus_human()`, then `streaming()` in order — each prints its own `--- section ---` header, and the script exits after the last one (no server, no loop).

## Walkthrough

`example.py`:
1. Builds a chat model via `common.model_factory.get_chat_model()` (Claude by default).
2. Sends a single `HumanMessage` and prints the resulting `AIMessage` plus its token-usage metadata.
3. Sends a `SystemMessage` + `HumanMessage` pair to show how system prompts steer behavior.
4. Demonstrates `.stream()` for token-by-token output.

## Using a different model

```python
# Anthropic (default)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-5")

# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# Local Ollama (no API key needed)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.1")
```
All four implement the exact same `.invoke(messages)` / `.stream(messages)` interface — that uniformity is the entire point of LangChain's model abstraction.

## Reference Docs

- LangChain chat models: https://python.langchain.com/docs/concepts/chat_models/
- LangChain messages: https://python.langchain.com/docs/concepts/messages/
- Anthropic Claude API + models: https://docs.anthropic.com/en/docs/about-claude/models
- `langchain-anthropic` integration: https://python.langchain.com/docs/integrations/chat/anthropic/

## Exercises

1. Change the system prompt so Claude always answers in the style of a pirate, and confirm it holds across three different questions.
2. Print `response.usage_metadata` and calculate the approximate cost of your call using Anthropic's published per-token pricing.
3. Replace `.invoke()` with `.stream()` in the second example and print each chunk as it arrives instead of the final message.
4. Swap `LLM_PROVIDER` to `ollama` in your `.env` (with a local model pulled) and confirm the same script runs unmodified.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
