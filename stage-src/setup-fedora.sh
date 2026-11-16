#!/usr/bin/env bash
set -euo pipefail

# EVO-X3 Staged Fedora Setup Script (Phase A1 — Plan rev 8 + Brief rev 5)
# Implements units U5-U8, U10, U12, U14, U17, U18 (loopback), and helpers for U13/U19.
# NOT YET RUN ON THE EVO — run on Fedora 44 Server ONLY after U4b passes.

STAGE_DIR="${STAGE_DIR:-/opt/evo-x3/stage}"
RECORDS_DIR="${RECORDS_DIR:-/opt/evo-x3/records}"
SVC_USER="${SVC_USER:-evo}"
SANDBOX_USER="${SANDBOX_USER:-evosandbox}"

log_ct() {
  printf '[%s] %s\n' "$(TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z')" "$*"
}

require_root() {
  if [[ "$EUID" -ne 0 ]]; then
    echo "ERROR: Run as root (sudo)." >&2
    exit 1
  fi
}

cmd_u5() {
  require_root
  log_ct "U5: Configuring ttm pages_limit=31457280 (120 GiB) and Podman..."
  install -m 0644 "${STAGE_DIR}/config/modprobe.d/ttm.conf" /etc/modprobe.d/ttm.conf
  dnf install -y podman skopeo snapper python3 jq curl
  if ! id "$SVC_USER" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "$SVC_USER"
  fi
  usermod -aG video,render "$SVC_USER"
  dracut --force
  log_ct "U5 installed. Reboot now, then verify:"
  log_ct "  Pass: cat /sys/module/ttm/parameters/pages_limit == 31457280"
  log_ct "  Pass: mem_info_gtt_total ≈ 120 GiB; ls -l /dev/kfd /dev/dri/renderD*"
}

cmd_u6_pin_help() {
  log_ct "U6: Pin live container digests before starting quadlets or llama-swap:"
  log_ct "  podman pull ghcr.io/gufo-org/toolboxes/gufo-runtime:latest"
  log_ct "  podman pull docker.io/kyuz0/amd-strix-halo-toolboxes:vulkan-radv"
  log_ct "  podman pull docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-10.0-strix-llama"
  log_ct "  podman inspect --format '{{index .RepoDigests 0}}' <image>"
  log_ct "  Update PIN_DIGEST_AT_BUILD_TIME in /etc/evo-x3/llama-swap.yaml and /etc/containers/systemd/*.container"
  log_ct "  Pass: engine log shows gfx1151 (not CPU); Flash-Next at 32K >= 35 tok/s decode & >= 800 prefill;"
  log_ct "  Pass: 4-arm bake-off (Gufo vs Halogen vs Strata vs rocm-10.0-strix-llama) + cold TTFT + 27B DFlash2 pair + Heretic tok/s recorded."
}

cmd_u7() {
  require_root
  log_ct "U7: Installing llama-swap config (no single default model) and systemd unit..."
  mkdir -p /etc/evo-x3
  chmod 0755 /etc/evo-x3
  if [[ ! -f /etc/evo-x3/llm.env ]]; then
    echo "STOP: /etc/evo-x3/llm.env missing. Derrick must create it (chmod 0600) with Vaultwarden keys before starting llama-swap." >&2
    exit 1
  fi
  chmod 0600 /etc/evo-x3/llm.env
  chown root:root /etc/evo-x3/llm.env

  cp "${STAGE_DIR}/config/llama-swap/config.yaml" /etc/evo-x3/llama-swap.yaml
  chmod 0644 /etc/evo-x3/llama-swap.yaml
  if grep -q "PIN_DIGEST_AT_BUILD_TIME" /etc/evo-x3/llama-swap.yaml; then
    echo "ERROR: Replace PIN_DIGEST_AT_BUILD_TIME in /etc/evo-x3/llama-swap.yaml with verified image digests first." >&2
    exit 1
  fi

  install -m 0644 "${STAGE_DIR}/config/systemd/llama-swap.service" /etc/systemd/system/llama-swap.service
  systemctl daemon-reload
  systemctl enable --now llama-swap.service
  log_ct "U7 Pass checks: ss -ltnp shows 127.0.0.1:8080 & 127.0.0.1:8081 only; no-key curl returns 401; named flash-next and gemma4-heretic respond."
}

cmd_u8() {
  require_root
  if [[ "${1:-}" != "--confirm-acl-card" ]]; then
    echo "HARD STOP (ACL GATE): Do not publish U8 until Derrick approves the Tailscale ACL preview card." >&2
    echo "Run with --confirm-acl-card only after Derrick's yes card is on file." >&2
    exit 1
  fi
  log_ct "U8: Configuring Tailscale Serve (443 -> http://127.0.0.1:8080, Funnel OFF) and closing LAN SSH..."
  tailscale serve --bg 443 http://127.0.0.1:8080
  tailscale funnel status || true
  firewall-cmd --permanent --remove-service=ssh || true
  firewall-cmd --reload
  log_ct "U8 Pass checks: LAN curl :8080/:8081 refused; tailnet no-key=401; with-key works; funnel empty; LAN SSH refused."
}

