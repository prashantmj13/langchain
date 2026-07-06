"""
Module 23 - MCP HTTP server: the same tools as module 21, served over streamable HTTP.

Run: python modules/23_mcp_http_client/server_http.py
Then, in a separate terminal, run client_http.py.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("utilities-http-server", port=8000)


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
    mcp.run(transport="streamable-http")
