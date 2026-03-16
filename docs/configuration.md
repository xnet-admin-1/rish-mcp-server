# Configuration Guide

## Prerequisites

1. **Shizuku installed and running** on your Android device
2. **Terminal app** (Termux recommended) with Shizuku permission granted
3. **Python 3.10+** with virtual environment support

## Setup

### 1. Copy Rish Files

Ensure `rish` and `rish_shizuku.dex` are in `~/rish/`:

```bash
mkdir -p ~/rish
cp /path/to/rish ~/rish/
cp /path/to/rish_shizuku.dex ~/rish/
```

### 2. Configure RISH_APPLICATION_ID

Edit `~/rish/rish` and replace `PKG` with your terminal app's package name:

```bash
# For Termux
export RISH_APPLICATION_ID="com.termux"

# For other terminals, find the package name in app info
```

### 3. Install MCP Server

```bash
cd ~/rish-mcp-server
./install.sh
```

### 4. Configure MCP Client

#### Claude Desktop

Edit `~/.config/claude/config.json`:

```json
{
  "mcpServers": {
    "rish-shizuku": {
      "command": "/path/to/rish-mcp-server/.venv/bin/python",
      "args": ["/path/to/rish-mcp-server/src/server.py"],
      "env": {
        "RISH_APPLICATION_ID": "com.termux",
        "RISH_DIR": "/data/data/com.termux/files/home/rish"
      }
    }
  }
}
```

#### Other MCP Clients

Use the same configuration structure - specify the Python interpreter and server.py as arguments.

## Testing

Test the connection:

```bash
source .venv/bin/activate
python src/server.py
```

The server will start and listen on stdio for MCP protocol messages.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RISH_APPLICATION_ID` | Terminal app package name | `com.termux` |
| `RISH_DIR` | Directory containing rish files | `~/rish` |
