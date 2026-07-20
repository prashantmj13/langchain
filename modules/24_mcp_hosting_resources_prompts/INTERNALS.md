# Module 24 — Internals

## `@mcp.resource("handbook://sections/{section}")`

**What it is:** A decorator similar to `@mcp.tool()` (module 21's INTERNALS.md), but registered in a separate "resources" registry, and keyed by a **URI template** instead of just a name.

**How it works internally:**
1. The string `"handbook://sections/{section}"` is a URI template — `FastMCP` parses out the `{section}` placeholder the same way `ChatPromptTemplate` parses `{variable}` placeholders (module 02's INTERNALS.md) out of a template string.
2. When a client calls `read_resource("handbook://sections/time-off")`, the server matches the requested URI against every registered resource's template, extracts `section="time-off"` from the matched portion, and calls your decorated function with that as the argument — `get_handbook_section(section="time-off")`.
3. The function's return value becomes the resource's content, wrapped in the response the client's `read_resource()` call receives.

A resource with no placeholders at all (like `handbook://full`, from this module's exercise 1) is just a URI template with zero variables to extract — matched by exact string equality instead.

**Real source:** [`mcp/server/fastmcp/resources/`](https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server/fastmcp/resources) in the Python SDK — look for `resource_manager.py` and the URI template matching logic.

## `@mcp.prompt()`

**How it works internally:** Registers your function in a separate "prompts" registry. Unlike a tool (which the *model* decides to call) or a resource (which the *host* fetches as context), a prompt is meant to be explicitly requested by name — `get_prompt("summarize_section", {"section": "remote-work", "tone": "casual"})` looks up `summarize_section` in the registry, calls your Python function with those arguments, and wraps whatever string (or list of messages) it returns into the MCP response shape (`rendered.messages`) the client reads back.

**Real source:** [`mcp/server/fastmcp/prompts/`](https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server/fastmcp/prompts) in the same repo.

**How to validate both are working:**
```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # Resource: confirm the {section} placeholder extraction works
        resource = await session.read_resource("handbook://sections/expenses")
        print(resource.contents[0].text)   # should be the expenses section specifically, not time-off or remote-work

        # Prompt: confirm arguments actually get threaded through
        rendered = await session.get_prompt("summarize_section", {"section": "expenses"})
        print(rendered.messages[0].content.text)  # should mention "expenses" in the rendered prompt text
```
If the resource returns the wrong section (or an error), the URI template match is the first thing to check — print the exact URI you're requesting and compare it character-for-character against the template registered in `server.py`.
