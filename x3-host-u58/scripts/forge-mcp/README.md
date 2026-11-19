# Forge Subagents MCP Server

Stdio MCP server that lets Antigravity (`agy`) sessions delegate one-shot coding tasks (`pi -p --no-session`) to X3 Forge or AlienPc Forge without touching interactive Forge panes or configs.

## Tools

- `forge_x3(task, cwd?, timeout_seconds=900)`: runs one-shot `pi --approve --print --no-session` as `evo` using `/home/evo/.pi/panes/forge` (`x3-local-coding/flash-next-uncensored-v2`, thinking `medium`), defaulting `cwd` to `/home/evo/AI/forge`.
- `forge_alienpc(task, cwd?, timeout_seconds=900)`: runs one-shot `pi --approve --print --no-session` over SSH/Tailscale (`derek@100.64.221.102`, `BatchMode=yes`, PowerShell `-EncodedCommand`) using `llama-swap/coding_swift15_iq3s_esp` (thinking `off`), defaulting `cwd` to `C:\Users\derek\forge`.

## Setup

```bash
uv venv /home/derekboone/evo-x3/.venv-forge-mcp --python python3
uv pip install --python /home/derekboone/evo-x3/.venv-forge-mcp/bin/python -r /home/derekboone/evo-x3/scripts/forge-mcp/requirements.txt
```

Registered in `~/.gemini/config/mcp_config.json` with `timeoutSeconds: 960` (so the server's 900s default subprocess timeout fires cleanly before agy's client timeout).

## Environment overrides

- X3: `FORGE_X3_USER`, `FORGE_X3_DEFAULT_CWD`, `FORGE_X3_AGENT_DIR`, `FORGE_X3_MEMORY_DIR`, `FORGE_X3_MODEL`, `FORGE_X3_THINKING`, `FORGE_X3_PATH`
- AlienPc: `FORGE_ALIENPC_SSH_TARGET`, `FORGE_ALIENPC_SSH_PORT`, `FORGE_ALIENPC_SSH_KEY`, `FORGE_ALIENPC_SSH_CONNECT_TIMEOUT`, `FORGE_ALIENPC_DEFAULT_CWD`, `FORGE_ALIENPC_PROVIDER`, `FORGE_ALIENPC_MODEL`, `FORGE_ALIENPC_THINKING`

## Tests

```bash
/home/derekboone/evo-x3/.venv-forge-mcp/bin/pytest -v /home/derekboone/evo-x3/scripts/forge-mcp/test_server.py
```
