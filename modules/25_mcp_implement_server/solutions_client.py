"""
Module 25 - Exercise solutions: a client exercising the extended job-board server.

Run: python modules/25_mcp_implement_server/solutions_client.py
"""

import asyncio
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

            print("--- Exercise 2: semantic search_jobs ---")
            result = await session.call_tool("search_jobs", {"query": "LangChain and FAISS experience", "k": 2})
            print(result.content[0].text)

            print("\n--- Exercise 3: validation errors ---")
            for bad_args in [{"query": "", "k": 2}, {"query": "engineer", "k": 0}, {"query": "engineer", "k": 20}]:
                result = await session.call_tool("search_jobs", bad_args)
                print(f"{bad_args} -> isError={result.isError}, {result.content[0].text}")

            print("\n--- Exercise 4: job summary resource ---")
            summary = await session.read_resource("job://ml_engineer/summary")
            print(summary.contents[0].text)

            print("\n--- Exercise 1: check server.log was written ---")
            log_path = Path(__file__).resolve().parent / "server.log"
            print(f"{log_path} exists: {log_path.exists()}")


if __name__ == "__main__":
    asyncio.run(main())
