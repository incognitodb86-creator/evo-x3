#!/usr/bin/env python3
"""Stdio MCP server exposing X3 Forge and AlienPc Forge as one-shot pi subagents."""

from __future__ import annotations

import asyncio
import base64
import getpass
import os
from dataclasses import dataclass
from typing import Sequence

from mcp.server.fastmcp import FastMCP

DEFAULT_TIMEOUT_SECONDS = 900
MAX_TIMEOUT_SECONDS = 3600

X3_USER = os.environ.get("FORGE_X3_USER", "evo")
X3_DEFAULT_CWD = os.environ.get("FORGE_X3_DEFAULT_CWD", "/home/evo/AI/forge")
X3_AGENT_DIR = os.environ.get("FORGE_X3_AGENT_DIR", "/home/evo/.pi/panes/forge")
X3_MEMORY_DIR = os.environ.get("FORGE_X3_MEMORY_DIR", "/home/evo/.pi/panes/forge/memory")
X3_MODEL = os.environ.get("FORGE_X3_MODEL", "x3-local-coding/flash-next-uncensored-v2")
X3_THINKING = os.environ.get("FORGE_X3_THINKING", "medium")
X3_PATH = os.environ.get(
    "FORGE_X3_PATH",
    "/home/evo/AI/render/x3/.venv/bin:/home/evo/.local/bin:/usr/local/bin:/usr/bin:/bin",
)

ALIENPC_SSH_TARGET = os.environ.get("FORGE_ALIENPC_SSH_TARGET", "derek@100.64.221.102")
ALIENPC_SSH_PORT = os.environ.get("FORGE_ALIENPC_SSH_PORT", "22")
ALIENPC_SSH_KEY = os.environ.get("FORGE_ALIENPC_SSH_KEY", "")
ALIENPC_SSH_CONNECT_TIMEOUT = os.environ.get("FORGE_ALIENPC_SSH_CONNECT_TIMEOUT", "10")
ALIENPC_DEFAULT_CWD = os.environ.get("FORGE_ALIENPC_DEFAULT_CWD", r"C:\Users\derek\forge")
ALIENPC_PROVIDER = os.environ.get("FORGE_ALIENPC_PROVIDER", "llama-swap")
ALIENPC_MODEL = os.environ.get("FORGE_ALIENPC_MODEL", "coding_swift15_iq3s_esp")
ALIENPC_THINKING = os.environ.get("FORGE_ALIENPC_THINKING", "off")


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


mcp = FastMCP(
    name="forge-subagents",
    instructions=(
        "Delegate focused coding tasks to one-shot Forge (pi -p) instances on X3 "
        "(forge_x3) or AlienPc (forge_alienpc). Each call spawns a fresh print-mode "
        "process and does not touch interactive Forge panes. Default timeout is 900s."
    ),
    log_level="WARNING",
)


def _validate_inputs(task: str, timeout_seconds: int) -> str:
    cleaned = task.strip()
    if not cleaned:
        raise ValueError("task must be a non-empty string")
    if timeout_seconds < 1 or timeout_seconds > MAX_TIMEOUT_SECONDS:
        raise ValueError(f"timeout_seconds must be between 1 and {MAX_TIMEOUT_SECONDS}")
    return task


def _ps_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def encode_powershell_command(script: str) -> str:
    """Encode a PowerShell script as UTF-16LE Base64 for -EncodedCommand."""
    return base64.b64encode(script.encode("utf-16-le")).decode("ascii")


def build_x3_command(
    task: str,
    cwd: str | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    current_user: str | None = None,
) -> list[str]:
    """Build the argv to run one-shot Forge pi -p on X3 as X3_USER."""
    target_cwd = (cwd or "").strip() or X3_DEFAULT_CWD
    active_user = current_user if current_user is not None else getpass.getuser()

    inner = [
        "timeout",
        "--kill-after=10s",
        f"{timeout_seconds}s",
        "env",
        "-u",
        "HERDR_ENV",
        "-u",
        "HERDR_SOCKET_PATH",
        "-u",
        "HERDR_PANE_ID",
        f"PI_CODING_AGENT_DIR={X3_AGENT_DIR}",
        f"PI_MEMORY_DIR={X3_MEMORY_DIR}",
        f"PATH={X3_PATH}",
        "PYTHONUTF8=1",
        "PYTHONIOENCODING=utf-8",
        "bash",
        "-c",
        'cd -- "$1" && shift && exec pi "$@"',
        "_",
        target_cwd,
        "--approve",
        "--print",
        "--no-session",
        "--model",
        X3_MODEL,
        "--thinking",
        X3_THINKING,
        "--",
        task,
    ]
    if active_user != X3_USER:
        return ["sudo", "-n", "-u", X3_USER, *inner]
    return inner


