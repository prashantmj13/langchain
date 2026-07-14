# 13 — Job Search Helper (capstone project)

## Theory

Nothing new to learn here — this module just takes everything from modules 09-12 (embeddings, similarity search, vector stores) and Claude, and puts them together on one realistic task, so you can see how they combine before we give this combination a name ("RAG") in [module 16](../16_rag).

Here's the full pipeline, step by step:
1. **Load** a handful of sample job postings from text files.
2. **Turn each posting into an embedding** and store all of them in a FAISS vector store ([module 15](../15_faiss_vector_store) explains FAISS specifically).
3. **Turn a candidate's resume into an embedding too**, and search the stored job postings to find which ones are the closest match.
4. **Ask Claude to explain the match** — hand it the resume and the best-matching job, and have it write a short explanation of why this job fits, and what skills (if any) the candidate is missing.

## Use Case

This is a realistic shape for a "matching" feature: recommend jobs to a candidate, recommend candidates to a recruiter, match support tickets to the right knowledge-base article, match resumes to job descriptions in an ATS. Anywhere you need "find the most relevant items, then explain the match in natural language."

## How to Run

```bash
python modules/13_job_search_helper/example.py
python modules/13_job_search_helper/solutions.py   # exercise solutions
```
Requires both an embeddings key (`VOYAGE_API_KEY`) and `ANTHROPIC_API_KEY`. The FAISS index here is built fresh in memory on every run from `sample_data/jobs/*.txt` — nothing is persisted to disk, so there's no state to clean up between runs.

## Walkthrough

`example.py`:
1. Reads all `.txt` files from `sample_data/jobs/`.
2. Builds a FAISS store from them (embedding via `common.embedding_factory`).
3. Reads `sample_data/resume.txt` and searches the store with it as the query.
4. Prints the top 3 matching jobs with similarity scores.
5. Sends the resume + the #1 match to Claude and prints its fit analysis.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `FAISS.from_documents(docs, embedding=...)` | Embeds a list of documents and builds a new FAISS index from them in one call (same pattern as `Chroma.from_documents` in module 12, different vector store underneath). | Used in `build_job_store()` to turn the job postings into a searchable index. |
| `.similarity_search_with_score(resume_text, k=3)` | Searches using the whole resume text as the query, returning the top 3 most similar postings plus their scores. | Used to find which job postings are the closest semantic match to the resume — this is the "matching" in "job matching." |
| `Document(page_content=..., metadata={"source": ...})` | Wraps each job posting's text with a metadata tag naming which file it came from. | Used so the results can report *which* job posting matched, not just the raw matching text. |
| `prompt \| llm` then `.invoke(...).content` | Builds a chain and calls it, taking just the plain-text answer. | Used in `explain_fit()` to ask Claude to explain the match in a few sentences, once we already know *which* job is the best match. |

## Using a different model

- Swap the embedding provider via `EMBEDDING_PROVIDER` (Voyage/OpenAI/HuggingFace) — matching quality will vary since providers embed differently.
- Swap the "explain the fit" generation step via `get_chat_model(provider=...)` exactly as in earlier modules.

## Reference Docs

- FAISS vector store integration: https://python.langchain.com/docs/integrations/vectorstores/faiss/
- RAG concept overview (the general pattern this project is a preview of): https://python.langchain.com/docs/concepts/rag/

## Exercises

1. Add 3 more sample job postings covering different roles (e.g. data engineer, product manager) and confirm the matcher still ranks correctly for a matching resume.
2. Add a second sample resume for a different role and verify it matches a *different* job than the first resume.
3. Change the generation step to also output a `match_score: 0-100` and a bullet list of missing skills, using `.with_structured_output()`.
4. Extend the pipeline to accept a resume PDF (via `pypdf`) instead of a plain `.txt` file.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
