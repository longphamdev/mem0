#!/usr/bin/env python3
"""Capture session state via the MCP server.

Safety net for PreCompact and Stop hooks — reads the transcript JSONL,
extracts structured session state, and stores it via the MCP server.

Used by:
  - PreCompact hook: Tags with "pre-compaction" (context about to be lost)
  - Stop hook:       Tags with "session-end" (session ending, Claude can't respond)

Input:  JSON on stdin with transcript_path, session_id, cwd
Output: stderr logs only (exit 0 always — must not block)
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import urllib.request
import urllib.error

log = logging.getLogger("mem0-capture")
log.setLevel(logging.DEBUG)
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[mem0-capture] %(message)s"))
log.addHandler(_handler)

# MCP server configuration
MCP_PROTOCOL = os.environ.get("MCP_PROTOCOL", "http")
MCP_HOST = os.environ.get("MCP_HOST", "localhost")
MCP_PORT = os.environ.get("MCP_PORT", "8765")
MCP_USER_ID = os.environ.get("MEM0_USER_ID", os.environ.get("USER", "default"))
MCP_CLIENT_ID = os.environ.get("MCP_CLIENT_ID", "plugin")
MCP_URL = f"{MCP_PROTOCOL}://{MCP_HOST}:{MCP_PORT}/mcp/{MCP_USER_ID}/http/{MCP_CLIENT_ID}"

MAX_TAIL_LINES = 500
MAX_USER_MESSAGES = 30
MAX_BASH_COMMANDS = 20
MAX_ASSISTANT_TEXT = 10000


def mcp_call(method: str, request_body: dict) -> dict:
    """Make a JSON RPC call to the MCP server."""
    body = {
        "jsonrpc": "2.0",
        "id": 99,
        "method": method,
        "params": request_body
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        MCP_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        log.warning("MCP call failed: %s", e)
        return {}


def mcp_add_memory(text: str, source: str) -> bool:
    """Store session state as a memory via MCP server."""
    body = {
        "name": "add_memories",
        "arguments": {
            "text": text,
            "infer": False  # Store verbatim without LLM inference
        }
    }
    result = mcp_call("tools/call", body)
    if result and "result" in result:
        log.info("Session state stored successfully")
        return True
    log.warning("MCP call did not return expected result: %s", result)
    return False


def tail_lines(filepath: str, n: int) -> list[str]:
    """Read last n lines of a file efficiently."""
    try:
        with open(filepath, "rb") as f:
            f.seek(0, 2)
            file_size = f.tell()
            if file_size == 0:
                return []
            chunk_size = min(file_size, n * 4096)
            f.seek(max(0, file_size - chunk_size))
            data = f.read().decode("utf-8", errors="replace")
            return data.splitlines()[-n:]
    except OSError:
        return []


def parse_transcript(lines: list[str]) -> dict:
    """Parse transcript JSONL lines and extract session state."""
    user_messages: list[str] = []
    files_modified: set[str] = set()
    bash_commands: list[str] = []
    last_assistant_text = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        entry_type = entry.get("type")
        if entry_type not in ("user", "assistant"):
            continue
        if entry.get("isSidechain"):
            continue

        message = entry.get("message", {})
        content_blocks = message.get("content", [])

        if entry_type == "user":
            parts = []
            if isinstance(content_blocks, str):
                parts.append(content_blocks)
            elif isinstance(content_blocks, list):
                for block in content_blocks:
                    if isinstance(block, str):
                        parts.append(block)
                    elif isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
            text = "\n".join(parts).strip()
            if text and len(text) > 10 and not text.startswith("<"):
                user_messages.append(text)

        elif entry_type == "assistant":
            for block in content_blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    text = block.get("text", "").strip()
                    if text:
                        last_assistant_text = text
                if block.get("type") == "tool_use":
                    tool_name = block.get("name", "")
                    tool_input = block.get("input", {})
                    if tool_name in ("Write", "Edit"):
                        fp = tool_input.get("file_path", "")
                        if fp:
                            files_modified.add(fp)
                    elif tool_name == "Bash":
                        cmd = tool_input.get("command", "")
                        if cmd:
                            bash_commands.append(cmd)

    return {
        "user_messages": user_messages[-MAX_USER_MESSAGES:],
        "files_modified": sorted(files_modified),
        "bash_commands": bash_commands[-MAX_BASH_COMMANDS:],
        "last_assistant_text": last_assistant_text[:MAX_ASSISTANT_TEXT],
    }


def build_content(state: dict, source: str) -> str:
    """Build structured markdown from parsed state."""
    parts = [f"## Session State ({source})\n"]

    if state["user_messages"]:
        parts.append("### What the user was working on")
        for msg in state["user_messages"]:
            truncated = msg[:5000] + "..." if len(msg) > 5000 else msg
            parts.append(f"- {truncated}")
        parts.append("")

    if state["files_modified"]:
        parts.append("### Files modified this session")
        for fp in state["files_modified"]:
            parts.append(f"- `{fp}`")
        parts.append("")

    if state["bash_commands"]:
        parts.append("### Recent commands")
        for cmd in state["bash_commands"]:
            truncated = cmd[:1000] + "..." if len(cmd) > 1000 else cmd
            parts.append(f"- `{truncated}`")
        parts.append("")

    if state["last_assistant_text"]:
        parts.append("### Last context")
        parts.append(state["last_assistant_text"])
        parts.append("")

    return "\n".join(parts)


def main():
    source = "pre-compaction"
    for arg in sys.argv[1:]:
        if arg.startswith("--source="):
            source = arg.split("=", 1)[1]

    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        log.debug("No valid JSON on stdin")
        return

    transcript_path = hook_input.get("transcript_path", "")
    if not transcript_path:
        log.debug("No transcript_path provided")
        return

    lines = tail_lines(transcript_path, MAX_TAIL_LINES)
    if not lines:
        log.debug("Transcript empty or unreadable: %s", transcript_path)
        return

    state = parse_transcript(lines)
    if not state["user_messages"] and not state["files_modified"]:
        log.debug("No meaningful session state to capture")
        return

    content = build_content(state, source)

    log.info(
        "Capturing session state: %d user msgs, %d files, %d commands",
        len(state["user_messages"]),
        len(state["files_modified"]),
        len(state["bash_commands"]),
    )

    mcp_add_memory(content, source)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("Unexpected error: %s", e)
    sys.exit(0)
