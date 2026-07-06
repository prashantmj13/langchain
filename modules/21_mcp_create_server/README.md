# 21 — Create an MCP Server

## Theory

The Python MCP SDK's `FastMCP` class is the fast path to a working server: decorate a function with `@mcp.tool()` and it's automatically exposed, with its type hints and docstring turned into the tool's schema/description for the model to read. `mcp.run(transport="stdio")` starts the server listening on stdin/stdout — the simplest possible transport, since the client just launches this script as a subprocess.

- **`@mcp.tool()`** — registers a function as a callable tool; argument types and the docstring become what the LLM sees when deciding whether/how to call it.
- **Type hints matter** — `def get_weather(city: str) -> str` gives the client enough schema to validate arguments before ever calling your code.
- **stdio transport** — no ports, no networking; the server's lifecycle is tied to the client process that spawned it.

## Use Case

The starting point for *any* MCP server: wrapping a handful of functions (a calculator, a lookup, an internal API call) so any MCP-compatible client can use them without custom integration code.

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
