# Projects — build these yourself

The `modules/` side of this repo teaches one concept at a time, with worked examples and solutions. These projects are the opposite: each one is a **problem brief**, not code. You get a scenario, requirements, a suggested approach, and a definition of done — you write every line yourself. That's on purpose: reading a solution teaches you what the author knows; building something from a spec teaches you what *you* know (and don't, yet).

## How to use these

1. Read the whole brief before writing any code — especially "Suggested Approach," which is deliberately high-level (steps, not code) so you still have to make real design decisions.
2. Skim the "Reference Modules" links first if a technique is unfamiliar (e.g. you've never done structured output or vision before) — go read that module's theory and example, then come back and apply it here.
3. Build the smallest version that satisfies "Definition of Done" before attempting the stretch goals. A working, boring version beats a half-finished ambitious one.
4. There is no `solutions.py` for these, deliberately. If you get stuck, re-read the relevant module(s) or ask an LLM to explain a *concept* you're missing — try not to ask it to write the project for you.

## Prerequisites

All eight projects assume you've been through at least modules 00-03 (Python/LLM basics, prompt templates, chains). Beyond that, each project lists which specific modules it draws on.

## The projects

| # | Project | Domain | Difficulty | Draws on |
|---|---------|--------|------------|----------|
| 01 | [CI/CD Failure Explainer](01_cicd_failure_explainer) | DevOps automation | Beginner | Prompts, structured output |
| 02 | [Natural-Language Ops Assistant](02_natural_language_ops_assistant) | DevOps automation | Advanced | Agents, MCP |
| 03 | [Cloud Cost Explainer](03_cloud_cost_explainer) | Cloud automation | Beginner | Prompts, structured output |
| 04 | [Infrastructure-as-Code Change Reviewer](04_iac_change_reviewer) | Cloud automation | Intermediate | Structured output, chains |
| 05 | [Receipt & Invoice Extractor](05_receipt_invoice_extractor) | Image processing | Beginner | Vision, structured output |
| 06 | [Screenshot Bug Reporter](06_screenshot_bug_reporter) | Image processing | Intermediate | Vision, structured output |
| 07 | [PDF Knowledge Base Assistant](07_pdf_knowledge_base_assistant) | PDF processing | Intermediate | RAG, retrieval, chat history |
| 08 | [Contract Diff & Risk Reviewer](08_contract_diff_reviewer) | PDF processing | Advanced | RAG, structured output, chains |

Each domain has one easier, more contained project and one harder, more open-ended one — do the easier one first if the domain is new to you.
