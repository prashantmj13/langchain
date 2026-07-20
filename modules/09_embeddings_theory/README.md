# 09 — Embeddings Theory

## Theory

Computers can't compare the *meaning* of two pieces of text directly — they need everything turned into numbers first. An **embedding** does exactly that: it converts a piece of text into a long list of numbers (say, 1024 of them) that captures what the text *means*. Texts with similar meaning end up with similar lists of numbers, even if they don't share any of the same words.

- **It's about meaning, not spelling.** "dog" and "puppy" end up close together, because they mean similar things — even though they don't share a single letter in the same spot. Meanwhile "dog" and "dot" end up far apart, even though they look almost identical as words, because they mean completely different things.
- **"How similar" is a number you can calculate.** There's a standard formula (called cosine similarity) for measuring how close two of these number-lists are — it gives you a score from -1 (opposite meaning) to 1 (same meaning). You don't need to know the math, just that "closer to 1 = more similar."
- **Longer lists capture more detail, at a cost.** A list of 1536 numbers can capture more nuance than a list of 256, but it also takes more space to store and more time to search through. Some models let you safely shorten a long list without losing much accuracy, when you need to save space.
- **An embedding is a fingerprint, not an answer.** You can't ask an embedding "why are these two similar?" — it's just a list of numbers useful for comparing things, not for having a conversation. For that, you still need a chat model like Claude.

## Use Case

Semantic search, recommendation ("find me articles like this one"), clustering/deduplication, and — most importantly for this repo — **retrieval** ([module 14](../14_retrieval)), the "R" in RAG ([module 16](../16_rag)).

## How to Run

```bash
python modules/09_embeddings_theory/example.py
python modules/09_embeddings_theory/solutions.py   # exercise solutions
```
`toy_vector_demo()` needs no API key (plain `numpy` math). `real_embedding_demo()` needs an embeddings provider key — `VOYAGE_API_KEY` by default, or set `EMBEDDING_PROVIDER` in `.env` to switch.

## Walkthrough

`example.py` (no API key required for the core demo):
1. Defines 5 tiny toy vectors by hand and computes cosine similarity between them with plain `numpy`, to build intuition before any real embedding model is involved.
2. Then calls a real embedding model (via `common.embedding_factory`) on 4 short sentences and prints the pairwise similarity matrix, showing that "The cat sat on the mat" is close to "A kitten was resting on the rug" but far from "The stock market fell sharply today."

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `get_embeddings()` (this repo's `common/embedding_factory.py`) | Returns an embeddings model instance for whichever provider is configured (Voyage AI by default). | The entry point for turning text into embeddings — everything else in `real_embedding_demo()` uses its output. |
| `.embed_documents([text1, text2, ...])` | Sends a list of texts to the embeddings provider and returns one number-list (vector) per text. | Used to embed all 4 sample sentences in a single call, so their vectors can be compared to each other. |
| `np.dot`, `np.linalg.norm` (from `numpy`, not LangChain) | Standard vector math: dot product and vector length. | Used together inside `cosine_similarity()` to implement the similarity formula from this module's Theory section by hand, so you see exactly what it's computing. |

For how the shared `Embeddings` interface actually works internally (and why `embed_query` and `embed_documents` return matching results) — plus a hand-checkable validation of the cosine similarity math — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

See [module 10](../10_embedding_models) for the full provider comparison (Voyage AI / OpenAI / local HuggingFace) — this module focuses on the underlying math, which is identical regardless of provider.

## Reference Docs

- Anthropic's embeddings guide (why Claude has no native embedding model, and what to use instead): https://docs.anthropic.com/en/docs/build-with-claude/embeddings
- LangChain embeddings concept: https://python.langchain.com/docs/concepts/embedding_models/
- Voyage AI embeddings docs: https://docs.voyageai.com/docs/embeddings

## Exercises

1. **Building intuition with the simplest possible vectors.** Using the `cosine_similarity()` function from `example.py`, compute the similarity between `[1, 0]` and `[0, 1]` (two 2D vectors pointing in completely different directions — think of them as points on an X and Y axis). You should get exactly `0.0`. Write a sentence explaining *why*, in terms of the formula: what does a dot product of 0 mean geometrically?
2. **Confirming cosine similarity ignores vector length, only direction.** Take one of the toy vectors from `toy_vector_demo()` (e.g. `king = [0.9, 0.8, 0.1]`) and create a scaled copy: `king_doubled = 2 * king` (using `numpy`, this is just `2 * king_vector`). Compute `cosine_similarity(king, king_doubled)` — it should come out to `1.0` (identical), even though the two vectors have very different magnitudes. This demonstrates that cosine similarity only cares about *direction*, not length.
3. **Testing that embeddings actually cluster by meaning, not just wording.** Write 6 short sentences: 3 clearly about sports (e.g. different sports, different sentence structures) and 3 clearly about cooking. Embed all 6 with `real_embedding_demo()`'s pattern, then compute cosine similarity for a same-topic pair (e.g. sports sentence 1 vs. sports sentence 2) and a cross-topic pair (sports sentence 1 vs. cooking sentence 1). Confirm the same-topic score comes out higher.
4. **How much accuracy do you lose by shortening a vector?** Embed 2-3 sentences and get their full-length vectors (however many dimensions your provider returns — check with `len(vector)`). Compute cosine similarity using the full vectors, then recompute it using only each vector's first 256 numbers (`vector[:256]`). Compare the two similarity scores — are they close, or meaningfully different? This is what "truncating an embedding to save space" actually costs you in practice.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
