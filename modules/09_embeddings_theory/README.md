# 09 — Embeddings Theory

## Theory

An **embedding** is a fixed-length vector of floats (e.g. 1024 dimensions) that represents the *meaning* of a piece of text, produced by a neural network trained so that semantically similar texts end up as nearby vectors in that high-dimensional space. Key ideas:

- **Semantic, not lexical, similarity.** "dog" and "puppy" land close together even though they share no characters; "dog" and "dot" land far apart despite looking similar as strings.
- **Cosine similarity** is the standard way to compare two embeddings: `cos(θ) = (A · B) / (|A| |B|)`, ranging from -1 (opposite meaning) to 1 (identical meaning). Most embedding APIs normalize vectors to unit length, so cosine similarity reduces to a dot product.
- **Dimensionality** is a trade-off: higher-dimensional embeddings (e.g. 1536, 3072) capture more nuance but cost more to store/search; many modern models (e.g. Voyage, OpenAI's v3 embeddings) support "Matryoshka" truncation — you can safely cut a 1024-dim vector down to 256 dims and lose relatively little quality.
- **Embeddings are not free-text.** You cannot ask an embedding model "why are these similar" — it's a fixed-size numeric fingerprint, useful only for comparison/search, not generation.

## Use Case

Semantic search, recommendation ("find me articles like this one"), clustering/deduplication, and — most importantly for this repo — **retrieval** ([module 14](../14_retrieval)), the "R" in RAG ([module 16](../16_rag)).

## Walkthrough

`example.py` (no API key required for the core demo):
1. Defines 5 tiny toy vectors by hand and computes cosine similarity between them with plain `numpy`, to build intuition before any real embedding model is involved.
2. Then calls a real embedding model (via `common.embedding_factory`) on 4 short sentences and prints the pairwise similarity matrix, showing that "The cat sat on the mat" is close to "A kitten was resting on the rug" but far from "The stock market fell sharply today."

## Using a different model

See [module 10](../10_embedding_models) for the full provider comparison (Voyage AI / OpenAI / local HuggingFace) — this module focuses on the underlying math, which is identical regardless of provider.

## Reference Docs

- Anthropic's embeddings guide (why Claude has no native embedding model, and what to use instead): https://docs.anthropic.com/en/docs/build-with-claude/embeddings
- LangChain embeddings concept: https://python.langchain.com/docs/concepts/embedding_models/
- Voyage AI embeddings docs: https://docs.voyageai.com/docs/embeddings

## Exercises

1. By hand, compute the cosine similarity between `[1, 0]` and `[0, 1]` and explain why it's 0.
2. Add a 5th toy vector that's a scaled copy of an existing one (e.g. `2 * v1`) and confirm cosine similarity treats it as identical to `v1` (cosine similarity ignores magnitude).
3. Embed 6 sentences from 2 different topics (3 sports, 3 cooking) and confirm same-topic pairs score higher than cross-topic pairs.
4. Truncate a real embedding vector to its first 256 dimensions and compare similarity scores before/after truncation — how much does ranking order change?

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
