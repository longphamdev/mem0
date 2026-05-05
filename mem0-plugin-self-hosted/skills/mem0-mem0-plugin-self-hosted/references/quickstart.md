# Mem0 OpenMemory Quickstart

Get started with self-hosted memory in 2 minutes.

## Prerequisites

- Docker and Docker Compose
- Ollama running with embedding model (e.g., `nomic-embed-text`)
- LLM server for memory inference

## Step 1: Start Services

```bash
cd /path/to/mem0
docker compose up -d
```

This starts:
- `openmemory-mcp` on `localhost:8765`
- `mem0_store` (Qdrant) on `localhost:6333`
- `openmemory-ui` on `localhost:3000`

## Step 2: Configure Environment

Create a `.env` file or export variables:

```bash
# LLM for memory inference
export CHAT_LLM_PROVIDER=openai-compatible
export CHAT_LLM_MODEL=MiniMax-M2.7
export CHAT_LLM_API_KEY=your-api-key
export CHAT_LLM_BASE_URL=http://your-llm:8317/v1

# Ollama for embeddings
export EMBEDDED_PROVIDER=ollama
export EMBEDDED_MODEL=nomic-embed-text
export EMBEDDED_BASE_URL=http://localhost:11434
export EMBEDDING_MODEL_DIMS=768

# Qdrant
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
```

## Step 3: Test the MCP Server

Initialize connection:
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

## Step 4: Add Your First Memory

```bash
curl -X POST "http://localhost:8765/mcp/default/http/default" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add_memories",
      "arguments": {"text": "I am a Python developer", "infer": false}
    }
  }'
```

## Step 5: Search Memories

```bash
curl -X POST "http://localhost:8765/mcp/default/http/default" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_memory",
      "arguments": {"query": "Python"}
    }
  }'
```

## Using the MCP Client Library

The plugin includes a bash library at `scripts/mcp_client.sh`:

```bash
cd mem0-plugin-self-hosted/scripts
source mcp_client.sh

# Initialize
mcp_initialize

# Add memory
mcp_add_memory "I love coding" false

# Search
mcp_search_memories "coding"

# List all
mcp_list_memories

# Get one
mcp_get_memory "memory-uuid"

# Update
mcp_update_memory "memory-uuid" "Updated text"

# Delete
mcp_delete_memories '["memory-uuid"]'

# Delete all
mcp_delete_all_memories
```

## Verify with MCP Client

```bash
cd mem0-plugin-self-hosted/scripts
bash -c 'source mcp_client.sh && mcp_check_connection && echo "MCP connection OK"'
```

## Docker Commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart MCP server
docker compose restart openmemory-mcp

# View logs
docker compose logs -f openmemory-mcp

# Check status
docker compose ps
```
