# 08 — Display History

## Theory

Once you're storing a conversation ([module 07](../07_chat_history)), you'll want to actually look at it — for debugging, for showing it in a chat window, or for saving it somewhere. This module is just about turning that list of messages into something readable:

- A plain transcript you can print to the screen, like `HUMAN: hello` / `AI: hi there`.
- A nicely formatted chat log you could drop into a document.
- A format you can save to a file or a database and load back later.

Every message object already tells you who sent it (human, AI, or system) and what it says — this module is just different ways of formatting that same information for different purposes.

## Use Case

Debugging a multi-turn agent (dumping the full transcript when something goes wrong), building a chat UI (rendering messages as bubbles), and audit logging (persisting conversations for compliance/analytics) all need a formatter over the same underlying message list.

## How to Run

```bash
python modules/08_display_history/example.py
python modules/08_display_history/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY` in `.env`. The exercise solutions write a couple of small demo files (`transcript_demo.json`, etc.) into this folder — already covered by `.gitignore`, safe to delete anytime.

## Walkthrough

`example.py`:
1. Runs a short conversation (reusing the pattern from [module 07](../07_chat_history)).
2. Pretty-prints the transcript to the console with role labels.
3. Renders the same transcript as a markdown string.
4. Serializes it to JSON via `.model_dump()` for storage/transmission.

## Using a different model

Display formatting only touches `BaseMessage` objects, which are identical regardless of which provider produced them — no changes needed to swap models.

## Reference Docs

- Messages concept (message types, `.type`, `.content`): https://python.langchain.com/docs/concepts/messages/
- `BaseChatMessageHistory`: https://python.langchain.com/api_reference/core/chat_history/langchain_core.chat_history.BaseChatMessageHistory.html

## Exercises

1. Add timestamps to each displayed message (store them alongside the message when it's added, since `BaseMessage` doesn't carry one natively).
2. Write a formatter that redacts anything that looks like an email address before printing the transcript.
3. Render the transcript as HTML (`<div class="human">...</div>` / `<div class="ai">...</div>`) suitable for embedding in a web page.
4. Write the JSON transcript to a file and reload it back into a list of `HumanMessage`/`AIMessage` objects.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
