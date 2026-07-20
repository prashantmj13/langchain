# 01 — LangChain Basics

## Theory

Think of LangChain as a box of LEGO pieces for building things with AI models. Each piece — a model, a prompt, a way to parse the output — snaps together with the others the same way. Three things to know before anything else:

- **You talk to Claude using "messages", not a single block of text.** A conversation is a list of messages, each one labeled with who it's from: a `SystemMessage` (your instructions to the model, like "you are a helpful assistant"), a `HumanMessage` (what the user typed), and an `AIMessage` (what the model replied). You send the whole list, and the model replies with one more `AIMessage`. (Older, simpler AI tools just took one block of text and returned one block of text back — that style still exists, but it's not how you should work with Claude.)
- **Every LangChain piece is used the same way.** Whether it's a model, a prompt, or something that reformats the model's answer, they all share the same three buttons: `.invoke()` (give it input, get one output), `.batch()` (do that for a list of inputs at once), and `.stream()` (get the answer back piece by piece, as it's generated, instead of waiting for the whole thing). Because every piece has the same three buttons, you can snap them together with the `|` symbol — that's covered in [module 03](../03_chains_lcel).
- **A conversation is just a growing list.** Each time you or the model says something, that becomes one more item in a `list[BaseMessage]`. You hand the whole list to `.invoke()` every time — the model has no memory of its own, so *you* carry the conversation forward by keeping this list around.

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

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `ChatAnthropic` (via `get_chat_model()`) | The LangChain class that wraps Claude's API — the object every example call goes through. | It's the entry point for talking to Claude at all; every other class in this table exists to build input for it or process its output. |
| `HumanMessage` | Represents one message from the user in a conversation. | Used to wrap the plain-text questions we send to the model, so the model can tell they came from the user rather than the system or itself. |
| `SystemMessage` | Represents an instruction that sets the model's overall behavior, separate from the conversation itself. | Used in `system_plus_human()` to tell the model to answer tersely, as a senior engineer would — steering style without it being part of the "conversation." |
| `.invoke(messages)` | Sends a list of messages to the model and waits for one complete response. | The basic way to get an answer: call it, get an `AIMessage` back. Used in `basic_invoke()` and `system_plus_human()`. |
| `.stream(messages)` | Same as `.invoke()`, but returns the answer piece by piece as it's generated instead of waiting for the whole thing. | Used in `streaming()` to show output appearing token-by-token, the way it looks in a chat UI. |
| `response.content` | The plain-text answer inside an `AIMessage`. | This is the actual text we want to print or use — the rest of the `AIMessage` object is metadata. |
| `response.usage_metadata` | A dict of token counts (input/output) for that specific call. | Printed in `basic_invoke()` to show how you'd track usage/cost per call. |

For how `ChatAnthropic`, the message classes, and `.invoke()`/`.stream()` actually work internally — plus a quick check to validate each one — see [`INTERNALS.md`](INTERNALS.md) in this folder.

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

1. **System prompts control persona, not just topic.** Copy `system_plus_human()` from `example.py` and change the `SystemMessage` so Claude always answers in the voice of a pirate — something like `"You always answer in the voice of a pirate."` Ask it 3 different, unrelated questions (e.g. about Python, about cooking, about the weather) in 3 separate `.invoke()` calls, and confirm the pirate voice holds in all 3 — that's what proves the system message is steering *style*, not just answering one lucky question.
2. **Reading and using token usage.** Take `basic_invoke()`'s response and print `response.usage_metadata` — you'll see a dict with `input_tokens` and `output_tokens`. Look up Anthropic's current per-million-token pricing at anthropic.com/pricing, and compute the approximate cost of that one call by hand (or in code): `(input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price`.
3. **`.stream()` returns chunks, not one final message.** Take the `system_plus_human()` example and replace `llm.invoke(messages)` with a `for chunk in llm.stream(messages):` loop, printing `chunk.content` (with `end=""` so it doesn't add a newline after every chunk) as each piece arrives, instead of printing one complete `response.content` at the end.
4. **Confirming the provider-swap actually works.** In your `.env` file, change `LLM_PROVIDER=anthropic` to `LLM_PROVIDER=ollama` (after installing Ollama and running `ollama pull llama3.1` locally). Re-run `example.py` completely unmodified — no code changes — and confirm it now answers using your local model instead of Claude. This is the payoff of `common/model_factory.py` existing at all: one env var, zero code changes.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
