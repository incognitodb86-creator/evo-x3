# AlienPc live snapshot (agent instructions, pi config, Forge loop)

Snapshot taken 2026-11-19 ~10:50 AM CT (America/Chicago) by Max Architect, read-only, for Opus review on GitHub.
These are COPIES. The live files stay on AlienPc; editing these copies changes nothing until Max imports and applies them.
Secret scan: gitleaks `--no-git` on the staged copies found no leaks (2026-11-19 10:51 AM CT).

| Copy in this folder | Live path on AlienPc | Notes |
|---|---|---|
| `pi-agent/AGENTS.md` | `C:\Users\derek\.pi\agent\AGENTS.md` | Global AGENTS for AlienPc Forge (and any pi chat without its own AGENTS). Line 1 says it is a hard link of `C:\AI\community\agent-shared\AGENTS.md`; that is no longer true (hashes differ on 2026-11-19), so both are tracked: the community copy is on branch `alienpc-community` `agent-shared/AGENTS.md`. Has the "EVO-X3 access" section (x3run.ps1 / x3put.ps1). |
| `pi-agent/settings.json` | `C:\Users\derek\.pi\agent\settings.json` | Default model `coding_swift15_iq3s_esp` (AlienPc llama-swap), packages, skill roots. |
| `pi-agent/pi-permissions.jsonc` | `C:\Users\derek\.pi\agent\pi-permissions.jsonc` | Permission rules for AlienPc pi chats. |
| `pi-agent/web-search.json` | `C:\Users\derek\.pi\agent\web-search.json` | Search provider config (no key). |
| `pi-agent/extensions/loop-guard.ts`, `extensions/*/config.json` | `C:\Users\derek\.pi\agent\extensions\...` | `herdr-agent-state.ts` is identical to the X3 copy in `hosts/x3/live/pi-evo/agent/extensions/` and is not duplicated here. |
| `forge/README.md` | `C:\Users\derek\forge\README.md` (`forge` is a junction to `C:\Users\derek\5slock`) | Forge working root map. Not a git repo. |
| `forge/x3run.ps1`, `forge/x3put.ps1` | `C:\Users\derek\forge\` | AlienPc Forge's way to run bash / push a small file on the EVO-X3 over SSH (key auth, `BatchMode`). |
| `forge/.pi/bin/ps-ladder.cmd` | `C:\Users\derek\forge\.pi\bin\ps-ladder.cmd` | Project pi helper. |
| `forge/ralph-community/{PROMPT.md,ralph.ps1,README.md,gitignore}` | `C:\Users\derek\forge\ralph-community\` | Ralph loop runner + standing pass prompt (`gitignore` = the live `.gitignore`). |

Not copied (on purpose):
- `ralph-community\fix_plan.md`: per-task state that quotes an adult render ask word for word (rule: no adult prompt text in git). Its standing rules are in `PROMPT.md` and `pi-agent/AGENTS.md`.
- `ralph-community\.gitleaksignore`, `sessions\`, `runs\`, `wfsnap\`, `backups\`, `logs\`, `notes\`: fingerprints, chat transcripts, run outputs, backups.
- `pi-agent\auth.json`, `mcp.json`, `mcp-auth.json`, `models.json`, `models-store.json`: credentials or key-bearing config.
- Anything under `C:\Users\derek\sydney\` (never opened).

Skills loaded by AlienPc pi (all directory symlinks in `C:\Users\derek\.pi\agent\skills\`):

| Skill | Target | Tracked at |
|---|---|---|
| alienpc-hardcore-i2v-director, alienpc-stills-pose-edit-prompting, comfy-render, h3-hc-render, h3-max-ref2va-prompt, h3-parody-identity, h3-prompting, image-render, video-render | `C:\AI\community\skills\<name>` | branch `alienpc-community` `skills/<name>/` (live checkout clean for these paths) |
| ralph-loop | `C:\AI\community\agent-shared\skills\ralph-loop` | branch `alienpc-community` `agent-shared/skills/ralph-loop/SKILL.md` |
| rea-video | `C:\Users\derek\forge\tools\rea-video\skills\rea-video` | upstream clone `https://github.com/JuneYaooo/rea-video` at `e385853` (cloned 2026-11-17 9:43 PM CT); only local change is an untracked `HANDOFF-forge.md`. Read upstream for the skill text. |

Other skill roots in `settings.json`: `C:/AI/community/agent-shared/skills` (branch `alienpc-community`) and `C:/AI/fleet-brain/20_skills/current` (the fleet brain, not this repo).
