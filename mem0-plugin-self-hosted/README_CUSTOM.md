# Mem0 Plugin Self-Hosted — Custom Domain Setup

Hướng dẫn cài đặt mem0-plugin-self-hosted với custom domain (HTTPS).

## Requirements

- Docker & Docker Compose
- Domain pointing to your server (ví dụ: `mem0.longphamthien.us`)
- SSL certificate cho domain (có thể dùng nginx proxy với Let's Encrypt)
- MCP server đang chạy (hoặc cấu hình reverse proxy đến MCP server)

## Environment Variables

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_PROTOCOL` | `http` | Protocol: `http` hoặc `https` |
| `MCP_HOST` | `localhost` | MCP server host (domain hoặc IP) |
| `MCP_PORT` | `8765` | MCP server port |
| `MEM0_USER_ID` | current user | User identifier cho MCP |

### Optional Variables (for MCP Server)

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAT_LLM_PROVIDER` | - | LLM provider (ví dụ: `openai-compatible`) |
| `CHAT_LLM_MODEL` | - | LLM model name |
| `CHAT_LLM_API_KEY` | - | API key cho LLM |
| `CHAT_LLM_BASE_URL` | - | Base URL của LLM server |
| `EMBEDDED_PROVIDER` | `ollama` | Embedding provider |
| `EMBEDDED_MODEL` | `nomic-embed-text` | Embedding model |
| `EMBEDDED_BASE_URL` | `http://localhost:11434` | Ollama URL |
| `EMBEDDING_MODEL_DIMS` | `768` | Embedding dimensions |
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |

## Docker Compose Setup

### 1. MCP Server + Qdrant (Minimal)

```yaml
version: '3.8'

services:
  mem0_store:
    image: qdrant/qdrant:v1.13.0
    network_mode: "host"
    ports:
      - "6333:6333"  # Qdrant HTTP
      - "6334:6334"  # Qdrant GRPC
    volumes:
      - ./mem0_store/storage:/qdrant/storage
    restart: unless-stopped

  openmemory-mcp:
    image: mem0-openmemory-mcp  # Hoặc build từ source
    network_mode: "host"
    ports:
      - "8765:8765"  # MCP Server
    environment:
      - CHAT_LLM_PROVIDER=openai-compatible
      - CHAT_LLM_MODEL=MiniMax-M2.7
      - CHAT_LLM_API_KEY=${CHAT_LLM_API_KEY}
      - CHAT_LLM_BASE_URL=http://your-llm-server:8317/v1
      - EMBEDDED_PROVIDER=ollama
      - EMBEDDED_MODEL=nomic-embed-text
      - EMBEDDED_BASE_URL=http://localhost:11434
      - EMBEDDING_MODEL_DIMS=768
      - QDRANT_HOST=localhost
      - QDRANT_PORT=6333
    restart: unless-stopped
```

### 2. Full Stack (với Nginx Proxy HTTPS)

```yaml
version: '3.8'

services:
  mem0_store:
    image: qdrant/qdrant:v1.13.0
    network_mode: "host"
    volumes:
      - ./mem0_store/storage:/qdrant/storage

  openmemory-mcp:
    image: mem0-openmemory-mcp
    network_mode: "host"
    environment:
      - CHAT_LLM_PROVIDER=openai-compatible
      - CHAT_LLM_MODEL=MiniMax-M2.7
      - CHAT_LLM_API_KEY=${CHAT_LLM_API_KEY}
      - CHAT_LLM_BASE_URL=http://your-llm-server:8317/v1
      - EMBEDDED_PROVIDER=ollama
      - EMBEDDED_MODEL=nomic-embed-text
      - EMBEDDED_BASE_URL=http://localhost:11434
      - QDRANT_HOST=localhost
      - QDRANT_PORT=6333

  nginx:
    image: nginx:latest
    network_mode: "host"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - openmemory-mcp
```

### 3. Nginx Config for HTTPS Proxy

```nginx
# /etc/nginx/conf.d/mem0.conf

upstream mem0_mcp {
    server 127.0.0.1:8765;
}

server {
    listen 80;
    server_name mem0.longphamthien.us;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mem0.longphamthien.us;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location /mcp/ {
        proxy_pass http://mem0_mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

## Plugin Configuration

### .mcp.json

```json
{
  "mcpServers": {
    "mem0": {
      "type": "http",
      "url": "https://mem0.longphamthien.us/mcp/default/http/plugin"
    }
  }
}
```

### Scripts (.bashrc or .env)

```bash
# Custom domain settings
export MCP_PROTOCOL=https
export MCP_HOST=mem0.longphamthien.us
export MCP_PORT=8765
export MEM0_USER_ID=default
```

## Quick Start

### Step 1: Start Services

```bash
# Clone repo
git clone https://github.com/mem0ai/mem0.git ~/mem0
cd ~/mem0

# Start MCP + Qdrant
docker compose up -d

# Or use custom compose file
docker compose -f docker-compose-custom.yml up -d
```

### Step 2: Setup Nginx Proxy

```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/conf.d/mem0.conf

# Edit config with your domain
sudo nano /etc/nginx/conf.d/mem0.conf

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Test Connection

```bash
# From anywhere
curl -X POST "https://mem0.longphamthien.us/mcp/default/http/plugin" \
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

### Step 4: Install Plugin

```bash
# In Claude Code
/plugin install mem0-openmemory@~/mem0/mem0-plugin-self-hosted
```

## MCP Client Library

File `scripts/mcp_client.sh` hỗ trợ custom host:

```bash
# Option 1: Set env vars before sourcing
export MCP_PROTOCOL=https
export MCP_HOST=mem0.longphamthien.us
export MCP_PORT=8765
export MEM0_USER_ID=myuser

source mcp_client.sh

# Test functions
mcp_check_connection && echo "OK"
mcp_add_memory "Test" false
mcp_search_memories "test"
mcp_list_memories
```

## Troubleshooting

### Connection Refused

```bash
# Check MCP server is running
docker compose ps openmemory-mcp

# View logs
docker compose logs -f openmemory-mcp

# Restart if needed
docker compose restart openmemory-mcp
```

### SSL Certificate Error

```bash
# If using self-signed cert or private CA
# Add cert to system trust store
sudo cp your-cert.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

### Nginx 502 Bad Gateway

```bash
# Check nginx can reach MCP
curl -v http://localhost:8765/mcp/default/http/plugin

# Check nginx error logs
tail -f /var/log/nginx/error.log
```

### Test MCP Tools

```bash
MCP_PROTOCOL=https MCP_HOST=mem0.longphamthien.us source mcp_client.sh

# Add memory
mcp_add_memory "I love coding in Python" false

# Search
mcp_search_memories "Python"

# List all
mcp_list_memories
```

## File Structure

```
mem0-plugin-self-hosted/
├── .mcp.json                    # MCP server URL config
├── scripts/
│   └── mcp_client.sh            # Bash library for MCP calls
├── skills/
│   ├── mem0-openmemory/         # Self-hosted memory skill
│   └── mem0-codex/              # Codex memory protocol
├── hooks/
│   └── hooks.json               # Lifecycle hooks
├── docker-compose.yml           # Base compose
└── README_CUSTOM.md              # This file
```

## Security Notes

- HTTPS được khuyến nghị cho production
- Nếu dùng API key cho LLM, bảo mật nó trong `docker-compose.yml` hoặc `.env`
- Firewall chỉ mở ports 80, 443 (web) và 8765 nếu cần direct access
- Consider using fail2ban để prevent brute force attacks
