#!/usr/bin/env python3
"""
Rish MCP Server - Bridge Mode
Uses terminal tool as proxy when super_admin:shell is unavailable
"""

import asyncio
import json
import sys
import os
import subprocess
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

APP = "rish-mcp-server-bridge"
RISH_DIR = os.path.expanduser("~/rish")

server = Server(APP)


class BridgeExecutor:
    """
    Executor that tries multiple strategies:
    1. Direct Android shell (if available)
    2. Local shell with Android file access via /sdcard
    3. Bridge mode via terminal proxy
    """
    
    def __init__(self):
        self.strategy = self._detect_strategy()
    
    def _detect_strategy(self) -> str:
        """Detect best execution strategy"""
        # Check for direct Android access
        if os.path.exists("/system/bin/app_process"):
            return "android_direct"
        
        # Check for sdcard access (proot with storage)
        if os.path.exists("/sdcard/Android"):
            return "proot_storage"
        
        # Fallback to pure local
        return "local_fallback"
    
    async def execute(self, command: str, timeout: int = 30) -> dict[str, Any]:
        """Execute command using best available strategy"""
        
        if self.strategy == "android_direct":
            # Try to use app_process if available
            return await self._try_android_exec(command, timeout)
        
        elif self.strategy == "proot_storage":
            # Use local shell but note we have storage access
            return await self._exec_with_storage(command, timeout)
        
        else:
            # Pure local fallback
            return await self._local_exec(command, timeout)
    
    async def _try_android_exec(self, command: str, timeout: int) -> dict[str, Any]:
        """Try Android direct execution via app_process"""
        try:
            # Check if rish is usable
            rish_script = os.path.join(RISH_DIR, "rish")
            dex_path = os.path.join(RISH_DIR, "rish_shizuku.dex")
            
            if os.path.exists(rish_script) and os.path.exists(dex_path):
                env = os.environ.copy()
                env.update({
                    "RISH_APPLICATION_ID": env.get("RISH_APPLICATION_ID", "com.termux"),
                    "BASEDIR": RISH_DIR,
                    "DEX": dex_path,
                })
                
                full_cmd = f'sh {rish_script} -c {json.dumps(command)}'
                
                proc = await asyncio.create_subprocess_shell(
                    full_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )
                
                return {
                    "success": proc.returncode == 0,
                    "returncode": proc.returncode,
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "mode": "android_rish"
                }
        except Exception as e:
            pass  # Fall through to storage mode
        
        return await self._exec_with_storage(command, timeout)
    
    async def _exec_with_storage(self, command: str, timeout: int) -> dict[str, Any]:
        """Execute with proot + storage access"""
        result = await self._local_exec(command, timeout)
        result["mode"] = "proot_storage"
        result["storage_access"] = os.path.exists("/sdcard/Android")
        return result
    
    async def _local_exec(self, command: str, timeout: int) -> dict[str, Any]:
        """Pure local execution"""
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            return {
                "success": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "mode": "local"
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Timeout after {timeout}s",
                "mode": "local"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "local"
            }


executor = BridgeExecutor()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools - same as main server"""
    return [
        Tool(
            name="android_shell",
            description="Execute shell commands (auto-detects best execution method)",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "default": 30}
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="android_status",
            description="Check execution environment and capabilities",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="storage_access",
            description="Access Android storage via /sdcard",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to /sdcard"},
                    "command": {"type": "string", "enum": ["ls", "cat", "stat"]}
                },
                "required": ["path", "command"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Handle tool calls"""
    
    if name == "android_shell":
        result = await executor.execute(
            arguments["command"],
            arguments.get("timeout", 30)
        )
        return [TextContent(text=json.dumps(result, indent=2))]
    
    elif name == "android_status":
        status = {
            "execution_strategy": executor.strategy,
            "rish_available": os.path.exists(os.path.join(RISH_DIR, "rish")),
            "dex_available": os.path.exists(os.path.join(RISH_DIR, "rish_shizuku.dex")),
            "app_process_exists": os.path.exists("/system/bin/app_process"),
            "storage_mounted": os.path.exists("/sdcard/Android"),
            "working_directory": os.getcwd(),
        }
        return [TextContent(text=json.dumps(status, indent=2))]
    
    elif name == "storage_access":
        base_path = "/sdcard"
        target = arguments["path"].lstrip("/")
        full_path = os.path.join(base_path, target)
        
        # Security: ensure path stays within /sdcard
        real_path = os.path.realpath(full_path)
        if not real_path.startswith(os.path.realpath(base_path)):
            return [TextContent(text=json.dumps({"error": "Path traversal attempt blocked"}))]
        
        cmd = arguments["command"]
        if cmd == "ls":
            result = await executor.execute(f"ls -la {json.dumps(full_path)}", 10)
        elif cmd == "cat":
            result = await executor.execute(f"cat {json.dumps(full_path)} 2>&1 | head -c 10000", 10)
        elif cmd == "stat":
            result = await executor.execute(f"stat {json.dumps(full_path)}", 10)
        else:
            result = {"error": f"Unknown command: {cmd}"}
        
        return [TextContent(text=json.dumps(result, indent=2))]
    
    return [TextContent(text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    """Main entry with enhanced capabilities"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
