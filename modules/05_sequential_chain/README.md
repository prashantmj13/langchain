# 05 — Sequential Chain (multi-input/output)

## Theory

Module 04 was a straight line: step 1's one output becomes step 2's one input. Real workflows are messier than that — a later step often needs *several* pieces of information at once, not just whatever the step right before it produced. Here, instead of passing along a single value, we pass along a small dictionary of named values that grows as it moves through the chain, and later steps can pick out whichever named values they need:

- **Keeping the original input around.** If a later step still needs the original text (say, the customer's review) even after other steps have computed new things from it, `RunnablePassthrough` just means "copy this value forward unchanged" instead of losing it.
- **Doing several things at once.** `RunnableParallel` (written as a plain `{...}` dictionary in a chain) runs several smaller chains at the same time, each one filling in a different named value — so a later step can use `review`, `sentiment`, and `reply` all together, computed side by side instead of one after another.
- **Adding to what you already have.** `.assign()` is a convenient way to say "keep everything I already computed, and add one more named value to it" — so you never accidentally throw away earlier results while adding new ones.

## Use Case

Anything where a later stage needs *more than one* piece of earlier context — e.g. a customer-support pipeline that needs both the original message *and* a separately-computed sentiment label to draft a reply, or a document pipeline that needs both a summary and extracted keywords to generate a title.

## How to Run

```bash
python modules/05_sequential_chain/example.py
python modules/05_sequential_chain/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY` in `.env`. Running `example.py` builds the pipeline and calls `.invoke()` once on a hardcoded sample review, then prints the `sentiment`, `summary`, and `reply` fields it computed.

## Walkthrough

`example.py` builds a 3-key pipeline for handling a customer review:
1. From the raw `review` text, compute `sentiment` (one sub-chain) and `summary` (another sub-chain) **in parallel**.
2. A final stage receives `review`, `sentiment`, and `summary` together and drafts a reply — something no single-input chain could do, since it genuinely needs all three.

For exactly what `RunnablePassthrough.assign()` and the `RunnableParallel(...)` dict do at runtime — including why the `sentiment`/`summary` branches actually run concurrently rather than one after another — see [module 03's Execution Internals](../03_chains_lcel#execution-internals-the-runnable-protocol).

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `RunnablePassthrough.assign(sentiment=..., summary=...)` | Keeps the current dict of values as-is, and adds new named keys computed by running the given chains. | Used to keep the original `review` around while adding `sentiment` and `summary`, computed in parallel, without losing `review` in the process. |
| `RunnableParallel(review=..., sentiment=..., reply=...)` | Runs each named value concurrently and returns a dict with all the results. | Used as the final stage to assemble the exact output shape we want (`review`, `sentiment`, `summary`, `reply`) — note that `reply_chain` itself depends on `sentiment`/`summary` already being computed by the earlier `enrich` stage. |
| A `lambda x: x["review"]` inside `RunnableParallel` | A tiny function that just picks one key out of the incoming dict. | Used to pass `review`/`sentiment`/`summary` straight through into the final output dict unchanged, alongside the newly-computed `reply`. |

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
