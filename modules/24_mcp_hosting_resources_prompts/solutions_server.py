"""
Module 24 - Exercise solutions: an extended server covering exercises 1-2.

Launched by solutions_client.py, which also covers exercises 3-4.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("handbook-server-solutions")

SECTIONS = {
    "time-off": (
        "Full-time employees accrue 15 days of PTO per year, accrued monthly. "
        "Requests must be submitted 5 business days in advance. Up to 5 unused "
        "days carry over into the next year; the rest is forfeited on Dec 31st."
    ),
    "remote-work": (
        "Employees may work remotely up to 3 days per week. Fully remote "
        "arrangements require manager approval, reviewed quarterly. Remote "
        "employees must be reachable 10am-3pm local time."
    ),
    "expenses": (
        "Business expenses must be submitted within 30 days with an itemized "
        "receipt. Reimbursements process within 2 pay cycles. Travel meals are "
        "reimbursed up to $75/day."
    ),
}


@mcp.resource("handbook://sections/{section}")
def get_handbook_section(section: str) -> str:
    """Return the text of one handbook section."""
    return SECTIONS.get(section, f"No section named '{section}'. Available: {list(SECTIONS)}")


@mcp.resource("handbook://full")
def get_full_handbook() -> str:
    """Return the full handbook text, all sections concatenated (exercise 1)."""
    return "\n\n".join(f"## {name}\n{text}" for name, text in SECTIONS.items())


@mcp.prompt()
def summarize_section(section: str, tone: str = "neutral") -> str:
    """Build a prompt asking the model to summarize a section in a given tone (exercise 2)."""
    return (
        f"Summarize the '{section}' policy from the employee handbook in exactly "
        f"one sentence, in a {tone} tone, suitable for a new-hire FAQ."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
