"""
Module 26 - Implement Client: a Claude/LangGraph agent consuming tools from the
module 25 MCP server via langchain-mcp-adapters.

Start modules/25_mcp_implement_server/server.py first, then run:
    python modules/26_mcp_implement_client/client.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from common.model_factory import get_chat_model

MCP_SERVERS = {
    "job_board": {
        "url": "http://127.0.0.1:8100/mcp",
        "transport": "streamable_http",
    }
}


async def main():
    mcp_client = MultiServerMCPClient(MCP_SERVERS)
    tools = await mcp_client.get_tools()

    print("--- Tools discovered from MCP server(s) ---")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    llm = get_chat_model()
    agent = create_react_agent(llm, tools)

    question = (
        "Find a job posting that best matches someone with LangChain and FAISS "
        "experience, then draft a short cover letter for 'Alex Chen' for that job."
    )
    result = await agent.ainvoke({"messages": [("human", question)]})

    print("\n--- Full message trace ---")
    for message in result["messages"]:
        message.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
