"""
Module 13 - Job Search Helper (capstone): embeddings + FAISS + Claude generation.

Run: python modules/13_job_search_helper/example.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from common.embedding_factory import get_embeddings
from common.model_factory import get_chat_model

MODULE_DIR = Path(__file__).resolve().parent
JOBS_DIR = MODULE_DIR / "sample_data" / "jobs"
RESUME_PATH = MODULE_DIR / "sample_data" / "resume.txt"


def load_jobs() -> list[Document]:
    documents = []
    for path in sorted(JOBS_DIR.glob("*.txt")):
        documents.append(Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name}))
    return documents


def build_job_store() -> FAISS:
    embeddings_model = get_embeddings()
    return FAISS.from_documents(load_jobs(), embedding=embeddings_model)


def explain_fit(resume: str, job_posting: str) -> str:
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "A candidate's resume:\n\n{resume}\n\n"
                "A job posting:\n\n{job}\n\n"
                "In 3-4 sentences, explain why this is (or isn't) a good match, "
                "and name one skill gap the candidate should address, if any.",
            )
        ]
    )
    chain = prompt | llm
    return chain.invoke({"resume": resume, "job": job_posting}).content


if __name__ == "__main__":
    resume_text = RESUME_PATH.read_text(encoding="utf-8")
    store = build_job_store()

    print("--- Top matching jobs for the resume ---")
    matches = store.similarity_search_with_score(resume_text, k=3)
    for doc, score in matches:
        title_line = doc.page_content.splitlines()[0]
        print(f"  ({score:.3f}) {doc.metadata['source']:<25} {title_line}")

    top_job = matches[0][0]
    print(f"\n--- Fit analysis for top match: {top_job.metadata['source']} ---")
    print(explain_fit(resume_text, top_job.page_content))
