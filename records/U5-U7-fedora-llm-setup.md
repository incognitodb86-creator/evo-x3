# U5–U7 morning closeout: Fedora LLM setup (2026-11-15, America/Chicago)

- **Host:** evo-X3 / Fedora 44 Server / kernel 7.3.3-200.fc44.x86_64
- **Plan:** 2026-11-11-evo-x3-setup-plan.md rev 8
- **Status:** Working optimized loopback setup for embed-small, qwen27b, and gemma4-heretic. Flash-Next is on disk and SHA-verified but does not load until Derrick sets BIOS UMA to 512 MB.
- **Full log:** `runs/fedora_llm_20261115/overnight-20261114.md`
- **Production llama-swap config:** `stage/config/llama-swap/config-production.yaml` (live copy of `/etc/evo-x3/llama-swap.yaml`)

## What was already done overnight (2026-11-14)

fedora-root grown to 1.62 TiB (Windows / BACKUP_OS / Recovery / EFI untouched). Kernel caps, llama-swap v272, pinned Gufo 0.34.0 and kyuz0 llama.cpp 12405 images, and all eight GGUF files downloaded and SHA256-verified. The box then rebooted into Windows, so tests and unit enable did not finish that night.

## What this session finished (2026-11-15 07:38–07:48 CT)

- Confirmed Fedora boot with `amdgpu.gttsize=122880 ttm.pages_limit=31457280`. UEFI BootOrder left at `0003,0000,0001` (Fedora first). No BIOS / UMA change.
- Re-verified all eight model files against official Hugging Face LFS sha256 values (`runs/fedora_llm_20261115/SHA256SUMS`, `sha256-verify.log`). ok=8 fail=0 at 07:42:10 CT.
- Enabled llama-swap was already active on `127.0.0.1:8080`. Pulled the same pinned images into the root podman store (they had only been in the user store).
- Config fixes (backups on the host): official Qwen3.8-27B thinking-mode sampling; llama.cpp 12405 flags `--load-mode none -fa on` (dropped invalid `--no-mmap`); `gufo serve llm` (image has no ENTRYPOINT); `healthCheckTimeout: 900`. `${env.LLM_KEY_*}` placeholders left empty for Derrick to type. No secrets in git.
- Loopback completion tests (`runs/fedora_llm_20261115/model-tests.json`):

| model | result | prompt tok/s | gen tok/s |
|---|---|---:|---:|
| embed-small | 200, 768-dim embedding in 1.33 s | — | — |
| qwen27b | 200, 6.99 s wall, 262144 ctx, q8_0 KV | 45.52 | 11.21 |
| gemma4-heretic | 200, 4.36 s wall, 65536 ctx, q8_0 KV | 61.56 | 45.47 |
| flash-next | 500, device allocation failed | — | — |

qwen27b and gemma4-heretic returned empty message content because the 16-token smoke budget was consumed by thinking; timings still recorded.

## Flash-Next blocker (no BIOS change made)

Gufo `diagnose` reports a 62.4 GiB unified memory pool (`totalBytes=67019173888`), which is the OS-visible RAM while BIOS UMA is still 64 GB. Weights are ~103.69 GiB + 2.60 GiB MTP. Load failed with `device allocation failed for blk.36.ffn_up_exps.weight`. After Derrick sets UMA to 512 MB, retry `--context 32768`, then 65536 if it allocates. Native 262144 will still need the KTD2 cap bump.

## Not done (still need Derrick's yes)

- BIOS UMA 512 MB and Balanced 85 W (his morning task)
- Tailscale Serve / ACL for publishing the endpoint off loopback
- Typing API keys into `/etc/evo-x3/llm.env` (chmod 0600, root:root) and restarting llama-swap
- Removing `/etc/sudoers.d/90-max-setup` is the last step of this session, after this record is committed and pushed
