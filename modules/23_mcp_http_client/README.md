# 23 — MCP HTTP Client

## Theory

Modules 21-22 had the client start the server itself, and the two were tied together. That doesn't work when the server needs to be shared — say, one internal tool used by everyone's agents across a whole company. **Streamable HTTP** is the other connection method: the server runs on its own, independently, the same way a website runs on its own server, and clients connect to it over a URL — just like your web browser connects to a website — instead of the client having to start it.

- **The server just becomes a small web server.** Instead of listening on stdin/stdout, it listens on a URL, e.g. `http://localhost:8000`.
- **The client code barely changes.** You swap out "start this program and talk to it" for "connect to this URL," but everything after that — asking what tools exist, calling a tool — works exactly the same way as the stdio client from module 22.
- **The server doesn't care if anyone's connected.** Unlike stdio (where the server dies the moment its one client disconnects), an HTTP server keeps running in the background, ready for any client to connect to it at any time — including several clients at once.

## Use Case

A shared MCP server used by multiple people/agents (e.g. a company-wide "internal docs" MCP server), or any deployment where the server needs to live on different infrastructure than the client (a container, a separate host, behind a load balancer).

## How to Run

This is the one module in the repo that genuinely needs **two terminals**, because — unlike stdio — the HTTP server is a long-lived, independent process, not something the client spawns for you:
```bash
# terminal 1 -- starts and blocks, serving on localhost:8000
python modules/23_mcp_http_client/server_http.py

# terminal 2 -- connects to it and exits when done
python modules/23_mcp_http_client/client_http.py
python modules/23_mcp_http_client/solutions.py   # exercise solutions (needs the server running too)
```
No API key needed. Leave terminal 1 running for as long as you want to keep issuing client calls against it.

## Walkthrough

1. `server_http.py` — the same `get_weather`/`word_count` tools from module 21, now served over `streamable-http` on `localhost:8000`.
2. `client_http.py` — connects via `streamablehttp_client("http://127.0.0.1:8000/mcp")` instead of spawning a subprocess, then runs the identical `list_tools`/`call_tool` sequence as module 22.

## Classes & Methods Used

Everything here is the same as module 22 (`ClientSession`, `.initialize()`, `.list_tools()`, `.call_tool()` — see [module 22's table](../22_mcp_stdio_client#classes--methods-used)) except for the connection method:

| API | What It Does | Why We Use It Here |
|---|---|---|
| `FastMCP("utilities-http-server", port=8000)` | Same server-building class as module 21, but given a port number. | The port is what makes this an HTTP-reachable server instead of a stdio one — the tools themselves (`get_weather`, `word_count`) are unchanged from module 21. |
| `mcp.run(transport="streamable-http")` | Starts the server listening on an HTTP port instead of stdin/stdout. | This one argument is the entire difference between module 21's server and this one. |
| `streamablehttp_client(url)` (used with `async with`) | Connects to an already-running MCP server at a URL, instead of starting one as a subprocess. | Replaces module 22's `stdio_client(server_params)` — same role (get connected read/write streams), different transport underneath. |

## Using a different model

Still pure transport/protocol — no model involved. See [module 26](../26_mcp_implement_client) for wiring an MCP client (of either transport) into a Claude agent.

## Reference Docs

- Streamable HTTP transport spec: https://modelcontextprotocol.io/docs/concepts/transports
- Python SDK HTTP client: https://github.com/modelcontextprotocol/python-sdk#streamable-http-transport

## Exercises

1. **Changing which port the server listens on.** In `server_http.py`, change `FastMCP("utilities-http-server", port=8000)` to `port=8010`. In `client_http.py`, update `SERVER_URL` to `"http://127.0.0.1:8010/mcp"`. Restart the server and confirm the client can still connect and call tools — this is worth doing once so port numbers stop feeling like magic.
2. **Confirming the server genuinely handles multiple clients.** With `server_http.py` running in one terminal, run `client_http.py` twice in quick succession (two separate terminal windows, or two background processes) — both should independently connect, list tools, and get correct results, without one client's calls interfering with the other's. This is the behavior stdio (module 22) can't offer, since each stdio client gets its own private server subprocess.
3. **A clear error instead of a confusing one when the server isn't running.** Stop `server_http.py` (or just don't start it), then run `client_http.py`. You'll likely get a raw connection-refused exception. Wrap the connection attempt in a `try/except` and print a clear, specific message like `"Could not connect -- is server_http.py running on port 8000?"` instead of letting the raw traceback surface.
4. **Watching the server survive its client disconnecting.** With `server_http.py` running, start `client_http.py`, then hit Ctrl+C on the *client* mid-run (not the server). Confirm the server terminal is still running and unaffected — then run `client_http.py` again fresh and confirm it still works, proving the server's lifecycle is genuinely independent of any one client's.

**Solutions:** see [`solutions.py`](solutions.py) in this folder (start `server_http.py` first for exercises 1-2).
