Goal: After `UNI-APPLY-X3-B-PIJOB` and `UNI-APPLY-X3-D` have a `RESULT.md`, make Hermes do renders itself (unified plan `H9`, Hermes plan `U1`/`U4`-`U6`), with pi used only for coding, on the EVO-X3 under the X3 lease.

# UNI-APPLY-X3-E-HERMES (X3 Forge): Hermes renders directly, pi only for coding, Nov 19 2026

Authority: Derrick t2598u (Hermes renders with no pi hop), t2600u (same agreed rules as Render), t2609u (keep the pi coding hand-off), ~12:35 CT decision A (Hermes is the main chat and calls pi only for coding), 14:05 CT yes to the apply briefs, and 14:38 CT ("hermes is the entry point and handles all renders and stuff. and then delegates to pi"). Plans: `records/uplan/PLAN.md` (`H9`, step `X4b`) and `records/hermes-direct-render/PLAN.md` (`U1`, `U4`-`U6`; Update 2026-11-19 15:00 CT). Max verifies your `RESULT.md` afterwards.

## Needs before launch (ALL required)
- `records/UNI-APPLY-X3-B-PIJOB/RESULT.md` and `records/UNI-APPLY-X3-D/RESULT.md` exist (pi-job installed and the Hermes -> pi coding test passed; skills and `writer_prompt.md` synced). If either is missing, stop (`BLOCKED`) and do not take the lease.
- Max pulled `mono` at this brief's commit or newer into `/home/derekboone/evo-x3` and the `mono` clone (`--prose-file` must be in `/home/evo/AI/community/scripts/parody/render_writer_pipeline.py`).
- X3 lease free (`/home/derekboone/AI/locks/x3-lease.txt` empty). No render running. Not during the `BENCH-X3-W1` quiet window. No Hermes chat mid-turn (Max checks with Derrick).

## Access & Lease
- **Doer:** X3 Forge as `evo`. No sudo needed.
- **Source:** `/home/derekboone/evo-x3/hosts/x3/hermes/` (`bin/build-hermes-skills.sh`, `skills/h3-render/HEAD.md`, `skills/h3-writer/SKILL.md`, `skills/pi-job/SKILL.after-h9.md`, `memories/USER.md`, `SOUL.md`).
- **Backup root:** `/home/evo/.hermes/_archive/20261119-h9/`.
- **Lease take:** one line to `/home/derekboone/AI/locks/x3-lease.txt`: `forge-x3 | UNI-APPLY-X3-E-HERMES | <start time>`. If not empty, stop.
- **Lease release:** `: > /home/derekboone/AI/locks/x3-lease.txt` when done or blocked.

## Work (stop on first failure)

### Step 0 - Backups and baseline
```bash
B=/home/evo/.hermes/_archive/20261119-h9; mkdir -p "$B"
cp -a /home/evo/.hermes/config.yaml /home/evo/.hermes/SOUL.md "$B/"
cp -a /home/evo/.hermes/skills/pi-job/SKILL.md "$B/pi-job.SKILL.md"
[ -d /home/evo/.hermes/memories ] && cp -a /home/evo/.hermes/memories "$B/memories"
[ -d /home/evo/.hermes/skills/flux-klein-prompting ] && cp -a /home/evo/.hermes/skills/flux-klein-prompting "$B/"
hermes config show > "$B/config-show.before.txt" 2>&1
hermes skills list > "$B/skills.before.txt" 2>&1
```

### Item 1 - Build the two render skills
```bash
bash /home/derekboone/evo-x3/hosts/x3/hermes/bin/build-hermes-skills.sh
bash /home/derekboone/evo-x3/hosts/x3/hermes/bin/build-hermes-skills.sh --check   # must print OK
```

### Item 2 - Config (skills from the community folder, guards, limits)
```bash
hermes config set skills.external_dirs '[/home/evo/AI/community/skills]'
hermes config set skills.disabled '[alienpc-hardcore-i2v-director, alienpc-stills-pose-edit-prompting, comfy-render, h3-hc-render, h3-max-ref2va-prompt, image-render, video-render, ascii-video, manim-video, comfyui]'
hermes config set skills.write_approval true
hermes config set approvals.timeout 300
hermes config set agent.max_turns 80
hermes config set agent.reasoning_effort low
hermes config show > /home/evo/.hermes/_archive/20261119-h9/config-show.after.txt 2>&1
```
- If `hermes config set` refuses (for example the live `config.yaml` has `terminal:`, `agent:` and `gateway:` twice), stop (`BLOCKED`), restore `config.yaml` from Step 0 and report the exact error. Do not hand-edit `config.yaml`.
- The diff of `config-show.before.txt` vs `.after.txt` must show only these 6 keys.
- Move the local `flux-klein-prompting` copy out (the community folder copy now loads, and a local copy would shadow it): `mv /home/evo/.hermes/skills/flux-klein-prompting /home/evo/.hermes/_archive/20261119-h9/flux-klein-prompting.local` (skip if absent).

