"""
Module 26 - Exercise solutions.

Exercises 1-3 require modules/25_mcp_implement_server/server.py running on
http://127.0.0.1:8100 first:
    python modules/25_mcp_implement_server/server.py

Then run: python modules/26_mcp_implement_client/solutions.py
"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from common.model_factory import get_chat_model

JOB_BOARD_SERVER = {"job_board": {"url": "http://127.0.0.1:8100/mcp", "transport": "streamable_http"}}

UTILITIES_SERVER_SCRIPT = Path(__file__).resolve().parents[1] / "21_mcp_create_server" / "server.py"
TWO_SERVERS = {
    **JOB_BOARD_SERVER,
    "utilities": {"command": sys.executable, "args": [str(UTILITIES_SERVER_SCRIPT)], "transport": "stdio"},
}


async def exercise_1():
    """Add a 2nd MCP server (module 21's stdio server) alongside the HTTP job-board server."""
    mcp_client = MultiServerMCPClient(TWO_SERVERS)
    tools = await mcp_client.get_tools()

    print("--- Exercise 1: tools from two servers ---")
    print([t.name for t in tools])

    llm = get_chat_model()
    agent = create_react_agent(llm, tools)
    result = await agent.ainvoke(
        {
            "messages": [
                (
                    "human",
                    "What's the weather in Tokyo, and separately, find a job matching "
                    "someone with backend Python and PostgreSQL experience.",
                )
            ]
        }
    )
    print(result["messages"][-1].content)


async def exercise_2():
    """Print tool schemas from get_tools(), confirm they match the server's definitions."""
    mcp_client = MultiServerMCPClient(JOB_BOARD_SERVER)
    tools = await mcp_client.get_tools()

    print("\n--- Exercise 2: tool schemas from get_tools() ---")
    for t in tools:
        print(f"{t.name}: {t.description}")
        print(f"  args_schema: {t.args_schema.model_json_schema() if t.args_schema else 'n/a'}")


async def exercise_3():
    """A question requiring search_jobs to be called twice with different queries."""
    mcp_client = MultiServerMCPClient(JOB_BOARD_SERVER)
    tools = await mcp_client.get_tools()
    llm = get_chat_model()
    agent = create_react_agent(llm, tools)

    print("\n--- Exercise 3: two searches in one conversation ---")
    result = await agent.ainvoke(
        {
            "messages": [
                (
                    "human",
                    "First find the best match for someone with React/TypeScript experience. "
                    "Then, separately, find the best match for someone with data pipeline/SQL experience.",
                )
            ]
        }
    )
    print(result["messages"][-1].content)


@tool
def search_jobs_local(query: str) -> str:
    """A local stand-in for the MCP search_jobs tool, for the latency comparison."""
    return f"(local) top match for {query!r}: ml_engineer"


async def exercise_4():
    """Compare this MCP-based agent's latency to a local-tools agent (module 19 style)."""
    llm = get_chat_model()

    mcp_client = MultiServerMCPClient(JOB_BOARD_SERVER)
    mcp_tools = await mcp_client.get_tools()
    mcp_agent = create_react_agent(llm, mcp_tools)

    local_agent = create_react_agent(llm, [search_jobs_local])

    question = "Find the best job match for someone with LangChain experience."

    start = time.perf_counter()
    await mcp_agent.ainvoke({"messages": [("human", question)]})
    mcp_time = time.perf_counter() - start

    start = time.perf_counter()
    local_agent.invoke({"messages": [("human", question)]})
    local_time = time.perf_counter() - start

    print("\n--- Exercise 4: MCP agent vs. local-tools agent latency ---")
    print(f"MCP agent:   {mcp_time:.2f}s")
    print(f"Local agent: {local_time:.2f}s")
    print("(MCP adds a small amount of protocol/transport overhead per tool call.)")


async def main():
    try:
        await exercise_1()
        await exercise_2()
        await exercise_3()
        await exercise_4()
    except Exception as exc:  # noqa: BLE001
        print(f"Skipped -- start modules/25_mcp_implement_server/server.py first. ({exc.__class__.__name__}: {exc})")


if __name__ == "__main__":
    asyncio.run(main())
