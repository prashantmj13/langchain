# Project 13 — Contract Diff & Risk Reviewer

**Difficulty:** Expert
**Domain:** PDF processing
**Time estimate:** 6-10 hours

## The Problem

When a contract (or terms of service, or a policy document) comes back from the other party with "just a few small changes," finding out what actually changed — and whether any of it is meaningfully risky — usually means a slow side-by-side read. You're going to build a tool that takes two versions of the same PDF document, identifies what actually changed between them, and flags anything that looks like it shifts risk or obligations, explained in plain language.

## What You'll Build

A script that:
1. Takes two PDF file paths — an "original" and a "revised" version of the same document (use two versions of any real document you have, or find a public one — e.g. an open-source project's terms of service from two different points via web.archive.org, or write your own toy contract and make deliberate edits to a copy).
2. Extracts and roughly aligns the two documents by section/clause (this is the hard, interesting part of the project — see below).
3. For each section that changed, produces: what changed (a plain-language description, not just a text diff), and whether it looks like it favors one party more than the original did.
4. Produces an overall summary: total number of changes, how many look substantive vs. cosmetic (e.g. rewording without changing meaning), and a list of the most important ones to review first.

## Suggested Approach

1. This project is meaningfully harder than a plain-text diff because contract sections can be reordered, renumbered, or reworded without changing meaning — a naive line-by-line diff will report huge amounts of noise. Think about your alignment strategy before writing code: one reasonable approach is to split each document into sections/clauses (by heading detection, or just by paragraph if the document has no clear structure), embed each section (modules 09-12), and match each section in the revised document to its most similar counterpart in the original — genuinely new sections won't have a good match, which is itself a signal.
2. Once you have matched pairs of "this section in v1 corresponds to this section in v2," a plain Python text diff (the `difflib` module in the standard library) between the two can help you see what changed at the character level — but don't stop there, since a difflib diff of legal text is unreadable. Feed the before/after pair to Claude and ask it to describe the change in plain language and assess whether it's substantive.
3. For unmatched sections (things that appear in the revised doc with no good match in the original, or vice versa), report them separately as "added" or "removed" sections rather than trying to force a comparison.
4. Design your structured output per changed section: section identifier, change_type (added/removed/modified/reworded-only), plain_language_summary, and a risk_shift assessment (e.g. "no meaningful change" / "favors the other party" / "favors us" / "unclear, needs legal review" — pick categories that make sense for your document).
5. Build the overall summary as a final pass over all the per-section results, not a separate independent analysis — you want it grounded in what was actually found, not a fresh guess.

## Tech You'll Need

- `pypdf` for text extraction
- An embeddings provider (module 10) for section matching
- `difflib` (Python standard library) as a helper input into your prompts, not as the final output
- A Pydantic model + `.with_structured_output()` for the per-section and summary results

## Stretch Goals

- Generate an actual redlined document (or at least a Markdown file with strikethrough/additions marked) instead of just a structured list — much closer to how a lawyer would actually want to review this.
- Handle more than two versions — track changes across a whole revision history of a document.
- Add a configurable "risk policy" (similar to project 04's stretch goal) describing what your organization specifically cares about (e.g. "always flag any change to indemnification or liability clauses"), so the risk assessment reflects your actual priorities rather than generic legal judgment.
- Test your section-matching approach on a document with sections deliberately reordered between versions, and confirm it still matches them correctly instead of reporting every section as "removed and re-added."

## Definition of Done

Given two versions of a test document where you know exactly what you changed (because you made the edits yourself), your tool correctly identifies every substantive change you made, doesn't report unchanged sections as changed, and produces plain-language descriptions that accurately reflect what actually changed — verified by comparing the tool's output against your own edit log.

## Reference Modules

- [09 — Embeddings Theory](../../modules/09_embeddings_theory) through [12 — Vector Stores](../../modules/12_vector_stores) for section matching
- [16 — RAG](../../modules/16_rag) for the overall load/split/analyze pattern
- [03 — Chains (LCEL)](../../modules/03_chains_lcel) for structured output