### Item 3 - SOUL, memory, pi-job skill (one switch)
- First: if `/home/evo/.hermes/memories/USER.md` exists and is not empty, stop (`BLOCKED`) and report its size only (do not overwrite or print Derrick's memories).
```bash
S=/home/derekboone/evo-x3/hosts/x3/hermes
install -m 0644 "$S/SOUL.md" /home/evo/.hermes/SOUL.md
mkdir -p /home/evo/.hermes/memories && install -m 0644 "$S/memories/USER.md" /home/evo/.hermes/memories/USER.md
install -m 0644 "$S/skills/pi-job/SKILL.after-h9.md" /home/evo/.hermes/skills/pi-job/SKILL.md
```
- `SOUL.md` goes back to tone only (Hermes docs: SOUL is identity and tone, not workflow). The OC and 18+ facts move to `memories/USER.md`. The render routing lives in the `h3-render` skill; `pi-job` is coding only.

### Item 4 - Restart and check (no render)
- Restart the gateway only when no chat is mid-turn: `systemctl --user restart hermes-gateway`; then `systemctl --user is-active hermes-gateway hermes-webui` (both `active`).
- `hermes skills list` shows `h3-render`, `h3-writer`, `h3-prompting`, `h3-parody-identity`, `flux-klein-prompting`, `pi-job`, `pixlstash-image-library`, and none of the 10 disabled names.
- `wc -c /home/evo/.hermes/memories/USER.md` is at most 1375.
- `cd /home/evo/AI/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q -p no:cacheprovider test_prose_file_gate.py` -> `3 passed`.
- `hermes chat --oneshot -q "Which skill do you use to render a video, and which to change code in a repo? Reply with the two skill names only."` -> names `h3-render` and `pi-job`. (If this Hermes build has no `--oneshot`, mark this check `SKIPPED` and say why.)

### Item 5 - Derrick's chat checks (Max tells Derrick it is ready; Forge does not run these)
In Hermes WebUI, Derrick's own asks:
1. A render ask -> still + full prompt + "Render this?", nothing queued.
2. The same ask with "write it yourself" -> `<run_dir>/hermes_prose.txt` exists, READY or an exact NOT_READY reason, nothing queued.
3. Derrick's yes on one READY run -> queued, the 2x clip plays inline (`MEDIA:` link from `/home/evo/.hermes/image_cache/`).
4. A small coding ask -> `pi-job code` job ID -> `DONE` + commit SHA (or `STUCK`).
Max records these in `RESULT.md` under "Derrick checks". If 3 does not play inline, Max checks `MEDIA_ALLOWED_ROOTS` in `hermes-webui.service` (it lists only `/home/evo/AI/5slock/libraries`) before changing anything.

### Rollback
```bash
B=/home/evo/.hermes/_archive/20261119-h9
cp -a "$B/config.yaml" "$B/SOUL.md" /home/evo/.hermes/
cp -a "$B/pi-job.SKILL.md" /home/evo/.hermes/skills/pi-job/SKILL.md
rm -rf /home/evo/.hermes/memories/USER.md; [ -d "$B/memories" ] && cp -a "$B/memories/." /home/evo/.hermes/memories/
rm -rf /home/evo/.hermes/skills/creative/h3-render /home/evo/.hermes/skills/creative/h3-writer
[ -d "$B/flux-klein-prompting.local" ] && mv "$B/flux-klein-prompting.local" /home/evo/.hermes/skills/flux-klein-prompting
systemctl --user restart hermes-gateway
```

## Later (not this brief)
- After `render/OPERATOR.md` or `writer_prompt.md` changes (for example `X7` / `W4`), rerun `build-hermes-skills.sh` and `--check`.
- `pi-job render|approve|queue` stay in the script until Derrick's yes after 3 good Hermes renders (Hermes plan R13).
- Pipeline-vs-write-it-yourself comparison (card 43) runs after `X7`, in the same chat (step `X8`).

## Rules
- Stop on first failure. No renders, no `--queue`, no `queue-remote.sh` (Derrick's check 3 is his yes, not yours).
- No `llama-swap.yaml` edits. Restart only `hermes-gateway`.
- Never read, print or copy secrets (`.env`, `/home/evo/.config/evo-x3/*`, `/home/evo/.config/pixlstash/*.token`). Never view PixlStash library contents.
- Cite `mono` SHAs in `RESULT.md`.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-E-HERMES/RESULT.md`, then release the lease and stop. List Step 0 and Items 1-4 as `DONE`, `BLOCKED` or `SKIPPED` with exact commands and outputs (the `--check` line, the `hermes skills list` lines, the pytest line, the `--oneshot` reply), backup paths, `snapshot: pending Max`, and rollback status if triggered. Leave "Derrick checks" for Max.
