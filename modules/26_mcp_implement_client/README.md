# 26 — Implement Client (Claude agent over MCP)

## Theory

This is where the MCP track connects back to [module 19 (Agents)](../19_agents). In module 19, the agent's tools were plain Python functions written right there in the same file. Here, instead, the agent asks an MCP server "what tools do you have?", automatically turns whatever it finds into tools the agent can use, and then works exactly the same way as module 19 from that point on.

- **One client, possibly several servers.** You can point at more than one MCP server at once — maybe one for job postings, another for something else entirely — and this piece handles connecting to all of them.
- **Turning MCP tools into LangChain tools automatically.** One function call fetches every tool from every connected server and converts them into the exact same kind of tool object module 19 used — so they can be handed straight to the same agent-building function, no extra work needed.
- **The agent can't tell the difference.** Whether a tool is a local Python function (module 19) or lives on a separate server somewhere else (this module), the agent uses it exactly the same way — that's the whole point of MCP: it hides *where* a tool lives, so your agent code doesn't need to know or care.

## Use Case

Any agent that needs to call into tools/data that live outside your own codebase — a shared company MCP server, a third-party MCP server, or (as here) your own server process kept separate for reuse across multiple agents/hosts.

## How to Run

Needs two terminals, same as module 23 (this client talks to module 25's server over HTTP, which is a long-lived process the client doesn't spawn itself):
```bash
# terminal 1
python modules/25_mcp_implement_server/server.py

# terminal 2
python modules/26_mcp_implement_client/client.py
python modules/26_mcp_implement_client/solutions.py   # exercise solutions (needs the server running too)
```
Requires `ANTHROPIC_API_KEY` (the agent's LLM). The whole run is one `agent.ainvoke(...)` call — internally the agent may call `search_jobs` and read `draft_cover_letter`'s prompt template over MCP one or more times before producing the final message; `message.pretty_print()` on the trace shows each of those steps.

## Walkthrough

`client.py`:
1. Configures `MultiServerMCPClient` pointing at the [module 25](../25_mcp_implement_server) job-board server over HTTP.
2. Fetches its tools with `get_tools()`.
3. Builds a Claude-powered `create_react_agent` with those tools.
4. Asks: *"Find a job that matches someone with LangChain and FAISS experience, then draft a short cover letter for 'Alex Chen' for that job."* — this requires the agent to call `search_jobs`, read the result, then use the `draft_cover_letter` prompt/resource information to write a letter, all through MCP.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `MultiServerMCPClient({"job_board": {"url": ..., "transport": "streamable_http"}})` | Configures connections to one or more MCP servers at once, by name. | Used to point at module 25's job-board server — the dict key (`"job_board"`) is just a label; the `url`/`transport` describe how to actually reach it. |
| `await mcp_client.get_tools()` | Connects to every configured server, discovers their tools, and returns them already converted into LangChain `BaseTool` objects. | This is the bridge between MCP and LangChain — one call turns "tools living on a separate server" into "tools `create_react_agent` can use," exactly like the local `@tool`-decorated functions in module 19. |
| `create_react_agent(llm, tools)` | Same agent-building function from module 19. | Used identically to module 19 — the agent has no idea (and doesn't need to know) that these tools came from MCP instead of being defined locally. |
| `await agent.ainvoke({"messages": [...]})` | The async version of `agent.invoke()` (module 19) — runs the same think/call-tool/think-again loop. | `ainvoke` (not `invoke`) is used because this script is already running inside `async def main()`, needed for the MCP connection above. |

## Using a different model

Swap `get_chat_model(provider=...)` exactly as in every other module — `MultiServerMCPClient`/`get_tools()` are entirely model-agnostic; only the agent's LLM changes.

## Reference Docs

- `langchain-mcp-adapters`: https://github.com/langchain-ai/langchain-mcp-adapters
- LangGraph `create_react_agent`: https://langchain-ai.github.io/langgraph/reference/prebuilt/
- MCP overview (ties back to module 20): https://modelcontextprotocol.io/

## Exercises

1. **One agent, tools from two different servers.** Add a second entry to `MCP_SERVERS`, pointing at [module 21](../21_mcp_create_server)'s stdio server (using `{"command": sys.executable, "args": [path_to_server.py], "transport": "stdio"}` instead of the HTTP config). Confirm `get_tools()` now returns tools from *both* servers combined, and ask the agent a question requiring one tool from each (e.g. "what's the weather in Tokyo, and separately, find a matching job for someone with Python and SQL experience").
2. **Confirming the MCP→LangChain tool conversion is faithful.** After calling `await mcp_client.get_tools()`, loop over the results and print each `tool.name`, `tool.description`, and (if you want to go further) `tool.args_schema.model_json_schema()`. Compare this against what module 25's `search_jobs` function actually looks like in code — confirm nothing got lost or garbled in the conversion from MCP tool to LangChain `BaseTool`.
3. **A question requiring the same tool called twice with different arguments.** Ask the agent something like "Find the best match for someone with React experience, then separately find the best match for someone with data engineering experience" — this needs `search_jobs` called twice, with two different queries, in one conversation. Check the message trace to confirm it actually did call the tool twice rather than reusing one result for both.
4. **MCP overhead vs. local tools.** Time this module's agent answering a question against module 19's local-tools agent answering an equivalent one, using `time.perf_counter()` around each `.invoke()`/`.ainvoke()` call. MCP adds a network/protocol round-trip per tool call that local Python function calls don't have — is the difference noticeable in practice for a single tool call?

**Solutions:** see [`solutions.py`](solutions.py) in this folder (start `modules/25_mcp_implement_server/server.py` first).
