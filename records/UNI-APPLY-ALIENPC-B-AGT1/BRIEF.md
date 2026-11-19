Goal: Apply AGT1 (AlienPc global AGENTS.md + approved INV1b + backup-writer lines, Forge settings.json -> `coding_swift15_iq3s`, ralph PROMPT/script, agent-shared pointer; keeps `C:\AI\render\AGENTS.md` writer book and all 9 skills linked) on AlienPc under the AlienPc lease.

# UNI-APPLY-ALIENPC-B-AGT1 (AlienPc Forge): Apply AGT1 agent files redo on AlienPc, Nov 19 2026

Authority: Derrick 2026-11-19 12:29 CT (side chat: Card 21 ESP-off everywhere -> `coding_swift15_iq3s`; `INV1` resolved as single master `C:\Users\derek\.pi\agent\AGENTS.md` -> `AGT1`; Card 38 `INV1b` APPROVED — brief from X3/Max, AlienPc Forge is the hands), Derrick 2026-11-19 12:54 CT (orchestrator chat: AlienPc = backup prompt writer when X3 is busy coding and AlienPc is idle -> keep writer book and all 9 skills linked), and `records/unified-implementation/PLAN.md`. Max verifies your `RESULT.md` afterwards.

## Needs before launch (ALL required — do not launch until met)
1. **Derrick's live yes in chat:** Card 21 (`coding_swift15_iq3s` ESP off everywhere), `INV1` -> `AGT1`, and Card 38 (`INV1b`) are **ANSWERED YES** (Derrick 2026-11-19 12:29 CT, side chat); Card 1 live apply yes for AGT1 answered in chat (Max records id).
2. **AlienPc lease free** (AlienPc lease per brain `10_packs/max/max-briefing.md`). The doer takes it as ONE line (`<who> | <what> | <start time>`) and clears it when done; no lease-taken/released files, no brain or `records/status/` mirrors, no git commit for the lease, no message to Derrick.
3. **Max-owned Prerequisite (ESP-off alias `coding_swift15_iq3s`) COMPLETE before copying `settings.json`** (same prerequisite as `records/UNI-APPLY-X3-B-PIJOB/BRIEF.md`; Max confirms in the launch message — Forge never reads `models.json`).
4. **Max import + staged files ready** from `mono` tip `bab584a (or newer at Max import)` (**ONE BRANCH:** `mono` is the ONLY branch anyone pushes — Derrick ~13:05 CT, no part-branch pushes; `gitleaks` clean; includes AGT1 backup-writer revert of A4/A5/A6).
   - Until `MONO-S6` passes smoke (recommended next — it ends the bridge), Max stages the AGT1 source files locally on the X3 under `/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-B-AGT1/` with a `SHA256SUMS.txt` (Forge copies them read-only via `scp x3:`; allowed even while X3 Forge holds the X3 lease). After `MONO-S6`, read directly from `C:\AI\evo-x3`.

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
- **Backup root:** `C:\AI\_archive\20261119\agents\` (create subdirs `pi-agent`, `ralph-community`, `forge`, `agent-shared` first). No deletes.
- **Lease:** AlienPc lease (brain `10_packs/max/max-briefing.md`): ONE line `alienpc-forge | UNI-APPLY-ALIENPC-B-AGT1 | <start time>` at start, cleared when done or blocked; no status files, mirrors, commits, or messages for the lease.
- **No GPU, no ComfyUI restart, no renders; confirm idle first:**
  ```powershell
  Test-Path C:\AI\locks\gpu-render.lock
  curl.exe -s -o NUL -w "%{http_code}`n" https://alienpc.tailf242b2.ts.net:8447/health
  ```
  Expected: `False` and `200`. **STOP** if a render is running.

## Work (stop on first failure; back up every file before overwriting)

1. **Pre-checks & fetch staged files:**
   - Confirm Max's launch message states `coding_swift15_iq3s` is live in AlienPc `llama-swap` and `models.json` (**do NOT read `models.json`**).
   - Create backup dirs under `C:\AI\_archive\20261119\agents\{pi-agent,ralph-community,forge,agent-shared}`.
   - Allowed X3 command (Plan finding 14; read-only copy allowed even while X3 Forge holds the X3 lease):
     `scp -r x3:/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-B-AGT1 C:\AI\_archive\20261119\agents\_staged`
     Verify every file's SHA256 against `SHA256SUMS.txt` (stop on mismatch).

2. **Install files (backup first for each; NO writer-book archive and NO skill unlinks — Derrick 2026-11-19 12:54 CT backup-writer decision):**
   - `hosts/alienpc/live/pi-agent/AGENTS.md` -> `C:\Users\derek\.pi\agent\AGENTS.md` | backup: `C:\AI\_archive\20261119\agents\pi-agent\AGENTS.md`
   - `hosts/alienpc/live/pi-agent/settings.json` (UTF-8 without BOM; **only after prereq**) -> `C:\Users\derek\.pi\agent\settings.json` | backup: `C:\AI\_archive\20261119\agents\pi-agent\settings.json`
   - `hosts/alienpc/live/forge/ralph-community/PROMPT.md` -> `C:\Users\derek\forge\ralph-community\PROMPT.md` | backup: `C:\AI\_archive\20261119\agents\ralph-community\PROMPT.md`
   - `hosts/alienpc/live/forge/ralph-community/ralph.ps1` -> `C:\Users\derek\forge\ralph-community\ralph.ps1` | backup: `C:\AI\_archive\20261119\agents\ralph-community\ralph.ps1`
   - `hosts/alienpc/live/forge/README.md` -> `C:\Users\derek\forge\README.md` | backup: `C:\AI\_archive\20261119\agents\forge\README.md`
   - `alienpc/community/agent-shared/AGENTS.md` (2-line pointer; break any hard link by writing to a temp file and replacing) -> `C:\AI\community\agent-shared\AGENTS.md` | backup: `C:\AI\_archive\20261119\agents\agent-shared\AGENTS.md`
   - **Keep untouched:** `C:\AI\render\AGENTS.md` (writer book stays in place), `C:\AI\render\writer_pipeline\writer_prompt.md`, and **all 9 community skill symlinks** in `C:\Users\derek\.pi\agent\skills\` (do **not** unlink or move any skills).

## Tests (CPU / offline + pi smoke only — no GPU, no ComfyUI)

1. **`pi` starts on `coding_swift15_iq3s`:**
   - Verify `settings.json` has no UTF-8 BOM and `defaultModel` is `coding_swift15_iq3s`.
   - Run `pi -p --no-session "reply ok"` -> exits 0 using `coding_swift15_iq3s`.
2. **Writer book & backup-writer lines present:**
   - Confirm `C:\AI\render\AGENTS.md` (writer book) is still present and intact, `C:\AI\render\writer_pipeline\writer_prompt.md` is untouched, and `"backup"` / backup-writer lines are present in `C:\Users\derek\.pi\agent\AGENTS.md` (and `C:\Users\derek\forge\README.md`).
3. **`agent-shared\AGENTS.md` pointer & no hard link:**
   - Confirm `C:\AI\community\agent-shared\AGENTS.md` is the 2-line pointer and `fsutil hardlink list C:\Users\derek\.pi\agent\AGENTS.md` lists only 1 path.
4. **All 9 community skill links still intact:**
   - Confirm all 9 community skill symlinks (plus `ralph-loop` and `rea-video`) remain linked in `C:\Users\derek\.pi\agent\skills\`.
5. **`INV1b` line present:**
   - `Select-String -Path C:\Users\derek\.pi\agent\AGENTS.md -Pattern "BRIEF"` confirms the X3/Max BRIEF exception line is present.

## Rollback (run immediately if any test fails)
- Restore every backed-up file from `C:\AI\_archive\20261119\agents\{pi-agent,ralph-community,forge,agent-shared}\` to its live path.
- Confirm `pi -p --no-session "reply ok"` exits 0.

## Rules
- **No ComfyUI restart, no ComfyUI-Manager, no GPU use, no renders, do not run while a render is active.**
- Do **not** delete any files, unlink any skills, or archive `C:\AI\render\AGENTS.md`.
- Do **not** open `C:\Users\derek\sydney\`. Never read or print `models.json` or any secret/token.
- Cite `mono` SHAs at Max import in `RESULT.md`.

STOP CONDITION: when done or blocked, write `C:\AI\_archive\20261119\UNI-APPLY-ALIENPC-B-AGT1-RESULT.md` (Max collects and files it into `evo-x3/records/UNI-APPLY-ALIENPC-B-AGT1/RESULT.md`), then stop. List Pre-checks, each installed file + backup path, and Tests 1-5 as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs and rollback status if triggered.
