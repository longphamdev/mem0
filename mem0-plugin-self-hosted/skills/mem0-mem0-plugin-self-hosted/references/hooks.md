# Lifecycle Hooks

How the plugin uses lifecycle hooks to automatically capture memories.

## Hook Overview

| Hook | Trigger | Action |
|------|---------|--------|
| `SessionStart` | startup, resume, compact | Prompts Claude to load memories |
| `UserPromptSubmit` | every user message | Injects relevant memories |
| `PreCompact` | before compaction | Saves session summary |
| `Stop` | after response | Reminds to store learnings |
| `TaskCompleted` | task marked complete | Prompts to extract learnings |
| `PreToolUse` | Write/Edit tool | Blocks MEMORY.md writes |

---

## SessionStart Hook

**Matcher:** `startup|resume|compact`

**When:** On Claude Code startup, session resume, or context compaction

**What it does:**

For `startup`:
```
You have access to persistent memory via mem0 MCP tools. Before doing anything else:

1. Call `search_memory` with a query related to the current project.
2. Review the returned memories.
3. If appropriate, call `list_memories` to browse all stored memories.
```

For `resume`:
```
This is a resumed session. Your prior context is already loaded.

1. Call `search_memory` to refresh relevant memories.
2. If significant time passed, search for recent updates.
```

For `compact`:
```
Context was just compacted. You may have lost important session context.

1. Call `search_memory` to reload relevant knowledge.
2. Check for saved session state memories.
```

---

## UserPromptSubmit Hook

**When:** Before every user message is processed

**What it does:**

1. If prompt is < 20 chars, skips (not worth a network call)
2. Calls `search_memory` with the user's prompt
3. Injects relevant memories into Claude's context

**Example output:**
```
## Relevant memories from mem0

- User prefers dark mode
- Project uses Python 3.11
- Last worked on authentication feature
```

---

## PreCompact Hook

**When:** Before context compaction (last chance to save context)

**What it does:**

Prompts Claude to store a comprehensive session summary:

```
CRITICAL: Pre-Compaction Session Summary

Context compaction is about to happen. You MUST store a comprehensive session summary NOW using `add_memories`.

### Store:
1. Session summary (user goal, accomplishments, decisions, files modified)
2. Current state (what's in progress, pending items)
3. Any unstored learnings with metadata

### Then:
Acknowledge that session state has been saved.
```

A companion Python script (`on_pre_compact.py`) also captures transcript state directly.

---

## Stop Hook

**When:** After Claude finishes responding

**What it does:**

Prompts Claude to store learnings:

```
Before finishing, check if there are important learnings from this interaction:

1. Decisions made -> Store with metadata `{"type": "decision"}`
2. Patterns discovered -> Store with metadata `{"type": "task_learning"}`
3. Failed approaches -> Store with metadata `{"type": "anti_pattern"}`
4. User preferences -> Store with metadata `{"type": "user_preference"}`
5. Environment discoveries -> Store with metadata `{"type": "environmental"}`

Memories can include code snippets, file paths, examples.
```

A companion Python script captures transcript state in the background.

---

## TaskCompleted Hook

**When:** When a task is marked as completed

**What it does:**

Prompts Claude to extract learnings:

```
Task completed: "task_subject"

Extract key learnings from this completed task and store them using `add_memories`:

1. What strategy worked well? -> metadata `{"type": "task_learning"}`
2. Were there failed approaches? -> metadata `{"type": "anti_pattern"}`
3. Were there architectural decisions? -> metadata `{"type": "decision"}`
4. New conventions established? -> metadata `{"type": "convention"}`
```

---

## PreToolUse Hook

**Matcher:** `Write|Edit`

**When:** Before a Write or Edit tool call

**What it does:**

Blocks writes to MEMORY.md and similar files:

```
BLOCKED: Do not write to MEMORY.md. Use mem0 MCP `add_memories` tool instead.
```

This redirects Claude to use persistent memory via MCP instead of writing to files.

---

## Script Architecture

All hooks use the shared `mcp_client.sh` library:

```
scripts/
├── mcp_client.sh          # Shared MCP functions
├── on_session_start.sh    # SessionStart hook
├── on_user_prompt.sh      # UserPromptSubmit hook
├── on_pre_compact.sh      # PreCompact hook (bash)
├── on_pre_compact.py      # PreCompact hook (Python)
├── on_stop.sh             # Stop hook
├── on_stop_codex.sh       # Stop hook (Codex variant)
├── on_task_completed.sh   # TaskCompleted hook
└── block_memory_write.sh  # PreToolUse hook
```

### mcp_client.sh Functions

```bash
mcp_initialize()                    # Initialize MCP connection
mcp_add_memory(text, infer)         # Add a memory
mcp_search_memories(query)          # Search memories
mcp_list_memories()                 # List all memories
mcp_get_memory(memory_id)            # Get one by ID
mcp_update_memory(memory_id, text)  # Update content
mcp_delete_memories(memory_ids)      # Delete by IDs
mcp_delete_all_memories()            # Delete all
mcp_extract_result(response)        # Parse MCP response
mcp_check_connection()               # Health check
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `localhost` | MCP server host |
| `MCP_PORT` | `8765` | MCP server port |
| `MEM0_USER_ID` | current user | User identifier |
| `MCP_CLIENT_ID` | `plugin` | Client identifier |

### MCP URL

The hooks construct the MCP URL as:
```
http://${MCP_HOST}:${MCP_PORT}/mcp/${MEM0_USER_ID}/http/${MCP_CLIENT_ID}
```

Default: `http://localhost:8765/mcp/default/http/plugin`

---

## Troubleshooting

### Hook not firing
- Check `hooks/hooks.json` has correct entries
- Verify `${CLAUDE_PLUGIN_ROOT}` path is correct

### MCP call failing
- Check MCP server is running: `docker compose ps openmemory-mcp`
- Test connection: `source mcp_client.sh && mcp_check_connection`

### Memory not found
- Check user_id matches (case-sensitive)
- Verify memories exist: `mcp_list_memories`
