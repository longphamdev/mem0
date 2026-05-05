# OpenMemory Architecture

Self-hosted memory system architecture using MCP, Qdrant, and Ollama.

## Overview

```
┌──────────────┐      MCP (JSON-RPC)      ┌─────────────────────┐
│  Claude Code │ ◄─────────────────────► │  OpenMemory MCP     │
│   (Agent)    │                          │  Server (FastAPI)   │
└──────────────┘                          └──────────┬──────────┘
                                                      │
                                     ┌────────────────┼────────────────┐
                                     │                │                │
                                     ▼                ▼                ▼
                              ┌──────────┐    ┌──────────────┐    ┌──────────┐
                              │  Qdrant │    │   Ollama     │    │   LLM    │
                              │ (Vector)│    │ (Embeddings)│    │(Inference)│
                              └──────────┘    └──────────────┘    └──────────┘
```

## Components

### OpenMemory MCP Server

- **Technology:** FastAPI + MCP Python SDK
- **Port:** 8765
- **Protocol:** JSON-RPC over Streamable HTTP
- **Responsibilities:**
  - Expose 7 MCP tools for memory operations
  - Handle user/app authentication via URL parameters
  - Coordinate with Qdrant and Ollama
  - Log access for audit trails

### Qdrant (Vector Store)

- **Technology:** Qdrant v1.13+
- **Ports:** 6333 (HTTP), 6334 (GRPC)
- **Purpose:** Semantic search and memory storage
- **Collections:** Stores memory vectors with payloads

### Ollama (Embeddings)

- **Technology:** Ollama with local models
- **Port:** 11434
- **Default Model:** `nomic-embed-text`
- **Purpose:** Convert text to vectors for semantic search

### LLM (Inference)

- **Purpose:** Fact extraction from natural language input
- **Configurable:** Via `CHAT_LLM_*` environment variables
- **Used by:** `add_memories` with `infer=true`

## Memory Processing Pipeline

### Add Memory (infer=true)

```
User Input Text
      │
      ▼
┌─────────────────┐
│  LLM Inference  │  Extract structured facts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ollama Embed   │  Convert to vector
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Qdrant Store   │  Store vector + payload
└─────────────────┘
```

### Add Memory (infer=false)

```
User Input Text
      │
      ▼
┌─────────────────┐
│  Direct Store   │  No LLM inference
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ollama Embed   │  Convert to vector
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Qdrant Store   │  Store vector + payload
└─────────────────┘
```

### Search Memory

```
Search Query
      │
      ▼
┌─────────────────┐
│  Ollama Embed   │  Convert query to vector
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Qdrant Search  │  Find similar vectors
└────────┬────────┘
         │
         ▼
   Ranked Results
   (by similarity score)
```

## MCP Tool Flow

### User Identification

The MCP URL includes user/client identifiers:

```
http://localhost:8765/mcp/{user_id}/http/{client_id}
```

- `user_id`: Identifies the user (stored in database)
- `client_id`: Identifies the client app (e.g., "plugin", "web")

### Access Control

1. **User/App lookup:** Each request validates user exists and app is active
2. **Memory-level ACL:** Memories track which apps can access them
3. **Delete permissions:** Apps can only delete memories they created

## Data Model

### Memory

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `user_id` | UUID | Owner user |
| `app_id` | UUID | Creating app |
| `content` | text | Memory content |
| `state` | enum | active, deleted, archived, paused |
| `metadata_` | JSON | Custom metadata |
| `created_at` | datetime | Creation time |
| `updated_at` | datetime | Last update |

### MemoryAccessLog

Tracks every access to memories for audit:

| Field | Type | Description |
|-------|------|-------------|
| `memory_id` | UUID | Accessed memory |
| `app_id` | UUID | Accessing app |
| `access_type` | string | get, search, list, update, delete |
| `accessed_at` | datetime | Access time |
| `metadata_` | JSON | Access details (query, score, etc.) |

### MemoryStatusHistory

Tracks state changes:

| Field | Type | Description |
|-------|------|-------------|
| `memory_id` | UUID | Memory |
| `changed_by` | UUID | User who changed |
| `old_state` | enum | Previous state |
| `new_state` | enum | New state |
| `changed_at` | datetime | Change time |

## Performance Characteristics

| Operation | Typical Latency | Notes |
|-----------|----------------|-------|
| `add_memories` (infer=true) | 3-22s | LLM inference + embedding |
| `add_memories` (infer=false) | ~1s | Just embedding |
| `search_memory` | 70-150ms | Vector search |
| `list_memories` | 15-30ms | DB query |
| `get_memory` | <50ms | DB lookup |
| `update_memory` | ~100ms | DB + vector update |
| `delete_memories` | 1-8s | First call slower |
| `delete_all_memories` | 15-35s | Scales with count |

## Memory Layers

Mem0/OpenMemory supports three layers:

### 1. Conversation Memory
- In-flight messages within a turn
- **Lifetime:** Single response
- **Managed by:** Agent, not Mem0

### 2. Session Memory
- Short-lived facts for current task
- **Lifetime:** Minutes to hours
- **Managed by:** Mem0 with session scope

### 3. User Memory
- Long-lived knowledge per user
- **Lifetime:** Weeks to forever
- **Managed by:** Mem0 with user scope

## Environment Configuration

```bash
# LLM Provider
CHAT_LLM_PROVIDER=openai-compatible
CHAT_LLM_MODEL=MiniMax-M2.7
CHAT_LLM_API_KEY=xxx
CHAT_LLM_BASE_URL=http://llm:8317/v1

# Embedding Provider
EMBEDDED_PROVIDER=ollama
EMBEDDED_MODEL=nomic-embed-text
EMBEDDED_BASE_URL=http://ollama:11434
EMBEDDING_MODEL_DIMS=768

# Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Docker Services

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| `openmemory-mcp` | custom (Dockerfile) | 8765 | MCP server |
| `mem0_store` | qdrant/qdrant:v1.13.0 | 6333, 6334 | Vector DB |
| `openmemory-ui` | mem0/openmemory-ui:latest | 3000 | Web UI |
