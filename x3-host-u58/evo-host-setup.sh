#!/usr/bin/env bash
# EVO-X3 overnight host setup (packages, kernel args, llama-swap, boot order).
# Does NOT download models (that's download-models.sh) and does NOT reboot.
set -euo pipefail
LOG="${HOME}/evo-x3/overnight-20261114.md"
STAGE_SRC="${HOME}/evo-x3/stage-src"
DEST_STAGE="/opt/evo-x3/stage"
DEST_RECORDS="/opt/evo-x3/records"
SVC_USER="evo"

progress() {
  local msg="$1"
  local ts
  ts="$(TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "[$ts] $msg"
  python3 - "$ts" "$msg" "$LOG" <<'PY'
import sys
from pathlib import Path
ts, msg, logp = sys.argv[1], sys.argv[2], sys.argv[3]
p = Path(logp)
text = p.read_text() if p.exists() else ""
line = f"PROGRESS: {ts} | IN PROGRESS | {msg}"
lines = [l for l in text.splitlines() if not l.startswith("PROGRESS:")]
if lines and lines[0].startswith("# "):
    out = [lines[0], "", line, ""] + lines[1:]
else:
    out = [line, ""] + lines
p.write_text("\n".join(out) + "\n")
PY
}

append_log() {
  printf '\n%s\n' "$1" >> "$LOG"
}

progress "HOST SETUP start: packages, kernel args, llama-swap, boot order"

# --- packages (safe if dnf upgrade already installed them) ---
progress "Installing remaining packages (podman toolbox distrobox firmware helpers)"
sudo dnf -y install linux-firmware amd-gpu-firmware podman toolbox distrobox skopeo snapper python3-dnf-plugin-versionlock python3 jq curl grubby efibootmgr

