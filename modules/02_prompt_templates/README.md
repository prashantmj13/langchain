# 02 — Prompt Templates

## Theory

Hardcoding f-strings into prompts doesn't scale — you lose reuse, validation, and composability. LangChain's prompt templates solve this:

- **`PromptTemplate`** — a parameterized plain-text template (`"Translate {text} into {language}"`), for legacy/completion-style calls.
- **`ChatPromptTemplate`** — the one you'll actually use with Claude: builds a *list of messages* from templated strings, e.g. `[("system", "..."), ("human", "{question}")]`.
- **Partial variables** — pre-fill some template variables now, leave others for later (e.g. bake in today's date, leave `question` open).
- **Few-shot prompting** — `FewShotChatMessagePromptTemplate` injects example input/output pairs before the real question, steering the model's output format/style without fine-tuning.

Templates are `Runnable`s themselves — they implement `.invoke()` and can be piped with `|`, which is what makes chains (module 03) possible.

## Use Case

Any prompt that's reused across requests with different inputs (support bot answering different questions, a summarizer given different documents) should be a template, not a string you `.format()` by hand. Few-shot templates are the cheapest way to get a model to follow a specific output format (e.g. strict JSON, a particular tone) without fine-tuning.

## How to Run

```bash
python modules/02_prompt_templates/example.py
python modules/02_prompt_templates/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY` in `.env`. `example.py` runs `basic_template()`, `partial_template()`, then `few_shot_template()` in sequence, each making one or more `.invoke()` calls and printing the model's response.

## Walkthrough

`example.py`:
1. Builds a `ChatPromptTemplate` with a system + human message and fills it with `.invoke({...})`.
2. Uses `.partial()` to pre-bind one variable.
3. Builds a `FewShotChatMessagePromptTemplate` that teaches the model a "sentiment: <label>" output format from 3 examples, then applies it to a new sentence.

## Using a different model

Prompt templates are provider-agnostic — the same `ChatPromptTemplate` object works whether the downstream model is `get_chat_model()` (Anthropic) or a directly-instantiated `ChatOpenAI`/`ChatGoogleGenerativeAI`. Only the model at the end of the pipe changes; see [module 01](../01_langchain_basics) for the swap snippet.

## Reference Docs

- Prompt templates concept: https://python.langchain.com/docs/concepts/prompt_templates/
- `ChatPromptTemplate` API: https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.chat.ChatPromptTemplate.html
- Few-shot prompting how-to: https://python.langchain.com/docs/how_to/few_shot_examples_chat/

## Exercises

1. Add a third templated variable (e.g. `{tone}`) to the system message and pass different tones (`formal`, `sarcastic`) across three calls.
2. Build a few-shot template with 5 examples that gets Claude to classify support tickets into `bug` / `feature-request` / `question`, then test it on 3 new tickets.
3. Use `.partial()` to bake in a `current_date` value computed from `datetime.now()`, and confirm the model can answer "what is today's date" correctly.
4. Serialize a `ChatPromptTemplate` to a dict with `.dict()` and reload it — confirm the reloaded template produces identical output.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
