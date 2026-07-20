# Module 26 — Internals

## `MultiServerMCPClient`

**What it is:** A `langchain-mcp-adapters` class that manages connections to one or more MCP servers at once, keyed by the names you give them in its config dict.

**How it works internally:** For each server entry in the config, it builds the appropriate transport internally — a `stdio_client` (module 22) if you gave it a `command`, or a `streamablehttp_client` (module 23) if you gave it a `url` — and wraps each with its own `ClientSession`. It doesn't connect eagerly at construction time; connections are established lazily, when you actually call something like `get_tools()`.

**Real source:** [`langchain_mcp_adapters/client.py`](https://github.com/langchain-ai/langchain-mcp-adapters/blob/main/langchain_mcp_adapters/client.py) in the `langchain-ai/langchain-mcp-adapters` repo.

## `await mcp_client.get_tools()` — the actual MCP-to-LangChain bridge

**How it works internally:**
1. For each configured server, it opens a connection (module 22/23's mechanics) and calls `list_tools()` (module 22's INTERNALS.md) to get that server's tool schemas.
2. For every MCP tool it finds, it constructs a LangChain `StructuredTool` (the same class `@tool` produces — module 19's INTERNALS.md) whose `args_schema` is built directly from the MCP tool's `inputSchema`, and whose actual invocation function is a small wrapper that — instead of running local Python code — opens a connection to the right MCP server and calls `call_tool(name, args)` on it, then unwraps the MCP result back into whatever plain value LangChain expects.
3. The result is a `list[BaseTool]` that's indistinguishable, from the agent's point of view, from a list of locally-defined `@tool` functions — which is exactly why `create_react_agent(llm, tools)` needs zero changes to accept them (module 19).

**Real source:** Same file as above — look for `load_mcp_tools` (the function `get_tools()` calls internally per server).

**How to validate the bridge is working correctly:**
```python
tools = await mcp_client.get_tools()
for t in tools:
    print(t.name, type(t))   # <class 'langchain_core.tools.structured.StructuredTool'> -- a real LangChain tool

# Confirm a tool call genuinely round-trips through the MCP server, not just returns a stub:
search_tool = next(t for t in tools if t.name == "search_jobs")
result = await search_tool.ainvoke({"query": "Python backend", "k": 2})
print(result)   # should match what calling search_jobs directly via ClientSession.call_tool() would return
```

## `await agent.ainvoke(...)`

**What it is:** The async version of `agent.invoke()` (module 19's INTERNALS.md covers the underlying LangGraph loop). Needed here specifically because MCP tool calls are async under the hood (they involve real network/subprocess I/O), so the agent's tool-execution step needs to `await` them rather than block synchronously.

**How to validate you're not accidentally blocking:** If you called `agent.invoke()` (the sync version) on an agent with MCP tools instead of `.ainvoke()`, LangGraph would need to run the async tool calls via an internal event loop workaround — this generally still works but adds overhead and can behave unexpectedly if you're already inside an async context (like this module's `async def main()`). Sticking to `.ainvoke()` throughout, as `client.py` does, avoids that entirely.
