# Project 09 — Infrastructure-as-Code Change Reviewer

**Difficulty:** Intermediate
**Domain:** Cloud automation
**Time estimate:** 4-6 hours

## The Problem

A `terraform plan` (or a CloudFormation diff, or a Pulumi preview) tells you exactly what's about to change in your infrastructure — but it's dense, mechanical output that's easy to skim past. Someone approves a PR without noticing that a security group is about to open to `0.0.0.0/0`, or that a database is about to be replaced (meaning: destroyed and recreated) instead of updated in place. You're going to build a tool that reviews infrastructure change output and flags anything risky in plain language, the way a careful senior engineer would in a PR review.

## What You'll Build

A script that:
1. Takes a `terraform plan` output (or equivalent) as input — either piped in, or read from a saved text file.
2. Parses out the individual resource changes (Terraform's plan output has a fairly consistent structure: `+ create`, `- destroy`, `~ update in-place`, `-/+ replace`).
3. Sends the changes to Claude with instructions to review for risk — specifically watching for: resources being destroyed/replaced (data loss risk), security groups/firewall rules being opened up, IAM permissions being widened, and anything else that looks unusual.
4. Produces a structured review: overall risk level (low/medium/high), and a list of specific concerns, each tied to the specific resource/line that triggered it.

## Suggested Approach

1. Generate real plan output to test against. If you don't have a cloud account to run real Terraform against, you can still get realistic plan output by writing a small `.tf` file describing a few fake resources and running `terraform plan` locally (it'll fail to actually apply without real credentials, but `plan` output for well-known providers is often generatable, or you can hand-write realistic-looking sample plan text — the important thing is the shape of the input your prompt needs to handle). Include a mix of safe changes (e.g. a tag update) and risky ones (e.g. a security group rule change, a resource replacement) in your test samples.
2. Decide how much preprocessing to do yourself vs. leaving to the model. At minimum, isolate the "resource change" blocks from the plan's surrounding noise before sending it to Claude — don't make the model hunt through hundreds of lines of Terraform's verbose formatting.
3. Write your risk criteria explicitly into the prompt (don't assume the model will independently invent your organization's risk policy) — e.g. "flag any change that: destroys or replaces a resource, widens a security group / firewall rule, widens IAM permissions, or removes an encryption/backup setting."
4. Design your structured output (module 03) with a risk level enum and a list of concern objects (resource name, concern description, severity).
5. Test against your safe-vs-risky sample plans and confirm the safe one gets a low risk rating and the risky one gets flagged specifically (not just "this plan has changes, be careful").

## Tech You'll Need

- Terraform CLI (optional — only needed if you want to generate real plan output rather than hand-crafting sample text)
- A Pydantic model + `.with_structured_output()` for the risk report

## Stretch Goals

- Wire this into a GitHub Action that runs on every PR touching `.tf` files, posting the review as a PR comment automatically.
- Support CloudFormation change sets or Pulumi previews as additional input formats, not just Terraform.
- Add a policy file (a simple YAML/JSON list of "things to always flag") that you can edit without touching the prompt — separating your organization's specific risk policy from the tool's code.
- Have it check the change against a previous review to see if a previously-flagged risk was addressed or ignored.

## Definition of Done

Given a plan with at least one genuinely risky change and at least one harmless change, your tool correctly assigns a higher risk level to the risky plan and names the specific resource/reason for the concern — verified by you reading the raw plan and confirming the tool's assessment matches reality.

## Reference Modules

- [03 — Chains (LCEL)](../../modules/03_chains_lcel) for structured output
- [02 — Prompt Templates](../../modules/02_prompt_templates)
