# MCP Tools Reference

Complete reference for all 7 MCP tools exposed by the local OpenMemory server.

## Tool List

| Tool | Parameters | Description |
|------|-------------|-------------|
| `add_memories` | `text: string`, `infer?: boolean` | Store a new memory |
| `search_memory` | `query: string` | Semantic search |
| `list_memories` | (none) | List all memories |
| `get_memory` | `memory_id: string` | Get one by ID |
| `update_memory` | `memory_id: string`, `text: string` | Update content |
| `delete_memories` | `memory_ids: string[]` | Delete by IDs |
| `delete_all_memories` | (none) | Delete all memories |

---

## add_memories

Store a new memory. The `infer` parameter controls whether LLM extracts structured facts.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `text` | `string` | Yes | - | The memory content to store |
| `infer` | `boolean` | No | `true` | If `true`, LLM extracts facts; if `false`, stores verbatim |

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "add_memories",
    "arguments": {
      "text": "I love coding in Python and TypeScript",
      "infer": false
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"results\": [{\"id\": \"uuid-here\", \"memory\": \"I love coding in Python and TypeScript\", \"event\": \"ADD\", \"actor_id\": null, \"role\": \"user\"}]}"
      }
    ],
    "isError": false
  }
}
```

### Inference Mode

- **`infer=true`** (default): LLM extracts structured facts from the text. Best for natural language input.
- **`infer=false`**: Stores text exactly as provided. Best for pre-structured data or bulk imports.

---

## search_memory

Semantic search across stored memories.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | `string` | Yes | Natural language search query |

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_memory",
    "arguments": {
      "query": "What programming languages do I know?"
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"results\": [\n    {\n      \"id\": \"uuid-here\",\n      \"memory\": \"I love coding in Python and TypeScript\",\n      \"hash\": \"abc123\",\n      \"created_at\": \"2025-05-05T12:00:00Z\",\n      \"updated_at\": \"2025-05-05T12:00:00Z\",\n      \"score\": 0.85\n    }\n  ]\n}"
      }
    ],
    "isError": false
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Memory UUID |
| `memory` | `string` | Memory content |
| `hash` | `string` | Content hash |
| `created_at` | `string` | ISO timestamp |
| `updated_at` | `string` | ISO timestamp |
| `score` | `number` | Relevance score (0-1) |

---

## list_memories

List all memories for the current user.

### Parameters

None (empty object).

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "list_memories",
    "arguments": {}
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  {\n    \"id\": \"uuid-1\",\n    \"memory\": \"First memory\",\n    \"hash\": \"hash1\",\n    \"created_at\": \"...\",\n    \"updated_at\": \"...\"\n  },\n  {\n    \"id\": \"uuid-2\",\n    \"memory\": \"Second memory\",\n    \"hash\": \"hash2\",\n    \"created_at\": \"...\",\n    \"updated_at\": \"...\"\n  }\n]"
      }
    ],
    "isError": false
  }
}
```

---

## get_memory

Get a specific memory by its ID.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `memory_id` | `string` | Yes | UUID of the memory to retrieve |

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "get_memory",
    "arguments": {
      "memory_id": "e51e4e8a-76fe-47f4-bdf5-c407cc5512db"
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"id\": \"e51e4e8a-76fe-47f4-bdf5-c407cc5512db\",\n  \"memory\": \"I love coding in Python and TypeScript\",\n  \"hash\": null,\n  \"created_at\": \"2025-05-05T12:15:58.574013\",\n  \"updated_at\": \"2025-05-05T12:15:58.574015\",\n  \"state\": \"active\"\n}"
      }
    ],
    "isError": false
  }
}
```

---

## update_memory

Update a memory's content by ID.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `memory_id` | `string` | Yes | UUID of the memory to update |
| `text` | `string` | Yes | New content |

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "update_memory",
    "arguments": {
      "memory_id": "e51e4e8a-76fe-47f4-bdf5-c407cc5512db",
      "text": "Updated memory content"
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"id\": \"e51e4e8a-76fe-47f4-bdf5-c407cc5512db\",\n  \"memory\": \"Updated memory content\",\n  \"updated\": true\n}"
      }
    ],
    "isError": false
  }
}
```

---

## delete_memories

Delete specific memories by their IDs.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `memory_ids` | `string[]` | Yes | Array of memory UUIDs to delete |

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "delete_memories",
    "arguments": {
      "memory_ids": ["uuid-1", "uuid-2", "uuid-3"]
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Successfully deleted 3 memories"
      }
    ],
    "isError": false
  }
}
```

---

## delete_all_memories

Delete ALL memories for the current user.

### Parameters

None (empty object).

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "delete_all_memories",
    "arguments": {}
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Successfully deleted all memories"
      }
    ],
    "isError": false
  }
}
```

### Warning

This operation is irreversible. Use with caution.

---

## Error Responses

All tools return error messages as plain text when something goes wrong:

```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: user_id not provided"
      }
    ],
    "isError": true
  }
}
```

Common errors:
- `Error: user_id not provided` - No user_id in context
- `Error: client_name not provided` - No client_name in context
- `Error: Memory system is currently unavailable` - MCP server or Qdrant down
- `Error: Invalid memory ID format: xxx` - Malformed UUID
