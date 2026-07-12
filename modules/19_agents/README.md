# 19 — Agents

## Theory

A **chain** follows a fixed sequence of steps you wrote in advance. An **agent** lets the LLM itself decide, at runtime, which tools to call and in what order, looping until it has enough information to answer. The core pieces:

- **Tools** — plain Python functions decorated with `@tool`, each with a name, description, and typed arguments. The description is what the model reads to decide *when* to use it — write it like documentation for a very literal colleague.
- **Tool calling** — Claude (and other modern chat models) can emit structured "call this tool with these arguments" responses instead of plain text; LangChain parses these into `ToolCall` objects.
- **The agent loop (ReAct pattern)** — the model reasons, decides to call a tool, receives the tool's result as a new message, and reasons again — repeating until it produces a final answer instead of another tool call.
- **`langgraph.prebuilt.create_react_agent`** — the modern, actively-maintained way to build this loop (the older `AgentExecutor` class from core LangChain is legacy). It returns a runnable graph you `.invoke({"messages": [...]})`.

## Use Case

Anything requiring the model to take real actions or fetch live data mid-conversation: look up today's weather, run a calculation, query a database, call an internal API, search the web — then reason over the result before answering. [Module 26](../26_mcp_implement_client) extends this exact pattern to tools served over MCP instead of defined locally.

## How to Run

```bash
python modules/19_agents/example.py
python modules/19_agents/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY`. `agent.invoke(...)` runs the full reasoning loop internally (the model decides which tools to call, the tools execute locally in-process, results feed back to the model) — `message.pretty_print()` on each message in the result is what lets you see every step of that loop instead of just the final answer.

## Walkthrough

`example.py`:
1. Defines two local tools: `add(a, b)` (a calculator) and `get_word_length(word)`.
2. Builds a ReAct agent with `create_react_agent(llm, tools)`.
3. Asks a question that requires both tools ("How much longer is the word 'LangChain' than the sum of 3 and 4?") and prints the full message trace, showing the tool calls and their results, not just the final answer.

## Using a different model

Tool-calling quality varies by provider and model size; swap via `get_chat_model(provider=...)` — smaller/local models (e.g. via Ollama) may need simpler tool descriptions or more explicit prompting to reliably call tools correctly.

## Reference Docs

- LangGraph `create_react_agent`: https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent
- Tool calling concept: https://python.langchain.com/docs/concepts/tool_calling/
- Anthropic tool use guide: https://docs.anthropic.com/en/docs/build-with-claude/tool-use

## Exercises

1. Add a third tool, `reverse_string(s)`, and ask a question that requires all three tools to answer.
2. Print each intermediate `ToolMessage` in the trace to see exactly what arguments the model chose to pass.
3. Give the agent a bad tool (one that raises an exception for certain inputs) and observe how it recovers (or doesn't) from a tool error.
4. Rebuild the calculator tool as `add`, `subtract`, `multiply`, `divide` (four separate tools) and ask a multi-step arithmetic question requiring several calls.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
