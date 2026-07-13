# 25 — Implement a (Production-Style) MCP Server

## Theory

This module doesn't introduce anything new — it just takes everything from the MCP modules so far (tools, resources, prompts, running over HTTP) and combines them into one server built the way you'd actually want to run it for real, not just as a teaching example:

- **Keeping a record of what happened.** Every time a tool is called, the server writes down what it was asked to do and what it returned — so if something goes wrong later, you can look back and see exactly what the agent did.
- **Catching bad input cleanly instead of crashing.** If a tool is asked to do something invalid (like search with an empty question), it reports a clear error message instead of crashing the whole server — and the model on the other end can actually see that error and try again with better input.
- **One server, several related capabilities.** This is a small "job board" server that offers a tool to search job postings, a resource to look up one specific posting, and a prompt to help draft a cover letter — all living together since they're all about the same thing (job postings).

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
