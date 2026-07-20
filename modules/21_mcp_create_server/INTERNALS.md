# Module 21 — Internals

## `FastMCP`

**What it is:** The Python MCP SDK's high-level server class — a thin, decorator-driven layer on top of the lower-level MCP protocol implementation, the same relationship `FastAPI` has to raw ASGI, if you've seen that before.

**How it works internally:**
1. `FastMCP("utilities-server")` creates a server object holding empty registries for tools, resources, and prompts, plus the server's name (which is what identifies it to a connecting client during the handshake).
2. `mcp.run(transport="stdio")` starts an event loop that reads JSON-RPC 2.0 messages (MCP's actual wire protocol — a standard for structured request/response messages, not something MCP invented) from stdin, dispatches each one to the right internal handler (e.g. "list tools," "call tool `get_weather`"), and writes JSON-RPC responses back to stdout.
3. Everything your server code interacts with (`@mcp.tool()`, etc.) is really just populating those registries *before* `.run()` starts the event loop — no client connection exists yet at the point your `@mcp.tool()`-decorated functions are defined; they're just being registered for whenever a client eventually asks.

**Real source:** [`mcp/server/fastmcp/server.py`](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/server.py) in the `modelcontextprotocol/python-sdk` repo.

## `@mcp.tool()`

**How it works internally:** Very similar to LangChain's `@tool` (module 19's INTERNALS.md) — it reads your function's type hints and docstring, builds a JSON Schema from them, and registers `(name, description, schema, the actual function)` in the server's tool registry. When a client later calls `list_tools()`, the server just serializes that registry's contents back as the response; when a client calls `call_tool("get_weather", {"city": "Tokyo"})`, the server looks up `get_weather` in the registry, validates the arguments against the stored schema, and calls the real Python function with them.

**Real source:** [`mcp/server/fastmcp/tools/tool_manager.py`](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/tools/tool_manager.py) and `mcp/server/fastmcp/tools/base.py` in the same repo.

**How to validate the schema generation is working as expected:** A server has no client connected to itself, so the practical way to see what schema your `@mcp.tool()` functions actually produced is from the *client* side — connect with a real client and call `list_tools()`, which is exactly what [module 22's INTERNALS.md](../22_mcp_stdio_client/INTERNALS.md) walks through. That's the validation path to use here: run `server.py`, connect `client.py` to it, and print each tool's `inputSchema`.
