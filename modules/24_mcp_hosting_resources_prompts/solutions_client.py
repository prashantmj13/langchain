"""
Module 24 - Exercise solutions: a client exercising the extended server.

Run: python modules/24_mcp_hosting_resources_prompts/solutions_client.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from common.model_factory import get_chat_model

SERVER_SCRIPT = Path(__file__).resolve().parent / "solutions_server.py"


async def main():
    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("--- Exercise 1: full-handbook resource ---")
            full = await session.read_resource("handbook://full")
            print(full.contents[0].text[:200], "...")

            print("\n--- Exercise 2: default vs explicit tone ---")
            default_prompt = await session.get_prompt("summarize_section", {"section": "time-off"})
            casual_prompt = await session.get_prompt(
                "summarize_section", {"section": "time-off", "tone": "casual and upbeat"}
            )
            print("default:", default_prompt.messages[0].content.text)
            print("casual: ", casual_prompt.messages[0].content.text)

            print("\n--- Exercise 3: list + fetch all static resources ---")
            resources = (await session.list_resources()).resources
            for resource in resources:
                content = await session.read_resource(resource.uri)
                byte_length = len(content.contents[0].text.encode("utf-8"))
                print(f"{resource.uri}: {byte_length} bytes")

            print("\n--- Exercise 4: send a fetched prompt's messages to Claude ---")
            rendered = await session.get_prompt("summarize_section", {"section": "remote-work"})
            llm = get_chat_model()
            claude_messages = [HumanMessage(content=m.content.text) for m in rendered.messages]
            response = llm.invoke(claude_messages)
            print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
