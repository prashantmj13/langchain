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
4. Serializes it to JSON (using each message's `.type` and `.content`) for storage/transmission, then reloads it back into real `HumanMessage`/`AIMessage` objects.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `message.type` | A string telling you which kind of message this is (`"human"`, `"ai"`, or `"system"`). | Used in every formatter to decide how to label/render each message (e.g. `"You"` vs. `"Assistant"` in the markdown version). |
| `message.content` | The plain-text body of the message. | The actual text we're formatting/saving in every function in this module. |
| `history.add_user_message(text)` / `.add_ai_message(text)` | Shortcut methods on `ChatMessageHistory` that wrap a plain string in the right message type and append it. | Used in `run_short_conversation()` as a slightly shorter way to build up history than constructing `HumanMessage`/`AIMessage` objects by hand. |
| `HumanMessage(content=...)` / `AIMessage(content=...)` | Construct a message object directly from role + text. | Used in `messages_from_json()` to turn plain dicts (loaded from JSON) back into real LangChain message objects. |

For why `.type` and `.content` are reliable enough to build formatters around — see [`INTERNALS.md`](INTERNALS.md) in this folder.

## Using a different model

Display formatting only touches `BaseMessage` objects, which are identical regardless of which provider produced them — no changes needed to swap models.

## Reference Docs

- Messages concept (message types, `.type`, `.content`): https://python.langchain.com/docs/concepts/messages/
- `BaseChatMessageHistory`: https://python.langchain.com/api_reference/core/chat_history/langchain_core.chat_history.BaseChatMessageHistory.html

## Exercises

1. **Messages don't have a built-in timestamp — you have to track it yourself.** As you add each message to history (following `run_short_conversation()`'s pattern), also record `datetime.now()` in a separate list or tuple alongside it. Then print a transcript where each line is prefixed with its timestamp, like `[14:32:01] [HUMAN] What is a vector database?`.
2. **Redacting sensitive-looking content before display.** Using Python's `re` module, write a regular expression that matches something-looking-like-an-email-address (e.g. `[\w.+-]+@[\w-]+\.[\w.-]+`), and use `re.sub()` to replace any match in a message's `.content` with `[redacted-email]` before printing it. Test it on a message you write yourself that contains a fake email address.
3. **Turning the transcript into embeddable HTML.** Following `to_markdown()`'s pattern (loop over messages, build up a list of formatted lines, join them), instead build a list of HTML `<div>` lines — `<div class="human">...</div>` for human messages, `<div class="ai">...</div>` for AI ones — so the result could be dropped directly into a web page's `<body>`.
4. **Round-tripping a transcript through JSON.** Write a short conversation's messages out as JSON (following `to_json()`'s pattern: a list of `{"role": ..., "content": ...}` dicts) to an actual file on disk with `Path(...).write_text(...)`. Then, in the same script (or a separate run), read that file back with `.read_text()`, parse the JSON, and reconstruct real `HumanMessage`/`AIMessage` objects from it (see `messages_from_json()` for the reconstruction pattern) — confirm the reloaded messages have identical `.content` to the originals.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
