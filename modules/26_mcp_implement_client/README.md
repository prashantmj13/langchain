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

## Using a different model

Swap `get_chat_model(provider=...)` exactly as in every other module — `MultiServerMCPClient`/`get_tools()` are entirely model-agnostic; only the agent's LLM changes.

## Reference Docs

- `langchain-mcp-adapters`: https://github.com/langchain-ai/langchain-mcp-adapters
- LangGraph `create_react_agent`: https://langchain-ai.github.io/langgraph/reference/prebuilt/
- MCP overview (ties back to module 20): https://modelcontextprotocol.io/

## Exercises

1. Add a second MCP server to `MultiServerMCPClient`'s config (e.g. the module 21 stdio server) and confirm the agent can call tools from both servers in one conversation.
2. Print the tool schemas returned by `get_tools()` to confirm they match the server's `@mcp.tool()` definitions exactly.
3. Ask the agent a question that requires calling `search_jobs` twice with different queries, and check whether it does so correctly.
4. Compare this agent's behavior to the module 19 local-tools agent on an equivalent task — does going through MCP add noticeable latency?

**Solutions:** see [`solutions.py`](solutions.py) in this folder (start `modules/25_mcp_implement_server/server.py` first).
