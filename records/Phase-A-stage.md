# Phase A Stage Verification Record (A1, A2, A3, A4)

- **Recorded:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` sync)
- **Status:**
  - **A1 (Runbook & setup script):** `DONE`
  - **A2 (Config templates, zero secrets):** `DONE`
  - **A3 (Model downloads to QNAP):** `DEFERRED` (Household QNAP share name and free space are `NO_DATA`; full download list & SHA-256 verification helper staged in [RUNBOOK.md](file:///C:/evo-x3/stage/RUNBOOK.md) and [MANIFEST.md](file:///C:/evo-x3/stage/models/MANIFEST.md))
  - **A4 (Explicit untested gate list):** `DONE`
  - **Step 5 (`fedora-bootstrap.sh`):** `DONE`

## Staged Files Inventory (`C:\evo-x3\stage\`)
- [README.md](file:///C:/evo-x3/stage/README.md) — Phase A4 declaration ("not yet run on the EVO"), untested GPU/Linux gates, and Phase B hard gates
- [RUNBOOK.md](file:///C:/evo-x3/stage/RUNBOOK.md) — Complete U1–U20 build runbook quoting all plan pass tests + A3 deferred model list + U4b recovery
- [setup-fedora.sh](file:///C:/evo-x3/stage/setup-fedora.sh) — Staged bash implementation of U5–U8, U10, U13, U14, U17, U18
- [fedora-bootstrap.sh](file:///C:/evo-x3/stage/fedora-bootstrap.sh) — First-boot Fedora 44 script installing `agy`, copying stage tree, verifying U3/U4/U4b prereqs, and listing U5–U20 next units
- [run-elevated-prep.ps1](file:///C:/evo-x3/stage/run-elevated-prep.ps1) — Consolidated Administrator PowerShell script for remaining Windows prep
- [compose-reference.yml](file:///C:/evo-x3/stage/compose-reference.yml) — Documentation-only compose equivalent (live units are Podman quadlets)
- [ttm.conf](file:///C:/evo-x3/stage/config/modprobe.d/ttm.conf) — `options ttm pages_limit=31457280`
- Quadlets in `config/quadlets/`: [gufo.container](file:///C:/evo-x3/stage/config/quadlets/gufo.container), [halogen-bakeoff.container](file:///C:/evo-x3/stage/config/quadlets/halogen-bakeoff.container), [strata-bakeoff.container](file:///C:/evo-x3/stage/config/quadlets/strata-bakeoff.container), [kyuz0-strix-llama-bakeoff.container](file:///C:/evo-x3/stage/config/quadlets/kyuz0-strix-llama-bakeoff.container), [kyuz0-vulkan-fallback.container](file:///C:/evo-x3/stage/config/quadlets/kyuz0-vulkan-fallback.container)
- llama-swap configs in `config/llama-swap/`: [config.yaml](file:///C:/evo-x3/stage/config/llama-swap/config.yaml) (no single default; callers pick `flash-next`, `gemma4-heretic`, or `qwen27b` by name), [config-u13-with-small-group.yaml](file:///C:/evo-x3/stage/config/llama-swap/config-u13-with-small-group.yaml)
- Systemd units in `config/systemd/`: [llama-swap.service](file:///C:/evo-x3/stage/config/systemd/llama-swap.service), [evo-rate-proxy.service](file:///C:/evo-x3/stage/config/systemd/evo-rate-proxy.service), [evo-mcp-proxy.service](file:///C:/evo-x3/stage/config/systemd/evo-mcp-proxy.service)
- Loopback proxies in `config/proxy/`: [evo-rate-proxy.py](file:///C:/evo-x3/stage/config/proxy/evo-rate-proxy.py), [evo-mcp-proxy.py](file:///C:/evo-x3/stage/config/proxy/evo-mcp-proxy.py)
- Sandbox & Browser hardening: [evo-sandbox-run.sh](file:///C:/evo-x3/stage/config/sandbox/evo-sandbox-run.sh), [playwright-mcp.container](file:///C:/evo-x3/stage/config/playwright/playwright-mcp.container), [playwright-egress-firewall.sh](file:///C:/evo-x3/stage/config/playwright/playwright-egress-firewall.sh)
- Fixtures & Models: [u12-tool-call-fixture.json](file:///C:/evo-x3/stage/fixtures/u12-tool-call-fixture.json), [u12-cold-ttft-prompt.py](file:///C:/evo-x3/stage/fixtures/u12-cold-ttft-prompt.py), [u9b-planted-prompt-injection-test.md](file:///C:/evo-x3/stage/fixtures/u9b-planted-prompt-injection-test.md), [MANIFEST.md](file:///C:/evo-x3/stage/models/MANIFEST.md), [verify-models-sha256.sh](file:///C:/evo-x3/stage/models/verify-models-sha256.sh)
- Lease copy: [evo-x3-lease.md](file:///C:/evo-x3/stage/30_handoff/status/evo-x3-lease.md)

## Pass Checks
- **A1:** `setup-fedora.sh` and `RUNBOOK.md` cover U5–U8 in order, quote plan pass tests, and use Podman + quadlets/systemd (`compose-reference.yml` is documentation only).
- **A2:** `llama-swap/config.yaml` defines `flash-next`, `gemma4-heretic`, and `qwen27b` with no single default model, binds `127.0.0.1:8080`, uses `${env.LLM_KEY_*}` placeholders only, and contains `captureBuffer: 0`. Secret scan (`gitleaks` + dry grep) recorded in [secret-scan.md](file:///C:/evo-x3/records/secret-scan.md).
- **A3:** Explicitly deferred waiting on Household QNAP SMB share and space confirmation.
- **A4:** `stage/README.md` explicitly states `"not yet run on the EVO"` and enumerates all untested Phase B GPU/Linux gates.
