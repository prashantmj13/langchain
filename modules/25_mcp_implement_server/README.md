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

## Classes & Methods Used

`FastMCP`, `@mcp.tool()`, `@mcp.resource()`, and `@mcp.prompt()` are the same building blocks from modules 21/24 — this module's point is combining all of them, plus:

| API | What It Does | Why We Use It Here |
|---|---|---|
| `logging.basicConfig(...)` / `logger.info(...)` / `logger.warning(...)` (Python standard library, not MCP-specific) | Sets up structured, timestamped log output and writes log lines. | Used so every `search_jobs` call and every failed lookup gets a record you can look back at — the "production-style" part of this module. |
| `raise ValueError(...)` inside a tool/resource function | Standard Python error signaling. | Used for bad input (an unknown `job_id`, an out-of-range `k`) — the MCP SDK turns this into a proper error response the calling client (and the LLM behind it) can see and react to, instead of the server crashing. |
| `mcp.run(transport="streamable-http")` | Same as module 23 — starts the server on an HTTP port instead of stdio. | Used because a "production-style" server is expected to run independently and be reachable by more than one client, not be spawned per-client like module 21's stdio server. |

## Using a different model

No model-specific code in the server — same as the rest of the MCP track, the server is provider-agnostic by design.

## Reference Docs

- MCP server best practices: https://modelcontextprotocol.io/docs/concepts/server
- FastMCP full reference: https://github.com/modelcontextprotocol/python-sdk

## Exercises

1. **Making logs persist across restarts.** `server.py`'s `logging.basicConfig(..., stream=sys.stderr)` only prints logs to the terminal — they're gone once the terminal scrolls past or the process exits. Add a `logging.FileHandler("server.log")` alongside the existing stderr output (`logger.addHandler(logging.FileHandler(...))`), call `search_jobs` a few times, and confirm `server.log` on disk actually contains those calls.
2. **Upgrading from keyword matching to real semantic search.** `search_jobs` currently ranks by counting overlapping words — it'll miss a query like "someone good with LLMs" against a posting that says "large language models" but never says "LLM". Rewrite it to embed the query and each job posting with `common.embedding_factory.get_embeddings()` (module 09-13's pattern) and rank by cosine similarity instead. Compare results on a query with no literal word overlap with the right posting.
3. **Rejecting an unreasonable `k` before doing any work.** Add a check at the top of `search_jobs`: if `k > 10`, `raise ValueError("k must be <= 10")` before any searching happens. Call it with `k=50` from a client and confirm you get a clear error back instead of the tool silently doing something unexpected.
4. **A resource returning less than the full data.** Following `get_job_posting`'s pattern, add a second resource registered at `job://{job_id}/summary` whose function returns just `_JOBS[job_id].splitlines()[0]` (the title line) instead of the whole posting. From a client, fetch both `job://ml_engineer` and `job://ml_engineer/summary` and confirm the second is meaningfully shorter.

**Solutions:** see [`solutions_server.py`](solutions_server.py) and [`solutions_client.py`](solutions_client.py) in this folder. Run `python modules/25_mcp_implement_server/solutions_client.py` -- it launches `solutions_server.py` automatically (over stdio, unlike the main `server.py`'s HTTP transport, so the whole demo runs in one process).
