# Module 19 — Internals

This module's README already has an [Execution Internals](README.md#execution-internals-why-agentinvoke-isnt-a-single-pass) section explaining the think/act/observe loop conceptually. This page goes one level deeper: what `@tool` and `create_react_agent` actually build.

## `@tool`

**What it is:** A decorator that wraps a plain Python function in a `StructuredTool` object — the same underlying idea as MCP's `@mcp.tool()` (module 21), but for tools defined locally instead of served over a protocol.

**How it works internally:**
1. It reads the function's name (becomes the tool's `name`, unless you override it), its docstring (becomes the tool's `description` — this is literally what the model reads to decide when to use it), and its type-hinted parameters (used to build a Pydantic schema describing valid arguments, the same JSON-Schema-generation idea covered in module 03's `.with_structured_output()` internals).
2. The decorated function itself becomes the tool's `.func` — the actual code that runs when the tool is called. Calling `add(3, 4)` directly still works exactly like a normal function call; `@tool` doesn't change how you can use the function yourself, it just *also* wraps it with the extra metadata an agent needs.
3. When you pass `[add, get_word_length]` to `create_react_agent`, each one gets bound to the model as an available "function" the model's API supports calling (Claude's native tool-calling capability, the same mechanism `.with_structured_output()` uses internally).

**Real source:** [`langchain_core/tools/convert.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/tools/convert.py) — look for the `tool` decorator function, and `langchain_core/tools/structured.py` for `StructuredTool` itself.

**How to validate it's working:**
```python
print(add.name)          # "add"
print(add.description)   # "Add two numbers together and return the sum."
print(add.args_schema.model_json_schema())   # the JSON schema built from add(a: float, b: float)
print(add.invoke({"a": 3, "b": 4}))          # 7.0 -- calling it through the tool wrapper still works
```

## `create_react_agent(llm, tools)`

**What it is:** A LangGraph prebuilt constructor that returns a compiled **graph** — not a plain `Runnable` chain like everything in modules 01-17, but a small state machine with nodes and edges.

**How it works internally:**
1. It builds a graph with (roughly) two nodes: an "agent" node (calls the LLM with the current messages + tool schemas) and a "tools" node (actually executes whichever tool(s) the LLM asked for).
2. It wires a conditional edge after the "agent" node: if the LLM's response contains tool calls, go to the "tools" node; if not, the graph ends and returns.
3. After the "tools" node runs, an edge routes back to the "agent" node — closing the loop this module's Execution Internals section walks through.
4. `.invoke({"messages": [...]})` runs this graph to completion, feeding the growing message list through the loop until the "no tool calls" exit condition is hit, then returns the final state (including the full accumulated `messages` list).

**Real source:** [`langgraph/prebuilt/chat_agent_executor.py`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/prebuilt/chat_agent_executor.py) in the `langchain-ai/langgraph` repo.

**How to validate the graph structure directly:**
```python
agent = build_agent()
print(type(agent))     # <class 'langgraph.graph.state.CompiledStateGraph'> -- confirms it's a graph, not a chain
print(agent.get_graph().nodes)    # shows you the actual node names LangGraph built
```
If you have `pip install grandalf` (an optional LangGraph dependency) or a Jupyter environment, `agent.get_graph().print_ascii()` or `.draw_mermaid()` will render the actual graph structure — genuinely useful the first time you want to *see* the loop instead of just reading about it.
