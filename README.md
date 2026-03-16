# Rish MCP Server

MCP (Model Context Protocol) server for Android system access via Shizuku.

## License

**GPL-3.0** - See [LICENSE](LICENSE) file for details.

## Credits

- **Organization:** XNet Inc. https://xnet.ngo
- **Author:** Josh Fordyce <admin@xnet.ngo>
- **Copyright:** © 2025 XNet Inc. All rights reserved.

## Description

Provides Android shell access through the Model Context Protocol, enabling AI assistants to execute commands on Android devices via Shizuku.

## Installation

### For Operit Package Manager

Import directly from GitHub:
```
https://github.com/xnet-admin-1/rish-mcp-server/releases/latest/download/rish-mcp-server.zip
```

### Manual Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python3 src/server_direct.py`

## Requirements

- Python 3.10+
- Android device with Shizuku running

## Usage

The server runs in stdio mode for MCP communication. Connect via any MCP client.
