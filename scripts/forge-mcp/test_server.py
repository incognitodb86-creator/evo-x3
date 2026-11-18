"""Tests for the Forge subagents stdio MCP server."""

from __future__ import annotations

import asyncio
import base64
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0, str(Path(__file__).resolve().parent))
import server


def test_validate_inputs_rejects_empty_and_bad_timeout() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        server._validate_inputs("   \n\t ", 900)
    with pytest.raises(ValueError, match="timeout_seconds"):
        server._validate_inputs("hello", 0)
    with pytest.raises(ValueError, match="timeout_seconds"):
        server._validate_inputs("hello", 3601)
    assert server._validate_inputs("-dash task", 60) == "-dash task"


def test_build_x3_command_defaults_and_sudo() -> None:
    cmd = server.build_x3_command("- Summarize", cwd=None, timeout_seconds=900, current_user="derekboone")
    assert cmd[:4] == ["sudo", "-n", "-u", "evo"]
    assert "timeout" in cmd
    assert "900s" in cmd
    assert "PI_CODING_AGENT_DIR=/home/evo/.pi/panes/forge" in cmd
    assert "PI_MEMORY_DIR=/home/evo/.pi/panes/forge/memory" in cmd
    assert "/home/evo/AI/forge" in cmd
    dash_idx = cmd.index("--")
    assert cmd[dash_idx + 1] == "- Summarize"
    assert "--no-session" in cmd
    assert "--print" in cmd
    assert "--approve" in cmd


def test_build_x3_command_custom_cwd_same_user() -> None:
    cmd = server.build_x3_command("hello", cwd="/tmp/work", timeout_seconds=120, current_user="evo")
    assert cmd[0] == "timeout"
    assert "120s" in cmd
    assert "/tmp/work" in cmd


def test_build_alienpc_ssh_command_utf16_roundtrip() -> None:
    task = "Print 'quotes', $HOME, and\n--flags"
    cmd = server.build_alienpc_ssh_command(task, cwd=r"C:\AI\community")
    assert cmd[0] == "ssh"
    assert "BatchMode=yes" in cmd
    assert "-EncodedCommand" in cmd
    encoded = cmd[cmd.index("-EncodedCommand") + 1]
    decoded = base64.b64decode(encoded).decode("utf-16-le")
    assert r"Set-Location -LiteralPath 'C:\AI\community'" in decoded
    assert "--provider 'llama-swap'" in decoded
    assert "--model 'coding_swift15_iq3s_esp'" in decoded
    assert "--thinking 'off'" in decoded
    assert "'Print ''quotes'', $HOME, and\n--flags'" in decoded


def test_run_command_timeout_kills_process() -> None:
    res = asyncio.run(server._run_command([sys.executable, "-c", "import time; time.sleep(10)"], timeout_seconds=1))
    assert res.timed_out is True
    assert res.returncode == 124


def test_mcp_stdio_lists_tools() -> None:
    async def _check() -> None:
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(Path(__file__).resolve().parent / "server.py")],
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                assert init.serverInfo.name == "forge-subagents"
                tools_resp = await session.list_tools()
                by_name = {t.name: t for t in tools_resp.tools}
                assert set(by_name.keys()) == {"forge_x3", "forge_alienpc"}
                for name in ("forge_x3", "forge_alienpc"):
                    props = by_name[name].inputSchema.get("properties", {})
                    assert "task" in props
                    assert "cwd" in props
                    assert "timeout_seconds" in props
                    assert "task" in by_name[name].inputSchema.get("required", [])

    asyncio.run(_check())
