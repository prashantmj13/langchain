# 10 — Embedding Models

## Theory

Claude is great at reading and writing text, but it doesn't make embeddings (the number-lists from module 09) — that's a different kind of model, made by a different company. [Anthropic's own docs point you to Voyage AI](https://docs.anthropic.com/en/docs/build-with-claude/embeddings) for this. Your main choices:

- **Voyage AI** — Anthropic's recommended partner for embeddings. You send them text over the internet, they send back the number-list. Has general-purpose models plus specialized ones (for code, finance, legal text, etc.).
- **OpenAI** — another popular internet-based option, often cheaper, widely used outside the Anthropic ecosystem.
- **A model that runs on your own computer** — slower to set up and generally a bit less accurate than the internet-based options, but free, private (your text never leaves your machine), and works without an API key.

Whichever one you pick, you use it the exact same way in code — `.embed_query(one_piece_of_text)` for a single piece of text, or `.embed_documents(a_list_of_texts)` for many at once. See [`common/embedding_factory.py`](../../common/embedding_factory.py) for how this repo lets you switch between them.

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
