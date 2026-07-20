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

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `.embed_documents(DOCUMENTS)` | Embeds the whole list of candidate documents in one call. | Used once, outside the query loop, so we don't re-embed the same fixed documents for every new query. |
| `.embed_query(query)` | Embeds a single piece of text — the query — the same way as a document, so the two are comparable. | Used to turn the user's question into a vector we can compare against every document's vector. |
| `sorted(..., key=..., reverse=True)` / `list.sort()` (plain Python, not LangChain) | Orders a list by a computed value, highest first. | Used to rank documents by similarity score and keep only the top `k` — this is the "search" part of similarity search, done by hand instead of by a vector database. |

For a step-by-step breakdown of the score/sort/slice ranking pattern (the same pattern a real vector store uses internally) — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

Swap the embedding provider via `common.embedding_factory.get_embeddings(provider=...)` — the ranking logic itself never touches the provider.

## Reference Docs

- Cosine similarity: https://en.wikipedia.org/wiki/Cosine_similarity
- LangChain "similarity_search" method (what vector stores do under the hood): https://python.langchain.com/docs/concepts/vectorstores/#similarity-search

## Exercises

1. **Growing the corpus and re-testing.** Add a 7th document to `example.py`'s `DOCUMENTS` list (write your own FAQ-style sentence about a new topic, e.g. account cancellation). Run `top_k()` with 3 different test queries — including at least one that should clearly match your new document — and confirm it shows up in the results when relevant, and doesn't show up when it isn't.
2. **Comparing distance metrics.** This module's `top_k()` ranks by cosine similarity. Write a second scoring function using Euclidean distance instead (`np.linalg.norm(a - b)` — note: for Euclidean distance, *lower* means more similar, the opposite of cosine similarity's *higher* means more similar). Rank the same corpus with both metrics for the same query and compare the top-3 results — do they come out in the same order?
3. **Rejecting weak matches instead of always returning `k` results.** Modify `top_k()` (or write a new version) so it only returns documents whose similarity score is above a threshold you choose (start with `0.5`) — even if that means returning fewer than `k` results, or zero. Test it with a query that's completely unrelated to anything in your corpus (e.g. "what's the weather like today?") and confirm you get zero results back instead of 3 weak, irrelevant ones.
4. **How does search time scale with corpus size?** Using `numpy`'s random number generation (`np.random.default_rng(42).random((10000, 384))` gives you 10,000 fake 384-dimensional vectors), time how long a brute-force cosine-similarity search against all 10,000 takes, using `time.perf_counter()`. Compare that to how fast it was against this module's 6-document corpus — this is the scaling problem that justifies FAISS (module 15) once your corpus gets big.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
