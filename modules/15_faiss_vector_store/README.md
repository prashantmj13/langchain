# 15 — FAISS Vector Store

## Theory

FAISS is different from Chroma (module 12) in one important way: it's not a database program you run separately — it's just a code library that does very fast similarity search, directly inside your own Python program. There's no server to install or manage; you just save its data as a couple of files on disk when you're done, and load them back later.

- **Different search modes for different sizes of data.** For a small or medium number of documents, FAISS can check every single one and get an exact answer. For millions of documents, it switches to faster approximate methods that are nearly as accurate but far quicker. This repo's examples are small enough to use the simple, exact method.
- **Saving and loading.** `.save_local(folder)` writes your search index to a couple of files on disk; loading them back later is instant — it doesn't need to redo any of the embedding work, it just reads the saved numbers straight from disk.
- **No built-in filtering by extra info.** Chroma lets you filter results by metadata (like "only search within category X") as part of the search itself. FAISS doesn't do this natively — LangChain's wrapper fetches candidates first and then filters them in plain Python, which works fine at small scale but isn't as efficient for huge datasets with heavy filtering.
- **Only load files you trust.** Loading a saved FAISS index runs some of Python's built-in "reconstruct an object from a file" machinery, which is a well-known way to accidentally run malicious code if the file came from someone you don't trust. Only load index files you created yourself, or that came from someone you trust.

## Use Case

FAISS shines for local prototyping, offline batch jobs, and any scenario where you want vector search with zero external services (e.g. bundling a small search index inside a CLI tool or a serverless function). [Module 13](../13_job_search_helper) and [module 16](../16_rag) both use FAISS for exactly this reason.

## How to Run

```bash
python modules/15_faiss_vector_store/example.py
python modules/15_faiss_vector_store/solutions.py   # exercise solutions
```
Requires an embeddings provider key. Writes a `faiss_index/` (or `faiss_index_solutions/`) folder into this directory containing `index.faiss` + `index.pkl` — gitignored; delete it anytime to force a clean rebuild (exercise 1 does this explicitly).

## Walkthrough

`example.py`:
1. Builds a FAISS index from a handful of documents.
2. Saves it to `./faiss_index/` on disk.
3. Reloads it in a fresh `FAISS.load_local(...)` call (simulating a new process) and confirms search still works without re-embedding.
4. Adds a new document to the reloaded index at runtime and re-saves.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `FAISS.from_documents(docs, embedding=...)` | Embeds the documents and builds a new, in-memory FAISS index (same pattern as `Chroma`/module 12, different vector store). | Used in `build_and_save()` to create the initial index before it's ever touched disk. |
| `.save_local(folder)` | Writes the index's data to two files (`index.faiss`, `index.pkl`) in the given folder. | Used after building and after adding a new document, so the index survives past this one script run. |
| `FAISS.load_local(folder, embeddings, allow_dangerous_deserialization=True)` | Reads a previously-saved index back from disk, ready to search immediately. | Used in `load_from_disk()` to simulate a fresh process picking up the index without re-embedding anything — see this module's Theory for why the `allow_dangerous_deserialization` flag exists. |
| `.add_documents([...])` | Embeds one or more new documents and adds them to an existing, already-built store. | Used to show that a FAISS store can grow after creation — you don't have to rebuild the whole index from scratch to add one more document. |

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
