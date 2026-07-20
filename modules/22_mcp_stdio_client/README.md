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

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `StdioServerParameters(command=..., args=[...])` | Describes how to launch a server process — which command to run and with what arguments. | Used to tell the client exactly how to start module 21's `server.py` as a subprocess. |
| `stdio_client(server_params)` (used with `async with`) | Starts the server subprocess described above and hands back read/write streams connected to it; automatically shuts the subprocess down when the `async with` block ends. | This is what actually launches and connects to the server — no server terminal needed, unlike module 23's HTTP version. |
| `ClientSession(read, write)` (used with `async with`) | Wraps the raw read/write streams with the actual MCP protocol logic. | Provides the `.initialize()`/`.list_tools()`/`.call_tool()` methods used below — it's the object you actually talk to. |
| `await session.initialize()` | Performs the MCP handshake — client and server agree on protocol version and capabilities. | Must be called once before any other session method will work; it's the "say hello" step. |
| `await session.list_tools()` | Asks the server what tools it exposes, returning each one's name, description, and argument schema. | Used to show what the server offers *before* calling anything — the same discovery step a real agent would do automatically. |
| `await session.call_tool(name, arguments)` | Asks the server to actually run one specific tool with the given arguments, and returns its result. | Used to call `get_weather` and `word_count` with real inputs and see their output. |

For how `stdio_client` actually spawns and manages the subprocess, and how `ClientSession` matches requests to responses — plus what to check if `.initialize()` hangs — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

This module is pure protocol plumbing — no LLM involved yet. [Module 26](../26_mcp_implement_client) is where an actual Claude-powered agent decides which of these tools to call and with what arguments.

## Reference Docs

- MCP client quickstart: https://modelcontextprotocol.io/quickstart/client
- Python SDK client reference: https://github.com/modelcontextprotocol/python-sdk#writing-mcp-clients

## Exercises

1. **Seeing everything a client can discover about a tool, not just its name.** `client.py`'s `list_tools()` loop only prints `tool.name` and `tool.description`. Modify it to also print `tool.inputSchema` (as JSON via `json.dumps(tool.inputSchema, indent=2)`) for each tool — this is the same schema module 21's exercise 4 asked you to inspect, now from the "generic client" side rather than knowing the server's code.
2. **Testing the server's fallback path deliberately.** `get_weather` in module 21's `server.py` only has mocked data for 3 cities. Call it with a city that isn't one of them (e.g. `"Atlantis"`) and confirm you get back the fallback message (`"No weather data available for '...'."`) instead of an error or empty result.
3. **What happens when the server can't even start.** Change `SERVER_SCRIPT` in your own copy of `client.py` to point at a file that doesn't exist. Run the client and observe what happens — does it hang forever, or fail with a clear error? If it hangs, wrap the connection attempt in `asyncio.wait_for(..., timeout=10)` so it fails loudly instead.
4. **Running two independent tool calls concurrently instead of one after another.** `client.py` currently calls `get_weather` then `word_count` sequentially, each with its own `await`. Rewrite it to fire both at once with `await asyncio.gather(session.call_tool("get_weather", {...}), session.call_tool("word_count", {...}))`, and confirm both results come back correctly (order in the returned tuple matches the order you passed the calls in).

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
