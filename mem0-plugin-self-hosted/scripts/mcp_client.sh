# MCP Client Library for mem0-plugin-self-hosted
# Provides functions to call the local MCP server
#
# Environment variables to configure:
#   MCP_HOST      - MCP server host (default: localhost)
#   MCP_PORT      - MCP server port (default: 8765)
#   MCP_PROTOCOL  - http or https (default: http)
#   MEM0_USER_ID  - User identifier (default: current user)
#   MCP_CLIENT_ID - Client identifier (default: plugin)
#
# Example: Use custom domain
#   export MCP_HOST=mem0.longphamthien.us
#   export MCP_PROTOCOL=https
#   export MEM0_USER_ID=myuser

set -uo pipefail

# Configuration
MCP_PROTOCOL="${MCP_PROTOCOL:-http}"
MCP_HOST="${MCP_HOST:-localhost}"
MCP_PORT="${MCP_PORT:-8765}"
MCP_USER_ID="${MEM0_USER_ID:-${USER:-default}}"
MCP_CLIENT_ID="${MCP_CLIENT_ID:-plugin}"

# Build the MCP endpoint URL
MCP_URL="${MCP_PROTOCOL}://${MCP_HOST}:${MCP_PORT}/mcp/${MCP_USER_ID}/http/${MCP_CLIENT_ID}"

# JSON RPC helper - makes a JSON RPC call to the MCP server
# Args:
#   $1 - method name (e.g., "tools/call")
#   $2 - request body as JSON string
mcp_call() {
    local method="$1"
    local body="$2"

    curl -s --max-time 30 \
        -X POST "$MCP_URL" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$body"
}

# Initialize MCP connection and get server info
mcp_initialize() {
    mcp_call "initialize" '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "mem0-plugin-self-hosted", "version": "1.0"}
        }
    }'
}

# Add a memory
# Args:
#   $1 - text to store
#   $2 - infer (true/false, default true)
mcp_add_memory() {
    local text="$1"
    local infer="${2:-true}"

    mcp_call "tools/call" "$(jq -n \
        --arg text "$text" \
        --argjson infer "$infer" \
        '{
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "add_memories",
                "arguments": {"text": $text, "infer": $infer}
            }
        }')"
}

# Search memories
# Args:
#   $1 - query string
mcp_search_memories() {
    local query="$1"

    mcp_call "tools/call" "$(jq -n \
        --arg query "$query" \
        '{
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_memory",
                "arguments": {"query": $query}
            }
        }')"
}

# List all memories
mcp_list_memories() {
    mcp_call "tools/call" '{
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "list_memories",
            "arguments": {}
        }
    }'
}

# Get a specific memory by ID
# Args:
#   $1 - memory_id
mcp_get_memory() {
    local memory_id="$1"

    mcp_call "tools/call" "$(jq -n \
        --arg memory_id "$memory_id" \
        '{
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_memory",
                "arguments": {"memory_id": $memory_id}
            }
        }')"
}

# Update a memory
# Args:
#   $1 - memory_id
#   $2 - new text
mcp_update_memory() {
    local memory_id="$1"
    local text="$2"

    mcp_call "tools/call" "$(jq -n \
        --arg memory_id "$memory_id" \
        --arg text "$text" \
        '{
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "update_memory",
                "arguments": {"memory_id": $memory_id, "text": $text}
            }
        }')"
}

# Delete specific memories
# Args:
#   $1 - JSON array of memory IDs
mcp_delete_memories() {
    local memory_ids="$1"

    mcp_call "tools/call" "$(jq -n \
        --argjson memory_ids "$memory_ids" \
        '{
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "delete_memories",
                "arguments": {"memory_ids": $memory_ids}
            }
        }')"
}

# Delete all memories
mcp_delete_all_memories() {
    mcp_call "tools/call" '{
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "delete_all_memories",
            "arguments": {}
        }
    }'
}

# Extract result from MCP response
# Args:
#   $1 - JSON response
mcp_extract_result() {
    local response="$1"
    echo "$response" | jq -r '.result.content[0].text // empty'
}

# Check if MCP server is available
mcp_check_connection() {
    local response
    response=$(curl -s --max-time 5 -o /dev/null -w "%{http_code}" "$MCP_URL" 2>/dev/null || echo "000")
    [ "$response" != "000" ]
}
