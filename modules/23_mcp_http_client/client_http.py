"""
Module 23 - MCP HTTP client: connects to server_http.py over streamable HTTP.

Run server_http.py first, in a separate terminal, then run this script:
    python modules/23_mcp_http_client/client_http.py
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    async with streamablehttp_client(SERVER_URL) as (read, write, _get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("--- Tools exposed by the HTTP server ---")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\n--- Calling get_weather('New York') ---")
            result = await session.call_tool("get_weather", {"city": "New York"})
            print(result.content[0].text)

            print("\n--- Calling word_count(...) ---")
            result = await session.call_tool(
                "word_count", {"text": "Streamable HTTP lets the server run independently."}
            )
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