cmd_u10_keys_check() {
  require_root
  log_ct "U10 (keys): Checking 0600 EnvironmentFiles before U17/U18..."
  for f in /etc/evo-x3/llm.env /etc/evo-x3/mcp.env /etc/evo-x3/sandbox.env; do
    if [[ ! -f "$f" ]]; then
      echo "MISSING: $f (Derrick must populate from Vaultwarden, chmod 0600 root:root)" >&2
      exit 1
    fi
    chmod 0600 "$f"
    chown root:root "$f"
  done
  log_ct "U10 keys verified (0600 root:root)."
}

cmd_u14() {
  require_root
  log_ct "U14: Enabling per-key rate-limiter & CT logger proxy (127.0.0.1:8080 -> llama-swap 127.0.0.1:8082)..."
  mkdir -p /etc/systemd/system/llama-swap.service.d
  cat > /etc/systemd/system/llama-swap.service.d/u14-port.conf <<'EOF'
[Service]
Environment=LISTEN_ADDR=127.0.0.1:8082
EOF
  install -m 0644 "${STAGE_DIR}/config/systemd/evo-rate-proxy.service" /etc/systemd/system/evo-rate-proxy.service
  systemctl daemon-reload
  systemctl restart llama-swap.service
  systemctl enable --now evo-rate-proxy.service
  log_ct "U14 Pass checks: Hermes burst gets 429/queued while pi succeeds; journalctl -u evo-rate-proxy shows key_id + CT time + tok/s with zero prompt strings."
}

cmd_u17() {
  require_root
  log_ct "U17: Setting up dedicated unprivileged sandbox user '$SANDBOX_USER' & rootless Podman wrapper..."
  if ! id "$SANDBOX_USER" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "$SANDBOX_USER"
  fi
  mkdir -p /var/lib/evosandbox/scratch/incoming
  chown -R "${SANDBOX_USER}:${SANDBOX_USER}" /var/lib/evosandbox
  chmod 0700 /var/lib/evosandbox /var/lib/evosandbox/scratch
  install -m 0755 "${STAGE_DIR}/config/sandbox/evo-sandbox-run.sh" /usr/local/bin/evo-sandbox-run
  log_ct "U17 configured. Verify '$SANDBOX_USER' CANNOT read /etc/evo-x3/* or /srv/models, and sandbox container has --network=none."
}

cmd_u18() {
  require_root
  log_ct "U18: Setting up hardened Playwright MCP (LOOPBACK ONLY until TOOLS PORT gate card)..."
  bash "${STAGE_DIR}/config/playwright/playwright-egress-firewall.sh"
  install -m 0644 "${STAGE_DIR}/config/playwright/playwright-mcp.container" /etc/containers/systemd/playwright-mcp.container
  install -m 0644 "${STAGE_DIR}/config/systemd/evo-mcp-proxy.service" /etc/systemd/system/evo-mcp-proxy.service
  systemctl daemon-reload
  systemctl enable --now playwright-mcp.service evo-mcp-proxy.service
  log_ct "U18 active on 127.0.0.1:8930 (auth proxy) -> 127.0.0.1:8931 (MCP). Do NOT expose via Tailscale Serve until TOOLS PORT card is approved."
}

cmd_u13() {
  require_root
  log_ct "U13: Deploying llama-swap config with persistent small embedding group..."
  cp "${STAGE_DIR}/config/llama-swap/config-u13-with-small-group.yaml" /etc/evo-x3/llama-swap.yaml
  chmod 0644 /etc/evo-x3/llama-swap.yaml
  systemctl restart llama-swap.service
  log_ct "U13 Pass check: /v1/embeddings returns vector while flash-next stays loaded."
}

case "${1:-help}" in
  u5) cmd_u5 ;;
  u6-help) cmd_u6_pin_help ;;
  u7) cmd_u7 ;;
  u8) shift; cmd_u8 "$@" ;;
  u10-keys) cmd_u10_keys_check ;;
  u14) cmd_u14 ;;
  u17) cmd_u17 ;;
  u18) cmd_u18 ;;
  u13) cmd_u13 ;;
  *)
    cat <<EOF
Usage: sudo $0 <command>
Commands (run strictly in plan order):
  u5         Configure ttm pages_limit=31457280, install podman, add user to video/render
  u6-help    Show container digest pinning & U6 4-arm bake-off reminders
  u7         Deploy llama-swap (127.0.0.1:8080, no single default model)
  u8         Enable Tailscale Serve 443 & close LAN SSH (requires --confirm-acl-card)
  u10-keys   Verify 0600 permissions on /etc/evo-x3/{llm,mcp,sandbox}.env
  u14        Enable U14 per-key rate-limiter & CT logger proxy
  u17        Create evosandbox user & rootless Podman fixed-flag wrapper
  u18        Deploy Playwright MCP egress firewall & loopback-only bearer proxy
  u13        Deploy U13 small persistent embedding group (after day-1 setup is live)
EOF
    ;;
esac
