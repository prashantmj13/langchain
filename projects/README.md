# Projects — build these yourself

The `modules/` side of this repo teaches one concept at a time, with worked examples and solutions. These projects are the opposite: each one is a **problem brief**, not code. You get a scenario, requirements, a suggested approach, and a definition of done — you write every line yourself. That's on purpose: reading a solution teaches you what the author knows; building something from a spec teaches you what *you* know (and don't, yet).

All 13 projects are ordered **beginner → intermediate → expert** — do them roughly in this order, especially projects 01-05, which explicitly build on each other.

## How to use these

1. Read the whole brief before writing any code — especially "Suggested Approach" (or the step-by-step guide in projects 01-05), which is deliberately high-level so you still have to make real design decisions.
2. Skim the "Reference Modules" links first if a technique is unfamiliar (e.g. you've never done structured output or vision before) — go read that module's theory and example, then come back and apply it here.
3. Build the smallest version that satisfies "Definition of Done" before attempting the stretch goals. A working, boring version beats a half-finished ambitious one.
4. There is no `solutions.py` for these, deliberately. If you get stuck, re-read the relevant module(s) or ask an LLM to explain a *concept* you're missing — try not to ask it to write the project for you.

## Prerequisites

All 13 projects assume you've been through at least modules 00-03 (Python/LLM basics, prompt templates, chains). Beyond that, each project lists which specific modules it draws on.

**Brand new to Python or LangChain?** Projects 01-05 are your on-ramp — small, need no external accounts or services beyond an Anthropic API key, and their instructions spell out every step explicitly, including exact class/function names to use and common mistakes to watch for. Do them in order (each one is written assuming you just finished the one before it). Once you're comfortable building a `prompt | llm` chain without thinking hard about it, move on to the Beginner-domain projects (06-08), then Intermediate (09-11), then Expert (12-13).

## Beginner

| # | Project | Domain | Time | Draws on |
|---|---------|--------|------|----------|
| 01 | [Text Summarizer](01_text_summarizer) | Warm-up | 1-2h | Your first chain, start to finish |
| 02 | [Language Translator](02_language_translator) | Warm-up | 1-2h | Getting input from the user at runtime |
| 03 | [Recipe Idea Generator](03_recipe_idea_generator) | Warm-up | 1-2h | Turning user input into a list, and back into a string |
| 04 | [Message Tone Rewriter](04_tone_rewriter) | Warm-up | 1-2h | Validating a user's choice against a fixed menu |
| 05 | [FAQ Chatbot with Memory](05_faq_chatbot_with_memory) | Warm-up | 2-3h | A real chat loop, with conversation memory |
| 06 | [CI/CD Failure Explainer](06_cicd_failure_explainer) | DevOps automation | 2-4h | Prompts, structured output |
| 07 | [Cloud Cost Explainer](07_cloud_cost_explainer) | Cloud automation | 3-5h | Prompts, structured output |
| 08 | [Receipt & Invoice Extractor](08_receipt_invoice_extractor) | Image processing | 3-5h | Vision, structured output |

Projects 01-05 are a tighter-knit sequence than 06-08 — each explicitly builds on the last and includes a full step-by-step guide. 06-08 are still beginner-difficulty but each stands alone, one per domain, with less hand-holding in "Suggested Approach."

## Intermediate

| # | Project | Domain | Time | Draws on |
|---|---------|--------|------|----------|
| 09 | [Infrastructure-as-Code Change Reviewer](09_iac_change_reviewer) | Cloud automation | 4-6h | Structured output, chains |
| 10 | [Screenshot Bug Reporter](10_screenshot_bug_reporter) | Image processing | 4-6h | Vision, structured output |
| 11 | [PDF Knowledge Base Assistant](11_pdf_knowledge_base_assistant) | PDF processing | 5-8h | RAG, retrieval, chat history |

## Expert

| # | Project | Domain | Time | Draws on |
|---|---------|--------|------|----------|
| 12 | [Natural-Language Ops Assistant](12_natural_language_ops_assistant) | DevOps automation | 6-10h | Agents, MCP |
| 13 | [Contract Diff & Risk Reviewer](13_contract_diff_reviewer) | PDF processing | 6-10h | RAG, structured output, chains |

These are the most open-ended briefs in the repo — real-world messiness (parsing inconsistent input, aligning mismatched document sections, safety constraints on agent tools) that you're expected to design a solution for yourself, not just fill in a template.
