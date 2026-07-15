# 19 — Agents

## Theory

Everything up to this point has been a **chain**: a fixed set of steps that always run in the same order, which *you* decided ahead of time. An **agent** is different — instead of you deciding the steps, the model itself decides, on the fly, what to do next, and keeps going until it thinks it's done. Here's what makes that possible:

- **Giving the model "tools" it can use.** A tool is just a regular Python function — like a calculator, or a function that looks something up — but with a name and a plain-English description attached, explaining what it does and when to use it. The model reads that description to decide whether it's useful for the current question.
- **The model asking to use a tool.** Instead of just replying with text, the model can reply with "please run this specific tool, with these specific inputs." LangChain understands this special kind of reply and knows to actually run the corresponding function.
- **Going back and forth until it's done.** The model can: think, ask to run a tool, receive that tool's result, think some more, maybe ask to run another tool — repeating as many times as it needs — until it finally has enough information to just answer in plain text instead of requesting another tool.
- **The tool that builds this loop for you.** `create_react_agent` sets up this whole "think, act, look at the result, think again" loop automatically — you just give it a model and a list of tools, and it handles the back-and-forth.

## Use Case

Anything requiring the model to take real actions or fetch live data mid-conversation: look up today's weather, run a calculation, query a database, call an internal API, search the web — then reason over the result before answering. [Module 26](../26_mcp_implement_client) extends this exact pattern to tools served over MCP instead of defined locally.

## Execution Internals: why `agent.invoke()` isn't a single pass

This is a meaningfully different execution model from [module 03's `RunnableSequence`](../03_chains_lcel#execution-internals-the-runnable-protocol), worth calling out explicitly: a plain LCEL chain's `.invoke()` runs each step exactly once, in a fixed order you wrote. `create_react_agent(...)` instead returns a LangGraph graph whose `.invoke({"messages": [...]})` runs a **loop with an unknown number of iterations**:

1. Call the LLM with the current message list (plus each tool's schema attached, so the model knows what it *can* call).
2. If the response is plain text with no tool calls, stop and return it — this is the exit condition.
3. If the response contains one or more tool calls, actually execute those Python functions locally (in-process, synchronously — no network call, unlike step 1), and append their results as `ToolMessage`s to the message list.
4. Go back to step 1 with the now-longer message list.

This is why `result["messages"]` after `agent.invoke(...)` often contains 4+ messages (human question → AI tool call → tool result → AI tool call → tool result → final AI answer) even though you only made one top-level call — each loop iteration is its own real LLM call (and its own cost/latency), which `message.pretty_print()` on every entry in that list makes visible.

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

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `@tool` (from `langchain_core.tools`) | Turns a plain Python function into something a model can be told about and asked to call — reads the function's type hints and docstring to build its description automatically (same idea as module 00's decorator explanation). | Applied to `add` and `get_word_length` so the agent can discover and use them, without us writing any tool-calling plumbing by hand. |
| `create_react_agent(llm, tools=[...])` | Builds the full "think, call a tool, look at the result, think again" loop (module 19's Theory) as a ready-to-use object. | The one call that turns a model + a list of tools into a working agent — see this module's Execution Internals for exactly what happens inside `.invoke()` on the result. |
| `agent.invoke({"messages": [("human", question)]})` | Runs the agent loop to completion and returns the full message list, not just the final answer. | Used so we can inspect every step the agent took (tool calls and results), not just its final response. |
| `message.pretty_print()` | Prints a message object in a readable, labeled format. | Used on every message in the result to display the full back-and-forth — the question, each tool call, each tool's result, and the final answer. |

## Using a different model

Tool-calling quality varies by provider and model size; swap via `get_chat_model(provider=...)` — smaller/local models (e.g. via Ollama) may need simpler tool descriptions or more explicit prompting to reliably call tools correctly.

## Reference Docs

- LangGraph `create_react_agent`: https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent
- Tool calling concept: https://python.langchain.com/docs/concepts/tool_calling/
- Anthropic tool use guide: https://docs.anthropic.com/en/docs/build-with-claude/tool-use

## Exercises

1. **A 3-tool question, to see the loop handle more steps.** Write a third `@tool`-decorated function, `reverse_string(s: str) -> str`, following `add`/`get_word_length`'s pattern (type hints + a docstring, since those are what the model reads). Add it to `create_react_agent(llm, tools=[...])`'s tool list, then ask a question that genuinely needs all 3 — e.g. "Reverse the word 'LangChain', tell me how many letters the reversed word has, then add that to 10."
2. **Inspecting exactly what arguments the model chose.** Run any multi-tool question and loop over `result["messages"]`. For messages that have `.tool_calls` (check `hasattr(message, "tool_calls") and message.tool_calls`), print each call's `name` and `args` — this shows you precisely what the model decided to pass to each tool, which is useful for debugging when an agent calls a tool "wrong."
3. **What happens when a tool fails mid-loop.** Write a tool that raises an exception for certain inputs — e.g. `divide(a, b)` that raises `ValueError("Cannot divide by zero.")` when `b == 0`. Ask the agent a question that triggers this (e.g. "What is 10 divided by 0?") and read through the full message trace: does the agent notice the error and explain it to you, or does the whole thing crash?
4. **Breaking one flexible tool into several narrow ones.** Instead of a single `add` tool, write 4 separate ones: `add`, `subtract`, `multiply`, `divide`, each taking two numbers. Ask a multi-step arithmetic question that requires chaining several of them (e.g. "Take 20, add 15, then multiply by 2, then divide by 5 — what's the final result?") and confirm the agent calls them in the right order.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
