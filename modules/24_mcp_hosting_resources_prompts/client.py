"""
Module 24 - client demonstrating list_resources/read_resource and list_prompts/get_prompt.

Run: python modules/24_mcp_hosting_resources_prompts/client.py
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).resolve().parent / "server.py"


async def main():
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("--- Reading a resource directly (by known URI) ---")
            resource = await session.read_resource("handbook://sections/time-off")
            print(resource.contents[0].text)

            print("\n--- Listing available prompts ---")
            prompts_response = await session.list_prompts()
            for prompt in prompts_response.prompts:
                print(f"- {prompt.name}: {prompt.description}")

            print("\n--- Fetching a rendered prompt ---")
            rendered = await session.get_prompt("summarize_section", {"section": "remote-work"})
            for message in rendered.messages:
                print(f"[{message.role}] {message.content.text}")


if __name__ == "__main__":
    asyncio.run(main())
