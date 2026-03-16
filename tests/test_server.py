#!/usr/bin/env python3
"""Tests for rish-mcp-server"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import RishExecutor, executor


async def test_status():
    """Test shizuku_status tool"""
    print("=== Testing shizuku_status ===")
    status = {
        "rish_available": executor.available,
        "rish_script": executor._check_rish(),
        "environment": "termux" if executor._detect_termux() else "standard",
    }
    print(json.dumps(status, indent=2))
    return status


async def test_execute():
    """Test command execution"""
    print("\n=== Testing command execution ===")
    result = await executor.execute("echo 'Hello from rish-mcp-server'", timeout=5)
    print(json.dumps(result, indent=2))
    return result


async def main():
    """Run all tests"""
    print("Rish MCP Server Tests")
    print("=" * 50)
    
    await test_status()
    await test_execute()
    
    print("\n" + "=" * 50)
    print("Tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
