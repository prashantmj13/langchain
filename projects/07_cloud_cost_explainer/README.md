# Project 07 — Cloud Cost Explainer

**Difficulty:** Beginner
**Domain:** Cloud automation
**Time estimate:** 3-5 hours

## The Problem

Cloud bills are a table of numbers nobody enjoys reading: service names, daily costs, region breakdowns. "Why did our bill go up 40% this month?" is a question that takes a human 20 minutes of spreadsheet-squinting to answer. You're going to build a tool that takes cost/usage data and produces a plain-English summary of what's driving spend and what changed.

You do **not** need a real cloud account for this project — a CSV export of cost data (real or synthetic) is enough. If you do have access to AWS/GCP/Azure billing data, even better, but it's optional.

## What You'll Build

A script that:
1. Loads a cost dataset — a CSV with columns like `date, service, region, cost` (make one up with a spreadsheet if you don't have a real export; include at least one obvious anomaly, like one service's cost tripling on a specific date, so you can verify your tool catches it).
2. Computes basic aggregates in plain Python/pandas first (total by service, week-over-week change, biggest movers) — do **not** ask the LLM to do arithmetic on a big table, models are unreliable at that; you compute the numbers, then ask the model to *explain* them.
3. Hands those computed aggregates to Claude and asks for a written summary: what's driving the total, what changed significantly, and (if there's an obvious anomaly) a guess at what could explain it.
4. Outputs a short report — plain text or Markdown is fine.

## Suggested Approach

1. Get comfortable with the data first, in plain Python, with no LLM involved: load the CSV, group by service, compute totals and percent changes. Print these numbers and sanity-check them by hand before writing a single prompt.
2. Design the prompt so the model receives *already-computed* numbers as input (e.g. a small table or a JSON blob of "service: total, % change from last period"), not raw transaction-level data — the model's job here is narration, not calculation.
3. Ask for a structured response (module 03): a one-paragraph executive summary, plus a list of "notable changes" each with a service name, the change, and a plausible explanation.
4. Test it against a dataset where you know the answer (you planted the anomaly), and confirm the model actually calls it out rather than glossing over it in generic language.

## Tech You'll Need

- `pandas` for loading and aggregating the CSV (or plain `csv` + dicts if you'd rather avoid the dependency)
- A Pydantic model + `.with_structured_output()` for the report shape
- If going for the AWS stretch goal: `boto3` and the Cost Explorer API

## Stretch Goals

- Pull real data from the AWS Cost Explorer API (or GCP's Cloud Billing API) instead of a CSV.
- Turn it into a scheduled report: run weekly, compare to the previous week automatically, and only send a notification (email/Slack) if the change exceeds some threshold — so you're not re-reading the same "nothing changed" report every week.
- Add a "forecast" section: given the trend so far this month, project the end-of-month total.
- Group by tag (team/project) instead of just service, if your data has that level of detail, so you can answer "which team's spend grew the most."

## Definition of Done

Given your test dataset with a planted anomaly, running the tool produces a report that (a) states the correct total and (b) explicitly calls out the anomaly with a specific, plausible explanation — not a vague "costs fluctuated."

## Reference Modules

- [02 — Prompt Templates](../../modules/02_prompt_templates)
- [03 — Chains (LCEL)](../../modules/03_chains_lcel) for structured output
