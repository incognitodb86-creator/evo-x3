# UNI-APPLY-X3-HERMES-WORKSPACES (X3 Forge or Max): two Hermes workspaces (render + code) with Flash-Next presets, Nov 20 2026

Derrick, 2026-11-20 ~8:17 AM CT (no message id yet): "We need to fix hermes and setup two workspaces one for rendering
and one for coding and optimize the qwen flashnext settings for both". Plan: [F4 follow-up](../source-plans/2026-11-18-x3-alienpc-followup-plan.md)
item **H7** (added today). This brief replaces the outside "Opus brief"
([../UNI-OPUS-HERMES-WORKSPACES/BRIEF.md](../UNI-OPUS-HERMES-WORKSPACES/BRIEF.md), Derrick t3015u), which review
blocked ([REVIEW-20261120-opus.md](../UNI-OPUS-HERMES-WORKSPACES/REVIEW-20261120-opus.md)). Max verifies your
`RESULT.md` afterwards.

## Goal

Keep today's render chat (the `default` profile) and add one coding chat (a new `code` profile). Both stay on the one
resident Gufo slot `flash-next-uncensored-v2` (zero swaps). Each gets the Qwen3.8-Flash-Next card's own sampler
through a llama-swap alias:

| Workspace | Hermes profile | Model name | Sampler (Qwen card) | Thinking | cwd |
|---|---|---|---|---|---|
| Render | `default` (unchanged except the model name) | `flash-next-render` | instruct: temp 0.7, top_p 0.8, top_k 20, min_p 0, presence 1.5 | off (`reasoning_effort: false`, Derrick's production rule) | `/home/evo/workspace` |
| Code | `code` (new, cloned from default) | `flash-next-code` | thinking: temp 1.0, top_p 0.95, top_k 20, min_p 0, presence 0 | medium (`model.reasoning_effort: medium`; Gufo default) | `/home/evo/AI/hermes-code` |

Why: Hermes sends no sampler values, so today both uses get Gufo's server defaults (1.0 / 0.95 / 20, the thinking
preset) even with thinking off (VERIFIED: `hosts/x3/live/llama-swap/llama-swap.yaml` Gufo cmd; live Hermes
`config.yaml` has no sampler keys). The aliases set only sampler values. Thinking stays in each Hermes profile,
because Gufo 0.35.0 returns HTTP 400 when `enable_thinking` and `reasoning_effort` arrive together
(`records/plan-v32/PHASE-0-RESULT.md`).

## Needs before launch

- Derrick's yes to this brief and his answer to Q-WS2 below (Max records the ids here).
- Max pulled `mono` at this brief's commit or newer into `/home/derekboone/evo-x3`.
- X3 lease free. No render running or queued from Hermes. No Hermes chat mid-turn. No `pi-job` running
  (`pi-job status` shows nothing RUNNING). Item 1 restarts llama-swap, which reloads Gufo: Hermes and pi are down
  for that minute.

## Access and lease

- Doer: X3 Forge or Max. `derekboone` with `sudo -n` for `/etc/evo-x3/llama-swap.yaml` and the llama-swap restart;
  Hermes steps as `evo` (`sudo -n -iu evo env HERMES_HOME=/home/evo/.hermes ...`).
- Source: `/home/derekboone/evo-x3/config/llama-swap.yaml` (the two new `setParamsByID` blocks) and
  `/home/derekboone/evo-x3/hosts/x3/hermes/workspaces/code/AGENTS.md`.
- Lease: one line `forge-x3 | UNI-APPLY-X3-HERMES-WORKSPACES | <start time>` in
  `/home/derekboone/AI/locks/x3-lease.txt`. Stop if it is not empty. Clear it when done or blocked.

## Work (stop on first failure)

### Step 0: backups
```bash
sudo -n cp -a /etc/evo-x3/llama-swap.yaml /etc/evo-x3/_archive/llama-swap.yaml-20261120-preWS
sudo -n -iu evo bash -c 'B=/home/evo/.hermes/_archive/20261120-ws; mkdir -p "$B" &&
  cp -a /home/evo/.hermes/config.yaml "$B/" && cp -a /home/evo/workspace/AGENTS.md "$B/workspace.AGENTS.md" &&
  hermes config show > "$B/config-show.before.txt" 2>&1 && hermes profile list > "$B/profiles.before.txt" 2>&1'
```

