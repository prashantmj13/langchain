# 10 — Embedding Models

## Theory

Anthropic does not train or serve its own embedding model — Claude is a generation model. For embeddings, [Anthropic's own docs recommend Voyage AI](https://docs.anthropic.com/en/docs/build-with-claude/embeddings), a partner that offers domain-tuned embedding models (general purpose, code, finance, law). Other common choices:

- **Voyage AI** (`voyage-3.5`, `voyage-code-3`, ...) — Anthropic's recommended partner; strong general + domain-specific models; API-based.
- **OpenAI** (`text-embedding-3-small`/`large`) — widely used, cheap, API-based; a common default outside the Anthropic ecosystem.
- **Local/HuggingFace** (`sentence-transformers/all-MiniLM-L6-v2` and similar) — runs on your own machine, no API key or network call, lower quality than the hosted options but free and private.

All three implement LangChain's `Embeddings` interface (`.embed_query(text)` for a single string, `.embed_documents(list[str])` for many) — see [`common/embedding_factory.py`](../../common/embedding_factory.py).

## Use Case

Choosing an embedding model is mostly about the trade-off between quality, cost, and where the data can live: Voyage/OpenAI need to send your text to a third-party API; a local HuggingFace model keeps everything on-device (important for regulated/sensitive data) at the cost of embedding quality and speed.

## How to Run

```bash
python modules/10_embedding_models/example.py
python modules/10_embedding_models/solutions.py   # exercise solutions
```
Each provider is tried independently and wrapped in `try/except` — set whichever of `VOYAGE_API_KEY`/`OPENAI_API_KEY` you have; the HuggingFace provider needs no key but downloads a small model to your machine on first run (via `sentence-transformers`).

## Walkthrough

`example.py`:
1. Embeds the same 3 sentences with Voyage AI, OpenAI, and a local HuggingFace model (skipping any provider whose key/package isn't available).
2. Prints each model's output vector dimensionality.
3. Compares how each model ranks the same 3 sentences by similarity to a query, to show results are directionally consistent across providers even though dimensions/scales differ.

## Using a different model

```python
from common.embedding_factory import get_embeddings

voyage_emb = get_embeddings(provider="voyage")          # default, Anthropic-recommended
openai_emb = get_embeddings(provider="openai")
local_emb = get_embeddings(provider="huggingface")       # no API key, runs locally
```

## Reference Docs

- Anthropic embeddings guide: https://docs.anthropic.com/en/docs/build-with-claude/embeddings
- Voyage AI docs: https://docs.voyageai.com/docs/embeddings
- LangChain embedding model integrations: https://python.langchain.com/docs/integrations/text_embedding/
- Sentence-Transformers models: https://www.sbert.net/docs/pretrained_models.html

## Exercises

1. Print the vector dimensionality of all three providers you have configured, and note which is largest/smallest.
2. Time `embed_documents()` on 50 short sentences for each available provider and compare latency.
3. Try `voyage-code-3` instead of the general-purpose Voyage model on a batch of code snippets, and compare similarity rankings against the general-purpose model.
4. Confirm that `embed_query("some text")` and `embed_documents(["some text"])[0]` return (numerically) the same vector for a given provider.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
