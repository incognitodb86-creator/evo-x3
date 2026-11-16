#!/usr/bin/env bash
set -euo pipefail

# EVO-X3 First-Boot Fedora 44 Bootstrap (Orchestrator Step 5)
# Run on Fedora 44 Server after U4/U4b dual-boot installation succeeds.
#
# Responsibilities:
#   1. Install Antigravity CLI (`agy`) using official installer
#   2. Copy the staged tree from mounted Windows / USB / QNAP path to /opt/evo-x3/stage
#   3. Run read-only U3/U4/U4b sanity checks (kernel >= 6.18.4, linux-firmware >= 20260110, MES != 0x83,
#      mem_info_vram_total ~0.5 GiB, mokutil --sb-state, timedatectl UTC, lsblk -f)
#   4. Print the exact remaining plan units (U5 onward incl. U6 bake-off, U7, U9-U20) for the next
#      Orchestrator run on Fedora to continue from here.

SRC_STAGE="${1:-$(cd "$(dirname "$0")" && pwd)}"
DEST_BASE="/opt/evo-x3"
DEST_STAGE="${DEST_BASE}/stage"
DEST_RECORDS="${DEST_BASE}/records"

echo "=== [1/4] Installing Antigravity CLI (agy) ==="
curl -fsSL https://antigravity.google/cli/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
command -v agy || echo "NOTE: Verify agy location in your PATH after shell reload."

echo "=== [2/4] Copying stage tree to ${DEST_STAGE} ==="
sudo mkdir -p "$DEST_STAGE" "$DEST_RECORDS" /srv/models
sudo cp -a "${SRC_STAGE}/." "$DEST_STAGE/"
sudo chmod +x "${DEST_STAGE}/setup-fedora.sh" \
              "${DEST_STAGE}/fedora-bootstrap.sh" \
              "${DEST_STAGE}/config/sandbox/evo-sandbox-run.sh" \
              "${DEST_STAGE}/config/playwright/playwright-egress-firewall.sh" \
              "${DEST_STAGE}/models/verify-models-sha256.sh"

