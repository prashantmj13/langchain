# 22 — MCP Stdio Client

## Theory

Module 21 built the server; this module builds the other half — the client that actually talks to it. A "stdio client" connects to a server by starting it up as its own little program and exchanging messages directly with it, without any networking involved. When the client shuts down, the server it started shuts down too — they're tied together.

Three pieces work together to make this happen:
- **A description of how to start the server** — basically "run this command" (e.g. `python server.py`).
- **Something that actually starts it** and hands you back a way to send and receive messages.
- **A "session" object** that wraps those messages with the real MCP conversation: say hello and agree on capabilities, ask "what tools do you have?", and "please run this tool with these arguments."

## Use Case

Local tool integrations where the "server" is really just a local script/binary you want the LLM host to be able to invoke — most desktop MCP integrations (e.g. Claude Desktop's local tool servers) use exactly this transport.

## How to Run

```bash
python modules/22_mcp_stdio_client/client.py
python modules/22_mcp_stdio_client/solutions.py   # exercise solutions
```
No API key needed, and no second terminal either: `stdio_client(server_params)` spawns [module 21](../21_mcp_create_server)'s `server.py` as a subprocess itself (using `sys.executable`, so it works regardless of how Python is aliased on your system), talks to it over its stdin/stdout, and tears it down automatically when the `async with` block exits.

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

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
