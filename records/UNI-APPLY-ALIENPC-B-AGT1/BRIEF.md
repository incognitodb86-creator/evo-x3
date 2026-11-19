Goal: Apply AGT1 (`mono` `4e49160`..`3217c67`: AlienPc global AGENTS.md + approved INV1b, Forge settings.json -> `coding_swift15_iq3s`, ralph PROMPT/script, render executor AGENTS.md, agent-shared pointer, and move 5 writer-skill links) on AlienPc under the AlienPc lease.

# UNI-APPLY-ALIENPC-B-AGT1 (AlienPc Forge): Apply AGT1 agent files redo on AlienPc, Nov 19 2026

Authority: Derrick 2026-11-19 12:29 CT (side chat: Card 21 ESP-off everywhere -> `coding_swift15_iq3s`; `INV1` resolved as single master `C:\Users\derek\.pi\agent\AGENTS.md` -> `AGT1`; Card 38 `INV1b` APPROVED — brief from X3/Max, AlienPc Forge is the hands) and `records/unified-implementation/PLAN.md`. Max verifies your `RESULT.md` afterwards.

## Needs before launch (ALL required — do not launch until met)
1. **Derrick's live yes in chat:** Card 21 (`coding_swift15_iq3s` ESP off everywhere), `INV1` -> `AGT1`, and Card 38 (`INV1b`) are **ANSWERED YES** (Derrick 2026-11-19 12:29 CT, side chat); Card 1 live apply yes for AGT1 answered in chat (Max records id).
2. **AlienPc lease taken (written by Max — Card 28 answered, Derrick 12:29 CT side chat, relayed by orchestrator; Max adds the message id):**
   - Take: `30_handoff/status/YYYY-MM-DD-HHMM-alienpc-lease-taken-alienpc-forge-uni-apply-alienpc-b-agt1.md` (mirrored to `records/status/`).
   - Release: `30_handoff/status/YYYY-MM-DD-HHMM-alienpc-lease-released-alienpc-forge-uni-apply-alienpc-b-agt1.md` (mirrored to `records/status/`, written by Max on closeout).
3. **Max-owned Prerequisite (ESP-off alias `coding_swift15_iq3s`) COMPLETE before copying `settings.json`** (same prerequisite as `records/UNI-APPLY-X3-B-PIJOB/BRIEF.md`; Max confirms in the launch message — Forge never reads `models.json`).
4. **Max import + staged files ready** from `mono` tip `3217c67 (or newer at Max import)` (`gitleaks` clean; `mono` SHAs: `4e49160` A1, `2f8db27` A2, `fc238ba` A3/A7/A8/A9, `6a6abb8` A4, `b83a0a7` A5, `3217c67` A6).
   - Until `MONO-S6` passes smoke, Max stages the 8 source files on the X3 under `/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-B-AGT1/` with a `SHA256SUMS.txt` (Forge copies them read-only via `scp x3:`; allowed even while X3 Forge holds the X3 lease). After `MONO-S6`, read directly from `C:\AI\evo-x3`.

