# Project 02 — Natural-Language Ops Assistant

**Domain:** DevOps automation
**Difficulty:** Advanced
**Time estimate:** 6-10 hours

## The Problem

Checking on running services usually means remembering exact commands: `docker ps`, `kubectl get pods -n prod`, `systemctl status nginx`, `df -h`. You're going to build an MCP server that exposes a handful of **read-only** ops commands as tools, and a Claude agent that lets you ask things like "is the payments service running?" or "which containers have restarted recently?" in plain English.

**Safety note:** every tool you build for this project must be read-only. Do not wire up anything that can start, stop, restart, delete, or modify anything. The point is answering questions about system state, not remote-controlling infrastructure from an LLM — a hallucinated "confirm" from a model is not something you want anywhere near a `kubectl delete` command.

## What You'll Build

1. An MCP server (following the pattern from [module 21](../../modules/21_mcp_create_server) / [module 25](../../modules/25_mcp_implement_server)) exposing 3-5 read-only tools, for example:
   - `list_containers()` — wraps `docker ps` (or `docker ps -a`)
   - `container_logs(name, lines)` — wraps `docker logs --tail N <name>`
   - `disk_usage()` — wraps `df -h`
   - `list_processes(filter)` — wraps `ps aux` with optional filtering
   - (If you have access to a Kubernetes cluster, even a local `minikube`/`kind` one: `list_pods(namespace)`, `pod_status(name)`)
2. A Claude agent ([module 19](../../modules/19_agents) pattern, extended to MCP tools per [module 26](../../modules/26_mcp_implement_client)) that connects to this server and can answer natural-language questions by calling one or more of these tools and reasoning over the results.
3. A simple REPL: run the script, type a question, get an answer, repeat.

## Suggested Approach

1. Start entirely with module 21's pattern: write 1-2 tools first (e.g. just `list_containers` and `container_logs`) and confirm they work by calling them directly with a raw MCP client (module 22's pattern) before involving any agent at all.
2. Each tool function should call the underlying system command (`subprocess.run(...)`) and return parsed, clean text — not raw command output with escape codes and noise. This parsing is most of the actual engineering work in this project.
3. Write tight tool descriptions. The model decides which tool to call based purely on the description you write — vague descriptions lead to the wrong tool being called, or the right tool being called with bad arguments.
4. Once individual tools work, wire the MCP client into a LangGraph agent per module 26, and test single-tool questions first ("what containers are running?") before multi-tool questions ("is anything using more than 80% disk, and if so what's been logging heavily on that container?").
5. Add basic error handling: what happens when Docker isn't running, or a container name doesn't exist? The tool should return a clear error message the model can react to, not crash the server.

## Tech You'll Need

- Docker installed locally (or substitute with whatever's actually running on your machine — even just `ps`/`df` on your own OS works if you don't have Docker)
- `subprocess` module for running shell commands
- The `mcp` Python SDK and `langchain-mcp-adapters`, both already in this repo's `requirements.txt`

## Stretch Goals

- Add a tool that queries a real monitoring system's read-only API (Prometheus, Datadog, CloudWatch) instead of/alongside local commands.
- Have the agent proactively flag anomalies it notices while answering (e.g. "by the way, container X has restarted 5 times in the last hour").
- Add a `--explain` mode that shows you exactly which tools the agent called and why, for debugging trust in its answers.
- Package the whole thing so a teammate could point their own Claude Desktop at your MCP server (streamable HTTP transport, module 23/25) instead of only working via your CLI.

## Definition of Done

You can ask at least 5 different natural-language ops questions and get accurate answers, including at least one question that requires the agent to call more than one tool to answer fully. You've confirmed (by reading your own tool code) that nothing in your tool set can modify system state.

## Reference Modules

- [19 — Agents](../../modules/19_agents)
- [20 — MCP Fundamentals](../../modules/20_mcp_fundamentals) through [26 — Implement Client](../../modules/26_mcp_implement_client)
