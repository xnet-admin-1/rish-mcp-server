#!/bin/bash
set -e

echo "Installing rish-mcp-server..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make server executable
chmod +x src/server.py

echo "Installation complete!"
echo ""
echo "To run:"
echo "  source .venv/bin/activate"
echo "  python src/server.py"
echo ""
echo "Or configure for Claude Desktop / other MCP clients:"
echo "  See docs/configuration.md"
