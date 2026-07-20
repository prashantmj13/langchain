# Module 09 — Internals

## The `Embeddings` interface (`.embed_documents()` / `.embed_query()`)

**What it is:** An abstract base class every embedding provider implements — `VoyageAIEmbeddings`, `OpenAIEmbeddings`, `HuggingFaceEmbeddings` (module 10) all inherit from it and provide the same two methods, the same way every chat model shares `.invoke()`/`.stream()` (module 01).

**How it works internally:**
1. `Embeddings` itself defines no real logic — it's a contract (an "abstract base class" in Python terms) specifying that any subclass must implement `embed_documents(texts: list[str]) -> list[list[float]]` and `embed_query(text: str) -> list[float]`.
2. Each provider's subclass implements these by calling out to that provider's actual embedding API (or, for `HuggingFaceEmbeddings`, running a local model on your machine instead of a network call).
3. `embed_query` is often implemented as a thin wrapper around `embed_documents` — many providers' subclasses literally do `return self.embed_documents([text])[0]` internally, which is exactly why exercise 4 in [module 10](../10_embedding_models) expects the two to return numerically identical vectors for the same text.
4. The return type is always a plain Python `list` of floats (or a list of lists, for the batch method) — not a `numpy` array. That's why `example.py` wraps each result in `np.array(...)` before doing any vector math — `numpy`'s functions need real arrays, not plain lists, to do `np.dot`/`np.linalg.norm` efficiently.

**Real source:** [`langchain_core/embeddings/embeddings.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/embeddings/embeddings.py) defines the abstract `Embeddings` class; each provider's implementation lives in its own package (e.g. [`langchain_voyageai`](https://github.com/langchain-ai/langchain/tree/master/libs/partners/voyageai)).

**How to validate it's working:**
```python
embeddings_model = get_embeddings()
print(isinstance(embeddings_model, Embeddings))   # True, regardless of which provider is configured

vectors = embeddings_model.embed_documents(["hello", "world"])
print(len(vectors))          # 2 -- one vector per input string
print(type(vectors[0]))      # <class 'list'> -- a plain Python list, not a numpy array
print(all(isinstance(x, float) for x in vectors[0]))  # True -- every element is a plain float
```

## `cosine_similarity()` (this module's own function, not a LangChain class)

**What it is:** A hand-written function in `example.py` — worth including here because "how does the actual math work" is exactly the kind of internals this page is about, even though it's not a class from a library.

**How it works internally:** `np.dot(a, b)` computes the dot product (multiply corresponding elements, sum the results). `np.linalg.norm(a)` computes the vector's length (square root of the sum of squares of its elements — the Pythagorean theorem, generalized to however many dimensions the vector has). Dividing the dot product by both norms cancels out the effect of vector length, leaving a value between -1 and 1 that reflects only the *angle* between the two vectors — which is what "meaning similarity" actually corresponds to geometrically.

**How to validate it by hand:** For 2D vectors, you can sanity-check the formula on paper: `cosine_similarity([1, 0], [1, 0])` should give `1.0` (identical direction), `[1, 0]` vs `[-1, 0]` should give `-1.0` (opposite direction), and `[1, 0]` vs `[0, 1]` should give `0.0` (perpendicular) — try all three and confirm the function agrees with what you'd expect from basic trigonometry.