def build_alienpc_powershell(task: str, cwd: str | None = None) -> str:
    """Build the remote PowerShell script executed on AlienPc Forge."""
    target_cwd = (cwd or "").strip() or ALIENPC_DEFAULT_CWD
    return "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            f"Set-Location -LiteralPath {_ps_single_quote(target_cwd)}",
            (
                "& pi --approve --print --no-session "
                f"--provider {_ps_single_quote(ALIENPC_PROVIDER)} "
                f"--model {_ps_single_quote(ALIENPC_MODEL)} "
                f"--thinking {_ps_single_quote(ALIENPC_THINKING)} "
                f"-- {_ps_single_quote(task)}"
            ),
            "exit $LASTEXITCODE",
        ]
    )


def build_alienpc_ssh_command(task: str, cwd: str | None = None) -> list[str]:
    """Build the ssh argv to run one-shot Forge pi -p on AlienPc over Tailscale."""
    encoded = encode_powershell_command(build_alienpc_powershell(task, cwd))
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={ALIENPC_SSH_CONNECT_TIMEOUT}",
        "-o",
        "ServerAliveInterval=30",
        "-o",
        "ServerAliveCountMax=3",
        "-p",
        str(ALIENPC_SSH_PORT),
    ]
    if ALIENPC_SSH_KEY:
        cmd.extend(["-i", ALIENPC_SSH_KEY])
    cmd.extend(
        [
            ALIENPC_SSH_TARGET,
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-EncodedCommand",
            encoded,
        ]
    )
    return cmd


async def _run_command(argv: Sequence[str], timeout_seconds: int) -> CommandResult:
    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout_seconds,
        )
        return CommandResult(
            returncode=proc.returncode if proc.returncode is not None else 1,
            stdout=stdout_b.decode("utf-8", errors="replace"),
            stderr=stderr_b.decode("utf-8", errors="replace"),
            timed_out=False,
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        except PermissionError:
            pass
        try:
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=5)
        except Exception:
            stdout_b, stderr_b = b"", b""
        return CommandResult(
            returncode=124,
            stdout=stdout_b.decode("utf-8", errors="replace"),
            stderr=stderr_b.decode("utf-8", errors="replace"),
            timed_out=True,
        )


def _format_failure(label: str, result: CommandResult, timeout_seconds: int) -> str:
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    parts: list[str] = []
    if result.timed_out or result.returncode == 124:
        parts.append(f"{label} timed out after {timeout_seconds}s")
    else:
        parts.append(f"{label} failed with exit code {result.returncode}")
    if stderr:
        parts.append(f"stderr: {stderr[-2000:]}")
    if stdout:
        parts.append(f"stdout: {stdout[-2000:]}")
    return "\n".join(parts)


@mcp.tool()
async def forge_x3(
    task: str,
    cwd: str | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    """Run a one-shot X3 Forge coding task (`pi -p`) and return the final text.

    Args:
        task: The coding task or prompt for X3 Forge.
        cwd: Optional working directory on X3 (defaults to /home/evo/AI/forge).
            Note: must be accessible to user `evo`.
        timeout_seconds: Subprocess timeout in seconds (default 900 / 15 min, max 3600).
    """
    validated_task = _validate_inputs(task, timeout_seconds)
    argv = build_x3_command(validated_task, cwd=cwd, timeout_seconds=timeout_seconds)
    result = await _run_command(argv, timeout_seconds=timeout_seconds + 15)
    if result.timed_out or result.returncode != 0:
        raise RuntimeError(_format_failure("forge_x3", result, timeout_seconds))
    out = result.stdout.strip()
    if not out and result.stderr.strip():
        return result.stderr.strip()
    return out


@mcp.tool()
async def forge_alienpc(
    task: str,
    cwd: str | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    """Run a one-shot AlienPc Forge coding task (`pi -p`) over SSH/Tailscale.

    Args:
        task: The coding task or prompt for AlienPc Forge.
        cwd: Optional working directory on AlienPc (defaults to C:\\Users\\derek\\forge).
        timeout_seconds: Subprocess timeout in seconds (default 900 / 15 min, max 3600).
    """
    validated_task = _validate_inputs(task, timeout_seconds)
    argv = build_alienpc_ssh_command(validated_task, cwd=cwd)
    result = await _run_command(argv, timeout_seconds=timeout_seconds)
    if result.timed_out or result.returncode != 0:
        raise RuntimeError(_format_failure("forge_alienpc", result, timeout_seconds))
    out = result.stdout.strip()
    if not out and result.stderr.strip():
        return result.stderr.strip()
    return out


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
