# EVO-X3 Hermes workspace

This folder is the Hermes CLI and WebUI working directory (`terminal.cwd`).
Keep project notes and scratch files here. Do not store keys, tokens, or session cookies here.

## Machines and paths

- **EVO-X3 (this host):** Hermes entry point, llama-swap at `http://127.0.0.1:8080/v1`, PixlStash, and the code trees under `/home/evo/AI/{community,render,forge}`.
- **Run folders:** `/home/evo/AI/community/runs/<run_name>`.
- **AlienPc:** ComfyUI renders and RTX 2x upscale. Queue only through the existing X3 scripts after approval.
- **X3 lease (changes only):** one line in `/home/derekboone/AI/locks/x3-lease.txt`. Take it before a restart, config edit, model load/unload, or install; clear that line when finished. Read-only checks need no lease.
- **PixlStash read token:** `/home/evo/.config/pixlstash/render-read.token` (never print it). Inbox: `/home/evo/AI/pixl-inbox`.

Do not edit llama-swap, ComfyUI server config, or live production templates unless Derrick asked for that exact change. Do not open `sydney/`, `models.json`, or Grok sidecars. Do not run `git remote -v` inside `community` or `render`.

## Who does what

- **Hermes** handles render asks with `h3-render` and `h3-writer`.
- **pi-job** is for code and reviews only (`pi-job code|review`). Do not use `pi-job render`, `pi-job approve`, or `pi-job queue` unless Derrick says to use the old pi render path.

## Render rules (U56 / Beta 7)

- Everyone depicted is 18+. A youth cue is a hard stop (`youth_hint` / `scale_adult` / equivalent).
- Prompts use MiniMax-H3 10Eros-Max **Beta 7** (U56 Decision #1): exactly four headers, in order — `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`. No pre-U56 headers, no Markdown in the prompt body, no labeled audio-header names. Diegetic sound stays in ordinary sentences at the end of `detailed_description`.
- Hermes writes the prompt itself (`h3-writer`). Then run the 18+ / Beta 7 lint and the ComfyUI JSON build (`fill_request.py` dry-run). Do not call the Python writer or judge models.
- **Single clip:** show the still and the full prompt, ask `Render this? (yes / no)`, and stop. Queue only after Derrick's clear yes in this chat, via `bash /home/evo/AI/render/x3/queue-remote.sh '<run_dir>' --yes-derrick`.
- **Overnight / batch:** only when Derrick explicitly asks for an autonomous overnight or batch render run. Then pick stills (18+ checked), write prompts, lint, build and validate the ComfyUI JSON, queue sequentially, and leave a summary in the chat plus a file under the batch folder. Do not add a new ntfy alert unless Derrick asks. That explicit batch ask is the yes for the run; still pass `--yes-derrick` on each queue command.
- For commands that may run longer than the terminal timeout, use the terminal tool with `background=true` and `notify_on_complete=true`, then the `process` tool to wait or poll. Never use `setsid` or `nohup` (Hermes blocks them). To wait for a finished 2x clip, poll `clip/render_ok.json` (a real status file) in short rounds or use `process` wait.
- Never print keys, tokens, RefMod or LoRA triggers, or adult prompt text in logs you do not need. Never browse PixlStash library folders, tags, character names, or `unmatched-person-names.txt`. Use the PixlStash search API or the `pixlstash-image-library` skill.
- Thinking stays off unless Derrick explicitly asks for it.
- If a tool call fails, write one short line saying what failed and what changed before retrying; never repeat the exact same failing command.

## Coding

- Back up before the first edit. Prefer small, reversible changes.
- Do not weaken gates, locks, allowlists, or the 18+ stop.
- After a repo save on this host, follow the existing check-push practice for Gitea.

## Time

Report times in America/Chicago (CT).
