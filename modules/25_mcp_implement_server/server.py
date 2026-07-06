"""
Module 25 - Implement Server: a production-style MCP server combining tools,
resources, and prompts, with logging and input validation, served over HTTP.

Run: python modules/25_mcp_implement_server/server.py
Then, in a separate terminal, run client.py in modules/26_mcp_implement_client.
"""

import logging
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [job-board-server] %(message)s", stream=sys.stderr)
logger = logging.getLogger("job-board-server")

JOBS_DIR = Path(__file__).resolve().parent / "sample_data" / "jobs"

_JOBS: dict[str, str] = {
    path.stem: path.read_text(encoding="utf-8") for path in sorted(JOBS_DIR.glob("*.txt"))
}

mcp = FastMCP("job-board-server", port=8100)


@mcp.tool()
def search_jobs(query: str, k: int = 3) -> list[dict]:
    """Search job postings by keyword overlap and return the top k matches with a snippet."""
    if k > 10:
        raise ValueError("k must be <= 10")

    query_words = set(query.lower().split())
    scored = []
    for job_id, text in _JOBS.items():
        overlap = len(query_words & set(text.lower().split()))
        scored.append((job_id, overlap, text.splitlines()[0]))

    scored.sort(key=lambda item: item[1], reverse=True)
    results = [{"job_id": job_id, "score": score, "title": title} for job_id, score, title in scored[:k]]
    logger.info("search_jobs(query=%r, k=%d) -> %d results", query, k, len(results))
    return results


@mcp.resource("job://{job_id}")
def get_job_posting(job_id: str) -> str:
    """Return the full text of a job posting by id."""
    if job_id not in _JOBS:
        logger.warning("get_job_posting: unknown job_id %r", job_id)
        raise ValueError(f"Unknown job_id '{job_id}'. Available: {list(_JOBS)}")
    return _JOBS[job_id]


@mcp.prompt()
def draft_cover_letter(job_id: str, candidate_name: str) -> str:
    """Build a ready-to-send prompt for drafting a cover letter for a given job."""
    if job_id not in _JOBS:
        raise ValueError(f"Unknown job_id '{job_id}'. Available: {list(_JOBS)}")
    return (
        f"Write a concise, enthusiastic cover letter for {candidate_name} applying to "
        f"this job posting:\n\n{_JOBS[job_id]}"
    )


if __name__ == "__main__":
    logger.info("Loaded %d job postings: %s", len(_JOBS), list(_JOBS))
    mcp.run(transport="streamable-http")
