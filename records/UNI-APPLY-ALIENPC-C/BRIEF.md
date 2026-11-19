Goal: After `UNI-APPLY-ALIENPC-A` and `UNI-APPLY-ALIENPC-B-AGT1` have RESULTs, apply the rest of the AlienPc file items (SK4/SK5 skills + backup-writer copy, FX1 skill, M4/TQ candidate templates, `comm.py` LOST_PROMPT fix) and check the Flux / Miraclein nodes load (M3, M1), under the AlienPc lease.

# UNI-APPLY-ALIENPC-C (AlienPc Forge): rest of the AlienPc files + Flux setup check, Nov 19 2026

Authority: Derrick 2026-11-19 (12:54 CT AlienPc backup writer; 13:15 CT skills/templates review; prompting chat FX1; 13:55 CT "install and test our setup for flux miraclein" while the X3 picks the writer) and `records/uplan/PLAN.md` "Order of work" step A3. The brief comes from Max/X3; AlienPc Forge is the hands (INV1b, card 38). Max verifies your RESULT.

## Needs before launch (ALL required)
- `UNI-APPLY-ALIENPC-A` and `UNI-APPLY-ALIENPC-B-AGT1` RESULTs exist (Max confirms in the launch message).
- AlienPc lease free: ONE line `alienpc-forge | UNI-APPLY-ALIENPC-C | <start time>` per brain `10_packs/max/max-briefing.md`, cleared when done or blocked. No GPU job: `C:\AI\locks\gpu-render.lock` absent and `:8447` idle.
- Max stages two patches on the X3 and gives their sha256 in the launch message (`C:\AI\community` and `C:\AI\render` track the separate Gitea repos; never run `git remote -v` or print their URLs):
  - `/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-C-community.patch` = `git diff --binary <base> <mono tip> --relative=alienpc/community/ -- alienpc/community`, where `<base>` = the `mono` commit `UNI-APPLY-ALIENPC-A`'s patch was staged from (`5ccba67` if staged as written). If A was staged from a tip that already has these changes, this patch is empty: skip Item 1 and do Item 2.
  - `/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-C-render.patch` = the `alienpc/render/` changes since what `C:\AI\render` holds (Max picks the base from AGT1's RESULT).
  - If `MONO-S6` already passed: skip the patches and `git -C C:\AI\evo-x3 pull --ff-only`.

## Work (stop on first failure)

### Step 0 — check, record, back up
- `git -C C:\AI\community status --porcelain -- templates scripts skills` and the same for `C:\AI\render`: note dirty files (M7). The patch check below stops on any overlap.
- Record both HEADs. Back up every file the patches touch into `C:\AI\_archive\20261119\alienpc-c\`.

### Item 1 — Apply the two patches
- Allowed X3 command (read-only copy): `scp x3:/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-C-*.patch C:\AI\_archive\20261119\alienpc-c\`
- Check each sha256 (`Get-FileHash -Algorithm SHA256`) against the launch message; stop if different.
- `git -C <repo> apply --check <patch>`, then apply; commit only the patched paths (`git add -- <paths>`; `git commit -m "UNI-APPLY-ALIENPC-C (mono <tip>)" -- <paths>`). No push.
- Contents: SK4/SK5 skills, `flux-klein-prompting` (FX1), backup-writer `AGENTS.md` / `writer_prompt.md` / `config.yaml` sha pin (SK4), M4 candidates on Miraclein 4.5, TQ candidates + U55/faces template sync (TQ7), `scripts/comm.py` LOST_PROMPT fix (carryover `4122e40`).
- Verify: `Get-FileHash C:\AI\render\writer_pipeline\writer_prompt.md` matches `writer_prompt_sha256` in `C:\AI\render\writer_pipeline\config.yaml`; `python -m pytest -q -p no:cacheprovider C:\AI\community\scripts\tests\test_template_allowlist.py` (12 passed; set `PYTHONDONTWRITEBYTECODE=1`); the template allowlist CLI still REFUSEs every `*.candidate.api.json`.

### Item 2 — Flux / Miraclein node check (M3) and MiniMaxH3Mod check (M1)
- Through AlienPc llama-swap (the same path `run_queue` uses), let `comfyui_auto` start, then read the start log for import errors from `ComfyUI-Flux2Klein9Mod` and `ComfyUI-MiniMaxH3Mod` (`comfy_api.latest` on ComfyUI 0.38.0).
- `GET /upstream/comfyui_auto/object_info` and list every node class from `ComfyUI-Flux2Klein9Mod` (expect 4, incl. `Klein9RefModsLoader`, `Klein9RefModApply`) and the MiniMaxH3Mod nodes. Save the widget names/enums of `Klein9RefModsLoader` and `Klein9RefModApply` to RESULT (the M4 candidates use `"partially_preserved (0.7)"`; report any mismatch, don't edit templates).
- No render, no still, no Manager, no downloads. Let llama-swap unload ComfyUI afterwards (ttl).
- If imports fail: `BLOCKED (M3)` with the error lines; FP8 / ComfyUI upgrade (R7) are separate Derrick yeses.

## Rollback
- `git -C <repo> revert --no-edit HEAD` (the one apply commit) or restore from `C:\AI\_archive\20261119\alienpc-c\`. Never `git reset --hard` (M7 dirty files).

## Rules
- No renders, no GPU jobs beyond letting ComfyUI start for the node check, no ComfyUI-Manager, no downloads. Don't open `C:\Users\derek\sydney\` or PixlStash library contents. No secrets in output.

STOP CONDITION: write `C:\AI\_archive\20261119\UNI-APPLY-ALIENPC-C-RESULT.md` (Max files it as `records/UNI-APPLY-ALIENPC-C/RESULT.md`), clear the lease line, then stop. List Step 0, Item 1, Item 2 as `DONE`, `BLOCKED` or `SKIPPED` with HEADs, patch sha256, test totals, node list and widget enums.
