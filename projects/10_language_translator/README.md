# Project 10 — Language Translator

**Domain:** Warm-up (general LangChain basics)
**Difficulty:** Beginner
**Time estimate:** 1-2 hours

**Before you start:** Complete [Project 09](../09_text_summarizer) first if you haven't — this project reuses the exact same shape of script (build a model, build a prompt, chain them, invoke), so if project 09 felt hard, do it again before this one rather than skipping ahead.

## The Problem

You type in a sentence and the name of a language, and your program prints the translation. Unlike a fixed translation tool, you'll also handle the edge case of *already-translated* text gracefully — a nice, small exercise in making a prompt more robust.

## What You'll Build

A script where you can:
1. Type in a sentence directly into the terminal (using Python's built-in `input()` function) instead of hardcoding it — this project introduces one new small thing over project 09: getting input while the script is running, instead of writing it into the code ahead of time.
2. Also type in a target language (e.g. `French`, `Japanese`, `Spanish`).
3. Get back just the translation — nothing else, no "Here is the translation:" preamble, no explanation.

## Step-by-Step Guide

1. Create `translate.py`. Set up the same `sys.path` bootstrap and imports as project 09 (`ChatPromptTemplate`, `get_chat_model`).

2. **Get input from the user at runtime.** Python's `input("Enter text to translate: ")` pauses your script, waits for the user to type something and press Enter, and returns what they typed as a string. Use it twice — once for the text, once for the target language:
   ```python
   text = input("Enter text to translate: ")
   language = input("Translate into which language? ")
   ```

3. **Build your prompt template.** This is the part worth spending real time on: your system message should be strict about the output format, something like *"You are a translator. Respond with ONLY the translation. No explanations, no quotation marks, no 'Here is the translation:' preamble."* Beginners often skip a strict system message and then get confused why the model adds extra commentary — write yours deliberately.

4. Your human message template needs **two** placeholders this time, not one: `{text}` and `{language}`. Something like: *"Translate the following into {language}:\n\n{text}"*.

5. Chain and invoke, same pattern as project 09, but now passing both values:
   ```python
   response = chain.invoke({"text": text, "language": language})
   ```

6. Print `response.content`.

7. Run it, and try it with a few different languages and sentence types (a question, a sentence with slang, a sentence with a proper noun) to see how it handles them.

## Example to Test Against

Try: text = `"Where is the nearest train station?"`, language = `"German"`. You should get back something like `"Wo ist der nächste Bahnhof?"` — just that, nothing else wrapped around it.

Also try translating text that's *already* in the target language (e.g. text = `"Bonjour"`, language = `"French"`) — a good prompt should recognize this and just return it unchanged (or note it's already in that language), rather than doing something strange.

## Common Mistakes

- **Not being strict enough in the system prompt**, then being surprised when the model adds "Sure, here's the translation:" before the actual translation. If this happens, that's your signal to go back and tighten the instruction — this is a real, common part of working with LLMs, not a sign you did something wrong in your code.
- **Confusing `input()` with `print()`** — `input()` is for *getting* text from the user (and it can optionally show a prompt message), `print()` is for *displaying* text. You need both, for different things, in this script.
- **Passing the wrong dict keys to `.invoke()`** — the keys you pass (`{"text": ..., "language": ...}`) must exactly match the `{placeholder}` names you used in the prompt template. A typo here causes a `KeyError`.

## Stretch Goals

- Loop: after printing one translation, ask if the user wants to translate something else, instead of the script just ending after one run.
- Detect the input language automatically and mention it in the output (e.g. "Detected: English → French").
- Support translating into *multiple* languages at once from a single input (e.g. a comma-separated list), printing each result labeled by language.

## Definition of Done

You can run the script, type in any sentence and any common language, and reliably get back just the translation with no extra commentary — tested with at least 3 different languages.

## Reference Modules

- [01 — LangChain Basics](../../modules/01_langchain_basics)
- [02 — Prompt Templates](../../modules/02_prompt_templates)
- [03 — Chains (LCEL)](../../modules/03_chains_lcel)
