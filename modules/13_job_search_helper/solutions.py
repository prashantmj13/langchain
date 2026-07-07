"""
Module 13 - Exercise solutions.

Run: python modules/13_job_search_helper/solutions.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from common.embedding_factory import get_embeddings
from common.model_factory import get_chat_model

MODULE_DIR = Path(__file__).resolve().parent
JOBS_DIR = MODULE_DIR / "sample_data" / "jobs"

EXTRA_JOBS = {
    "data_engineer": (
        "Title: Data Engineer\n\n"
        "Build and maintain ETL pipelines moving data into our warehouse (Snowflake). "
        "Requirements: 3+ years with Python and SQL, Airflow or similar orchestration, "
        "experience with dbt. Nice to have: exposure to vector databases and embedding pipelines."
    ),
    "product_manager": (
        "Title: Product Manager\n\n"
        "Own the roadmap for our AI features. Requirements: 4+ years of PM experience, "
        "comfortable writing PRDs, working closely with engineering. Nice to have: "
        "hands-on familiarity with LLM products and prompt engineering."
    ),
    "frontend_engineer_2": (
        "Title: Senior Frontend Engineer\n\n"
        "Lead frontend architecture for our chat UI. Requirements: 5+ years React/TypeScript, "
        "experience streaming LLM responses token-by-token in a UI, strong accessibility background."
    ),
}


def _load_jobs_with_extras() -> list[Document]:
    documents = []
    for path in sorted(JOBS_DIR.glob("*.txt")):
        documents.append(Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name}))
    for name, text in EXTRA_JOBS.items():
        documents.append(Document(page_content=text, metadata={"source": f"{name}.txt"}))
    return documents


def exercise_1():
    """Add 3 more postings (data engineer, product manager, senior frontend); confirm ranking still works."""
    store = FAISS.from_documents(_load_jobs_with_extras(), embedding=get_embeddings())

    ml_resume = (MODULE_DIR / "sample_data" / "resume.txt").read_text(encoding="utf-8")
    print("--- Exercise 1: 6-posting corpus ---")
    for doc, score in store.similarity_search_with_score(ml_resume, k=3):
        print(f"  ({score:.3f}) {doc.metadata['source']}")


PM_RESUME = """Morgan Lee
Product Manager

Summary: 5 years of product management experience, currently leading the AI features
roadmap at a mid-size SaaS company. Comfortable writing PRDs and working daily with
engineering on LLM-powered features, including prompt engineering for a support bot.

Skills: Product strategy, PRDs, roadmapping, LLM product experience, prompt engineering,
stakeholder management, SQL basics.
"""


def exercise_2():
    """A second resume (PM) should match a different job than the ML engineer resume."""
    store = FAISS.from_documents(_load_jobs_with_extras(), embedding=get_embeddings())

    print("\n--- Exercise 2: PM resume matches a different job ---")
    top_match, score = store.similarity_search_with_score(PM_RESUME, k=1)[0]
    print(f"Top match for PM resume: {top_match.metadata['source']} (score {score:.3f})")


class FitAnalysis(BaseModel):
    match_score: int = Field(description="0-100 fit score")
    missing_skills: list[str] = Field(description="Bullet list of skills the candidate is missing")
    explanation: str = Field(description="1-2 sentence explanation of the fit")


def exercise_3():
    """Structured fit analysis: match_score + missing_skills list."""
    llm = get_chat_model()
    structured_llm = llm.with_structured_output(FitAnalysis)

    resume = (MODULE_DIR / "sample_data" / "resume.txt").read_text(encoding="utf-8")
    job = (JOBS_DIR / "ml_engineer.txt").read_text(encoding="utf-8")

    prompt = ChatPromptTemplate.from_messages(
        [("human", "Resume:\n{resume}\n\nJob posting:\n{job}\n\nAnalyze the fit.")]
    )
    chain = prompt | structured_llm

    print("\n--- Exercise 3: structured fit analysis ---")
    print(chain.invoke({"resume": resume, "job": job}))


def exercise_4():
    """Accept a resume PDF via pypdf instead of a plain .txt file."""
    from pypdf import PdfWriter
    import io

    # Generate a tiny in-memory PDF so this exercise runs without needing a real file.
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)

    from pypdf import PdfReader

    reader = PdfReader(buffer)
    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)

    print("\n--- Exercise 4: PDF resume ingestion ---")
    print(f"Extracted {len(extracted_text)} characters from a (blank, demo) PDF.")
    print("In practice: PdfReader('resume.pdf') then feed the extracted text into")
    print("store.similarity_search(extracted_text) exactly like the plain-text resume.")


if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
