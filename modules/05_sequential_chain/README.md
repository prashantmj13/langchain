# 05 — Sequential Chain (multi-input/output)

## Theory

A general "sequential chain" differs from the [simple sequential chain (module 04)](../04_simple_sequential_chain) because stages can take **multiple** inputs and produce **multiple** named outputs that later stages pick and choose from — not just a single string handed straight down the line. The legacy `SequentialChain` class modeled this with named `input_variables`/`output_variables`; in modern LCEL you get the same effect with:

- **`RunnablePassthrough`** — forward part of the original input untouched, alongside new computed values.
- **`RunnableParallel`** (a plain `dict` in LCEL) — run several sub-chains concurrently, each writing to a different output key, so the next stage can `{review}`, `{sentiment}`, and `{reply}` all at once.
- **`.assign()`** — the idiomatic way to add a new computed key to a dict-like running state without dropping the existing keys.

## Use Case

Anything where a later stage needs *more than one* piece of earlier context — e.g. a customer-support pipeline that needs both the original message *and* a separately-computed sentiment label to draft a reply, or a document pipeline that needs both a summary and extracted keywords to generate a title.

## Walkthrough

`example.py` builds a 3-key pipeline for handling a customer review:
1. From the raw `review` text, compute `sentiment` (one sub-chain) and `summary` (another sub-chain) **in parallel**.
2. A final stage receives `review`, `sentiment`, and `summary` together and drafts a reply — something no single-input chain could do, since it genuinely needs all three.

## Using a different model

Different sub-chains can use different providers/temperatures independently, since each is just `prompt | get_chat_model(...) | parser` — see [module 06](../06_multiple_llms).

## Reference Docs

- `RunnableParallel`: https://python.langchain.com/docs/how_to/parallel/
- `RunnablePassthrough` / `.assign()`: https://python.langchain.com/docs/how_to/passthrough/
- Migrating from legacy `SequentialChain`: https://python.langchain.com/docs/versions/migrating_chains/sequential_chain/

## Exercises

1. Add a fourth parallel branch that extracts a list of complaint "categories" (e.g. `shipping`, `quality`, `price`) from the review.
2. Change the final stage so it also outputs a `priority: high|medium|low` field using `.with_structured_output()`.
3. Measure whether running `sentiment` and `summary` via `RunnableParallel` is actually faster than running them sequentially with two separate `.invoke()` calls.
4. Feed 3 different reviews through `.batch()` and print a table of `review | sentiment | reply`.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
