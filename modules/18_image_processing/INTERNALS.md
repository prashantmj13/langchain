# Module 18 — Internals

## Multimodal `HumanMessage` content blocks

**What it is:** Not a separate class — `HumanMessage` (module 01) already supports this. The difference is entirely in what you put in `.content`: instead of a plain string, you give it a `list` of typed content blocks.

**How it works internally:**
1. When `ChatAnthropic._generate()` (module 01's INTERNALS.md) serializes your messages into the JSON Anthropic's API expects, it checks whether each message's `.content` is a `str` or a `list`. A plain string becomes one text block in the API request; a list gets serialized as multiple content blocks in order — in this module's case, one `{"type": "text", ...}` block and one `{"type": "image", ...}` block, sent together as parts of the same message.
2. On Anthropic's side, Claude's vision capability reads the image content block's base64-encoded bytes directly, alongside the text — there's no separate OCR or image-captioning step happening before your prompt; the model itself has been trained to process pixels as an input modality, the same way it processes tokens of text.
3. The `source_type`/`mime_type` fields tell the API how to decode the base64 string (PNG vs JPEG, etc.) — get the `mime_type` wrong (e.g. label a JPEG as `image/png`) and decoding can fail or produce garbage, even though the base64 string itself is valid.

**Real source:** The content-block handling is in `ChatAnthropic`'s message-formatting logic in [`langchain_anthropic/chat_models.py`](https://github.com/langchain-ai/langchain/blob/master/libs/partners/anthropic/langchain_anthropic/chat_models.py); Anthropic's own vision API docs (linked in Reference Docs below) describe the exact JSON shape being constructed underneath.

**How to validate it's working:**
```python
message = HumanMessage(content=[
    {"type": "text", "text": "..."},
    {"type": "image", "source_type": "base64", "data": image_b64, "mime_type": "image/png"},
])
print(type(message.content))     # <class 'list'> -- not a str, confirming this is a multimodal message
print(len(message.content))      # 2 -- one text block, one image block
print(message.content[1]["mime_type"])  # "image/png" -- double-check this matches what you actually encoded
```

## `base64.b64encode()` (Python standard library, not LangChain)

**What it is:** A general-purpose encoding scheme (not specific to images or to LangChain) that turns arbitrary binary data into a string using only 64 safe, printable characters — necessary because JSON (the format API requests are sent in) can only contain text, not raw binary bytes.

**How it works internally:** It takes your image's raw bytes 3 at a time and maps each group of 3 bytes (24 bits) to 4 output characters (using 6 bits per character, from a fixed alphabet of 64 characters) — which is why base64-encoded data is always about 33% larger than the original binary. `.decode("utf-8")` at the end converts the encoding's byte-output into a normal Python `str`, since `b64encode()` itself returns `bytes`, not `str`.

**How to validate it round-trips correctly:**
```python
original_bytes = b"some binary data"
encoded = base64.b64encode(original_bytes).decode("utf-8")
decoded_back = base64.b64decode(encoded)
print(decoded_back == original_bytes)   # True -- confirms nothing was lost in the encode/decode round trip
```
