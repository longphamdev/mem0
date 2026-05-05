# Mem0 OpenMemory — Self-Hosted Memory Skill

Self-hosted memory integration for AI agents via local MCP server.

## Overview

This skill provides persistent memory capabilities for AI agents using:
- **Local MCP server** (no cloud dependency)
- **Qdrant** vector database
- **Ollama** for embeddings

## Quick Setup

### 1. Start Services

```bash
cd /path/to/mem0
docker compose up -d
```

### 2. Verify MCP Server

```bash
curl -X POST "http://localhost:8765/mcp/default/http/default" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0"}
    }
  }'
```

### 3. Test Memory Operations

```bash
# Add a memory
curl -X POST "http://localhost:8765/mcp/default/http/default" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add_memories",
      "arguments": {"text": "I love coding in Python", "infer": false}
    }
  }'

# Search memories
curl -X POST "http://localhost:8765/mcp/default/http/default" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_memory",
      "arguments": {"query": "coding"}
    }
  }'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEM0_USER_ID` | `default` | User identifier |
| `MCP_CLIENT_ID` | `plugin` | Client identifier |
| `MCP_HOST` | `localhost` | MCP server host |
| `MCP_PORT` | `8765` | MCP server port |

## Configuration

The MCP server expects these environment variables:

```bash
# LLM (for memory inference)
CHAT_LLM_PROVIDER=openai-compatible
CHAT_LLM_MODEL=MiniMax-M2.7
CHAT_LLM_API_KEY=your-key
CHAT_LLM_BASE_URL=http://llm-server:8317/v1

# Embeddings (Ollama)
EMBEDDED_PROVIDER=ollama
EMBEDDED_MODEL=nomic-embed-text
EMBEDDED_BASE_URL=http://localhost:11434
EMBEDDING_MODEL_DIMS=768

# Vector Store (Qdrant)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Included Tools

| Tool | Description |
|------|-------------|
| `add_memories` | Store a new memory |
| `search_memory` | Semantic search |
| `list_memories` | List all memories |
| `get_memory` | Get by ID |
| `update_memory` | Update content |
| `delete_memories` | Delete by IDs |
| `delete_all_memories` | Delete all |

## Lifecycle Hooks

The plugin automatically captures memories at key points:

- **SessionStart**: Load relevant memories on startup
- **UserPromptSubmit**: Inject relevant memories into prompt
- **PreCompact**: Save session summary before compaction
- **Stop**: Remind to store learnings after response
- **TaskCompleted**: Prompt to extract task learnings
- **PreToolUse**: Block writes to MEMORY.md files

## Troubleshooting

### Server not responding
```bash
docker compose logs openmemory-mcp
```

### Database issues
```bash
docker compose ps
docker compose restart openmemory-mcp
```

### Test MCP connection
```bash
source scripts/mcp_client.sh && mcp_check_connection
```
