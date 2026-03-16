#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, 'src')
from server_bridge import executor

async def main():
    print("=== Rish MCP Tools Test ===")
    print()
    print("Strategy:", executor.strategy)
    print()
    
    # Test 1
    print("Test 1: Echo")
    r = await executor.execute("echo Hello World", 5)
    print("  Output:", r.get("stdout", "").strip())
    print("  Mode:", r.get("mode"))
    print()
    
    # Test 2
    print("Test 2: ID command")
    r = await executor.execute("id", 5)
    print("  UID:", r.get("stdout", "")[:40])
    print("  Success:", r.get("success"))
    print()
    
    # Test 3  
    print("Test 3: List storage")
    r = await executor.execute("ls /sdcard/ | wc -l", 5)
    print("  File count:", r.get("stdout", "").strip())
    print()

asyncio.run(main())
