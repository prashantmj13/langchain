# 12 — Vector Stores

## Theory

A **vector store** is just a database built specifically for the "find the most similar items" search from [module 11](../11_similarity_search) — except it's fast even with millions of documents, and it remembers everything even after your program stops running (module 11's version forgot everything the moment the script ended).

LangChain gives every vector store the same set of buttons, no matter which one you use underneath:
- **Add documents to it** — hand it your texts (and any extra info about them), and it embeds and stores them for you.
- **Search it** — give it a question, get back the most similar documents, optionally along with a similarity score for each.
- **Search it while avoiding near-duplicates** — sometimes the top results are all nearly the same document repeated; this search mode deliberately picks a more varied set of results instead.
- **Plug it into a chain** — turn the vector store into something that fits directly into the `|` pipelines from module 03, which is the bridge into [module 14 (Retrieval)](../14_retrieval).

This module uses Chroma (a simple, general-purpose vector store) to introduce the ideas; [module 15](../15_faiss_vector_store) goes deep on FAISS specifically, a related but different tool built purely for very fast search.

## Use Case

Any RAG system, semantic search feature, or recommendation engine that needs to search over more documents than comfortably fit in a Python list, or needs the results to persist across process restarts.

## How to Run

```bash
python modules/12_vector_stores/example.py
python modules/12_vector_stores/solutions.py   # exercise solutions
```
Requires an embeddings provider key. The Chroma collection here is in-memory by default (the `solutions.py` persistence exercise writes a `chroma_db_demo/` folder into this directory — gitignored, safe to delete).

## Walkthrough

`example.py`:
1. Creates an in-memory Chroma vector store from a small set of documents (with metadata like `category`).
2. Runs `similarity_search` and `similarity_search_with_score`.
3. Runs `max_marginal_relevance_search` and compares its result set to plain similarity search on a query where the corpus has near-duplicate documents.
4. Deletes a document and confirms it no longer appears in search results.

## Using a different model

The vector store's embedding function is whatever `common.embedding_factory.get_embeddings()` returns — swap providers there; the vector store code itself is unaffected.

## Reference Docs

- Vector stores concept: https://python.langchain.com/docs/concepts/vectorstores/
- Chroma integration: https://python.langchain.com/docs/integrations/vectorstores/chroma/
- MMR search: https://python.langchain.com/docs/how_to/example_selectors_mmr/

## Exercises

1. Add metadata filtering: search only within documents where `category == "billing"`.
2. Compare `similarity_search` vs. `max_marginal_relevance_search` (`k=4, fetch_k=10`) on a corpus with 3 near-duplicate documents about the same topic.
3. Persist the Chroma store to disk (`persist_directory=...`), restart the script, and confirm the data survives without re-embedding.
4. Add a document, update its content in place, and confirm search results reflect the update (Chroma requires delete + re-add, not a true update — verify this).

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