## Max-owned Prerequisite: ESP-off alias `coding_swift15_iq3s` (same prereq as `UNI-APPLY-X3-B-PIJOB`; complete before launching Forge)
- **AlienPc `llama-swap` (Max, or AlienPc Forge via X3/Max brief — Card 38 `INV1b` APPROVED, Derrick 2026-11-19 12:29 CT, side chat):**
  1. Take the AlienPc lease. Confirm idle: `Test-Path C:\AI\locks\gpu-render.lock` is `False` and `https://alienpc.tailf242b2.ts.net:8447/health` returns `200` (never edit during a render).
  2. Back up AlienPc llama-swap config to `C:\AI\_archive\20261119\llama-swap\`.
  3. Add/enable the exact ESP-off alias `coding_swift15_iq3s` (ESP off everywhere — both AlienPc Forge and `pi-job` use `coding_swift15_iq3s`, Card 21), then reload llama-swap.
  4. Verify `/v1/models` lists exact id `"coding_swift15_iq3s"` (exact-id match count = `1`, not substring match on `_esp`).
  5. Rollback: restore from `C:\AI\_archive\20261119\llama-swap\` and reload llama-swap.
- **AlienPc `C:\Users\derek\.pi\agent\models.json` (Max ONLY — secrets rule; Forge never reads `models.json`):**
  1. Back up `C:\Users\derek\.pi\agent\models.json` to `C:\AI\_archive\20261119\agents\pi-agent\models.json` (never printed or committed).
  2. Ensure `coding_swift15_iq3s` is defined without printing any keys.
  3. Rollback: restore `C:\AI\_archive\20261119\agents\pi-agent\models.json`.
- State in the Forge launch message that both `llama-swap` and `models.json` aliases are verified live.

## Access & Lease
- **Doer:** AlienPc Forge (`C:\Users\derek\forge` -> `5slock`, pi panes `w2V:p3`/`p7`), running as user `derek` (sudo/admin: **no**).
- **Backup root:** `C:\AI\_archive\20261119\agents\` (create subdirs `pi-agent`, `ralph-community`, `forge`, `render`, `agent-shared`, `skills-links` first). No deletes.
- **Lease take/release (written by Max, Card 28):** `30_handoff/status/YYYY-MM-DD-HHMM-alienpc-lease-{taken,released}-alienpc-forge-uni-apply-alienpc-b-agt1.md` (mirrored to `records/status/`).
- **No GPU, no ComfyUI restart, no renders; confirm idle first:**
  ```powershell
  Test-Path C:\AI\locks\gpu-render.lock
  curl.exe -s -o NUL -w "%{http_code}`n" https://alienpc.tailf242b2.ts.net:8447/health
  ```
  Expected: `False` and `200`. **STOP** if a render is running.

## Work (stop on first failure; back up every file before overwriting)

1. **Pre-checks & fetch staged files:**
   - Confirm Max's launch message states `coding_swift15_iq3s` is live in AlienPc `llama-swap` and `models.json` (**do NOT read `models.json`**).
   - Create backup dirs under `C:\AI\_archive\20261119\agents\{pi-agent,ralph-community,forge,render,agent-shared,skills-links}`.
   - Allowed X3 command (Plan finding 14; read-only copy allowed even while X3 Forge holds the X3 lease):
     `scp -r x3:/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-B-AGT1 C:\AI\_archive\20261119\agents\_staged`
     Verify every file's SHA256 against `SHA256SUMS.txt` (stop on mismatch).

2. **Install files (exact Install lines from `reports\alienpc-agents.md`, backup first for each):**
   - `hosts/alienpc/live/pi-agent/AGENTS.md` (`4e49160`, `2f8db27`, `fc238ba`) -> `C:\Users\derek\.pi\agent\AGENTS.md` | backup: `C:\AI\_archive\20261119\agents\pi-agent\AGENTS.md`
   - `hosts/alienpc/live/pi-agent/settings.json` (`4e49160`, UTF-8 without BOM; **only after prereq**) -> `C:\Users\derek\.pi\agent\settings.json` | backup: `C:\AI\_archive\20261119\agents\pi-agent\settings.json`
   - `hosts/alienpc/live/forge/ralph-community/PROMPT.md` (`b83a0a7`) -> `C:\Users\derek\forge\ralph-community\PROMPT.md` | backup: `C:\AI\_archive\20261119\agents\ralph-community\PROMPT.md`
   - `hosts/alienpc/live/forge/ralph-community/ralph.ps1` (`4e49160`) -> `C:\Users\derek\forge\ralph-community\ralph.ps1` | backup: `C:\AI\_archive\20261119\agents\ralph-community\ralph.ps1`
   - `hosts/alienpc/live/forge/README.md` (`3217c67`) -> `C:\Users\derek\forge\README.md` | backup: `C:\AI\_archive\20261119\agents\forge\README.md`
   - `alienpc/render/_archive/AGENTS.writer-book-20261119.md` + `alienpc/render/AGENTS.md` (`6a6abb8`) -> `C:\AI\render\_archive\AGENTS.writer-book-20261119.md` and `C:\AI\render\AGENTS.md` (**keep `C:\AI\render\writer_pipeline\writer_prompt.md` untouched**) | backup: `C:\AI\_archive\20261119\agents\render\AGENTS.md`
   - `alienpc/community/agent-shared/AGENTS.md` (`2f8db27`, 2-line pointer; break any hard link by writing to a temp file and replacing) -> `C:\AI\community\agent-shared\AGENTS.md` | backup: `C:\AI\_archive\20261119\agents\agent-shared\AGENTS.md`

3. **Move (do NOT delete) the 5 writer-skill symlinks (A6, `3217c67`):**
   - Move these 5 links from `C:\Users\derek\.pi\agent\skills\` to `C:\AI\_archive\20261119\agents\skills-links\` (targets under `C:\AI\community\skills\` stay untouched):
     - `h3-prompting`
     - `h3-max-ref2va-prompt`
     - `h3-parody-identity`
     - `alienpc-hardcore-i2v-director`
     - `alienpc-stills-pose-edit-prompting`
   - Keep linked in `C:\Users\derek\.pi\agent\skills\`: `comfy-render`, `video-render`, `image-render`, `h3-hc-render`, `ralph-loop`, `rea-video`.

## Tests (CPU / offline + pi smoke only — no GPU, no ComfyUI)

1. **`pi` starts on `coding_swift15_iq3s`:**
   - Verify `settings.json` has no UTF-8 BOM and `defaultModel` is `coding_swift15_iq3s`.
   - Run `pi -p --no-session "reply ok"` -> exits 0 using `coding_swift15_iq3s`.
2. **`C:\AI\render\AGENTS.md` is the executor file:**
   - Confirm `C:\AI\render\AGENTS.md` is the 20-line executor file, `C:\AI\render\_archive\AGENTS.writer-book-20261119.md` exists, and `C:\AI\render\writer_pipeline\writer_prompt.md` is untouched.
3. **`agent-shared\AGENTS.md` pointer & no hard link:**
   - Confirm `C:\AI\community\agent-shared\AGENTS.md` is the 2-line pointer and `fsutil hardlink list C:\Users\derek\.pi\agent\AGENTS.md` lists only 1 path.
4. **5 writer-skill links moved, not deleted:**
   - Confirm all 5 links exist in `C:\AI\_archive\20261119\agents\skills-links\`, their 5 target folders still exist under `C:\AI\community\skills\`, and the 6 kept links remain in `C:\Users\derek\.pi\agent\skills\`.
5. **`INV1b` line present:**
   - `Select-String -Path C:\Users\derek\.pi\agent\AGENTS.md -Pattern "BRIEF"` confirms the X3/Max BRIEF exception line is present.

## Rollback (run immediately if any test fails)
- Restore every backed-up file from `C:\AI\_archive\20261119\agents\{pi-agent,ralph-community,forge,render,agent-shared}\` to its live path.
- Move the 5 skill links back from `C:\AI\_archive\20261119\agents\skills-links\` to `C:\Users\derek\.pi\agent\skills\`.
- Confirm `pi -p --no-session "reply ok"` exits 0.

## Rules
- **No ComfyUI restart, no ComfyUI-Manager, no GPU use, no renders, do not run while a render is active.**
- Do **not** delete any files or skill targets. Do **not** touch `C:\AI\render\writer_pipeline\writer_prompt.md`.
- Do **not** open `C:\Users\derek\sydney\`. Never read or print `models.json` or any secret/token.
- Cite `mono` SHAs (`4e49160`, `2f8db27`, `fc238ba`, `6a6abb8`, `b83a0a7`, `3217c67`) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `C:\AI\_archive\20261119\UNI-APPLY-ALIENPC-B-AGT1-RESULT.md` (Max collects and files it into `evo-x3/records/UNI-APPLY-ALIENPC-B-AGT1/RESULT.md`), then stop. List Pre-checks, each installed file + backup path, the 5 moved skill links, and Tests 1-5 as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs and rollback status if triggered.
