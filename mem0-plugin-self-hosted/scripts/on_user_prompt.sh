#!/usr/bin/env bash
# Hook: UserPromptSubmit
#
# Fires on every user message. Searches mem0 for relevant memories
# and injects them into Claude's context before processing.
#
# Input:  JSON on stdin with prompt, session_id, cwd, transcript_path
# Output: Matching memories as context text (exit 0)
#
# Skips search for very short prompts (< 20 chars) and when
# MCP server is not available. Uses a 3s timeout to minimize latency.

# Intentionally omit -e so the script always exits 0 even if
# curl or jq fail — must never block the user's prompt.
set -uo pipefail

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""' 2>/dev/null || echo "")

# Skip trivial prompts — not worth a network call
if [ ${#PROMPT} -lt 20 ]; then
  exit 0
fi

# Check if MCP server is available
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/mcp_client.sh"

if ! mcp_check_connection; then
  exit 0
fi

# Search mem0 for memories relevant to this prompt
RESPONSE=$(mcp_search_memories "$PROMPT")

if [ -z "$RESPONSE" ]; then
  exit 0
fi

# Extract result from MCP response
RESULT=$(mcp_extract_result "$RESPONSE")

if [ -z "$RESULT" ]; then
  exit 0
fi

# Parse the result to extract memories
MEMORIES=$(echo "$RESULT" | jq -r '
  if type == "array" then . else .results // [] end |
  if length == 0 then empty else
  "## Relevant memories from mem0\n\n" +
  (map(select(.memory != null) | "- " + .memory) | join("\n"))
  end
' 2>/dev/null || echo "")

if [ -n "$MEMORIES" ]; then
  echo "$MEMORIES"
fi

exit 0
