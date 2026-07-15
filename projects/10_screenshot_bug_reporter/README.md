# Project 10 — Screenshot Bug Reporter

**Difficulty:** Intermediate
**Domain:** Image processing
**Time estimate:** 4-6 hours

## The Problem

Filing a good bug report from a screenshot takes more effort than most people put in — "the button doesn't work" is not a report anyone can act on. You're going to build a tool that takes a screenshot plus a short note from the person who found the bug, and turns it into a properly structured bug report: a clear title, what's visible in the screenshot, steps to reproduce (as best they can be inferred), expected vs. actual behavior, and a suggested severity.

## What You'll Build

A script that:
1. Takes an image path (a screenshot) and a short free-text note (e.g. "checkout button does nothing when clicked").
2. Sends both to Claude, asking it to look at the screenshot and combine what it sees with the note to produce a structured bug report.
3. Outputs the report in a format ready to paste into an issue tracker: title, description, steps to reproduce, expected result, actual result, severity, and a list of any visible error messages/UI details worth noting.

## Suggested Approach

1. Collect test screenshots. You don't need real bugs — take screenshots of any website or app and imagine a plausible issue with each one (a form, a broken layout, an error message, a misaligned button). Write a one-line note for each, the way a real user might phrase it casually.
2. Build the multimodal message per module 18: image + your note, both in the same `HumanMessage`.
3. Think carefully about what the model can and can't reasonably infer. It can describe what's visible in the screenshot; it generally *can't* know your app's expected behavior unless you tell it, or unless it's obvious (e.g. a stack trace visibly printed on screen is clearly not expected behavior). Write your prompt to be honest about this — have the model note when it's inferring vs. when something is directly evidenced by the screenshot.
4. Design structured output (module 03) with fields for title, description, steps_to_reproduce (list), expected_result, actual_result, severity (enum: low/medium/high/critical), and visible_errors (list of any error text visible in the image).
5. Test against your sample screenshots and check whether the severity ratings feel reasonable — a visibly broken checkout flow should rate higher than a minor visual misalignment.

## Tech You'll Need

- Screenshots (your own OS's screenshot tool is enough)
- A Pydantic model + `.with_structured_output()`
- Pillow for any image resizing needed

## Stretch Goals

- Accept a short screen recording (as a sequence of frames) instead of just one screenshot, to capture bugs that only show up as a *sequence* of actions (e.g. "click X, then Y, then it breaks").
- Auto-file the generated report into a real issue tracker via its API (GitHub Issues, Jira, Linear) instead of just printing it.
- Detect duplicate bug reports: compare a new screenshot/report against previously-filed ones (using embeddings on the generated descriptions, module 09-12) and flag likely duplicates before filing.
- Add before/after screenshot comparison: given two screenshots (expected design vs. actual rendering), have the model describe the specific visual differences.

## Definition of Done

Given at least 4 different screenshot + note pairs, your tool produces bug reports where the "actual result" and any visible error details genuinely match what's in the screenshot (not hallucinated details), and the steps to reproduce are a reasonable reconstruction of what likely happened.

## Reference Modules

- [18 — Image Processing](../../modules/18_image_processing)
- [03 — Chains (LCEL)](../../modules/03_chains_lcel) for structured output