echo "=== [3/4] Checking U3 / U4 / U4b Prerequisites ==="
echo "Kernel: $(uname -r) (plan requires >= 6.18.4)"
rpm -q linux-firmware || true
echo "Systemd default target: $(systemctl get-default) (expect multi-user.target)"
mokutil --sb-state || true
timedatectl status || true
lsblk -f
echo "--- VRAM check (expect ~0.5 GiB = 536870912 bytes when UMA=512MB) ---"
cat /sys/class/drm/card*/device/mem_info_vram_total 2>/dev/null || echo "mem_info_vram_total not readable yet"
echo "--- MES firmware check (must NOT be 0x83) ---"
sudo grep -i mes /sys/kernel/debug/dri/*/amdgpu_firmware_info 2>/dev/null || echo "amdgpu_firmware_info not readable (check with root)"
echo "--- Versionlock check (pin kernel* and linux-firmware in U4) ---"
dnf versionlock list 2>/dev/null || echo "Install python3-dnf-plugin-versionlock and run: sudo dnf versionlock add 'kernel*' linux-firmware"

echo "=== [4/4] Next Plan Units to Execute via Fedora Orchestrator ==="
cat <<'EOF'

Run the remaining plan units in strict order (recording pass tests with America/Chicago times in /opt/evo-x3/records/):

  [U5]  GPU memory + devices:
        - sudo /opt/evo-x3/stage/setup-fedora.sh u5  (ttm pages_limit=31457280, podman, video/render groups)
        - Reboot & verify /sys/module/ttm/parameters/pages_limit == 31457280, mem_info_gtt_total ~120 GiB, /dev/kfd, /dev/dri/renderD*
  [A3/B5] Model staging to /srv/models:
        - Pull Qwen3.8-Flash-Next UD-Q4_K_XL (111.3 GB) + shared Q8 MTP (2.79 GB), Gemma 4 26B A4B Heretic, and Qwen3.8-27B UD-Q4_K_XL (17.6 GB)
        - Verify SHA-256 checksums via /opt/evo-x3/stage/models/verify-models-sha256.sh
  [U6]  Engine + 4-Arm Bake-off:
        - Pin container digests in /opt/evo-x3/stage/config/quadlets/*.container & llama-swap yaml
        - Test Gufo (Q3=A pick) vs Halogen vs Strata vs 4th arm kyuz0 rocm-10.0-strix-llama (NOT a default; do NOT run pwilkin installer)
        - Record engine-logged prefill/decode tok/s, cold TTFT (U12 Hermes-sized fixture, no warmup), tool-call success, Heretic tok/s
        - Test kyuz0 vulkan-radv fallback (qwen27b, -fa 1 --load-mode none) and 27B long-context decode with & without DFlash2
  [U7]  llama-swap front door (127.0.0.1:8080, NO single default model; callers select by name):
        - Derrick creates /etc/evo-x3/llm.env (0600) from Vaultwarden; sudo /opt/evo-x3/stage/setup-fedora.sh u7
  [HARD STOP: ACL GATE] Obtain Derrick yes card for Tailscale ACL preview (443 to whole tailnet, admin :22, deny tests)
  [U8]  Tailscale Serve 443 -> 127.0.0.1:8080 (Funnel off) + close LAN SSH in firewalld:
        - Derrick types one-off pre-tagged tag:llm auth key (<= 1 h expiry), then sudo /opt/evo-x3/stage/setup-fedora.sh u8 --confirm-acl-card
  [U9]  Fleet wiring (Max Architect 3, under AlienPc lease, never during render): Forge/pi -> EVO flash-next; disable (not delete) AlienPc Strata entry
  [U9b] Hermes Agent personal client (client only, NO local llama.cpp) -> EVO Serve URL + LLM_KEY_HERMES; planted "run this" test
  [U10] Keys first: create root-only 0600 /etc/evo-x3/mcp.env and sandbox.env before U17/U18
  [U12] Agent serving profile: tool-call fixture (structured tool_calls), parallel=2, q8_0 KV, --no-slots/401, cold Hermes TTFT fixture
  [U19] Day-1 A/B (defaults unchanged): IOMMU on vs amd_iommu=off (NPU/USB4 check) & Balanced 85 W vs 140 W on U12 fixture + temp/noise; restore defaults
  [U14] Fair share & logging: sudo /opt/evo-x3/stage/setup-fedora.sh u14 (per-key rate limiter, captureBuffer: 0, key_id+CT log, zero prompt leaks)
  [U16] Hermes -> QNAP SearXNG (port 8888; waits until QNAP Docker is back; verify planted "run this" test still holds)
  [U17] Rootless Podman code sandbox: sudo /opt/evo-x3/stage/setup-fedora.sh u17 (dedicated user evosandbox, --network=none, fixed-flag wrapper)
  [U18] Playwright MCP (loopback only): sudo /opt/evo-x3/stage/setup-fedora.sh u18 (isolated profile, egress nftables drop RFC1918/tailnet/host)
  [HARD STOP: TOOLS PORT GATE] Keep U18 on 127.0.0.1 until Derrick approves tools-port card with named callers
  [U10] Rest: gitleaks dir --redact clean, snapper pre-update snapshot workflow, check-push to Gitea
  [U11] Close: Alfred roster row (on Derrick yes), release EVO-X3 lease, record DONE/MISSING/UNVERIFIED
  [U13] After day-1 setup is live: sudo /opt/evo-x3/stage/setup-fedora.sh u13 (persistent small embedding group beside flash-next)
  [U15] Day-2: GLM-5.3-Flash bake-off vs Flash-Next (128 GB fit check + U12 fixture; default unchanged without Derrick yes)
  [U20] Day-2: Gemma 4 26B A4B Heretic on PolyStrata strata-poly vs kyuz0 llama.cpp + Prompt maker spot check (engine unchanged without Derrick yes)

EOF
echo "Bootstrap finished. Next: run the next Orchestrator session in Fedora pointing at /opt/evo-x3/stage/RUNBOOK.md."
