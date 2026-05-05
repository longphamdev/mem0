---
name: mem0-openmemory
description: >
  Self-hosted memory integration for AI agents via local MCP server.
  TRIGGER when: user mentions "openmemory", "self-hosted memory", "local mem0",
  "mem0 MCP", "localhost memory", "mem0-plugin-self-hosted", or needs to use
  Mem0 running on their own server with Qdrant + Ollama.
  DO NOT TRIGGER when: user asks about Mem0 Platform API key setup, hosted Mem0
  at api.mem0.ai, or CLI commands (use mem0-cli instead).
license: Apache-2.0
metadata:
  author: mem0ai
  version: "0.1.0"
  category: ai-memory
  tags: "memory, self-hosted, openmemory, local-mcp, qdrant, ollama"
compatibility: Requires Docker Compose running openmemory-mcp service on localhost:8765, Qdrant vector store, Ollama embedding provider.
---

# Mem0 OpenMemory — Self-Hosted Memory for AI Agents

> **This skill is for self-hosted Mem0 via OpenMemory.** It connects to a local MCP server instead of the cloud Mem0 Platform.

## What is This?

Mem0 OpenMemory is a self-hosted memory layer that stores, retrieves, and manages AI agent memories using:
- **Local MCP server** at `localhost:8765` (no external API calls)
- **Qdrant** vector database for semantic search
- **Ollama** for embeddings (e.g., `nomic-embed-text`)

All data stays on your infrastructure. No API keys needed.

## Quick Start

### 1. Start Local Services

```bash
cd /path/to/mem0
docker compose up -d
```

This starts:
- `openmemory-mcp` on `localhost:8765` (MCP server)
- `mem0_store` (Qdrant) on `localhost:6333`
- `openmemory-ui` on `localhost:3000` (web UI)

### 2. Configure Environment

Set these environment variables for the MCP server:

```bash
# LLM Provider (for memory inference)
CHAT_LLM_PROVIDER=openai-compatible
CHAT_LLM_MODEL=MiniMax-M2.7
CHAT_LLM_API_KEY=your-api-key
CHAT_LLM_BASE_URL=http://your-llm-server:8317/v1

# Embedding Provider (Ollama)
EMBEDDED_PROVIDER=ollama
EMBEDDED_MODEL=nomic-embed-text
EMBEDDED_BASE_URL=http://localhost:11434
EMBEDDING_MODEL_DIMS=768

# Vector Store (Qdrant)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 3. Use MCP Tools

The MCP server exposes 7 tools for memory operations:

| Tool | Purpose |
|------|---------|
| `add_memories(text, infer)` | Store a new memory |
| `search_memory(query)` | Semantic search |
| `list_memories()` | List all memories |
| `get_memory(memory_id)` | Get one by ID |
| `update_memory(memory_id, text)` | Update content |
| `delete_memories(memory_ids)` | Delete by IDs |
| `delete_all_memories()` | Delete all memories |

## MCP Tool Reference

### add_memories

Store a new memory. The `infer` parameter controls whether LLM extracts facts:

```bash
# With LLM inference (extracts facts)
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add_memories",
      "arguments": {"text": "I love cats and dogs", "infer": true}
    }
  }'

# Without inference (store verbatim)
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add_memories",
      "arguments": {"text": "Project deadline is Friday", "infer": false}
    }
  }'
```

### search_memory

Semantic search across memories:

```bash
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_memory",
      "arguments": {"query": "pets"}
    }
  }'
```

### list_memories

Get all memories for the current user:

```bash
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "list_memories",
      "arguments": {}
    }
  }'
```

### get_memory

Get a specific memory by ID:

```bash
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_memory",
      "arguments": {"memory_id": "uuid-here"}
    }
  }'
```

### update_memory

Update a memory's content:

```bash
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "update_memory",
      "arguments": {"memory_id": "uuid-here", "text": "Updated content"}
    }
  }'
```

### delete_memories

Delete specific memories by ID:

```bash
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "delete_memories",
      "arguments": {"memory_ids": ["uuid-1", "uuid-2"]}
    }
  }'
```

### delete_all_memories

Delete all memories for the current user:

```bash
curl -X POST "http://localhost:8765/mcp/{user_id}/http/{client_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "delete_all_memories",
      "arguments": {}
    }
  }'
```

## Plugin Lifecycle Hooks

The plugin includes lifecycle hooks that automatically capture memories:

| Hook | When | What it does |
|------|------|--------------|
| `SessionStart` | On startup/resume | Prompts to load relevant memories |
| `UserPromptSubmit` | Before each prompt | Injects relevant memories into context |
| `PreCompact` | Before context compaction | Saves session summary |
| `Stop` | After each response | Reminds to store learnings |
| `TaskCompleted` | When task completes | Prompts to extract learnings |
| `PreToolUse` | Before Write/Edit | Blocks writes to MEMORY.md |

See [references/hooks.md](references/hooks.md) for details.

## Architecture

The system uses:
- **MCP (Model Context Protocol)** for agent communication
- **Qdrant** vector store for semantic search
- **Ollama** for embeddings
- **LLM** for memory inference (fact extraction)

See [references/architecture.md](references/architecture.md) for details.

## MCP Server Endpoints

| Endpoint | Purpose |
|---------|---------|
| `POST /mcp/{user_id}/http/{client_id}` | Main MCP endpoint (JSON-RPC) |
| `GET /mcp/{client_id}/sse/{user_id}` | SSE endpoint (deprecated) |

## User/Client IDs

The MCP URL includes both `user_id` and `client_id`:
- `user_id`: Identifies the user (defaults to current user)
- `client_id`: Identifies the client app (defaults to "plugin")

You can set them via environment variables:
```bash
export MEM0_USER_ID=myuser
export MCP_CLIENT_ID=myclient
```

## Troubleshooting

### MCP server not responding
```bash
# Check if container is running
docker compose ps openmemory-mcp

# View logs
docker compose logs openmemory-mcp
```

### Qdrant connection issues
```bash
# Check Qdrant is running
docker compose ps mem0_store

# Test Qdrant API
curl http://localhost:6333/collections
```

### Embedding slow or failing
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Test embedding
curl -X POST http://localhost:11434/api/embed \
  -d '{"model": "nomic-embed-text", "input": "test"}'
```

## References

| Topic | File |
|-------|------|
| Quickstart | [references/quickstart.md](references/quickstart.md) |
| MCP Tools Reference | [references/mcp-tools.md](references/mcp-tools.md) |
| Lifecycle Hooks | [references/hooks.md](references/hooks.md) |
| Architecture | [references/architecture.md](references/architecture.md) |
