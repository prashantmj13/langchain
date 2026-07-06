"""
Module 22 - MCP Stdio Client: connects to the server from module 21 over stdio.

Run: python modules/22_mcp_stdio_client/client.py
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).resolve().parents[1] / "21_mcp_create_server" / "server.py"


async def main():
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("--- Tools exposed by the server ---")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\n--- Calling get_weather('Tokyo') ---")
            result = await session.call_tool("get_weather", {"city": "Tokyo"})
            print(result.content[0].text)

            print("\n--- Calling word_count(...) ---")
            result = await session.call_tool(
                "word_count", {"text": "The Model Context Protocol standardizes tool access."}
            )
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
