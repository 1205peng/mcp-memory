---
name: memory
description: Store and retrieve memories
---
# MCP Memory

Store and retrieve memories via HTTP API.

## store_memory
- URL: https://mcp-memory.zeabur.app/memory
- Method: POST
- Body: {"key": "xxx", "content": "xxx"}

## retrieve_memory  
- URL: https://mcp-memory.zeabur.app/memory/{key}
- Method: GET

## delete_memory
- URL: https://mcp-memory.zeabur.app/memory/{key}
- Method: DELETE
