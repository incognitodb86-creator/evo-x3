# AlienPc live snapshot (agent instructions, pi config, Forge loop)

> **Status:** pending AGT1 apply (not live yet — see `records/UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md`). Agent file copies in this folder remain the proposed AGT1 versions, not live.

Live refresh 2026-11-19 4:29 PM CT (America/Chicago): `C:\AI\community` local HEAD is `8eec1d3d` (see `community-HEAD.txt`). ComfyUI `custom-nodes.tsv` now shows `ComfyUI-Fantastic-MiniMaxH3-PromptBuilder` enabled (it was `.disabled` at 13:52 CT); `pip-freeze.txt` has eight Comfy frontend/template package bumps. Model inventory re-read: same counts as 12:30 PM CT (RefMods still counts only). Agent file copies are unchanged vs the proposed AGT1 versions; AGT1 still blocked (see `records/UNI-APPLY-ALIENPC-B-AGT1/RESULT-attempt1-blocked.md`).

Original snapshot taken 2026-11-19 ~10:50 AM CT (America/Chicago) by Max Architect, read-only, for Opus review on GitHub.
These are COPIES. The live files stay on AlienPc; editing these copies changes nothing until Max imports and applies them.
Secret scan: gitleaks `--no-git` on the staged copies found no leaks (2026-11-19 10:51 AM CT).

| Copy in this folder | Live path on AlienPc | Notes |
|---|---|---|
| `pi-agent/AGENTS.md` | `C:\Users\derek\.pi\agent\AGENTS.md` | Master global AGENTS for AlienPc Forge (and any pi chat without its own AGENTS). `alienpc/community/agent-shared/AGENTS.md` is now a 2-line pointer (no hard link). Includes Role, inline GPU-lock, idle rule, and scoped "EVO-X3 access" (`x3run.ps1` / `x3put.ps1`). |
| `pi-agent/settings.json` | `C:\Users\derek\.pi\agent\settings.json` | Default model `coding_swift15_iq3s_esp` (ESP on, Derrick t2764u; AlienPc llama-swap), packages, skill roots. |
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

Skills loaded by AlienPc pi (directory symlinks in `C:\Users\derek\.pi\agent\skills\`):

| Skill | Target | Status / Tracked at |
|---|---|---|
| `comfy-render`, `video-render`, `image-render`, `h3-hc-render` | `C:\AI\community\skills\<name>` | Keep linked (primary render + execution). Tracked on `mono` under `alienpc/community/skills/<name>/`. |
| `h3-prompting`, `h3-max-ref2va-prompt`, `h3-parody-identity`, `alienpc-hardcore-i2v-director`, `alienpc-stills-pose-edit-prompting` | `C:\AI\community\skills\<name>` | Keep linked (backup writer lane when X3 Gufo is busy coding). Tracked on `mono` under `alienpc/community/skills/<name>/`. |
| `ralph-loop` | `C:\AI\community\agent-shared\skills\ralph-loop` | Keep linked. Tracked on `mono` under `alienpc/community/agent-shared/skills/ralph-loop/SKILL.md`. |
| `rea-video` | `C:\Users\derek\forge\tools\rea-video\skills\rea-video` | Keep linked. Upstream clone `https://github.com/JuneYaooo/rea-video` at `e385853` (cloned 2026-11-17 9:43 PM CT); only local change is an untracked `HANDOFF-forge.md`. Read upstream for the skill text. |

Other skill roots in `settings.json`: `C:/AI/community/agent-shared/skills` (branch `alienpc-community`) and `C:/AI/fleet-brain/20_skills/current` (the fleet brain, not this repo).
