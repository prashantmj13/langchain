# 25 — Implement a (Production-Style) MCP Server

## Theory

This module consolidates everything from the MCP track so far — tools ([21](../21_mcp_create_server)), HTTP transport ([23](../23_mcp_http_client)), resources & prompts ([24](../24_mcp_hosting_resources_prompts)) — into one server built the way you'd actually ship it:

- **Structured logging** — every tool call logs its arguments and outcome, so you can debug what an agent actually did in production.
- **Input validation & error handling** — tools raise clear, typed errors (via `ValueError`) for bad input instead of crashing the process; MCP surfaces these as tool errors the calling LLM can see and react to (e.g. retry with corrected arguments).
- **Multiple tools + a resource + a prompt in one server** — a "job board" server: a `search_jobs` tool (reusing the sample data pattern from [module 13](../13_job_search_helper)), a resource exposing a job posting by id, and a prompt template for drafting a cover letter.
- **HTTP transport** — served over `streamable-http`, since production servers are rarely something a single client subprocess-launches.

## Use Case

This is the shape of a real internal MCP server: several related tools/resources/prompts around one domain (here, job postings), with the logging and error handling you'd want before letting an LLM-driven agent call it unsupervised.

## How to Run

```bash
python modules/25_mcp_implement_server/server.py       # starts and blocks, serving HTTP on localhost:8100
python modules/25_mcp_implement_server/solutions_client.py   # exercise solutions -- self-contained, one command
```
`server.py` itself needs no API key (keyword-matching search). `solutions_server.py` (launched automatically by `solutions_client.py`, no server terminal needed) upgrades to real semantic search and therefore needs an embeddings key (`VOYAGE_API_KEY`). To exercise `server.py` directly, leave it running in one terminal and drive it from [module 26](../26_mcp_implement_client)'s client in a second.

## Walkthrough

`server.py`:
1. Loads the same sample job postings used in module 13.
2. Exposes `search_jobs(query: str, k: int = 3)` as a tool (keyword-based here, to keep the server dependency-light — swap in real embeddings if desired).
3. Exposes `job://{job_id}` as a resource returning the full posting text.
4. Exposes a `draft_cover_letter(job_id, candidate_name)` prompt template.
5. Logs every tool call (arguments + result summary) to stderr, and raises a clear `ValueError` for an unknown `job_id`.

Run it directly to confirm startup (`python modules/25_mcp_implement_server/server.py`); [module 26](../26_mcp_implement_client) is the client that drives it with a real Claude agent.

## Using a different model

No model-specific code in the server — same as the rest of the MCP track, the server is provider-agnostic by design.

## Reference Docs

- MCP server best practices: https://modelcontextprotocol.io/docs/concepts/server
- FastMCP full reference: https://github.com/modelcontextprotocol/python-sdk

## Exercises

1. Add a `logging.FileHandler` so tool-call logs persist to a file instead of only stderr.
2. Make `search_jobs` reuse `common.embedding_factory` for real semantic search instead of keyword matching, and compare result quality.
3. Add a `k` bounds check (e.g. reject `k > 10`) that raises `ValueError` with a message explaining the limit.
4. Add a second resource, `job://{job_id}/summary`, that returns just the first line (title) instead of the full posting.

**Solutions:** see [`solutions_server.py`](solutions_server.py) and [`solutions_client.py`](solutions_client.py) in this folder. Run `python modules/25_mcp_implement_server/solutions_client.py` -- it launches `solutions_server.py` automatically (over stdio, unlike the main `server.py`'s HTTP transport, so the whole demo runs in one process).
