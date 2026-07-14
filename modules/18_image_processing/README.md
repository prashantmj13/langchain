# 18 — Image Processing (Multimodal)

## Theory

So far, every message we've sent Claude has been plain text. Claude can also "see" — you can include an image in the same message as your question, and Claude looks at it directly, the same way it reads text. No separate tool is needed to first extract the text or describe the picture; you just hand Claude the image and ask about it.

To do this, instead of a message being one plain string, it becomes a small list with two parts: one part is your text question, and the other part is the image itself, converted into a long text string (called base64) so it can travel inside the same request as everything else.

A few practical things to know:
- **The image gets encoded as text before sending**, using a standard method called base64 — you don't need to understand how that encoding works, just that Pillow (or any image library) can produce it for you.
- **Bigger images cost more** — just like longer text costs more tokens, a larger image uses more of your budget, so it's worth shrinking an image to a reasonable size before sending it.
- **You can send more than one image at once** — handy for "compare these two screenshots" or "what changed between these two pictures" type questions.
- **What this is good for:** reading text out of a photo or scanned document, describing what's in a picture, and comparing two images side by side.

## Use Case

Document/receipt/form understanding, UI review ("does this screenshot match the design spec"), accessibility (auto-generating alt text), and any workflow where the input is fundamentally visual rather than textual.

## How to Run

```bash
python modules/18_image_processing/example.py
python modules/18_image_processing/solutions.py   # exercise solutions
```
Requires `ANTHROPIC_API_KEY`. No image file is needed — `generate_placeholder_image()` draws one in memory with Pillow and base64-encodes it before sending it to Claude, so the whole demo is self-contained.

## Walkthrough

`example.py`:
1. Generates a small placeholder PNG on the fly with Pillow (a colored rectangle with text "LangChain" drawn on it) — no external image file needed to run the demo.
2. Base64-encodes it and sends it to Claude in a multimodal message asking it to describe what it sees and read any text.
3. Prints Claude's description.

## Classes & Methods Used

| API | What It Does | Why We Use It Here |
|---|---|---|
| `HumanMessage(content=[...])` | Same message class from module 01, but `content` is a *list* of parts instead of a plain string. | Used to combine a text part and an image part in a single message — this list-of-parts shape is what makes a message multimodal. |
| `{"type": "image", "source_type": "base64", "data": ..., "mime_type": "image/png"}` | A content block describing an image: how it's encoded (`base64`), the actual encoded data, and what image format it is. | This is the piece that actually carries the image to Claude, sitting alongside the text content block in the same message. |
| `base64.b64encode(...)` (Python standard library, not LangChain) | Converts raw image bytes into a text string safe to embed inside a JSON request. | Used because the image itself is binary data, but the request to Claude's API is JSON/text — base64 is the bridge between the two. |
| `Image.new(...)`, `ImageDraw.Draw(...)` (from Pillow, not LangChain) | Creates a blank image and draws shapes/text on it. | Used only to generate a test image on the fly, so this example needs no external image file to run. |

## Using a different model

OpenAI's GPT-4o multimodal content-block shape differs slightly (`{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}}` vs. Anthropic's `{"type": "image", "source_type": "base64", ...}`); LangChain's newer standard content-block format (`{"type": "image", "source_type": "base64", "data": ..., "mime_type": ...}`) is normalized across `ChatAnthropic` and `ChatOpenAI` in recent `langchain-core` versions, so the same message often works unchanged — the README's code comment shows the raw-provider difference for when you're not going through LangChain's abstraction.

## Reference Docs

- Anthropic vision guide: https://docs.anthropic.com/en/docs/build-with-claude/vision
- LangChain multimodal how-to: https://python.langchain.com/docs/how_to/multimodal_inputs/

## Exercises

1. Swap the generated placeholder image for a real photo on your machine and ask Claude to describe it.
2. Send two images in one message (e.g. two different placeholder colors) and ask Claude to compare them.
3. Ask Claude to transcribe text drawn on the placeholder image and verify the transcription is exact.
4. Try the same multimodal message with `get_chat_model(provider="openai", model="gpt-4o-mini")` and compare the response format/quality.

**Solutions:** see [`solutions.py`](solutions.py) in this folder.
