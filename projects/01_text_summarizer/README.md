# Project 01 — Text Summarizer

**Difficulty:** Beginner — start here if you're new to Python or LangChain
**Domain:** Warm-up (general LangChain basics)
**Time estimate:** 1-2 hours

**Before you start:** Go through [module 00](../../modules/00_python_and_llm_basics), [01](../../modules/01_langchain_basics), and [02](../../modules/02_prompt_templates) first. Everything you need for this project is covered there — this project just asks you to put those pieces together yourself, with nobody handing you the finished code.

## The Problem

You paste in a paragraph (or a whole article) of text, and your program prints back a short summary — 2-3 sentences, no matter how long the original was.

## What You'll Build

A single Python script that:
1. Has a block of sample text written directly into the script as a Python string (a few paragraphs — copy any article or long paragraph you like, or use the example text below).
2. Sends that text to Claude with a prompt asking for a short summary.
3. Prints the summary to the screen.

That's the whole project. Don't add anything else until this works.

## Step-by-Step Guide

If you've never written a LangChain script from scratch before, follow these steps in order — each one builds on the last, and you should be able to run your script after every single step to see it doing a little more.

1. **Create a new file** at `projects/09_text_summarizer/summarize.py` (or anywhere you like — this repo's project folders don't need code in them, remember).

2. **Set up the same "find the repo" trick every module's `example.py` uses**, so you can import `common.model_factory`:
   ```python
   import sys
   from pathlib import Path
   sys.path.append(str(Path(__file__).resolve().parents[2]))
   ```
   (If you're putting your file somewhere else, adjust `parents[2]` — it needs to count how many folders up from your file the repo root is. If you're unsure, just hardcode the full path to the repo root instead; it doesn't need to be elegant for a first project.)

3. **Import what you need:**
   ```python
   from langchain_core.prompts import ChatPromptTemplate
   from common.model_factory import get_chat_model
   ```

4. **Write your sample text as a plain Python string variable**, e.g. `ARTICLE = "..."`. Use the example text at the bottom of this file, or paste in something you actually want summarized.

5. **Build a chat model**: `llm = get_chat_model()`. (Review module 01 if you're not sure what this returns.)

6. **Build a prompt template** using `ChatPromptTemplate.from_messages([...])` (module 02) with one `"human"` message containing a `{text}` placeholder, e.g. something like: *"Summarize the following text in 2-3 sentences:\n\n{text}"*. Don't overthink the wording yet — get something working first, improve it after.

7. **Chain the prompt to the model** with `|` (module 03): `chain = prompt | llm`.

8. **Call it**: `response = chain.invoke({"text": ARTICLE})`.

9. **Print the result**: `print(response.content)`.

10. **Run it**: `python projects/09_text_summarizer/summarize.py` (or wherever you put it, from the repo root, with `ANTHROPIC_API_KEY` set in `.env`).

If it prints a short, sensible summary of your text, you're done with the core project.

## Example to Test Against

```python
ARTICLE = """
The Wright brothers, Orville and Wilbur, were two American aviation pioneers
credited with inventing, building, and flying the world's first successful
motor-operated airplane. They made the first controlled, sustained flight of
a powered, heavier-than-air aircraft on December 17, 1903, four miles south
of Kitty Hawk, North Carolina. In 1904-05, the brothers developed their
flying machine into the first practical fixed-wing aircraft. Although not
the first to build experimental aircraft, the Wright brothers were the first
to invent aircraft controls that made fixed-wing powered flight possible.
"""
```
A good summary should mention who they were, roughly when/where the first flight happened, and why it mattered — in a couple of sentences, not a paragraph-by-paragraph rehash.

## Common Mistakes

- **Forgetting `.content`** — `response` from `.invoke()` is a whole message object, not a string. If you try to print it directly you'll get something like `AIMessage(content='...')` instead of clean text; you want `response.content`.
- **Putting `{text}` in the wrong message role** — the placeholder needs to be inside the message string itself, like `"human", "Summarize:\n\n{text}"`, not passed as a separate argument.
- **The `sys.path` trick not working** — if `from common.model_factory import get_chat_model` fails with `ModuleNotFoundError`, double check you're running the script from the repo root, and that `parents[N]` in your `sys.path.append` line correctly counts the folders between your script and the repo root.

## Stretch Goals

- Let the summary length be adjustable — accept a "short" (1 sentence) vs. "detailed" (paragraph) mode.
- Read the text from a file path given on the command line instead of a hardcoded string (`sys.argv[1]`, or the `argparse` module).
- Ask for the summary as bullet points instead of prose, and see how much the prompt wording changes the result.

## Definition of Done

Running your script prints a summary that's noticeably shorter than the original text, and actually captures the main point — read it yourself and confirm it's not missing anything important or making anything up.

## Reference Modules

- [00 — Python & LLM Basics](../../modules/00_python_and_llm_basics)
- [01 — LangChain Basics](../../modules/01_langchain_basics)
- [02 — Prompt Templates](../../modules/02_prompt_templates)
- [03 — Chains (LCEL)](../../modules/03_chains_lcel)
