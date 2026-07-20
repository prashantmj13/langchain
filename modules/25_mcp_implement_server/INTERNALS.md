# Module 25 — Internals

`FastMCP`, `@mcp.tool()`, `@mcp.resource()`, and `@mcp.prompt()` are covered in [module 21's](../21_mcp_create_server/INTERNALS.md) and [module 24's](../24_mcp_hosting_resources_prompts/INTERNALS.md) INTERNALS.md pages. This page covers the one genuinely new mechanism this module relies on: how a Python exception inside a tool becomes a structured error the client (and the LLM behind it) can actually see.

## How `raise ValueError(...)` becomes a client-visible error, not a crash

**How it works internally:**
1. When a client calls `call_tool("search_jobs", {"k": 999})`, the MCP SDK's server-side dispatch logic calls your Python function (`search_jobs`) inside a `try`/`except` block it wraps around every tool invocation — this wrapping is the SDK's responsibility, not something `@mcp.tool()` requires you to write yourself.
2. If your function raises any exception (here, `ValueError("k must be <= 10")`), the SDK catches it, and instead of letting the exception propagate and kill the server process, it packages the exception's message into a proper MCP **tool error response** — a normal, well-formed JSON-RPC response, just one flagged as representing an error rather than a success.
3. That error response travels back to the client exactly like a successful response would — the client's `call_tool()` doesn't raise its own Python exception for this (worth confirming yourself, see below); instead, the returned `CallToolResult` object has `.isError` set to `True`, with your error message available in `.content`.
4. If an *agent* (module 26) is the one calling the tool, the LLM sees this error result as part of the conversation, just like it sees a successful result — which is exactly why a well-worded error message matters: it's not just for a human reading logs, it's input the model itself can reason about and potentially recover from (e.g. retrying with a corrected `k` value).

**Real source:** The error-wrapping logic lives in [`mcp/server/fastmcp/server.py`](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/server.py) and `mcp/server/lowlevel/server.py` — look for where tool calls are dispatched and wrapped.

**How to validate this behavior directly:**
```python
result = await session.call_tool("search_jobs", {"query": "engineer", "k": 999})
print(result.isError)        # True -- confirms it's flagged as an error, not a crash
print(result.content[0].text)  # "k must be <= 10" -- your original ValueError message, intact

# Confirm the server process itself is still alive and usable after the error:
healthy_result = await session.call_tool("search_jobs", {"query": "engineer", "k": 2})
print(healthy_result.isError)  # False -- the server kept running fine after the earlier error
```
