# Module 11 — Internals

This module doesn't introduce new LangChain classes — `.embed_documents()`/`.embed_query()` are covered in [module 09's INTERNALS.md](../09_embeddings_theory/INTERNALS.md), and `cosine_similarity()` is the same hand-written function from that module. What's worth a closer look here is the ranking step itself, since that's the actual "search" in this module's title.

## The ranking pattern: score, then sort, then slice

**How it works internally:**
```python
scored = [(doc, cosine_similarity(query_vector, doc_vector)) for doc, doc_vector in zip(DOCUMENTS, doc_vectors)]
scored.sort(key=lambda pair: pair[1], reverse=True)
return scored[:k]
```
1. `zip(DOCUMENTS, doc_vectors)` pairs each document with its corresponding embedding vector, walking both lists in lockstep — this only works correctly because `doc_vectors` was built by embedding `DOCUMENTS` in the same order, via `embed_documents(DOCUMENTS)` (a list comprehension preserves input order, which is what makes this pairing valid).
2. The list comprehension computes a `(document, score)` tuple for every document — this is `O(n)`, one similarity calculation per document, which is exactly the "brute-force" search this module's Theory section describes (as opposed to FAISS's indexed search in module 15).
3. `list.sort(key=..., reverse=True)` is Python's built-in sort — `key=lambda pair: pair[1]` tells it to sort by the score (the second element of each tuple), and `reverse=True` puts the highest scores first. Python's sort is stable and runs in `O(n log n)`.
4. `[:k]` is a plain list slice, taking just the first `k` entries after sorting — the "top-k" in "top-k search."

This whole pattern — embed everything, score everything, sort, slice — is exactly what a vector store's `.similarity_search()` (module 12) does internally too; the difference is that a real vector store uses an *index* (a data structure built ahead of time) so it doesn't have to re-score every single document on every single query.

**How to validate each step independently:**
```python
# Confirm zip() pairs things correctly:
for doc, vec in zip(DOCUMENTS[:2], doc_vectors[:2]):
    print(doc[:30], "->", vec[:3])   # first 3 numbers of each vector, just to eyeball alignment

# Confirm sort direction is correct (should be descending):
scored = [(doc, cosine_similarity(query_vector, v)) for doc, v in zip(DOCUMENTS, doc_vectors)]
scored.sort(key=lambda pair: pair[1], reverse=True)
scores_only = [score for _, score in scored]
print(scores_only == sorted(scores_only, reverse=True))  # True -- confirms it's sorted highest-first
```
