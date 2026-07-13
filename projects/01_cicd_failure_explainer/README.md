# Project 01 — CI/CD Failure Explainer

**Domain:** DevOps automation
**Difficulty:** Beginner
**Time estimate:** 2-4 hours

## The Problem

A CI pipeline (GitHub Actions, GitLab CI, Jenkins, whatever you use) fails and dumps a wall of log text — stack traces, shell output, sometimes hundreds of lines. A developer has to scroll through all of it to figure out what actually broke. You're going to build a small tool that takes a raw CI log as input and produces a short, human-readable explanation of what failed, why, and what to try first.

## What You'll Build

A command-line script that:
1. Takes a path to a log file (or reads from stdin) containing a failed CI/CD run's output.
2. Sends it to Claude with a prompt engineered to extract the *actual* failure from the noise (most CI logs are 90% successful setup steps and 10% the actual error).
3. Outputs a structured result containing at minimum:
   - A one-line summary of what failed (e.g. "Unit test `test_login` failed due to a missing environment variable")
   - The likely root cause
   - 1-3 concrete suggested next steps
   - Whether this looks like a flaky/transient failure vs. a real code/config problem
4. Prints this nicely formatted to the console.

## Suggested Approach

1. Find or create a few sample failed CI logs to test against — pull a real failed run's log from a public GitHub repo's Actions tab (there are plenty of open-source projects with public CI history), or intentionally break something small and run it locally to capture the output. Get at least 3 different *kinds* of failures (e.g. a failing test, a dependency install error, a linting failure) so you're not overfitting your prompt to one log shape.
2. Long logs won't fit (or won't be worth putting) entirely into a prompt. Decide on a strategy: send the whole thing if it's short, or find a way to trim it (e.g. keep the last N lines, or specifically look for lines containing "error"/"failed"/"exception" plus some surrounding context) before sending it to Claude.
3. Design your Pydantic model for the structured output first (summary, root_cause, suggested_steps, is_flaky) — module 03 covers `.with_structured_output()`.
4. Write your prompt. Iterate on it against your 3+ sample logs until the summaries are actually useful and specific (not generic advice like "check your code").
5. Wire it up as a CLI script: `python explain_failure.py path/to/log.txt`.

## Tech You'll Need

- `argparse` or `sys.argv` for the CLI
- `common.model_factory.get_chat_model()` from this repo
- A Pydantic model + `.with_structured_output()`

## Stretch Goals

- Post the explanation as a comment on the relevant GitHub PR automatically, using the GitHub API (`gh` CLI or `requests` against the REST API) — this turns it from a manual tool into something that could run in CI itself.
- Handle multiple failures in one log (e.g. 3 different tests failed) and report on each separately.
- Add a "confidence" field and have the model flag when it's not sure what actually went wrong (rather than confidently guessing).
- Cache/skip re-analyzing a log you've already seen (hash the log content).

## Definition of Done

Running your script against each of your 3+ sample logs produces a summary that correctly identifies the actual failure (not just "something failed") and gives at least one genuinely actionable suggestion — check this by reading the full log yourself and confirming the summary matches reality.

## Reference Modules

- [02 — Prompt Templates](../../modules/02_prompt_templates) for structuring the extraction prompt
- [03 — Chains (LCEL)](../../modules/03_chains_lcel) for `.with_structured_output()`