append_log "$(cat <<EOF
## 2. Packages
\`\`\`
$(rpm -q linux-firmware amd-gpu-firmware kernel kernel-core podman toolbox distrobox skopeo snapper python3-dnf-plugin-versionlock 2>&1)
$(uname -r)
\`\`\`
EOF
)"

# Versionlock kernel* and linux-firmware after a successful upgrade (plan KTD7)
if rpm -q python3-dnf-plugin-versionlock >/dev/null; then
  sudo dnf versionlock delete 'kernel*' linux-firmware >/dev/null 2>&1 || true
  sudo dnf versionlock add 'kernel*' linux-firmware amd-gpu-firmware || true
  append_log "$(cat <<EOF

versionlock:
\`\`\`
$(sudo dnf versionlock list 2>&1 || true)
\`\`\`
EOF
)"
fi

# --- users / groups / dirs ---
progress "Creating service user, GPU groups, /opt/evo-x3 and /srv/models"
if ! id "$SVC_USER" >/dev/null 2>&1; then
  sudo useradd -m -s /bin/bash "$SVC_USER"
fi
sudo usermod -aG video,render "$SVC_USER"
sudo usermod -aG video,render derekboone
sudo mkdir -p "$DEST_STAGE" "$DEST_RECORDS" /srv/models /etc/evo-x3
if [[ -d "$STAGE_SRC" ]]; then
  sudo rsync -a --delete "$STAGE_SRC"/ "$DEST_STAGE"/ || sudo cp -a "$STAGE_SRC"/. "$DEST_STAGE"/
fi
sudo chmod +x "$DEST_STAGE"/setup-fedora.sh "$DEST_STAGE"/fedora-bootstrap.sh \
  "$DEST_STAGE"/models/verify-models-sha256.sh 2>/dev/null || true
# Keep models writable by derekboone for the download script
sudo chown -R derekboone:derekboone /srv/models
# Rootless podman lingering
sudo loginctl enable-linger derekboone || true

# --- U5 kernel GPU memory: plan 120 GiB, IOMMU stays ON ---
# Community (strix-halo-toolboxes.com, opened 2026-11-14 CT) uses
#   amd_iommu=off amdgpu.gttsize=126976 ttm.pages_limit=32505856 (124 GiB)
# We adapt: no amd_iommu=off (plan Q10 / parent), 120 GiB caps (KTD2):
#   amdgpu.gttsize=122880  (120 GiB in MiB)
#   ttm.pages_limit=31457280  (120 GiB in 4 KiB pages)
progress "Applying ttm.conf + grubby kernel args (120 GiB GTT, IOMMU on)"
sudo tee /etc/modprobe.d/ttm.conf >/dev/null <<'EOF'
# EVO-X3 Kernel GPU Memory Configuration (Plan KTD2 / U5)
# 31457280 pages * 4 KiB = 120 GiB GTT/VRAM pool for Strix Halo (BIOS UMA = 512 MB).
# Step up to 32505856 (124 GiB) only on an allocation failure.
# amdgpu.gttsize is set via grubby as well (kyuz0/community still ships it; values kept in sync).
# IOMMU stays on (do NOT set amd_iommu=off).
options ttm pages_limit=31457280
EOF
sudo chmod 0644 /etc/modprobe.d/ttm.conf

# Persist in /etc/default/grub for future kernels, without removing existing args
if [[ -f /etc/default/grub ]]; then
  sudo cp -a /etc/default/grub /etc/default/grub.bak-overnight-20261114
  python3 - <<'PY'
from pathlib import Path
p = Path("/etc/default/grub")
text = p.read_text()
need = ["amdgpu.gttsize=122880", "ttm.pages_limit=31457280"]
# Refuse to add amd_iommu=off; if present, leave it (we won't add it).
lines = []
for line in text.splitlines():
    if line.startswith("GRUB_CMDLINE_LINUX=") and not line.startswith("GRUB_CMDLINE_LINUX_DEFAULT"):
        # extract quoted value
        if '"' in line:
            pre, rest = line.split('"', 1)
            val, post = rest.rsplit('"', 1)
            parts = val.split()
            for n in need:
                key = n.split("=",1)[0]
                parts = [x for x in parts if not x.startswith(key+"=")]
                parts.append(n)
            line = pre + '"' + " ".join(parts) + '"' + post
    lines.append(line)
Path("/tmp/grub.default.new").write_text("\n".join(lines) + "\n")
PY
  sudo cp /tmp/grub.default.new /etc/default/grub
fi

# Fedora official method: grubby
sudo grubby --update-kernel=ALL --args="amdgpu.gttsize=122880 ttm.pages_limit=31457280"
# Make sure we did not add amd_iommu=off
if sudo grubby --info=ALL | grep -q 'amd_iommu=off'; then
  echo "WARNING: amd_iommu=off is present in a kernel entry; leaving it only if it was pre-existing. Not adding it."
fi
sudo dracut --force
append_log "$(cat <<EOF
## 3. Kernel args (U5)
IOMMU left on. Applied via grubby --update-kernel=ALL and /etc/modprobe.d/ttm.conf + dracut --force.
Target: amdgpu.gttsize=122880 ttm.pages_limit=31457280 (120 GiB). Will take effect after reboot.
\`\`\`
$(cat /etc/default/grub)
$(sudo grubby --info=DEFAULT)
$(cat /etc/modprobe.d/ttm.conf)
\`\`\`
EOF
)"

# --- llama-swap v272 ---
progress "Installing llama-swap v272 (official GitHub release, checksum verified)"
TARBALL="${HOME}/evo-x3/llama-swap_272_linux_amd64.tar.gz"
if [[ ! -f "$TARBALL" ]]; then
  curl -fL -o "$TARBALL" https://github.com/mostlygeek/llama-swap/releases/download/v272/llama-swap_272_linux_amd64.tar.gz
fi
echo "3f21b4c13f55ea5576badcd6cc1d114ccdcf74a5d56346d3ac1e777d28e0fdf1  $TARBALL" | sha256sum -c
tmpdir=$(mktemp -d)
tar -xzf "$TARBALL" -C "$tmpdir" llama-swap
sudo install -m 0755 "$tmpdir/llama-swap" /usr/local/bin/llama-swap
rm -rf "$tmpdir"
/usr/local/bin/llama-swap --version || /usr/local/bin/llama-swap -version || true
append_log "$(cat <<EOF
## 4. llama-swap
Installed official v272 linux_amd64 (sha256 3f21b4c13f55ea5576badcd6cc1d114ccdcf74a5d56346d3ac1e777d28e0fdf1) to /usr/local/bin/llama-swap.
\`\`\`
$(/usr/local/bin/llama-swap --version 2>&1 || true)
\`\`\`
EOF
)"

# --- placeholder env (NO generated keys) ---
progress "Writing placeholder /etc/evo-x3/llm.env (no secrets) and llama-swap unit"
if [[ ! -f /etc/evo-x3/llm.env ]]; then
  sudo tee /etc/evo-x3/llm.env >/dev/null <<'EOF'
# Placeholder only. Derrick types each value from Vaultwarden.
# Do not put real keys in this file until Derrick pastes them locally.
# Empty values are not usable credentials.
LLM_KEY_ALIENPC=
LLM_KEY_PI=
LLM_KEY_BOX=
LLM_KEY_HERMES=
LLM_KEY_DERRICK_LAPTOP=
EOF
fi
sudo chmod 0600 /etc/evo-x3/llm.env
sudo chown root:root /etc/evo-x3/llm.env

# llama-swap yaml is written later after image digests are known, or a stub now.
# Install unit now; enable after yaml has real digests.
sudo install -m 0644 "${DEST_STAGE}/config/systemd/llama-swap.service" /etc/systemd/system/llama-swap.service
sudo systemctl daemon-reload

# --- boot order: Fedora first, then Windows, then the BACKUP_OS UEFI OS entry ---
# Do not delete or rewrite Windows/BACKUP_OS partitions or files.
progress "Setting firmware boot order with efibootmgr (Fedora first)"
BEFORE=$(sudo efibootmgr)
sudo efibootmgr -o 0003,0000,0001
AFTER=$(sudo efibootmgr)
append_log "$(cat <<EOF
## 5. Firmware boot order
Set \`efibootmgr -o 0003,0000,0001\` (Fedora, Windows Boot Manager, UEFI OS on BACKUP_OS). Did not touch partition contents. Firmware previously reset an order change from Windows; re-check after the upcoming reboot.
\`\`\`
BEFORE:
${BEFORE}

AFTER:
${AFTER}
\`\`\`
EOF
)"

progress "HOST SETUP commands finished (reboot still pending; image pulls may still be needed)"
echo HOST_SETUP_DONE
