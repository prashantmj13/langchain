"""
Module 21 - Create MCP Server: a minimal FastMCP server exposing two tools over stdio.

This script is meant to be launched by an MCP client (see modules/22_mcp_stdio_client),
not run standalone for output -- but running it directly will start the server and
block, listening on stdin/stdout, which confirms it's wired up correctly (Ctrl+C to stop).
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("utilities-server")


@mcp.tool()
def get_weather(city: str) -> str:
    """Return a (mocked) current weather summary for the given city."""
    fake_data = {
        "san francisco": "62F, foggy",
        "new york": "71F, partly cloudy",
        "tokyo": "78F, clear skies",
    }
    return fake_data.get(city.lower(), f"No weather data available for '{city}'.")


@mcp.tool()
def word_count(text: str) -> int:
    """Count the number of whitespace-separated words in the given text."""
    return len(text.split())


if __name__ == "__main__":
    mcp.run(transport="stdio")
