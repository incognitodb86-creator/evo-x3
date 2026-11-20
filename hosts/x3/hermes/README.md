# Hermes on EVO-X3 (snapshot, Derrick t2613u)

Live home: /home/evo/.hermes (local git, nightly hermes-state-commit, no remote). Not pushed itself: it holds .env, state DBs, sessions.
hermes-agent: https://github.com/NousResearch/hermes-agent.git @ ae2a81ccc00e9b7c06301523e5bb09608397149c
Unit: hosts/x3/systemd/user/hermes-gateway.service (+ .d drop-ins).
config.yaml: key/token/password values replaced with <redacted>. memories/ was empty at snapshot time.
Snapshot taken 2026-11-19 09:44 CST.

## H9 proposal: Hermes renders itself, pi only for coding (2026-11-19, not live until `UNI-APPLY-X3-E-HERMES`)

- `SOUL.md` here is the proposed SOUL: Hermes's tone paragraph only. The old extra lines (video -> pi-job, OC facts,
  adult rule) move: routing to the `h3-render` skill, facts to `memories/USER.md`. Hermes docs: SOUL is identity and
  tone; workflow and paths belong in skills or project files.
- `skills/h3-render/SKILL.md` + `skills/h3-writer/SKILL.md` + `bin/build-hermes-skills.sh`: slim native skills (Hermes writes the prompt; 18+ lint + `fill_request.py` build + queue). The build no longer splices `render/OPERATOR.md` or `writer_prompt.md`. Long commands use terminal `background=true` + `notify_on_complete=true`, then the `process` tool (never `setsid`/`nohup`). Overnight/batch mode is only when Derrick explicitly asks, and ends with a chat/file summary (no new ntfy unless he asks).
- `skills/pi-job/SKILL.after-h9.md`: the coding-only pi-job skill installed at the switch. `skills/pi-job/SKILL.md`
  stays the current one until then.
- `memories/USER.md`: Derrick's facts (OCs, 18+, Hermes renders / pi codes), 578 chars of the 1,375 limit.
- `memories/MEMORY.md`: starter lab facts (mono paths, services, Flux `--hybrid`, Beta 7 rules), 1,102 chars of the 2,200 limit.
- `skills/lab-status/SKILL.md`: read-only X3 + AlienPc status command (non-waking `:8446/system_stats`, `:8447/health`, `:8080/running`, `pi-job status`, inbox, disk).
- `skills/fleet-brain/SKILL.md`: read-only search/read over `/home/evo/AI/fleet-brain` (shared GrokBot/Max notes & decisions).
- `mcp-servers.readonly.yaml.example`: read-only Hermes `mcp_servers:` template (Gitea ready, Google Workspace & UniFi opt-in once creds populated; Vaultwarden omitted; `tools.exclude` write-deny globs; zero secrets).
- `agent-hooks/guard-render-queue.sh`: `pre_tool_call` `fail_closed` shell hook blocking `queue-remote.sh` / `flux_still.py --queue` / `render_writer_pipeline.py --queue` without `--yes-derrick` or when `*_NOT_READY.txt` exists.
- `scripts/morning-digest.sh`: 08:00 CT no-agent cron morning lab digest (zero LLM calls; optional `--ntfy` / `MORNING_DIGEST_NTFY=1` push via private QNAP `ntfy-renders`).
- Profile `writertest` (`/home/evo/.hermes/profiles/writertest`, created 2026-11-20 with `hermes profile create writertest --clone --no-alias`): writer dry-run tests only, `memory.memory_enabled: false` and `memory.user_profile_enabled: false`, memories emptied; run tests with `hermes -p writertest chat ...`. The default profile and gateway keep memory on. Re-clone it after an `h3-render` skill change (its skills are a copy).
