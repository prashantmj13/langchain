"""
Module 21 - Exercise solutions: a client verifying the extended server's behavior.

Run: python modules/21_mcp_create_server/solutions_client.py
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).resolve().parent / "solutions_server.py"


async def main():
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("--- Exercise 1: to_uppercase appears in list_tools() ---")
            tools = (await session.list_tools()).tools
            print([t.name for t in tools])

            print("\n--- Exercise 2: get_weather with an empty city raises an error ---")
            try:
                await session.call_tool("get_weather", {"city": ""})
            except Exception as exc:  # noqa: BLE001
                print(f"Error surfaced to client: {exc}")

            print("\n--- Exercise 3: units parameter (default vs explicit) ---")
            default_result = await session.call_tool("get_weather", {"city": "Tokyo"})
            explicit_result = await session.call_tool("get_weather", {"city": "Tokyo", "units": "fahrenheit"})
            print("default (celsius):", default_result.content[0].text)
            print("explicit fahrenheit:", explicit_result.content[0].text)

            print("\n--- Exercise 4: full generated schema for get_weather ---")
            weather_tool = next(t for t in tools if t.name == "get_weather")
            print(json.dumps(weather_tool.inputSchema, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
