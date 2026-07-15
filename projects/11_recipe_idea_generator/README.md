# Project 11 — Recipe Idea Generator

**Domain:** Warm-up (general LangChain basics)
**Difficulty:** Beginner
**Time estimate:** 1-2 hours

**Before you start:** Complete [Project 10](../10_language_translator) first. This project introduces one genuinely new idea — turning a list of things into a nicely formatted piece of the prompt — on top of everything projects 09-10 already covered.

## The Problem

You type in a list of ingredients you have at home, and your program suggests a few recipes you could actually make with (mostly) just those ingredients.

## What You'll Build

A script that:
1. Asks the user to list the ingredients they have (comma-separated, e.g. `eggs, spinach, cheese, bread`).
2. Sends that list to Claude, asking for 2-3 recipe ideas that mostly use those ingredients (allowing a few common staples like salt, oil, water to be assumed available).
3. Prints each recipe idea with a short description and a rough list of steps.

## Step-by-Step Guide

1. Create `recipe_ideas.py` with the same bootstrap/imports pattern as the previous two projects.

2. Get the ingredient list from the user with `input(...)`, as one comma-separated string:
   ```python
   ingredients_input = input("What ingredients do you have? (comma-separated): ")
   ```

3. **Turn that single string into a cleaner list.** This is the new Python idea in this project: `.split(",")` breaks a string into a list wherever a comma appears. You'll likely also want `.strip()` on each item to remove extra spaces (someone might type `"eggs, spinach , cheese"` with inconsistent spacing). A list comprehension (module 00) is a clean way to do both at once:
   ```python
   ingredients = [item.strip() for item in ingredients_input.split(",")]
   ```
   Print `ingredients` and check it looks right (e.g. `['eggs', 'spinach', 'cheese', 'bread']`) before moving on — don't skip this check.

4. **Turn the list back into a readable string for the prompt.** Your prompt template needs one `{ingredients}` string to insert, not a Python list object. `", ".join(ingredients)` turns a list back into a comma-separated string (the reverse of step 3) — or, since you already have `ingredients_input`, you could just reuse that directly instead. Either is fine; understanding *why* both work is the point.

5. Build your prompt: something like *"I have these ingredients: {ingredients}. Suggest 2-3 simple recipes I could make using mostly these ingredients (a few basic staples like oil, salt, and water can be assumed). For each recipe, give a name, a one-sentence description, and 3-5 short steps."*

6. Chain, invoke, print — same pattern as the last two projects.

## Example to Test Against

Try: `eggs, spinach, cheese, bread`. You should get back a small handful of genuinely plausible recipes (an omelette, a grilled cheese with spinach, etc.) — not something requiring ingredients you didn't list, and not something wildly impractical.

Try a deliberately awkward/small list too, like just `rice, soy sauce` — see how the model handles having very little to work with; a good response should either suggest something genuinely doable with just those two (plus staples) or clearly say what else would help.

## Common Mistakes

- **Passing the raw comma-separated string with weird spacing straight into the prompt** without cleaning it up first — it usually still works because the model is forgiving, but doing the cleanup properly (step 3) is the actual Python practice this project is for.
- **Forgetting that `.split(",")` returns a list, not a string** — if you try to drop the list directly into an f-string or a `{ingredients}` template value without joining it back into a string first, you'll get something ugly like `['eggs', 'spinach']` printed literally inside your prompt. It'll still often work because the model can parse that too, but it's not clean, and it's worth understanding why.

## Stretch Goals

- Let the user also specify a cuisine preference (e.g. "Italian-style") or a dietary restriction (e.g. "vegetarian") as a second input, and work it into the prompt.
- Ask for a full ingredient list *for the recipe*, not just steps, so you can see exactly what (if anything) beyond your listed ingredients each suggestion needs.
- Rank the suggested recipes by how many of your listed ingredients they actually use, and print that count next to each one.

## Definition of Done

Given at least 3 different ingredient lists (including one deliberately short one), your script produces recipe suggestions that are genuinely makeable with what was listed (plus reasonable staples), and the steps are coherent enough that you could actually follow them.

## Reference Modules

- [00 — Python & LLM Basics](../../modules/00_python_and_llm_basics) (list comprehensions, string methods)
- [02 — Prompt Templates](../../modules/02_prompt_templates)
- [03 — Chains (LCEL)](../../modules/03_chains_lcel)
