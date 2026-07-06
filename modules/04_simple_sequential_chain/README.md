# 04 — Simple Sequential Chain

## Theory

A "simple sequential chain" is the classic pattern where **one chain's single output feeds directly into the next chain's single input** — step 1's answer is step 2's question, nothing more. LangChain used to have a dedicated `SimpleSequentialChain` class for this; it's deprecated in favor of just piping LCEL chains together, because a sequential chain *is* an LCEL chain — `chain_1 | chain_2`.

The defining trait vs. the more general [Sequential Chain (module 05)](../05_sequential_chain) is **single in, single out** at every stage: no branching, no merging multiple upstream outputs.

## Use Case

Multi-stage text transformations where each stage only needs the previous stage's result: generate an outline → expand the outline into prose → summarize the prose. Any "assembly line" of one-shot LLM calls.

## Walkthrough

`example.py` builds a two-stage pipeline:
1. **Stage 1** — given a topic, generate a short blog post outline.
2. **Stage 2** — given that outline (and nothing else), write an opening paragraph.

Both stages are `prompt | llm | StrOutputParser()` chains; they're composed with a single `|` into one end-to-end chain, and also run manually step-by-step so you can see the intermediate output.

## Using a different model

Each stage can even use a *different* provider if you want (e.g. a cheap/fast model for the outline, Claude for the polished prose) — see [module 06](../06_multiple_llms) for that pattern. To swap both stages at once, just change the `get_chat_model()` call.

## Reference Docs

- LCEL concept guide: https://python.langchain.com/docs/concepts/lcel/
- Migrating off legacy chains: https://python.langchain.com/docs/versions/migrating_chains/

## Exercises

1. Add a third stage that takes the opening paragraph and produces a punchy one-line title for the post.
2. Print the intermediate outline separately from the final paragraph (don't just print the end result) to confirm each stage's output.
3. Rewrite the two-stage chain so stage 1 uses `temperature=0.9` (more creative outlines) and stage 2 uses `temperature=0.2` (more focused prose).
4. Time how long the composed chain takes vs. calling each stage manually in sequence — they should be about the same, since LCEL doesn't add overhead here.
