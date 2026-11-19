Fresh pre-cutover backup 20261117-070651 (after U1a, before U2). Owner-only.
Also: /etc/evo-x3/llama-swap.yaml.bak-20261117-070651-pre-gufo (root, beside the live file).
Secrets NOT copied (paths only): /etc/evo-x3/llm.env, /etc/evo-x3/openwebui.env, /home/evo/.pi/agent/auth.json, pane auth.json, MCP env.
Pane dirs copied without sessions/ and memory* (Sydney data rule; sessions are not config).
/home/evo/AI/render/.pi/agent/models.json ABSENT
Pane models.json/pi-permissions/AGENTS.md etc are symlinks to /home/evo/.pi/agent/* (copied as symlinks; targets copied under home-evo-pi-agent/). mcp.json copied owner-only (may hold MCP env); not read.
