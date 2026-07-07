# Module 20 - Exercise Solutions

These exercises are conceptual (no code to run), so solutions are discussed here instead of in a `solutions.py`.

## 1. Sketch an MCP setup for a scenario from your own work

Example: "Let engineers ask an agent questions about our internal ticketing system."
- **Server**: wraps the ticketing system's REST API. Exposes tools like `search_tickets(query)`, `get_ticket(id)`, `create_ticket(title, description)`, and a resource `ticket://{id}` for read-only lookups.
- **Transport**: streamable HTTP, since this server needs to be shared by multiple engineers' agents/hosts at once, not spawned per-client like a stdio subprocess.
- **Host**: any MCP-compatible client (a Slack bot, an internal chat UI, Claude Desktop with this server configured).

## 2. What a tool definition requires beyond a name and a function signature

Per the MCP spec, a tool definition needs: a unique `name`, a human/model-readable `description` (this is what the model reads to decide *when* to call it -- get this wrong and the model either never calls the tool or calls it inappropriately), an `inputSchema` (JSON Schema describing arguments, their types, and which are required), and optionally an `outputSchema`. `FastMCP`'s `@mcp.tool()` decorator generates the schema for you from Python type hints and the docstring -- which is exactly why type hints and docstrings matter so much in modules 21/25.

## 3. MCP primitives vs. a plain REST API

A REST API just exposes endpoints -- the caller has to already know what each endpoint does, what it returns, and how to sequence calls. MCP adds a **discovery layer** on top: `list_tools()`/`list_resources()`/`list_prompts()` let a client (and the LLM behind it) introspect *at runtime* what's available and how to call it, without a human writing integration code ahead of time. The tools/resources/prompts split also standardizes *intent* -- a REST API mixes "do a thing" and "get some data" endpoints indistinguishably, while MCP forces you to categorize each capability so clients can build sensible UI/behavior around each category (e.g., "attach a resource as context" vs. "let the model decide to call this tool").

## 4. Stdio vs. HTTP for your own server

Rule of thumb: if the client will always be the one launching the server as a local subprocess (a desktop tool, a personal CLI utility, a single developer's local integration) -- **stdio**. If the server needs to run independently of any one client, be reachable by multiple clients/agents at once, live on different infrastructure, or sit behind authentication -- **streamable HTTP**. For the ticketing-system example in exercise 1: HTTP, because many engineers' agents need to reach the same server concurrently.
