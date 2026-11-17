#!/bin/bash
# U34 final live backup of EVO-X3 to QNAP X3-drop. No weights (/srv), no container layers, no secrets.
set -uo pipefail
STAMP=$(date +%Y%m%d-%H%M)
DEST=/mnt/qnap/pi-drop/evo-x3-rollback/u34-final-$STAMP
LOCAL=/var/backups/evo-x3/u34-final-$STAMP
mkdir -p "$DEST" "$LOCAL"; chmod 700 "$LOCAL"
EX=(--exclude='./srv' --exclude='./tmp' --exclude='./var/tmp' --exclude='./proc' --exclude='./sys' --exclude='./dev' --exclude='./run' --exclude='./mnt' --exclude='./media'
 --exclude='./var/lib/containers/storage/overlay*' --exclude='./home/*/.local/share/containers/storage/overlay*'
 --exclude='./home/*/.cache' --exclude='./home/*/.npm' --exclude='./home/*/rocm' --exclude='./lost+found' --exclude='./boot/efi' --exclude='./var/backups'
 --exclude='*.gguf' --exclude='*.hgn' --exclude='*.safetensors' --exclude='./swapfile'
 --exclude='./etc/.git' --exclude='./etc/evo-x3/*.env' --exclude='./etc/evo-x3/*.cred' --exclude='./etc/shadow' --exclude='./etc/shadow-' --exclude='./etc/gshadow' --exclude='./etc/gshadow-'
 --exclude='./etc/ssh/*_key' --exclude='./etc/ssh/*_key.old' --exclude='./etc/NetworkManager/system-connections' --exclude='./etc/crypttab' --exclude='./etc/wpa_supplicant/wpa_supplicant.conf')
echo "start $(date)"
tar --anchored --zstd --acls --xattrs --numeric-owner --one-file-system -C / -cf "$LOCAL/rootfs.tar.zst" "${EX[@]}" . ./boot 2> "$LOCAL/tar.err"; echo "tar rc=$?"
podman volume export open-webui -o "$LOCAL/open-webui-volume.tar" 2>>"$LOCAL/tar.err"; echo "vol rc=$?"
rpm -qa | sort > "$LOCAL/rpm-qa.txt"; lsblk -f -o NAME,FSTYPE,SIZE,MOUNTPOINT > "$LOCAL/lsblk.txt"; findmnt > "$LOCAL/findmnt.txt"
if tar -tf "$LOCAL/rootfs.tar.zst" | grep -E '(^|/)(etc/evo-x3/[^/]+\.(env|cred)|etc/shadow-?$|etc/gshadow-?$|etc/ssh/[^/]+_key$|etc/\.git/)'; then echo "SECRET LEAK - aborting copy"; exit 1; fi
( cd "$LOCAL" && sha256sum * > SHA256SUMS ); chmod 600 "$LOCAL"/*
cp "$LOCAL"/* "$DEST"/; echo "cp rc=$?"
( cd "$DEST" && sha256sum -c SHA256SUMS ); echo "verify rc=$?"
du -sh "$DEST"; echo "done $(date)"
