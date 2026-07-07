"""
Module 22 - Exercise solutions.

Run: python modules/22_mcp_stdio_client/solutions.py
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).resolve().parents[1] / "21_mcp_create_server" / "server.py"


async def exercise_1():
    """Print the full JSON schema for each tool, not just name/description."""
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("--- Exercise 1: full tool schemas ---")
            for tool in (await session.list_tools()).tools:
                print(f"\n{tool.name}:")
                print(json.dumps(tool.inputSchema, indent=2))


async def exercise_2():
    """Call get_weather with a city not in the mocked dataset."""
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_weather", {"city": "Atlantis"})
            print("\n--- Exercise 2: unknown city fallback ---")
            print(result.content[0].text)


async def exercise_3():
    """Point at a wrong server script path and confirm a clear failure, not a hang."""
    print("\n--- Exercise 3: wrong server path ---")
    bad_params = StdioServerParameters(command=sys.executable, args=["nonexistent_server.py"])

    async def _attempt_connection():
        async with stdio_client(bad_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

    try:
        await asyncio.wait_for(_attempt_connection(), timeout=10)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed clearly (as expected): {exc.__class__.__name__}: {exc}")


async def exercise_4():
    """Call get_weather and word_count concurrently with asyncio.gather."""
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            weather_result, count_result = await asyncio.gather(
                session.call_tool("get_weather", {"city": "San Francisco"}),
                session.call_tool("word_count", {"text": "Concurrent MCP tool calls with asyncio.gather"}),
            )
            print("\n--- Exercise 4: concurrent tool calls ---")
            print("Weather:", weather_result.content[0].text)
            print("Word count:", count_result.content[0].text)


async def main():
    await exercise_1()
    await exercise_2()
    await exercise_3()
    await exercise_4()


if __name__ == "__main__":
    asyncio.run(main())
