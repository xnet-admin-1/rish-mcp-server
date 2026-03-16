# Rish MCP Server

A Model Context Protocol (MCP) server that provides privileged Android shell access via Shizuku.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   MCP       │────→│  rish-mcp   │────→│   Shizuku   │
│   Client    │     │   Server    │     │   Service   │
│  (AI/IDE)   │←────│  (stdio/    │←────│  (Android)  │
└─────────────┘     │   HTTP)     │     └─────────────┘
                    └─────────────┘
```

## Tools Provided

| Tool | Description |
|------|-------------|
| `shizuku_shell` | Execute shell commands via Shizuku |
| `shizuku_pm` | Package manager operations |
| `shizuku_am` | Activity manager operations |
| `shizuku_dumpsys` | System service information |
| `shizuku_settings` | Read/modify system settings |
