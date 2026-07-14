# 04 — Simple Sequential Chain

## Theory

This is the simplest possible chain shape: step 1 produces one thing, and that one thing becomes the entire input to step 2 — nothing else is added or mixed in along the way. Think of a factory line with two stations, where each station only ever sees what the station before it handed over.

LangChain used to have a class literally called `SimpleSequentialChain` for this. It isn't needed anymore — connecting two chains with `chain_1 | chain_2` (from module 03) does the exact same thing, more simply.

The one thing that makes this "simple" (versus the more flexible [Sequential Chain in module 05](../05_sequential_chain)) is that each step takes exactly one input and produces exactly one output. There's no combining information from two earlier steps, and no step that needs more than what the previous step gave it.

## Use Case

Multi-stage text transformations where each stage only needs the previous stage's result: generate an outline → expand the outline into prose → summarize the prose. Any "assembly line" of one-shot LLM calls.

## How to Run

```bash
python modules/04_simple_sequential_chain/example.py
python modules/04_simple_sequential_chain/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY` in `.env`. The script builds `stage_1` and `stage_2` as separate chains, calls them manually one after another (printing each intermediate result), then composes them into a single chain and calls that too — so you see both the step-by-step and the one-shot version of the same pipeline.

## Walkthrough

`example.py` builds a two-stage pipeline:
1. **Stage 1** — given a topic, generate a short blog post outline.
2. **Stage 2** — given that outline (and nothing else), write an opening paragraph.

Both stages are `prompt | llm | StrOutputParser()` chains; they're composed with a single `|` into one end-to-end chain, and also run manually step-by-step so you can see the intermediate output. The composed chain uses a bare `lambda` between the two stages (`stage_1 | (lambda outline_text: {"outline": outline_text}) | stage_2`) — see [module 03's Execution Internals](../03_chains_lcel#execution-internals-the-runnable-protocol) for exactly what happens when a raw function like that gets auto-wrapped into a `RunnableLambda` and dropped into a `|` pipe.

## Classes & Methods Used

Everything here is reused from earlier modules — `ChatPromptTemplate`, `StrOutputParser`, and `|` chaining (see modules [02](../02_prompt_templates#classes--methods-used) and [03](../03_chains_lcel#classes--methods-used) for those). The one new thing:

| API | What It Does | Why We Use It Here |
|---|---|---|
| A bare `lambda` inside a `\|` chain | LangChain auto-wraps a plain function dropped into a pipe as a `RunnableLambda` (module 03) — you don't have to write `RunnableLambda(...)` yourself. | Used between `stage_1` and `stage_2` to reshape stage 1's plain-string output into the `{"outline": ...}` dict shape that stage 2's prompt template expects. |

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

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
