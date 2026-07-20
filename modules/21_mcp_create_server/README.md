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

## Classes & Methods Used

These are from the `mcp` Python SDK (Anthropic's protocol library), not LangChain itself — MCP is a separate, LangChain-independent standard, which is exactly why it works the same regardless of what LLM framework ends up calling it.

| API | What It Does | Why We Use It Here |
|---|---|---|
| `FastMCP("utilities-server")` | Creates a new MCP server object with the given name. | The starting point for any server built with this SDK — everything else (tools, resources, prompts) gets registered onto this object. |
| `@mcp.tool()` | Registers the decorated function as a tool the server exposes, reading its type hints and docstring to build the schema a client will see. | Applied to `get_weather` and `word_count` so any MCP client can discover and call them — the MCP equivalent of LangChain's `@tool` from module 19. |
| `mcp.run(transport="stdio")` | Starts the server, listening for a client on stdin/stdout. | Used to actually launch the server process — `transport="stdio"` picks the simplest connection method (module 20's Theory covers the alternative, HTTP). |

For how `FastMCP` and `@mcp.tool()` actually work internally (the JSON-RPC event loop, the tool registry) — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

An MCP server doesn't know or care which LLM is calling it — this module has no model-specific code at all, which is the point of the protocol. See [module 26](../26_mcp_implement_client) for hooking this server up to a Claude-powered agent.

## Reference Docs

- FastMCP quickstart: https://modelcontextprotocol.io/quickstart/server
- Python SDK `FastMCP`: https://github.com/modelcontextprotocol/python-sdk#quickstart

## Exercises

You'll need a client to actually test these against — either write a small one following [module 22](../22_mcp_stdio_client)'s pattern, or just use `solutions_client.py` in this folder as a reference while you build your own version of `server.py`.

1. **Adding a 3rd tool from scratch.** Following `get_weather`/`word_count`'s pattern exactly (a type-hinted function with a docstring, decorated with `@mcp.tool()`), add `to_uppercase(text: str) -> str` that returns `text.upper()`. Connect a client and call `list_tools()` — confirm your new tool shows up alongside the original two, with a description pulled from your docstring.
2. **Making bad input fail clearly instead of silently.** Modify `get_weather` so that if `city` is an empty string, it `raise`s a `ValueError` with a clear message (e.g. `"city must not be empty."`) instead of trying to look it up. Call it from a client with `{"city": ""}` and observe how the error surfaces on the client side — is it a crash, or a structured error response?
3. **An optional parameter with a default value.** Add `units: str = "celsius"` as a second parameter to `get_weather`, and use it to pick between two hardcoded values per city (e.g. store both a celsius and fahrenheit reading). Call the tool twice from a client — once with just `{"city": "Tokyo"}` (relying on the default) and once with `{"city": "Tokyo", "units": "fahrenheit"}` — and confirm you get different results.
4. **Reading the schema the server actually generated.** From a client, call `list_tools()` and print `tool.inputSchema` (as JSON, e.g. with `json.dumps(tool.inputSchema, indent=2)`) for `get_weather`. Compare it line-by-line against your function's actual type hints — this is exactly what `FastMCP` builds automatically from your Python code, and it's worth seeing once so you trust it's really doing that.

**Solutions:** see [`solutions_server.py`](solutions_server.py) (the extended server) and [`solutions_client.py`](solutions_client.py) (a client that verifies all four exercises) in this folder. Run `python modules/21_mcp_create_server/solutions_client.py` -- it launches `solutions_server.py` automatically over stdio.
