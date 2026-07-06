# 23 — MCP HTTP Client

## Theory

Unlike stdio ([modules 21](../21_mcp_create_server)/[22](../22_mcp_stdio_client)), **streamable HTTP** transport runs the server as its own independent process (potentially on a different machine) that the client connects to over a URL, with the protocol's responses streamed back over the HTTP connection. This is what you need once a server isn't something the client can/should spawn itself — a shared team server, a server behind auth, or a server exposed to multiple clients at once.

- **Server side** — `mcp.run(transport="streamable-http")` (or `mcp.streamable_http_app()` mounted into your own ASGI app) starts an HTTP endpoint instead of reading stdin/stdout.
- **Client side** — `streamablehttp_client(url)` replaces `stdio_client(params)`; everything downstream (`ClientSession`, `.list_tools()`, `.call_tool()`) is identical — the transport is swappable without touching your protocol-level code.
- **Independent lifecycles** — the server keeps running regardless of whether any particular client is connected, unlike stdio where the server dies with the client.

## Use Case

A shared MCP server used by multiple people/agents (e.g. a company-wide "internal docs" MCP server), or any deployment where the server needs to live on different infrastructure than the client (a container, a separate host, behind a load balancer).

## Walkthrough

1. `server_http.py` — the same `get_weather`/`word_count` tools from module 21, now served over `streamable-http` on `localhost:8000`.
2. `client_http.py` — connects via `streamablehttp_client("http://127.0.0.1:8000/mcp")` instead of spawning a subprocess, then runs the identical `list_tools`/`call_tool` sequence as module 22.

Run the server first in one terminal, then the client in another:
```bash
python modules/23_mcp_http_client/server_http.py
# in a second terminal:
python modules/23_mcp_http_client/client_http.py
```

## Using a different model

Still pure transport/protocol — no model involved. See [module 26](../26_mcp_implement_client) for wiring an MCP client (of either transport) into a Claude agent.

## Reference Docs

- Streamable HTTP transport spec: https://modelcontextprotocol.io/docs/concepts/transports
- Python SDK HTTP client: https://github.com/modelcontextprotocol/python-sdk#streamable-http-transport

## Exercises

1. Change the server's port from 8000 to 8010 and update the client accordingly.
2. Start the server, then start two separate client processes calling it concurrently, and confirm both get correct independent responses.
3. Add basic error handling to the client for "server not running" (connection refused) with a clear error message.
4. Compare startup/teardown behavior: kill the client process (Ctrl+C) and confirm the HTTP server keeps running, unlike the stdio case in module 22 where the server dies with the client.
