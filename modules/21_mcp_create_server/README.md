# 21 — Create an MCP Server

## Theory

Building your first MCP server is easier than it sounds. The `FastMCP` class does most of the work: you write a normal Python function, add one line (`@mcp.tool()`) right above it, and it becomes something any MCP client can discover and call — no protocol code to write by hand.

- **`@mcp.tool()` turns a function into a tool.** LangChain's `@tool` decorator (from module 19) did something similar for local, in-process tools; this is the MCP version, for a function that's going to be served to other programs.
- **Your type hints and docstring do double duty.** They're not just documentation for other programmers anymore — `FastMCP` reads them automatically to tell any connecting client exactly what arguments the tool needs and what it does. That's why writing clear type hints and a clear docstring (module 00) actually matters here, not just as a nice habit.
- **This server uses the simplest connection method (stdio).** No network setup at all — a client just starts this script as a small program and talks to it directly.

## Use Case

The starting point for *any* MCP server: wrapping a handful of functions (a calculator, a lookup, an internal API call) so any MCP-compatible client can use them without custom integration code.

## How to Run

```bash
python modules/21_mcp_create_server/server.py       # starts and blocks, listening on stdin/stdout (Ctrl+C to stop)
python modules/21_mcp_create_server/solutions_client.py   # exercise solutions -- launches solutions_server.py itself
```
No API key needed (no LLM calls here, just the MCP protocol). You normally don't run `server.py` on its own for output — it's meant to be *launched* by a client as a subprocess, which is exactly what [module 22](../22_mcp_stdio_client)'s `client.py` and this module's `solutions_client.py` do automatically; running it directly just confirms it starts without error.

## Walkthrough

`server.py` defines a tiny "utilities" server with two tools: `get_weather(city)` (a canned/mocked response — no real API call, to keep the example dependency-free) and `word_count(text)`. Run it directly to confirm it starts (`python modules/21_mcp_create_server/server.py`); [module 22](../22_mcp_stdio_client) builds the client that actually talks to it.

## Using a different model

An MCP server doesn't know or care which LLM is calling it — this module has no model-specific code at all, which is the point of the protocol. See [module 26](../26_mcp_implement_client) for hooking this server up to a Claude-powered agent.

## Reference Docs

- FastMCP quickstart: https://modelcontextprotocol.io/quickstart/server
- Python SDK `FastMCP`: https://github.com/modelcontextprotocol/python-sdk#quickstart

## Exercises

1. Add a third tool, `to_uppercase(text: str) -> str`, and confirm it appears when a client lists tools.
2. Make `get_weather` raise a clear error for an empty city string, and check how that surfaces to a client.
3. Add a `units: str = "celsius"` optional parameter to `get_weather` and test both default and explicit values.
4. Read the generated tool schema (via a client's `list_tools()`, see module 22) and confirm it matches your function's type hints exactly.

**Solutions:** see [`solutions_server.py`](solutions_server.py) (the extended server) and [`solutions_client.py`](solutions_client.py) (a client that verifies all four exercises) in this folder. Run `python modules/21_mcp_create_server/solutions_client.py` -- it launches `solutions_server.py` automatically over stdio.
