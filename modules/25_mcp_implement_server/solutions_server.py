"""
Module 25 - Exercise solutions: an extended job-board server covering exercises 1, 2, 3, 4.

Uses stdio transport (instead of HTTP like server.py) so solutions_client.py can
launch and test it in a single self-contained run, without needing two terminals.
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import numpy as np
from mcp.server.fastmcp import FastMCP

from common.embedding_factory import get_embeddings

LOG_FILE = Path(__file__).resolve().parent / "server.log"
JOBS_DIR = Path(__file__).resolve().parent / "sample_data" / "jobs"

# Exercise 1: log to a file, not just stderr.
logger = logging.getLogger("job-board-server-solutions")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(LOG_FILE))
logger.addHandler(logging.StreamHandler(sys.stderr))

_JOBS: dict[str, str] = {path.stem: path.read_text(encoding="utf-8") for path in sorted(JOBS_DIR.glob("*.txt"))}

# Exercise 2: real semantic search via common/embedding_factory.py, embedded once at startup.
_embeddings_model = get_embeddings()
_job_ids = list(_JOBS)
_job_vectors = {
    job_id: np.array(vec) for job_id, vec in zip(_job_ids, _embeddings_model.embed_documents(list(_JOBS.values())))
}


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


mcp = FastMCP("job-board-server-solutions")


@mcp.tool()
def search_jobs(query: str, k: int = 3) -> list[dict]:
    """Semantically search job postings and return the top k matches with a snippet."""
    # Exercise 3: bounds/validation (the k > 10 upper bound already existed in server.py;
    # this rounds it out with a lower bound and an empty-query check).
    if not query.strip():
        raise ValueError("query must not be empty.")
    if k > 10:
        raise ValueError("k must be <= 10")
    if k < 1:
        raise ValueError("k must be >= 1")

    query_vector = np.array(_embeddings_model.embed_query(query))
    scored = [
        (job_id, _cosine_similarity(query_vector, vector), _JOBS[job_id].splitlines()[0])
        for job_id, vector in _job_vectors.items()
    ]
    scored.sort(key=lambda item: item[1], reverse=True)

    results = [{"job_id": job_id, "score": round(score, 3), "title": title} for job_id, score, title in scored[:k]]
    logger.info("search_jobs(query=%r, k=%d) -> %d results", query, k, len(results))
    return results


@mcp.resource("job://{job_id}")
def get_job_posting(job_id: str) -> str:
    """Return the full text of a job posting by id."""
    if job_id not in _JOBS:
        raise ValueError(f"Unknown job_id '{job_id}'. Available: {list(_JOBS)}")
    return _JOBS[job_id]


@mcp.resource("job://{job_id}/summary")
def get_job_summary(job_id: str) -> str:
    """Return just the title line of a job posting (exercise 4)."""
    if job_id not in _JOBS:
        raise ValueError(f"Unknown job_id '{job_id}'. Available: {list(_JOBS)}")
    return _JOBS[job_id].splitlines()[0]


if __name__ == "__main__":
    logger.info("Loaded %d job postings: %s", len(_JOBS), list(_JOBS))
    mcp.run(transport="stdio")
