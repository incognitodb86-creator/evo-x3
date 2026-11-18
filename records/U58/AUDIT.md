# U58 - X3 Forge chat-read fix: evidence lock (Phase 1)

Date: 2026-11-18. Mode: read-only, nothing changed on the box.
Ask: Derrick "check Gitea for issues, ce-brainstorm/ce-plan a fix for X3 Forge fails to read x3 chats" -> approved plan `C:\Users\derek\forge\plans\2026-11-18-x3-forge-chat-read-plan.md` (Derrick said yes 2026-11-18).

Gitea state: no open issues in `derrick/evo-x3`. The chat-read failure is recorded in the local audit
`C:\Users\derek\forge\notes\2026-11-17-x3-forge-config-audit-plan.md`, not as a Gitea issue.

## Reproduce all of this with
```bash
cd ~/AI/forge && python3 records/U58/evidence.py     # output: records/U58/evidence.txt (same dir, 2026-11-18)
pi --version                                          # 1.5.2
grep -n "PI_CODING_AGENT_DIR\|session-dir\|cd " ~/evo-x3/pi-chats/forge-pi.sh ~/evo-x3/pi-chats/render-pi.sh
ls -la ~/.pi/panes/forge/sessions ~/.pi/panes/render/sessions   # symlinks -> ~/.pi/agent/sessions (2026-11-16 16:30)
python3 -c "import json;print(json.load(open('/home/evo/AI/forge/.pi/settings.json'))['compaction'])"
```

## Findings (verbatim output in evidence.txt)
1. **Sessions exist and parse.** 40 session files under `~/.pi/agent/sessions/`: 16 (`--home-evo-AI-forge--`),
   22 (`--home-evo-AI-render--`), 2 (`--home-derekboone-AI-forge--`). No corrupt first lines.
2. **The X3 chat history begins 2026-11-15 23:54 UTC (17:54 CT).** Nothing from the pre-X3 AlienPc Forge is present;
   the per-pane `sessions` symlinks (made 2026-11-16 16:30 CT) hide any earlier pane-local tree.
3. **Session root depends on how pi is launched.** Launchers set `PI_CODING_AGENT_DIR=$HOME/.pi/panes/<pane>` and
   `cd` into the repo, with no `--session-dir` and no `sessionDir` setting. pi resolves sessions from
   `$PI_CODING_AGENT_DIR/sessions`; a pane dir without that symlink shows an empty picker. The live herdr panes
   (w3:p1 render, w4:p1 forge) do point at real session files, so in-pane reading works; the break is for any launch
   that does not inherit the launcher environment (plain shell `pi`, a new pane, phone path).
4. **Context thrash on the coding chat.** `~/AI/forge/.pi/settings.json` sets
   `compaction = {enabled:true, reserveTokens:131072, keepRecentTokens:32768}` on models whose contextWindow is
   262144 -> auto-compaction should fire above 131072. Observed: 78 of 965 assistant calls above that threshold,
   `flash-next-uncensored` reaching **236139** tokens, and **zero** compaction entries in the Forge trees
   (the Render tree has 4). So the coding chats run far past their own threshold and lose the thread at provider
   overflow instead of a clean summary. `keepRecentTokens: 32768` also keeps more than pi's default 20000, so each
   compaction frees less.
5. Model facts (`~/.pi/panes/forge/models.json`): `flash-next`, `flash-next-uncensored`, `gemma4-heretic`,
   `qwen27b` = 262144 ctx / 32768 out; the `-sub` aliases = 131072 ctx / 8192 out. Forge default is
   `x3-local-coding/flash-next-uncensored`; Render default is `x3-local/flash-next-uncensored`.
6. Closed since the Nov 16 audit: B4 (X3 tree in Gitea) - branches `x3-pi-config`, `x3-forge`, `x3-community`,
   `x3-render` exist on `derrick/evo-x3`; ralph.sh GPU gate now uses `flock -n` like `queue-remote.sh`.
7. Two launcher copies drift: `~/AI/forge/launcher/forge-pi.sh` (tracked in the forge repo) vs
   `~/evo-x3/pi-chats/forge-pi.sh` (what `herdr-panes.sh` runs, newer, has the thinking/sampling comments).

## Untouched by this audit
llama-swap (:8080), model files, GPU lock, render queue. No writes outside `records/U58/`.
