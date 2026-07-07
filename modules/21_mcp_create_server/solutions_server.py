"""
Module 21 - Exercise solutions: an extended server covering exercises 1-3.

This server is launched by solutions_client.py, which also covers exercise 4
(reading the generated tool schema).
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("utilities-server-solutions")

WEATHER_DATA = {
    "san francisco": {"celsius": "17C, foggy", "fahrenheit": "62F, foggy"},
    "new york": {"celsius": "22C, partly cloudy", "fahrenheit": "71F, partly cloudy"},
    "tokyo": {"celsius": "26C, clear skies", "fahrenheit": "78F, clear skies"},
}


@mcp.tool()
def get_weather(city: str, units: str = "celsius") -> str:
    """Return a (mocked) current weather summary for the given city, in celsius or fahrenheit."""
    if not city.strip():
        raise ValueError("city must not be empty.")
    if units not in ("celsius", "fahrenheit"):
        raise ValueError("units must be 'celsius' or 'fahrenheit'.")

    entry = WEATHER_DATA.get(city.lower())
    if entry is None:
        return f"No weather data available for '{city}'."
    return entry[units]


@mcp.tool()
def word_count(text: str) -> int:
    """Count the number of whitespace-separated words in the given text."""
    return len(text.split())


@mcp.tool()
def to_uppercase(text: str) -> str:
    """Return the given text converted to uppercase (exercise 1)."""
    return text.upper()


if __name__ == "__main__":
    mcp.run(transport="stdio")
