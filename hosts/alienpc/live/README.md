# AlienPc live snapshot (agent instructions, pi config, Forge loop)

> **Status:** pending AGT1 apply (not live yet — see `records/UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md`). Agent file copies in this folder remain the proposed AGT1 versions, not live.

Live refresh 2026-11-20 1:24–1:25 PM CT (America/Chicago), via Grok Bot local execution on AlienPc (OpenSSH still not used for this snapshot): `C:\AI\community` HEAD is now `ad6d62d9` (was `8eec1d3d`; subject: snapshot before ralph M6 Flux likeness 20261120, 11:30 AM CT). Re-read ComfyUI `custom-nodes.tsv`, `pip-freeze.txt`, `comfy.settings.json`, and `extra_model_paths.yaml`; added `start_comfy_bg.ps1` and `user-default-extra_model_paths.yaml` to the ComfyUI copy. Redacted AlienPc Swift llama-swap copy refreshed (source mtime 2026-11-17 5:11 PM CT; scrubber found no inline secret values). Model inventory re-read: Miraclein 2 files; Klein9 RefMod counts only (2913 files); `loras\klein9` and `loras\MinimaxH3` had 0 files at the live inventory path used this run. `community-promo-hashes.txt` re-read: `allowlist_promoted.json` is still `[]`, `oc_ref_2pass.api.json` / `oc_ref.api.json` / `fill_request.py` hashes unchanged. Agent file copies in this folder remain the proposed AGT1 versions, not live. Forge `x3run.ps1` / `x3put.ps1` and pi-permissions/web-search/extensions were re-copied from live.

Live refresh 2026-11-20 8:45 AM CT (America/Chicago), via Grok Bot local execution on AlienPc (no sshd on AlienPc, so SSH refreshes fail): `C:\AI\community` HEAD still `8eec1d3d`. `community-promo-hashes.txt` re-read after the picker rollback: `allowlist_promoted.json` is `[]` (`37517e5f…`), `scripts/parody/fill_request.py` matches mono (`4a45b567…`), `oc_ref_2pass.api.json` unchanged on disk (`1d3ec1da…`, candidate). REA-Video run setup copied to `alienpc/community/runs-setup/reavideo/`. Other files in this folder were not re-read.

Refresh attempted again 2026-11-20 07:52 CT from the box: SSH to `alienpc.tailf242b2.ts.net` closed the connection. Folder not rewritten.

Refresh attempted 2026-11-20 07:23 CT (America/Chicago) from the box as part of the mono push dual-host snapshot. SSH to `alienpc.tailf242b2.ts.net:22` timed out, and the X3 has no AlienPc SSH host in `~/.ssh/config`. This folder was **not** rewritten; the newest copy is still the 2026-11-19 9:07 PM CT refresh below.

Live refresh 2026-11-19 9:07 PM CT (America/Chicago): re-read `C:\AI\community` HEAD (still `8eec1d3d`; promoted `oc_ref_2pass.api.json` and `allowlist_promoted.json` on disk match mono sha256 `1d3ec1da...` / `834d1d0a...`). Re-read global pi agent files, Forge loop scripts, the redacted AlienPc Swift llama-swap copy, and ComfyUI `custom-nodes.tsv`, `pip-freeze.txt`, `comfy.settings.json`, and `extra_model_paths.yaml`. ComfyUI checkout is now `a277b5bf` (was `6b747c04` in the morning inventory). Model inventory was not re-counted this refresh. Agent file copies remain the proposed AGT1 versions where that still applies.

Live refresh 2026-11-19 7:55 PM CT (America/Chicago): re-read `C:\AI\community` HEAD (still `8eec1d3d`), `C:\Users\derek\.pi\agent\AGENTS.md` (same as the copy here), `settings.json` (still the live version with the duplicate key; the copy here stays the proposed AGT1 version), ComfyUI custom node folders (50, of which 31 `.disabled`; same as `custom-nodes.tsv`), and the AlienPc Swift llama-swap file (unchanged since 2026-11-17). No files changed.

Live refresh 2026-11-19 6:23 PM CT (America/Chicago): re-read ComfyUI `custom-nodes.tsv`, `pip-freeze.txt`, `comfy.settings.json`, and `extra_model_paths.yaml`. `community-HEAD.txt` is still `8eec1d3d`. `ComfyUI-KJNodes` is enabled live (it was `.disabled` at 5:58 PM CT). `pip-freeze.txt`, `comfy.settings.json`, and `extra_model_paths.yaml` are unchanged. Model inventory re-read: RefMod counts unchanged; the archived stomach-bulge LoRA is no longer in `loras\MinimaxH3` (t2885u). The redacted AlienPc Swift llama-swap copy no longer has `--fast fp16_accumulation` on the ComfyUI launch line (it was present in the 5:58 PM CT copy; the live file was not edited). Agent file copies stay the proposed AGT1 versions.

Live refresh 2026-11-19 5:58 PM CT (America/Chicago): re-read ComfyUI `custom-nodes.tsv`, `pip-freeze.txt`, `comfy.settings.json`, and `extra_model_paths.yaml` (unchanged vs the 5:33 PM CT copies). `community-HEAD.txt` is still `8eec1d3d`. Updated the redacted live AlienPc Swift llama-swap copy: the ComfyUI launch line now includes `--fast fp16_accumulation` (R6). Agent file copies stay the proposed AGT1 versions. Inventory file left as the 5:25 PM CT copy (this refresh did not rewrite counts).

Live refresh 2026-11-19 5:33 PM CT (America/Chicago): re-read ComfyUI `custom-nodes.tsv`, `pip-freeze.txt`, `comfy.settings.json`, `extra_model_paths.yaml`, `community-HEAD.txt`, and `model-inventory.txt`. Added a redacted copy of the live AlienPc Swift llama-swap file (`C:\AI\director\config\llama-swap.yaml`) at `llama-swap/llama-swap.yaml` (S8 gap). Agent file copies stay the proposed AGT1 versions (live `settings.json` still has the duplicate `compaction.modelOverrides` key that B3 fixed in the repo copy).

Live refresh 2026-11-19 4:54 PM CT (America/Chicago): re-read `community-HEAD.txt` (still `8eec1d3d`), `custom-nodes.tsv`, `pip-freeze.txt`, `comfy.settings.json`, `extra_model_paths.yaml`; all unchanged since 4:29 PM CT. `model-inventory.txt` not re-read this time.

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
