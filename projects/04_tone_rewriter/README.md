# Project 04 — Message Tone Rewriter

**Difficulty:** Beginner
**Domain:** Warm-up (general LangChain basics)
**Time estimate:** 1-2 hours

**Before you start:** Complete [Project 03](../03_recipe_idea_generator) first. This project's new idea is letting the user pick from a fixed set of options and having your prompt behave differently depending on the choice — a small step toward more flexible tools.

## The Problem

You've written a blunt or awkward message (an email, a text, a Slack message) and want it rewritten in a specific tone — more formal, friendlier, more apologetic, more assertive — without changing what it actually says.

## What You'll Build

A script that:
1. Asks the user to paste in a message.
2. Asks the user to pick a target tone from a short, fixed menu (e.g. `formal`, `friendly`, `apologetic`, `assertive`).
3. Rewrites the message in that tone, keeping the original meaning intact, and prints the result.

## Step-by-Step Guide

1. Create `rewrite_tone.py` with the usual bootstrap/imports.

2. Get the message from the user. Since messages can be long and might span multiple lines, plain `input()` only reads one line — that's fine for this project (ask the user to paste it as a single line, or write it as one line without pressing Enter mid-message). If you want to support multi-line input as a stretch goal, see below.

3. **Show the user a fixed menu of tones and validate their choice.** This is the new idea in this project: don't just trust whatever the user types — check it against a known list.
   ```python
   valid_tones = ["formal", "friendly", "apologetic", "assertive"]
   tone = input(f"Choose a tone ({', '.join(valid_tones)}): ").strip().lower()
   if tone not in valid_tones:
       print(f"'{tone}' isn't one of the supported tones. Defaulting to 'formal'.")
       tone = "formal"
   ```
   This is a plain Python `if` check — no LangChain involved — but it's exactly the kind of input-validation habit that matters once you start building anything a real user (not just you) will type into.

4. Build your prompt. The key instruction to get right: the model should change *how* the message sounds, not *what* it says. Something like: *"Rewrite the following message in a {tone} tone. Keep the same meaning and all the same information — only change the wording and tone.\n\nOriginal message:\n{message}"*.

5. Chain, invoke with `{"tone": tone, "message": message}`, print `response.content`.

6. Test it with the same message across all four tones and compare the outputs side by side — this is the fun part of this project, seeing how differently the same content can be presented.

## Example to Test Against

Try this blunt message: `"I need the report by Friday. Don't be late again like last time."`

- **formal** should read like something you'd actually send in a professional context, dropping the "like last time" jab but keeping the deadline and the underlying expectation.
- **friendly** should soften it while still communicating the deadline clearly.
- **apologetic** is a good stress test — ask yourself whether the rewritten version still makes sense as something *you'd* send, or whether the model over-corrected into something that no longer matches the original intent.

## Common Mistakes

- **A vague prompt that lets the model change the actual content**, not just the tone — e.g. it might drop the deadline entirely instead of just softening how it's mentioned. If you notice this happening, that's a sign to make your prompt more explicit about what must stay the same.
- **Not lowercasing/stripping the user's tone input** before comparing it to your `valid_tones` list — `"Formal"` (capital F) won't match `"formal"` in a plain `in` check, which is why `.strip().lower()` matters in step 3.
- **Testing with only one message** — try at least 2-3 different original messages of different lengths/subjects before deciding your prompt works well.

## Stretch Goals

- Support multi-line input: instead of `input()`, keep calling it in a loop and collecting lines until the user types a blank line or a specific "done" marker, joining them into one multi-line message.
- Add a tone not in the original list (e.g. `"concise"` or `"enthusiastic"`) and see how well your prompt generalizes without you needing to change anything but the menu.
- Show the original and rewritten message side by side (or as a diff) instead of just printing the new version, so it's easier to compare what actually changed.

## Definition of Done

Given the same original message rewritten in each of the 4 tones, all 4 outputs preserve the original's actual content/facts while genuinely sounding different from each other — verified by reading all 4 side by side yourself.

## Reference Modules

- [02 — Prompt Templates](../../modules/02_prompt_templates)
- [03 — Chains (LCEL)](../../modules/03_chains_lcel)
