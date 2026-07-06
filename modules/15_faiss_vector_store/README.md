# 15 — FAISS Vector Store

## Theory

FAISS (Facebook AI Similarity Search) is a **library**, not a database server — it's an in-process, highly optimized nearest-neighbor search index that you save to / load from local disk as flat files. That makes it the simplest possible way to get real vector search without standing up any infrastructure. Key concepts specific to FAISS:

- **Index types** — `IndexFlatL2`/`IndexFlatIP` do exact brute-force search (small/medium corpora); `IndexIVFFlat`/`HNSW` trade a small accuracy loss for much faster search on millions of vectors. LangChain's `FAISS.from_documents(...)` uses a flat index by default.
- **Local persistence** — `.save_local(folder)` writes an `index.faiss` + `index.pkl` pair; `FAISS.load_local(folder, embeddings, allow_dangerous_deserialization=True)` reloads without re-embedding anything.
- **No metadata filtering server-side** — unlike Chroma, FAISS itself has no query language for metadata; LangChain's wrapper filters in Python after retrieving candidates, so it's less efficient for heavy metadata filtering at scale.
- **`allow_dangerous_deserialization`** — loading a FAISS index unpickles Python objects; only load index files you created/trust.

## Use Case

FAISS shines for local prototyping, offline batch jobs, and any scenario where you want vector search with zero external services (e.g. bundling a small search index inside a CLI tool or a serverless function). [Module 13](../13_job_search_helper) and [module 16](../16_rag) both use FAISS for exactly this reason.

## Walkthrough

`example.py`:
1. Builds a FAISS index from a handful of documents.
2. Saves it to `./faiss_index/` on disk.
3. Reloads it in a fresh `FAISS.load_local(...)` call (simulating a new process) and confirms search still works without re-embedding.
4. Adds a new document to the reloaded index at runtime and re-saves.

## Using a different model

Only the embedding function passed to `FAISS.from_documents(...)`/`FAISS.load_local(...)` changes; swap via `common.embedding_factory.get_embeddings(provider=...)`. Note: an index built with one embedding model's vectors is **not** compatible with a different embedding model at load time (dimensions/semantics won't match) — always reload with the same provider that built the index.

## Reference Docs

- LangChain FAISS integration: https://python.langchain.com/docs/integrations/vectorstores/faiss/
- FAISS project (Meta AI): https://github.com/facebookresearch/faiss
- FAISS index types guide: https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index

## Exercises

1. Delete the on-disk `faiss_index/` folder and re-run the script to confirm it rebuilds cleanly from scratch.
2. Add a `delete()` call to remove a document by id and confirm it no longer appears in search after re-saving and reloading.
3. Try loading the saved index with a *different* embedding provider than the one that built it, and observe what goes wrong (either an error or nonsensical results).
4. Build an index from 5,000 short synthetic strings and measure `similarity_search` latency versus the 4-document demo index.
