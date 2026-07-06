# 22 — MCP Stdio Client

## Theory

A stdio client connects to an MCP server by **launching it as a subprocess** and communicating over its stdin/stdout pipes — no ports, no network config, and the server's lifetime is scoped to the client's. The Python SDK's client pieces:

- **`StdioServerParameters(command, args)`** — describes how to launch the server process (e.g. `python server.py`).
- **`stdio_client(params)`** — an async context manager that spawns the subprocess and returns `(read, write)` streams.
- **`ClientSession(read, write)`** — wraps those streams with the actual MCP protocol: `.initialize()` (handshake), `.list_tools()`, `.call_tool(name, arguments)`.

This is the client-side counterpart to [module 21](../21_mcp_create_server)'s server.

## Use Case

Local tool integrations where the "server" is really just a local script/binary you want the LLM host to be able to invoke — most desktop MCP integrations (e.g. Claude Desktop's local tool servers) use exactly this transport.

## Walkthrough

`client.py`:
1. Points `StdioServerParameters` at `../21_mcp_create_server/server.py` and launches it as a subprocess.
2. Opens a `ClientSession`, calls `.initialize()`, then `.list_tools()` and prints each tool's name/description/schema.
3. Calls `get_weather` and `word_count` with real arguments and prints the results.

## Using a different model

This module is pure protocol plumbing — no LLM involved yet. [Module 26](../26_mcp_implement_client) is where an actual Claude-powered agent decides which of these tools to call and with what arguments.

## Reference Docs

- MCP client quickstart: https://modelcontextprotocol.io/quickstart/client
- Python SDK client reference: https://github.com/modelcontextprotocol/python-sdk#writing-mcp-clients

## Exercises

1. Print the full JSON schema for each tool (not just name/description) to see exactly what a client can introspect before calling.
2. Call `get_weather` with a city not in the mocked dataset and confirm the fallback message comes through unchanged.
3. Add error handling for the case where the server script path is wrong, and confirm you get a clear failure rather than a hang.
4. Modify the client to call both tools concurrently with `asyncio.gather` instead of sequentially.
