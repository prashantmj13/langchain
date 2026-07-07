# 01 — LangChain Basics

## Theory

LangChain is a framework for building applications on top of LLMs by composing small, standard building blocks — models, prompts, output parsers, retrievers, tools — into pipelines called **Runnables**. Three ideas matter before anything else:

- **Chat models vs. legacy LLMs.** Modern providers (Claude, GPT-4o, Gemini) are *chat* models: they take a list of role-tagged **messages** (`SystemMessage`, `HumanMessage`, `AIMessage`) and return an `AIMessage`. The old plain-text "LLM" interface (`llm.predict("...")`) still exists for a few completion-style APIs but is not how you should talk to Claude.
- **The Runnable interface.** Every LangChain component — a model, a prompt template, a parser — implements `.invoke()`, `.batch()`, and `.stream()`. This uniform interface is what lets you pipe them together with `|` (covered in [module 03](../03_chains_lcel)).
- **Messages carry the conversation.** A `SystemMessage` sets behavior/persona, `HumanMessage` is user input, `AIMessage` is model output. You build up a `list[BaseMessage]` and pass the whole thing to `.invoke()`.

## Use Case

Every LangChain app — a chatbot, a RAG pipeline, an agent — bottoms out in one of these primitives. Understanding `invoke`/`stream`/messages here means every later module is just "more pipes."

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
