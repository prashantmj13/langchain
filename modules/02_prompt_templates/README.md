# 02 — Prompt Templates

## Theory

If you find yourself writing `f"Translate {text} into {language}"` by hand everywhere, you've just reinvented what this module gives you for free — plus some extra abilities. A **prompt template** is a prompt with blanks in it that you fill in later:

- **`PromptTemplate`** — the plain-text version: a template like `"Translate {text} into {language}"` where `{text}` and `{language}` get swapped out for real values. This is the older style, from before chat-style models were the norm.
- **`ChatPromptTemplate`** — the one you'll actually use with Claude. Instead of one string, it builds the whole labeled message list from module 01 for you, e.g. `[("system", "..."), ("human", "{question}")]`, and fills in the blanks when you call it.
- **Filling in some blanks now, some later.** You can lock in a value for one blank (say, today's date) while leaving another (the user's question) open until you actually need it. This is handy when part of the prompt is fixed and part changes every time.
- **Showing examples instead of just instructions ("few-shot prompting").** Instead of telling the model what format to answer in, you can show it a few example question/answer pairs first, then ask your real question. The model picks up the pattern from the examples — often more reliably than a written instruction alone.

Prompt templates plug into the same `.invoke()` / `|` system from module 01 — that's what lets you chain a template straight into a model, which is what module 03 is about.

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

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `ChatPromptTemplate` | Builds a list of role-tagged messages from templates with `{blanks}` in them. | The reusable, fillable version of the message lists from module 01 — used in all three functions to define the prompt shape once and fill it in with different values. |
| `.from_messages([...])` | Builds a `ChatPromptTemplate` from a list of `(role, template_string)` pairs. | The standard way to construct a chat prompt template — used everywhere in this module instead of building `SystemMessage`/`HumanMessage` objects by hand. |
| `.partial(persona="...")` | Returns a copy of a template with one or more blanks already filled in, leaving the rest open. | Used in `partial_template()` to lock in the `persona` value ahead of time, so callers only need to supply `question` later. |
| `FewShotChatMessagePromptTemplate` | Injects a set of example input/output message pairs into the prompt before the real question. | Used in `few_shot_template()` to teach the model the exact output format (`"sentiment: <label>"`) by example, instead of just describing the format in words. |
| `prompt \| llm` | Chains the template into the model: fill in the template, then send the result to `.invoke()`. | Every function ends with this pattern — it's the first real use of the `|` chaining from module 03, applied here to "template then call the model." |

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
