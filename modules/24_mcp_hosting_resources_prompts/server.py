"""
Module 24 - Hosting Resources & Prompts: extends the module 21 server with
@mcp.resource and @mcp.prompt, not just tools.

Run: python modules/24_mcp_hosting_resources_prompts/server.py
(meant to be launched by client.py, same stdio pattern as module 22)
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("handbook-server")

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
    """Return the text of one handbook section (time-off, remote-work, or expenses)."""
    return SECTIONS.get(section, f"No section named '{section}'. Available: {list(SECTIONS)}")


@mcp.prompt()
def summarize_section(section: str) -> str:
    """Build a ready-to-send prompt asking the model to summarize a handbook section."""
    return (
        f"Summarize the '{section}' policy from the employee handbook in exactly "
        f"one sentence, suitable for a new-hire FAQ."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