### Item 1: llama-swap aliases (root file)
1. In `/etc/evo-x3/llama-swap.yaml`, under `models."flash-next-uncensored-v2".filters.setParamsByID`, add the two
   blocks `"flash-next-render"` and `"flash-next-code"` exactly as in mono `config/llama-swap.yaml` (comment lines
   included). Do not copy the whole mono file over the live one. Keep both `-sub` entries and `concurrencyLimit: 4`.
2. Restore the two `halogen-only` pins the 2026-11-19 TEST-WINDOW commented out
   (`gemma4-heretic: flash-next-uncensored-v2`, `gemma4-heretic-sub: flash-next-uncensored-v2`). Derrick 2026-11-20
   ~8:40 AM CT: Gemma is dropped and the X3 stays on Qwen Flash-Next. W1b is closed (t2898u). Without the pins, any
   `gemma4-heretic` call loads the real Gemma in the exclusive `main` group and unloads Gufo. Leave the
   `gemma4-heretic` model block and its weights in place; deleting the 25 GiB of weights is a separate yes.
3. Parse check, then restart:
```bash
sudo -n python3 -c 'import yaml,sys; c=yaml.safe_load(open("/etc/evo-x3/llama-swap.yaml")); m=c["models"]["flash-next-uncensored-v2"]; p=m["filters"]["setParamsByID"]; assert {"flash-next-render","flash-next-code"} <= set(p) and m["concurrencyLimit"]==4; print("OK")'
sudo -n systemctl restart llama-swap
```
   Wait until `flash-next-uncensored-v2` shows ready in llama-swap `/running` (the on_startup preload loads it).

### Item 2: render workspace (default profile)
```bash
sudo -n -iu evo env HERMES_HOME=/home/evo/.hermes hermes config set model.default flash-next-render
```
Leave everything else as is (`reasoning_effort: false`, `terminal.cwd`, `key_env`, `secrets.command`, the
`guard-render-queue.sh` hook, skills, `auxiliary.vision`).

### Item 3: coding workspace (new `code` profile)
```bash
sudo -n -iu evo env HERMES_HOME=/home/evo/.hermes bash -c '
set -e
hermes profile create code --clone --no-alias --description "Coding workspace: reviews, debugging, pi-job code|review"
mkdir -p /home/evo/AI/hermes-code
install -m 0644 /home/derekboone/evo-x3/hosts/x3/hermes/workspaces/code/AGENTS.md /home/evo/AI/hermes-code/AGENTS.md
P="hermes -p code config set"
$P model.default flash-next-code
$P model.reasoning_effort medium
$P terminal.cwd /home/evo/AI/hermes-code
$P skills.external_dirs "[]"
$P skills.disabled "[alienpc-hardcore-i2v-director, alienpc-stills-pose-edit-prompting, comfy-render, h3-hc-render, h3-max-ref2va-prompt, image-render, video-render, ascii-video, manim-video, comfyui, h3-render, h3-writer, pixlstash-image-library]"
'
```
- `--clone --no-alias` are the flags Max used for `writertest` (`hosts/x3/hermes/README.md`). If `--description` is not
  accepted, drop it and put the description line in the profile's `profile.yaml`, like `writertest`.
- If `/home/derekboone/evo-x3/hosts/x3/hermes/workspaces/code/AGENTS.md` is not readable by `evo`, copy it as
  `derekboone` to a temp path first. Do not change the file's text.
- `.env`: handle the clone's `.env` the same way as the existing `writertest` profile. Check with `ls -l` only; never
  print the contents.
- Keep the cloned `hooks.pre_tool_call` guard, `key_env`, and `secrets.command` (the clone carries them; confirm in
  `hermes -p code config show`).
- Restart the gateway only when no chat is mid-turn: `sudo -n systemctl --user -M evo@ restart hermes-gateway`.

