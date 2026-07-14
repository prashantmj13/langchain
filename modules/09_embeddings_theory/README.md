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
