# 12 — Vector Stores

## Theory

A **vector store** is a database purpose-built to store embeddings alongside their source text/metadata, and to answer "give me the k most similar vectors to this query vector" efficiently — the same operation you did by hand in [module 11](../11_similarity_search), but indexed for speed and persisted to disk/a server instead of recomputed in a Python list every time.

LangChain's `VectorStore` interface standardizes this across dozens of backends:
- `add_texts(texts, metadatas)` / `add_documents(documents)` — ingest.
- `similarity_search(query, k)` — plain nearest-neighbor search.
- `similarity_search_with_score(query, k)` — same, with distance/similarity scores attached.
- `max_marginal_relevance_search` (MMR) — nearest-neighbor search that also penalizes redundancy, so results aren't all near-duplicates of each other.
- `.as_retriever()` — wraps the store as a `Runnable` retriever, the bridge into chains ([module 14](../14_retrieval)).

This module uses an in-memory `Chroma` collection as a general-purpose introduction; [module 15](../15_faiss_vector_store) does a dedicated deep dive on FAISS specifically (a library rather than a full database, optimized for raw ANN search speed).

## Use Case

Any RAG system, semantic search feature, or recommendation engine that needs to search over more documents than comfortably fit in a Python list, or needs the results to persist across process restarts.

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
