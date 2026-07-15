# 24 — Hosting Resources & Prompts

## Theory

So far, an MCP server has only offered tools — things the model can *do*. MCP also has two other, different kinds of things a server can offer:

- **Resources — data you can fetch, not an action.** Think of a resource like a specific file or web page the server can hand over on request — for example, "the PTO policy section of the handbook." Nobody is "calling" it the way you call a tool; the app just fetches it and shows it to the model as background reading.
- **Prompts — ready-made questions/instructions the server provides.** Instead of every app that connects to this server having to figure out the best way to ask it a question, the server itself can offer a ready-made template — like "summarize this section" — that any connecting app can reuse as-is.

Why bother separating these from tools instead of just making everything a tool? Because they mean different things: a tool is something the model decides to *do*, a resource is *information* to look at, and a prompt is a *ready-made question*. Keeping them separate lets apps like Claude Desktop build sensible interfaces around each — for example, showing resources as things you can "attach" to a conversation, and prompts as quick shortcuts you can pick from a menu.

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

`client.py` connects over stdio and demonstrates `read_resource()` (fetching a resource by its known URI), `list_prompts()`, and `get_prompt()`, printing what each returns.

## Classes & Methods Used

Connection setup (`StdioServerParameters`, `stdio_client`, `ClientSession`, `.initialize()`) is the same as [module 22](../22_mcp_stdio_client#classes--methods-used). What's new here:

| API | What It Does | Why We Use It Here |
|---|---|---|
| `@mcp.resource("handbook://sections/{section}")` | Registers the decorated function as a resource, addressable by a URI template with a `{section}` placeholder. | Used so the client can fetch one specific handbook section by URI, e.g. `handbook://sections/time-off`, instead of getting the whole handbook every time. |
| `@mcp.prompt()` | Registers the decorated function as a reusable prompt template the server offers to clients. | Used for `summarize_section()`, so any connecting client can ask for a ready-made "summarize this section" prompt instead of writing its own. |
| `await session.read_resource(uri)` | Fetches the content at a specific resource URI. | Used to pull the `time-off` section's text directly, by URI, on the client side. |
| `await session.list_prompts()` | Asks the server what prompt templates it offers. | Used to show prompt discovery, the same way `list_tools()` (module 22) shows tool discovery. |
| `await session.get_prompt(name, arguments)` | Fetches a specific prompt template, filled in with the given arguments, as ready-to-send messages. | Used to render `summarize_section` for the `remote-work` section and print the resulting message(s). |

## Using a different model

Resources and prompts are just structured data returned by the server — whichever LLM the host is driving decides what to do with the resource content or the prompt's messages. No provider-specific code here.

## Reference Docs

- MCP resources spec: https://modelcontextprotocol.io/docs/concepts/resources
- MCP prompts spec: https://modelcontextprotocol.io/docs/concepts/prompts
- FastMCP resources/prompts guide: https://github.com/modelcontextprotocol/python-sdk#resources

## Exercises

1. **A second, differently-scoped resource.** `server.py`'s `handbook://sections/{section}` resource returns one section at a time. Add a *second* resource, registered as `@mcp.resource("handbook://full")` (no `{section}` placeholder — a fixed URI), whose function returns all sections concatenated together. From a client, `read_resource("handbook://full")` and confirm you get the whole handbook back.
2. **Adding a parameter to a prompt template.** Give `summarize_section` a second parameter, `tone: str = "neutral"`, and use it inside the returned prompt string (e.g. `f"...in a {tone} tone..."`). From a client, call `get_prompt("summarize_section", {"section": "time-off"})` (relying on the default) and then again with `{"section": "time-off", "tone": "casual and upbeat"}` — confirm the two rendered prompt strings are visibly different.
3. **Discovering and fetching every resource programmatically.** From a client, call `list_resources()` (note: this lists *static* resources, not templated ones like `handbook://sections/{section}` — see if you can find the related method for listing resource templates too). For each one, call `read_resource()` and print `len(content.contents[0].text.encode("utf-8"))` — the size in bytes of each resource's content.
4. **Actually using a fetched prompt, not just printing it.** Call `get_prompt("summarize_section", {"section": "remote-work"})`, take the returned `rendered.messages`, convert them into LangChain `HumanMessage` objects (`HumanMessage(content=m.content.text)` for each), and send them to `get_chat_model()` from [`common/model_factory.py`](../../common/model_factory.py) — print Claude's actual summary, closing the loop from "server offers a prompt template" to "an LLM actually answers it."

**Solutions:** see [`solutions_server.py`](solutions_server.py) and [`solutions_client.py`](solutions_client.py) in this folder. Run `python modules/24_mcp_hosting_resources_prompts/solutions_client.py` -- it launches `solutions_server.py` automatically.
