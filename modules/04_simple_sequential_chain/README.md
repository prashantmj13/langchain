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

For how composing two already-built chains (`stage_1 | ... | stage_2`) actually works internally — plus a quick check to validate it — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

Each stage can even use a *different* provider if you want (e.g. a cheap/fast model for the outline, Claude for the polished prose) — see [module 06](../06_multiple_llms) for that pattern. To swap both stages at once, just change the `get_chat_model()` call.

## Reference Docs

- LCEL concept guide: https://python.langchain.com/docs/concepts/lcel/
- Migrating off legacy chains: https://python.langchain.com/docs/versions/migrating_chains/

## Exercises

1. **Extend the chain to 3 stages.** `example.py`'s pipeline is outline → opening paragraph. Add a `stage_3` that takes the opening paragraph (single input, matching this module's "single in, single out" theme) and asks for a punchy, one-line title for the post — then wire all 3 stages together the same way `example.py` composes stages 1 and 2.
2. **Verifying each stage in isolation, not just the final result.** Run `stage_1` on its own and print the outline it produces *before* passing it to `stage_2`. This isn't just about seeing more output — it's the habit of checking each link in a chain works correctly on its own, which becomes essential once chains get longer than 2 stages.
3. **Different temperatures per stage.** Build `stage_1` with `get_chat_model(temperature=0.9)` (more random/creative, good for brainstorming an outline) and `stage_2` with `get_chat_model(temperature=0.2)` (more focused/consistent, good for polished prose). Compare the outputs to a version where both stages use the default temperature — does the outline actually feel more varied across repeated runs?
4. **Confirming LCEL adds no real overhead.** Using `time.perf_counter()` before/after, time the composed `stage_1 | ... | stage_2` chain's `.invoke()` call. Separately, time calling `stage_1.invoke()` then `stage_2.invoke()` manually one after another. The two durations should come out close to equal — if the composed version were noticeably slower, that would mean `|` chaining has real cost, which it doesn't (see module 03's Execution Internals for why).

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
