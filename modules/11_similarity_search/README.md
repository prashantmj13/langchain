# 11 — Similarity Search

## Theory

Before reaching for a dedicated search tool ([module 12](../12_vector_stores)), it's worth doing "search" by hand once, so you can see exactly what's happening: turn your search question into an embedding, turn every candidate document into an embedding too, measure how close each candidate is to the question, and keep the closest few. That's genuinely all a vector database does internally — it just does this same simple idea much faster and at a much bigger scale.

- **Keeping the top few, not everything.** Once every candidate has a similarity score, you sort them from most similar to least, and just keep the top handful (say, the top 3) — those are your search results.
- **Different ways to measure "closeness."** Cosine similarity (from module 09) is the most common way to compare two embeddings for text search. There are other formulas too, but they usually agree closely enough that it rarely matters which one you pick.
- **Checking every candidate works fine — until it doesn't.** Comparing your question against every single document one by one is perfectly fast for a few hundred or thousand documents. Once you have millions, that becomes too slow, and you need smarter, index-based search structures instead (that's what [FAISS in module 15](../15_faiss_vector_store) is for).

## Use Case

Small, in-memory candidate sets (a FAQ list, a handful of product descriptions) don't need a full vector database — a `numpy` argsort over cosine similarities is simpler, faster to reason about, and has zero infrastructure.

## How to Run

```bash
python modules/11_similarity_search/example.py
python modules/11_similarity_search/solutions.py   # exercise solutions
```
Requires an embeddings provider key (`VOYAGE_API_KEY` by default). The script embeds the whole document list once per query, ranks by cosine similarity in plain Python/`numpy` (no vector database involved), and prints the top-k matches with their scores.

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
