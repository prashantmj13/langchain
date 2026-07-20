# Module 23 — Internals

`ClientSession` and its methods are covered in [module 22's INTERNALS.md](../22_mcp_stdio_client/INTERNALS.md) — everything there applies unchanged here. This page covers what's different about the HTTP transport specifically.

## `mcp.run(transport="streamable-http")` (server side)

**How it works internally:** Instead of the stdin/stdout event loop module 21's INTERNALS.md describes, this starts a real ASGI web server (using `uvicorn` under the hood, a common Python async web server) listening on the port you configured. Each MCP request arrives as an HTTP `POST` to a specific endpoint (`/mcp` in this module's examples), carrying the JSON-RPC message as the request body; the server processes it exactly the same way as the stdio version internally (same tool registry, same dispatch logic) — only the transport layer underneath actually differs.

**Real source:** [`mcp/server/fastmcp/server.py`](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/server.py) — the same file as module 21's `FastMCP`, since it's one class supporting multiple transports; look for `streamable_http_app()`.

## `streamablehttp_client(url)` (client side)

**How it works internally:** Where `stdio_client` (module 22) spawns a subprocess and wires up pipes, `streamablehttp_client` instead opens an HTTP connection to the given URL using an async HTTP client (`httpx`, under the hood). It sends your requests as HTTP `POST`s and reads the server's responses back over the same connection — using HTTP's chunked-transfer/streaming capability so responses can arrive incrementally rather than only after the entire response is ready, which is what "streamable" in the name refers to. Everything downstream of that (`ClientSession`, `.initialize()`, `.list_tools()`, `.call_tool()`) is identical to the stdio version, because `ClientSession` only cares about having *some* read/write stream pair — it doesn't know or care whether bytes are coming from a subprocess pipe or an HTTP connection.

**Real source:** [`mcp/client/streamable_http.py`](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/client/streamable_http.py).

**How to validate the HTTP transport is genuinely being used (not silently falling back to something else):**
```bash
# With server_http.py running, watch actual network traffic:
# on macOS/Linux: sudo lsof -i :8000   (confirms something is listening on port 8000)
# or just try connecting with curl to confirm it's a real HTTP endpoint:
curl -i http://127.0.0.1:8000/mcp
# You should get a real HTTP response back (likely a 4xx, since curl isn't speaking the MCP
# protocol correctly) -- but a response at all confirms a real HTTP server is listening there.
```
