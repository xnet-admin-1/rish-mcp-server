#!/usr/bin/env python3
"""
Rish MCP Server - Model Context Protocol server for Shizuku integration
"""

import asyncio
import json
import subprocess
import sys
import os
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, LoggingLevel

# Server metadata
APP = "rish-mcp-server"
VERSION = "0.1.0"

# Rish configuration
RISH_DIR = os.path.expanduser("~/rish")
RISH_SCRIPT = os.path.join(RISH_DIR, "rish")
DEX_PATH = os.path.join(RISH_DIR, "rish_shizuku.dex")

server = Server(APP)


class RishExecutor:
    """Execute commands via rish/Shizuku"""
    
    def __init__(self):
        self.available = self._check_rish()
    
    def _check_rish(self) -> bool:
        """Check if rish is available and configured"""
        if not os.path.exists(RISH_SCRIPT):
            return False
        if not os.path.exists(DEX_PATH):
            return False
        # Check if this is an Android environment where rish can work
        return os.path.exists("/system/bin/app_process") or self._detect_termux()
    
    def _detect_termux(self) -> bool:
        """Detect if running in Termux environment"""
        return "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux")
    
    async def execute(self, command: str, timeout: int = 30) -> dict[str, Any]:
        """Execute a shell command via rish"""
        if not self.available:
            # Fallback: use regular shell but indicate limitations
            return await self._fallback_execute(command, timeout)
        
        # Full Shizuku execution
        env = {
            **os.environ,
            "RISH_APPLICATION_ID": os.environ.get("RISH_APPLICATION_ID", "com.termux"),
            "BASEDIR": RISH_DIR,
            "DEX": DEX_PATH,
        }
        
        full_command = f'export BASEDIR="{RISH_DIR}" DEX="{DEX_PATH}" RISH_APPLICATION_ID="{env["RISH_APPLICATION_ID"]}" && sh {RISH_SCRIPT} -c {json.dumps(command)}'
        
        try:
            proc = await asyncio.create_subprocess_shell(
                full_command,
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
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }
    
    async def _fallback_execute(self, command: str, timeout: int) -> dict[str, Any]:
        """Fallback execution using regular shell"""
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
                "note": "WARNING: Running without Shizuku privileges (fallback mode)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Fallback execution failed"
            }


# Global executor instance
executor = RishExecutor()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="shizuku_shell",
            description="Execute shell commands with Shizuku privileges (or fallback to regular shell)",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="shizuku_pm",
            description="Package manager operations (pm commands)",
            inputSchema={
                "type": "object",
                "properties": {
                    "args": {
                        "type": "string",
                        "description": "pm command arguments (e.g., 'list packages', 'install path/to.apk')"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30
                    }
                },
                "required": ["args"]
            }
        ),
        Tool(
            name="shizuku_am",
            description="Activity manager operations (am commands)",
            inputSchema={
                "type": "object",
                "properties": {
                    "args": {
                        "type": "string",
                        "description": "am command arguments (e.g., 'start -n com.example/.MainActivity')"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30
                    }
                },
                "required": ["args"]
            }
        ),
        Tool(
            name="shizuku_dumpsys",
            description="Dump system service information",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name to dump (e.g., 'activity', 'window', 'package')",
                        "default": ""
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="shizuku_settings",
            description="Read or modify system settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "enum": ["global", "system", "secure"],
                        "description": "Settings namespace"
                    },
                    "command": {
                        "type": "string",
                        "enum": ["get", "put", "list"],
                        "description": "Operation to perform"
                    },
                    "key": {
                        "type": "string",
                        "description": "Setting key (for get/put)"
                    },
                    "value": {
                        "type": "string",
                        "description": "Setting value (for put only)"
                    }
                },
                "required": ["namespace", "command"]
            }
        ),
        Tool(
            name="shizuku_status",
            description="Check Shizuku/rish availability and configuration",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Handle tool calls"""
    
    if name == "shizuku_shell":
        result = await executor.execute(
            arguments["command"],
            arguments.get("timeout", 30)
        )
        return [TextContent(text=json.dumps(result, indent=2))]
    
    elif name == "shizuku_pm":
        result = await executor.execute(
            f"pm {arguments['args']}",
            arguments.get("timeout", 30)
        )
        return [TextContent(text=json.dumps(result, indent=2))]
    
    elif name == "shizuku_am":
        result = await executor.execute(
            f"am {arguments['args']}",
            arguments.get("timeout", 30)
        )
        return [TextContent(text=json.dumps(result, indent=2))]
    
    elif name == "shizuku_dumpsys":
        service = arguments.get("service", "")
        cmd = f"dumpsys {service}" if service else "dumpsys"
        result = await executor.execute(cmd, 60)  # dumpsys can be slow
        return [TextContent(text=json.dumps(result, indent=2))]
    
    elif name == "shizuku_settings":
        ns = arguments["namespace"]
        cmd = arguments["command"]
        key = arguments.get("key", "")
        value = arguments.get("value", "")
        
        if cmd == "list":
            full_cmd = f"settings list {ns}"
        elif cmd == "get":
            full_cmd = f"settings get {ns} {key}"
        elif cmd == "put":
            full_cmd = f"settings put {ns} {key} {value}"
        else:
            return [TextContent(text=json.dumps({"error": f"Unknown command: {cmd}"}))]
        
        result = await executor.execute(full_cmd, 30)
        return [TextContent(text=json.dumps(result, indent=2))]
    
    elif name == "shizuku_status":
        status = {
            "rish_available": executor.available,
            "rish_script": RISH_SCRIPT if os.path.exists(RISH_SCRIPT) else None,
            "dex_path": DEX_PATH if os.path.exists(DEX_PATH) else None,
            "app_process_available": os.path.exists("/system/bin/app_process"),
            "environment": "termux" if executor._detect_termux() else "standard",
            "rish_application_id": os.environ.get("RISH_APPLICATION_ID", "not set (default: com.termux)")
        }
        return [TextContent(text=json.dumps(status, indent=2))]
    
    return [TextContent(text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
