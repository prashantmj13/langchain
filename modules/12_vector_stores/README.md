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
3. Runs `max_marginal_relevance_search` on a query where the corpus has near-duplicate documents, to show it picking a more varied result set than plain similarity search would.
4. Runs a `similarity_search` filtered down to documents whose `category` metadata equals `"billing"`, to show searching within a subset instead of the whole store.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `Document(page_content=..., metadata={...})` | LangChain's standard wrapper for a piece of text plus any extra structured info about it. | Used to attach a `category` to each FAQ entry, so later searches can filter by it, not just by text similarity. |
| `Chroma.from_documents(docs, embedding=...)` | Embeds a list of documents and builds a new Chroma vector store from them in one call. | The simplest way to get a populated vector store — used in `build_store()` instead of creating an empty store and adding documents separately. |
| `.similarity_search(query, k=2)` | Returns the `k` documents most similar to the query. | The most basic vector store operation — used first to establish the baseline before showing the fancier search modes. |
| `.similarity_search_with_score(query, k=2)` | Same as above, but also returns each result's similarity score. | Used to show that scores are available when you need to know *how* similar a result is, not just its rank. |
| `.max_marginal_relevance_search(query, k=2, fetch_k=4)` | Returns `k` results chosen to be relevant *and* different from each other, by first considering `fetch_k` candidates. | Used to demonstrate avoiding near-duplicate results — the module's two password-reset FAQ entries would otherwise both show up for a password query. |
| `.similarity_search(query, k=2, filter={"category": "billing"})` | Same as `.similarity_search()`, but only considers documents whose metadata matches the filter. | Used to show narrowing a search to one category instead of searching the entire store. |

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
