# Mem0 Plugin for Claude Code — Self-Hosted

Add persistent memory to Claude Code using your own infrastructure. No external APIs, no API keys — all data stays on your server.

**This is the self-hosted version** of the Mem0 plugin. For the cloud version (Mem0 Platform), see the main `mem0-plugin` folder.

## Architecture

```
Claude Code ──MCP (JSON-RPC)──► OpenMemory MCP Server ──► Qdrant (vectors)
                                    │
                                    └──► Ollama (embeddings)
                                    │
                                    └──► LLM (inference)
```

## Prerequisites

- Docker and Docker Compose
- Ollama with embedding model (e.g., `nomic-embed-text`)
- LLM server for memory inference

## Quick Start

### Step 1: Start Services

```bash
cd /path/to/mem0
docker compose up -d
```

This starts:
- `openmemory-mcp` on `localhost:8765` — MCP server
- `mem0_store` on `localhost:6333` — Qdrant vector database
- `openmemory-ui` on `localhost:3000` — Web UI (optional)

### Step 2: Configure Environment

The MCP server needs these environment variables (set in docker-compose or `.env`):

```bash
# LLM for memory inference
CHAT_LLM_PROVIDER=openai-compatible
CHAT_LLM_MODEL=MiniMax-M2.7
CHAT_LLM_API_KEY=your-api-key
CHAT_LLM_BASE_URL=http://your-llm-server:8317/v1

# Ollama for embeddings
EMBEDDED_PROVIDER=ollama
EMBEDDED_MODEL=nomic-embed-text
EMBEDDED_BASE_URL=http://localhost:11434
EMBEDDING_MODEL_DIMS=768

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Step 3: Install the Plugin

In Claude Code:

```
/plugin marketplace add mem0ai/mem0
/plugin install mem0@mem0-plugins
```

Or clone this repo and install from local path:

```bash
git clone https://github.com/mem0ai/mem0.git ~/mem0-plugins
/plugin install mem0-openmemory@~/mem0-plugins/mem0-plugin-self-hosted
```

### Step 4: Verify Installation

Start a new session, then ask: *"Search my memories for coding"*

If the MCP tools appear and respond, you're all set.

## MCP Tools

Once connected, 7 tools are available:

| Tool | Purpose |
|------|---------|
| `add_memories(text, infer)` | Store a new memory |
| `search_memory(query)` | Semantic search |
| `list_memories()` | List all memories |
| `get_memory(memory_id)` | Get one by ID |
| `update_memory(memory_id, text)` | Update content |
| `delete_memories(memory_ids)` | Delete by IDs |
| `delete_all_memories()` | Delete all memories |

## Lifecycle Hooks

The plugin automatically captures memories at key points:

| Hook | When | What it does |
|------|------|--------------|
| `SessionStart` | Startup/resume | Prompts to load relevant memories |
| `UserPromptSubmit` | Every prompt | Injects relevant memories into context |
| `PreCompact` | Before compaction | Saves session summary |
| `Stop` | After response | Reminds to store learnings |
| `TaskCompleted` | Task complete | Prompts to extract learnings |
| `PreToolUse` | Write/Edit | Blocks writes to MEMORY.md |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEM0_USER_ID` | `default` | User identifier |
| `MCP_CLIENT_ID` | `plugin` | Client identifier |
| `MCP_HOST` | `localhost` | MCP server host |
| `MCP_PORT` | `8765` | MCP server port |

## Troubleshooting

### MCP server not responding

```bash
# Check if container is running
docker compose ps openmemory-mcp

# View logs
docker compose logs -f openmemory-mcp

# Restart
docker compose restart openmemory-mcp
```

### Qdrant connection issues

```bash
# Check Qdrant is running
curl http://localhost:6333/collections

# Restart Qdrant
docker compose restart mem0_store
```

### Test MCP connection

```bash
cd mem0-plugin-self-hosted/scripts
source mcp_client.sh && mcp_check_connection
```

## Skills

The plugin includes skills for Claude Code:

| Skill | Purpose |
|-------|---------|
| `mem0-openmemory` | How to use MCP tools for memory |
| `mem0-codex` | Memory protocol for Codex |

## Files

```
mem0-plugin-self-hosted/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server config
├── hooks/
│   └── hooks.json           # Lifecycle hooks
├── scripts/
│   ├── mcp_client.sh        # MCP bash library
│   ├── on_session_start.sh  # SessionStart hook
│   ├── on_user_prompt.sh    # UserPromptSubmit hook
│   ├── on_task_completed.sh # TaskCompleted hook
│   ├── on_stop.sh           # Stop hook
│   ├── on_pre_compact.sh    # PreCompact hook
│   ├── on_pre_compact.py    # Python fallback
│   └── block_memory_write.sh # PreToolUse hook
├── skills/
│   ├── mem0-openmemory/    # Self-hosted memory skill
│   └── mem0-codex/          # Codex memory protocol
└── README.md                 # This file
```

## License

Apache-2.0
