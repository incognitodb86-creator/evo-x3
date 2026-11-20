# M0 pre-flight snapshot — 2026-11-19 19:13 CT

Doer: Max Architect executor. Plan item M0 (AlienPc lane). Lease still held from A7 stage-2, then cleared 19:13:35 CT. TestRuntime only; original ComfyUI folder not touched. No deletes.

## Checks (VERIFIED, 19:13:08 CT)

- C: free **77.2 GB** (≥ 25 GB). Used 849.0 / 926.2 GB.
- `gpu-render.lock` absent. GPU 0%, 343 MiB / 16303 MiB. A7 stage-2 had just unloaded.
- Official Beta 7 UNET, text encoder, video VAE, and audio VAE are all present in the TestRuntime models tree (sizes 22,893,150,024; 15,687,142,551; 2,811,065,184; 605,254,808 bytes).

## Snapshot

The rollback archive was **already present** at `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\_archive\20261119_pre_miraclein\ComfyUI-MiniMaxH3Mod` (mtime 2026-11-19 13:04:46 CT). It was **not overwritten**.

- Archive `git rev-parse HEAD`: `517e8c419a8584fbf69fceb487bc39d83e6a6ec8` — this is the pin the plan named.
- Live TestRuntime `ComfyUI-MiniMaxH3Mod` is newer: `54f93eb6569fe35c9303e9bceb1c8b66c5722bbf` (2026-11-14 11:12:01 −0300, "Delete node.zip"). History still contains `517e8c41`.
- A verify note was added beside the existing snapshot: `M0-VERIFY-20261119-1913.txt`.

Pass test (backup + snapshot exist): **DONE** (pre-existing 13:04 CT snapshot at the plan pin, re-verified after the evening renders).
