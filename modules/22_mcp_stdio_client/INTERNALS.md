# Module 22 — Internals

## `stdio_client(server_params)`

**What it is:** An async context manager that spawns a subprocess and gives you back a pair of streams connected to its stdin/stdout.

**How it works internally:**
1. Internally, it uses Python's `asyncio.create_subprocess_exec()` (the standard-library way to launch and manage a child process asynchronously) to start the server command you described in `StdioServerParameters`.
2. It wires the subprocess's stdout to a `read` stream your code can await messages from, and the subprocess's stdin to a `write` stream your code can send messages through — these aren't the raw pipes, but wrapped versions that handle MCP's message framing (each JSON-RPC message needs to be delimited somehow so the reader knows where one message ends and the next begins).
3. When the `async with` block exits (normally, or due to an exception), it terminates the subprocess — this is why the server "dies with the client" for stdio: the subprocess's lifetime is directly tied to this context manager's lifetime.

**Real source:** [`mcp/client/stdio/__init__.py`](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/client/stdio/__init__.py) in the `modelcontextprotocol/python-sdk` repo.

## `ClientSession(read, write)`

**What it is:** The layer that turns raw read/write streams into the actual MCP protocol — `.initialize()`, `.list_tools()`, `.call_tool()`, etc.

**How it works internally:**
1. `.initialize()` sends an MCP `initialize` request over `write`, and awaits a response on `read` — this is the protocol handshake where client and server exchange their supported protocol version and capabilities. Nothing else will work correctly until this completes.
2. `.list_tools()`/`.call_tool(name, args)` each construct a JSON-RPC request with the right method name and parameters, write it to the `write` stream, then await a matching response on the `read` stream — since everything is async and the underlying connection is a single stream, `ClientSession` internally tracks request IDs to match each response back to the request that triggered it, even if messages could in principle arrive out of order.
3. The `result` objects these methods return (`tools_response.tools`, `result.content[0].text`) are typed Python objects that `ClientSession` builds by parsing the JSON-RPC response's `result` field according to the MCP spec's schema for that response type.

**Real source:** [`mcp/client/session.py`](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/client/session.py).

**How to validate the handshake and request/response matching are working:**
```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        init_result = await session.initialize()
        print(init_result.serverInfo.name)   # should print "utilities-server" -- confirms the handshake worked

        tools_response = await session.list_tools()
        print([t.name for t in tools_response.tools])  # ['get_weather', 'word_count']
```
If `.initialize()` hangs forever instead of returning, that's usually a sign the server process isn't actually starting correctly (wrong command/path) — check `SERVER_SCRIPT` and confirm `python your_server.py` runs cleanly on its own first.
