# 18 — Image Processing (Multimodal)

## Theory

Claude is multimodal: a `HumanMessage` can carry both text and image content blocks in the same call, and Claude reasons over the image directly (no separate OCR/vision pipeline needed). The message shape:

```python
HumanMessage(content=[
    {"type": "text", "text": "What's in this image?"},
    {"type": "image", "source_type": "base64", "data": base64_str, "mime_type": "image/png"},
])
```

Key points:
- **Images are base64-encoded** and embedded directly in the request (or referenced by URL, for providers/setups that support it).
- **Size/token limits** — large images cost more tokens and may be downscaled by the API; resizing to a reasonable resolution before sending is good practice.
- **Multiple images per message** are supported — useful for "compare these two screenshots" style prompts.
- Claude's vision use cases: reading charts/screenshots, describing scenes, transcribing handwritten or printed text, comparing UI mockups.

## Use Case

Document/receipt/form understanding, UI review ("does this screenshot match the design spec"), accessibility (auto-generating alt text), and any workflow where the input is fundamentally visual rather than textual.

## Walkthrough

`example.py`:
1. Generates a small placeholder PNG on the fly with Pillow (a colored rectangle with text "LangChain" drawn on it) — no external image file needed to run the demo.
2. Base64-encodes it and sends it to Claude in a multimodal message asking it to describe what it sees and read any text.
3. Prints Claude's description.

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
