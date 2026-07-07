# 11 — Similarity Search

## Theory

Before reaching for a full vector store ([module 12](../12_vector_stores)), it's worth building "search" by hand once: embed a query, embed a set of candidate documents, rank candidates by similarity to the query, take the top-k. This is exactly what a vector store does internally — the store just makes it fast at scale (via approximate-nearest-neighbor indexing) and persistent.

- **Top-k ranking** — sort candidates by similarity score, descending, take the first `k`.
- **Cosine similarity vs. dot product vs. Euclidean distance** — cosine is most common for text embeddings since it ignores vector magnitude; some models (already normalized) let you use a plain dot product as a shortcut for the same ranking.
- **Brute-force vs. approximate** — comparing a query against every document (`O(n)`) is fine for hundreds/thousands of documents; millions need approximate-nearest-neighbor structures like FAISS's indexes ([module 15](../15_faiss_vector_store)).

## Use Case

Small, in-memory candidate sets (a FAQ list, a handful of product descriptions) don't need a full vector database — a `numpy` argsort over cosine similarities is simpler, faster to reason about, and has zero infrastructure.

## Walkthrough

`example.py`:
1. Embeds a small corpus of 6 FAQ-style documents.
2. Embeds a user query.
3. Ranks all 6 by cosine similarity to the query and prints the top 3, with scores.
4. Repeats with a second, unrelated query to show ranking changes.

## Using a different model

Swap the embedding provider via `common.embedding_factory.get_embeddings(provider=...)` — the ranking logic itself never touches the provider.

## Reference Docs

- Cosine similarity: https://en.wikipedia.org/wiki/Cosine_similarity
- LangChain "similarity_search" method (what vector stores do under the hood): https://python.langchain.com/docs/concepts/vectorstores/#similarity-search

## Exercises

1. Add a 7th FAQ document and confirm it's correctly ranked against 3 different test queries.
2. Implement Euclidean distance ranking alongside cosine similarity and check whether the top-3 ordering changes for your corpus.
3. Add a similarity-score threshold (e.g. 0.5) below which no results are returned, and test a query that should return zero matches.
4. Benchmark brute-force search against 10,000 randomly generated vectors and note how latency scales with corpus size.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
