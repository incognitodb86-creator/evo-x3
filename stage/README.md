# EVO-X3 Fedora 44 Staged Setup Tree (Phase A)

> **STATUS: NOT YET RUN ON THE EVO.**
> Everything in `C:\evo-x3\stage\` was staged on the Windows side before Linux installation. No Linux kernel, ROCm, Vulkan, or GPU workload has been executed or benchmarked in this tree.

## What Must NOT Be Claimed as Tested Yet (Phase A4)
The following items are **Phase B gates** that require booting Fedora 44 Server on the physical GMKtec EVO-X3 hardware (`gfx1151`, `/dev/kfd`, `/dev/dri`):
- **Engines & toolboxes:** `Gufo`, `Halogen`, `Strata`, `kyuz0/amd-strix-halo-toolboxes:rocm-10.0-strix-llama`, `kyuz0/amd-strix-halo-toolboxes:vulkan-radv`, `PolyStrata` (`strata-poly`).
- **GPU runtime & metrics:** ROCm, Vulkan RADV, `gfx1151` log confirmation, `ttm.pages_limit` sysfs (`mem_info_gtt_total` ≈ 120 GiB), prefill/decode `tok/s`, cold TTFT on the U12 Hermes-sized fixture, DFlash2 long-context 27B decode pair, and `Gemma 4 26B A4B Heretic` on-disk size / `tok/s`.
- **Hardware & A/B knobs:** IOMMU on vs `amd_iommu=off` (NPU / USB4 dock behavior), BIOS power mode Balanced 85 W vs 140 W (temperatures & noise), and exact BIOS menu labels for UMA 512 MB / IOMMU / Balanced 85 W on `EVO-X3_V1.01`.
- **Container digests:** All container image references use `PIN_DIGEST_AT_BUILD_TIME` placeholders until pulled and inspected live on Fedora.

## Phase B Hard Gates (Require Explicit Derrick Yes / Action)
1. **BitLocker & Vaultwarden check (U1/U2/U2b):** Never decrypt or modify partitions if BitLocker is enabled until Derrick confirms the recovery key is saved in Vaultwarden.
2. **RESIZE GATE (after U2b shrink, before U4 Fedora install):** Requires Derrick's explicit `yes` card showing U2 Clonezilla checksum + restore verification result, tested recovery USB, BitLocker off, planned disk layout, and acknowledgment that bots have no AI server while booted into Windows.
3. **ACL / REMOTE-ACCESS GATE (before U8 Tailscale Serve publish):** Requires Derrick's explicit `yes` card with Tailscale ACL Preview result (`tagOwners`, `autogroup:member` + named machine tags on `tcp:443`, admin-only `:22`), one-off pre-tagged `tag:llm` auth key (≤ 1 h expiry) typed by Derrick, and API keys typed by Derrick from Vaultwarden.
4. **TOOLS PORT GATE (before U18 Playwright MCP leaves loopback):** U18 stays bound to `127.0.0.1` until Derrick approves a separate card naming the Serve port, Serve name, and **named callers** (whole-tailnet does NOT apply to tools).
5. **Post-bake-off default gates (U15, U19, U20):** Do not change Flash-Next routing, Gemma Heretic engine, Balanced 85 W, or IOMMU On defaults without a subsequent `yes` card from Derrick.

## Directory Layout
- `fedora-bootstrap.sh` — First-boot Fedora 44 script: installs `agy`, copies stage files, verifies U3/U4/U4b prereqs, and prints next Orchestrator units (`U5`–`U20`).
- `setup-fedora.sh` — Idempotent staged implementation of `U5`–`U8`, `U10` config/hardening, `U12`, `U14`, `U17`, `U18` (loopback), `U19`, and helper targets.
- `RUNBOOK.md` — Full unit-by-unit build & verification runbook (quoting Plan rev 8 + Brief rev 5 pass tests) and A3 deferred model download list.
- `config/modprobe.d/ttm.conf` — `options ttm pages_limit=31457280` (120 GiB).
- `config/quadlets/` — Rootless/systemd Podman quadlet templates for Gufo, bake-off arms (Halogen, Strata, `kyuz0 rocm-10.0-strix-llama`), and Vulkan RADV fallback.
- `config/llama-swap/` — Loopback-only `llama-swap` configs (`config.yaml` for day-1 with **no single default model**, and `config-u13-with-small-group.yaml` for U13).
- `config/proxy/` — `evo-rate-proxy.py` (U14 per-key limiter, `/slots` lockdown, zero-prompt CT logging) and `evo-mcp-proxy.py` (U18 `MCP_KEY_*` bearer proxy).
- `config/sandbox/` — U17 fixed-flag rootless Podman wrapper (`evo-sandbox-run.sh`).
- `config/playwright/` — U18 hardened Playwright MCP quadlet + podman egress firewall script.
- `config/systemd/` — systemd units for `llama-swap`, `evo-rate-proxy`, and `evo-mcp-proxy`.
- `fixtures/` — U12 structured tool-call fixture, U12 cold TTFT prompt generator, and U9b planted prompt-injection verification case.
- `models/` — A3 deferred model download manifest and SHA-256 verification helper.
- `run-elevated-prep.ps1` — Consolidated Windows Administrator PowerShell script for remaining Windows prep (`w32time`, Tailscale/Git installs, full `pnputil` export, `U1` admin checks, `U2b` hibernation/UTC/WU settings).
