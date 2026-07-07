# 08 — Display History

## Theory

Once you have a `BaseChatMessageHistory` ([module 07](../07_chat_history)), you need to *do something* with it: print it for debugging, render it in a chat UI, or export it for logging/analytics. This module is purely about the presentation layer over a message list — turning `list[BaseMessage]` into:

- A readable console transcript (`role: content`).
- A markdown chat log.
- A JSON-serializable structure (for storing in a database or sending to a frontend).

`BaseMessage` objects expose `.type` (`"human"`/`"ai"`/`"system"`), `.content`, and `.model_dump()` for exactly this purpose.

## Use Case

Debugging a multi-turn agent (dumping the full transcript when something goes wrong), building a chat UI (rendering messages as bubbles), and audit logging (persisting conversations for compliance/analytics) all need a formatter over the same underlying message list.

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
