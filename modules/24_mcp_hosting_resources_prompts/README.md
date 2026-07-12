# 24 — Hosting Resources & Prompts

## Theory

Tools ([modules 21](../21_mcp_create_server)-[23](../23_mcp_http_client)) are for *actions* the model chooses to invoke. MCP has two other primitives for different jobs:

- **Resources** (`@mcp.resource(uri_template)`) — addressable, read-only data the host can fetch, similar in spirit to a GET endpoint. A resource has a URI (e.g. `docs://handbook/pto-policy`) and returns content; the host decides when to fetch it (sometimes automatically, sometimes because the user or model asked to see it) rather than the model "deciding to call" it the way it decides to call a tool.
- **Prompts** (`@mcp.prompt()`) — reusable, parameterized prompt templates the server exposes for clients to use, so the *server* (which understands its own data best) owns useful prompt engineering instead of every client reinventing it. A client calls `list_prompts()`/`get_prompt(name, args)` and gets back ready-to-use messages.

Why this split matters: tools are for the model to *act*, resources are data for the host to *load as context*, and prompts are canned *conversation starters/templates* — conflating them (e.g. making everything a tool) works but loses the semantic distinction MCP clients (like Claude Desktop) use to build UI around each (e.g. showing resources as attachable context, prompts as slash-command-like shortcuts).

## Use Case

A documentation server that exposes each doc page as a resource (so a host can let a user "attach" a specific page as context) and exposes a `"summarize_page"` prompt template (so any client gets a consistent, well-tuned summarization prompt without re-authoring it).

## How to Run

```bash
python modules/24_mcp_hosting_resources_prompts/client.py
python modules/24_mcp_hosting_resources_prompts/solutions_client.py   # exercise solutions
```
No API key needed for the base walkthrough (exercise 4's Claude call needs `ANTHROPIC_API_KEY`). Same one-command pattern as module 22 — the client launches `server.py`/`solutions_server.py` itself over stdio, no second terminal required.

## Walkthrough

`server.py` extends the module 21 server with:
1. A resource `handbook://sections/{section}` returning one section of the sample handbook text (reusing the file from [module 16](../16_rag)).
2. A prompt `summarize_section(section)` that returns a ready-made message asking the model to summarize that section.

`client.py` connects over stdio and demonstrates `list_resources()`/`read_resource()` and `list_prompts()`/`get_prompt()`, printing what each returns.

## Using a different model

Resources and prompts are just structured data returned by the server — whichever LLM the host is driving decides what to do with the resource content or the prompt's messages. No provider-specific code here.

## Reference Docs

- MCP resources spec: https://modelcontextprotocol.io/docs/concepts/resources
- MCP prompts spec: https://modelcontextprotocol.io/docs/concepts/prompts
- FastMCP resources/prompts guide: https://github.com/modelcontextprotocol/python-sdk#resources

## Exercises

1. Add a second resource exposing the whole handbook (not just one section) under `handbook://full`.
2. Add a prompt parameter (`tone: str = "neutral"`) to `summarize_section` and confirm both default and explicit values produce different generated messages.
3. List all resources the server exposes and fetch each one in a loop, printing byte length of each.
4. Extend the client to actually send a fetched prompt's messages to Claude ([common/model_factory.py](../../common/model_factory.py)) and print the model's response.

**Solutions:** see [`solutions_server.py`](solutions_server.py) and [`solutions_client.py`](solutions_client.py) in this folder. Run `python modules/24_mcp_hosting_resources_prompts/solutions_client.py` -- it launches `solutions_server.py` automatically.