### Item 4: drop the Gemma profile (Derrick 2026-11-20 ~8:40 AM CT)
Before the gateway restart in Item 3, move `/home/evo/.hermes/profiles/gemma` into
`/home/evo/.hermes/_archive/20261120-ws/profiles-gemma` (archive, do not delete). Leave `writertest` alone.

## Tests

1. Alias probes. The key is read from the owner-only file and passed on stdin, never on argv:
```bash
probe() { sudo -n -iu evo bash -c '( set -a; . /home/evo/.config/evo-x3/llm.env; printf "header = \"Authorization: Bearer %s\"\n" "$LLM_KEY_HERMES" ) | curl -sS -K - -H "Content-Type: application/json" http://127.0.0.1:8080/v1/chat/completions -d "$1"' _ "$1"; }
probe '{"model":"flash-next-render","messages":[{"role":"user","content":"Say OK."}],"max_tokens":32,"chat_template_kwargs":{"enable_thinking":false}}'
probe '{"model":"flash-next-code","messages":[{"role":"user","content":"What is 17*23? Answer with the number."}],"max_tokens":1024}'
```
   Pass: both HTTP 200. Render: `reasoning_content` empty or absent. Code: `reasoning_content` not empty and the
   answer is 391. Record only the status, the token counts, and whether reasoning was present. Do not log the key.
2. `/running`: only `flash-next-uncensored-v2` from the `main` group is loaded (no Gemma, no ref2va).
3. Render chat:
   `hermes chat --oneshot -Q -q "Which skill renders a video, and which changes code? One line."` answers
   `h3-render` and `pi-job`, and `hermes config show` shows `model.default: flash-next-render`.
4. Code chat:
   `hermes -p code chat --oneshot -Q -q "Run pwd, then say which skill changes code. One line."` answers
   `/home/evo/AI/hermes-code` and `pi-job`. `hermes -p code skills list` shows `h3-render` disabled.
5. WebUI: pick profile `code` and ask `pwd`. If it answers `/home/evo/workspace` (the WebUI default from
   `hermes-webui.service.d/30-workspace.conf`), record that and set that chat's workspace to `/home/evo/AI/hermes-code`
   in the WebUI workspace picker. Do not edit the systemd drop-in in this brief.
6. Render smoke (Derrick, optional): in the render chat, one clip ask on a still he names reaches READY and
   `Render this? (yes / no)`. No queue. If Hermes garbles or repeats paths, the likely cause is `presence_penalty 1.5`:
   set it to `0.0` in the `flash-next-render` block, restart llama-swap, and record it.

## Rollback

- `sudo -n cp -a /etc/evo-x3/_archive/llama-swap.yaml-20261120-preWS /etc/evo-x3/llama-swap.yaml && sudo -n systemctl restart llama-swap`.
- `hermes config set model.default flash-next-uncensored-v2` (as evo).
- Move `/home/evo/.hermes/profiles/code` and `/home/evo/AI/hermes-code` into `/home/evo/.hermes/_archive/20261120-ws/`
  (archive, do not delete), move `profiles-gemma` back if Derrick wants it, then restart the gateway.

## Q-card for Derrick (answer in chat; Max records the id)

- **Q-WS2:** thinking in the code workspace: **medium** (default; your 2026-11-19 16:48 CT coding pick) or low.
- Settled by Derrick 2026-11-20 ~8:40 AM CT ("we are going to drop gemma. and stick with qwenflash next on x3"): the
  Gemma pins come back (Item 1) and the `gemma` profile is archived (Item 4).

## Rules

- Back up every changed file first (Step 0). No secrets on argv or in output. Never print `llm.env`, `.env`, or token
  files. Do not touch ComfyUI, the render pipeline, skills content, or `/home/evo/workspace/AGENTS.md`.
- Keep it small: no wrapper scripts, no prefill files, no new hooks, no extra aliases.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md`
and stop. List Step 0, Items 1-4 and Tests 1-6 as DONE, BLOCKED or SKIPPED with evidence: backup paths, the
`setParamsByID` keys as read back, `/running` output, the oneshot answers, the probe status lines, and the lease
take/clear times (CT).
