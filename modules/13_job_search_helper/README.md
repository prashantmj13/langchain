# 13 — Job Search Helper (capstone project)

## Theory

This module is a small end-to-end project that ties together everything from modules 09-12: embeddings, similarity, and vector stores, plus Claude for generation. There's no new concept here — the point is seeing the pieces work together on a realistic task before formalizing the pattern as "RAG" in [module 16](../16_rag).

Pipeline:
1. **Load** a handful of job postings from `sample_data/jobs/*.txt`.
2. **Embed** each posting and store it in a FAISS vector store ([module 15](../15_faiss_vector_store) covers FAISS specifically).
3. **Embed** a candidate resume (`sample_data/resume.txt`) and run similarity search against the job postings to find the best matches.
4. **Generate** — hand the top match and the resume to Claude and ask it to explain *why* this job is a good fit and what skills gap (if any) the candidate should address.

## Use Case

This is a realistic shape for a "matching" feature: recommend jobs to a candidate, recommend candidates to a recruiter, match support tickets to the right knowledge-base article, match resumes to job descriptions in an ATS. Anywhere you need "find the most relevant items, then explain the match in natural language."

## Walkthrough

`example.py`:
1. Reads all `.txt` files from `sample_data/jobs/`.
2. Builds a FAISS store from them (embedding via `common.embedding_factory`).
3. Reads `sample_data/resume.txt` and searches the store with it as the query.
4. Prints the top 3 matching jobs with similarity scores.
5. Sends the resume + the #1 match to Claude and prints its fit analysis.

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
