"""
Module 23 - Exercise solutions.

Exercises 1 and 2 require the server running (see instructions printed below);
exercises 3 and 4 are demonstrated/discussed here directly.

Run: python modules/23_mcp_http_client/solutions.py
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def call_server(url: str, label: str):
    async with streamablehttp_client(url) as (read, write, _get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_weather", {"city": "Tokyo"})
            print(f"[{label}] {result.content[0].text}")


async def exercise_1_and_2():
    """
    Exercise 1: change the server port (8000 -> 8010).
        In server_http.py: FastMCP("utilities-http-server", port=8010)
        In client_http.py: SERVER_URL = "http://127.0.0.1:8010/mcp"

    Exercise 2: two concurrent client connections to the same server, both get
    correct independent responses (MCP servers handle concurrent sessions).

    Start server_http.py first (`python modules/23_mcp_http_client/server_http.py`),
    then run this script.
    """
    print("--- Exercises 1 & 2: concurrent clients (requires server_http.py running) ---")
    try:
        await asyncio.gather(
            call_server("http://127.0.0.1:8000/mcp", "client-A"),
            call_server("http://127.0.0.1:8000/mcp", "client-B"),
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Skipped -- start server_http.py first. ({exc.__class__.__name__}: {exc})")


async def exercise_3():
    """Clear error handling for 'server not running' (connection refused)."""
    print("\n--- Exercise 3: server-not-running error handling ---")
    try:
        async with streamablehttp_client("http://127.0.0.1:9999/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
    except Exception as exc:  # noqa: BLE001
        print(f"Could not connect (server not running on port 9999): {exc.__class__.__name__}")
        print("A production client should catch this and retry with backoff, or surface a clear error to the caller.")


def exercise_4():
    """
    Exercise 4: kill the client (Ctrl+C) mid-request and confirm the HTTP
    server keeps running -- unlike module 22's stdio server, which dies with
    its client because the client is the one that spawned it as a subprocess.

    This is a manual test: start server_http.py, start this script, hit
    Ctrl+C on THIS script while it's mid-request, then run client_http.py
    again separately and confirm the server still answers.
    """
    print("\n--- Exercise 4 ---")
    print("Manual test -- see the docstring in solutions.py for steps.")


if __name__ == "__main__":
    asyncio.run(exercise_1_and_2())
    asyncio.run(exercise_3())
    exercise_4()
