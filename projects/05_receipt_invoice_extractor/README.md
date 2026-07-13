# Project 05 — Receipt & Invoice Extractor

**Domain:** Image processing
**Difficulty:** Beginner
**Time estimate:** 3-5 hours

## The Problem

Expense reports mean typing numbers off paper receipts into a spreadsheet by hand — vendor, date, line items, total. You're going to build a tool that takes a photo of a receipt or invoice and turns it directly into structured data, ready to drop into a spreadsheet or database.

## What You'll Build

A script that:
1. Takes an image file path as input (a photo of a receipt, or a screenshot/scan of an invoice — take your own photos with your phone for realistic test data).
2. Sends the image to Claude using its vision capability, asking it to extract: vendor name, date, individual line items (description + price), tax, and total.
3. Validates the extracted data against a strict schema — if the model returns something that doesn't fit the expected shape (e.g. a date in a weird format, a total that doesn't match the sum of line items plus tax), catch that rather than silently accepting bad data.
4. Outputs the result as a row you could append to a CSV, plus prints a warning if the extracted total doesn't match the sum of line items (a good sanity check that catches misreads).

## Suggested Approach

1. Collect 5-10 real test images: photograph a few receipts you have lying around (grocery, restaurant, gas station — they're formatted very differently from each other, which is exactly why this is a good test set), plus a couple of digital invoices (PDF invoices exported as images, or screenshots).
2. Start with module 18's pattern for sending an image to Claude, but instead of asking for a free-text description, use `.with_structured_output()` with a Pydantic model that matches the receipt shape you want (vendor: str, date: str, line_items: list[LineItem], tax: float, total: float).
3. Run it against your test images and see where it gets things wrong — blurry photos, unusual receipt formats, handwritten totals are all going to be harder. Note the failure modes; you don't need to fix all of them, but you should understand them.
4. Add the sanity check: does `sum(item.price for item in line_items) + tax` roughly equal `total`? If not, flag it — this is a good example of not blindly trusting model output, especially for a task (reading small print in a photo) it can plausibly get wrong.
5. Write the validated result to a CSV (one row per receipt), or print it, whichever is easier to verify by eye.

## Tech You'll Need

- A phone camera (or any camera) for test images — this project is much more useful if you test it against genuinely messy real-world photos, not clean synthetic ones
- Pillow, if you need to resize/rotate images before sending them (large photos cost more tokens — see module 18's theory on this)
- A Pydantic model + `.with_structured_output()`
- `csv` module for output

## Stretch Goals

- Categorize each receipt (groceries, dining, travel, etc.) as part of the extraction, using a fixed set of categories you define.
- Batch-process a whole folder of receipt images and produce one combined CSV.
- Handle multi-page invoices (multiple images that together represent one document).
- Build a tiny review step: show the extracted data next to the original image and let a human confirm/correct it before it's considered final — this is how you'd actually want to deploy something like this, since blind trust in extracted financial data is risky.

## Definition of Done

Running your tool against at least 5 real receipt/invoice photos of different types produces correctly extracted vendor, date, and total for at least 4 of them, and your sanity check correctly flags any case where the extracted total doesn't add up.

## Reference Modules

- [18 — Image Processing](../../modules/18_image_processing)
- [03 — Chains (LCEL)](../../modules/03_chains_lcel) for structured output
