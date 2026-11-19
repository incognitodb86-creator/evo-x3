#!/usr/bin/env bash
# Official Hugging Face downloads for EVO-X3 overnight bootstrap.
# Verifies each file against the SHA-256 in the HF git-lfs pointer.
set -euo pipefail
LOG="${HOME}/evo-x3/overnight-20261114.md"
STATUS="${HOME}/evo-x3/download-status.txt"
DEST_ROOT="/srv/models"
UA="evo-x3-overnight/2026-11-14"

progress() {
  local msg="$1"
  local ts
  ts="$(TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "$ts $msg" | tee -a "$STATUS"
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

# repo|remote_path|local_path|sha256|size_bytes
FILES=(
  "nomic-ai/nomic-embed-text-v1.5-GGUF|nomic-embed-text-v1.5.Q8_0.gguf|embed-small/nomic-embed-text-v1.5.Q8_0.gguf|3e24342164b3d94991ba9692fdc0dd08e3fd7362e0aacc396a9a5c54a544c3b7|146146432"
  "unsloth/Qwen3.8-27B-GGUF|Qwen3.8-27B-UD-Q4_K_XL.gguf|qwen27b/Qwen3.8-27B-UD-Q4_K_XL.gguf|2a5f3565f39cf885103da591182c1266da64745737b42b452fd3e675369f1211|17659407264"
  "mradermacher/gemma-4-26B-A4B-it-heretic-GGUF|gemma-4-26B-A4B-it-heretic.Q8_0.gguf|gemma4-heretic/gemma-4-26B-A4B-it-heretic.Q8_0.gguf|1f2e89b8382fd2182ef3a7e15a5cf272722f767a8a08a58dd69ae36c52edbf1c|26859855008"
  "unsloth/Qwen3.8-Flash-Next-GGUF|MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf|flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf|5ff54097406a905cf3a724c709124ceb0e3e10235ee862298969e91c96fa96e6|2786568256"
  "unsloth/Qwen3.8-Flash-Next-GGUF|UD-Q4_K_XL/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf|flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf|acc44040f74d0e55fb89c3967056cce5dbda1bcc52e909c3ba6fc72b5e9c0858|10946618"
  "unsloth/Qwen3.8-Flash-Next-GGUF|UD-Q4_K_XL/Qwen3.8-Flash-Next-UD-Q4_K_XL-00002-of-00004.gguf|flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00002-of-00004.gguf|45792ae869072d8229384c51c7c73dd959e191505252b41dd71852d9746f5ce4|49720539552"
  "unsloth/Qwen3.8-Flash-Next-GGUF|UD-Q4_K_XL/Qwen3.8-Flash-Next-UD-Q4_K_XL-00003-of-00004.gguf|flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00003-of-00004.gguf|8c76e79d444b16a663d9c8db54e585ed3b1da13eebd2619c37b0c355da803c82|32803030176"
  "unsloth/Qwen3.8-Flash-Next-GGUF|UD-Q4_K_XL/Qwen3.8-Flash-Next-UD-Q4_K_XL-00004-of-00004.gguf|flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00004-of-00004.gguf|5de8b5dbf89409acc39468decafd4a4a95b13c29d88a14b0356107897829ec36|28800138432"
)

mkdir -p "${DEST_ROOT}/embed-small" "${DEST_ROOT}/qwen27b" "${DEST_ROOT}/gemma4-heretic" "${DEST_ROOT}/flash-next"

ok=0
fail=0
for spec in "${FILES[@]}"; do
  IFS='|' read -r repo rpath dest sha size <<<"$spec"
  out="${DEST_ROOT}/${dest}"
  part="${out}.partial"
  url="https://huggingface.co/${repo}/resolve/main/${rpath}"
  if [[ -f "$out" ]]; then
    got=$(stat -c%s "$out")
    if [[ "$got" == "$size" ]]; then
      actual=$(sha256sum "$out" | awk '{print $1}')
      if [[ "$actual" == "$sha" ]]; then
        progress "ALREADY OK $dest (${got} bytes, sha256 match)"
        ok=$((ok+1))
        continue
      else
        progress "HASH MISMATCH existing $dest — removing and re-downloading"
        rm -f "$out"
      fi
    else
      progress "INCOMPLETE existing $dest ($got != $size) — removing"
      rm -f "$out"
    fi
  fi
  progress "DOWNLOAD START $dest from ${repo} (expected ${size} bytes)"
  # resume partial if present
  curl -fL --retry 25 --retry-delay 5 --retry-all-errors \
    --continue-at - \
    --connect-timeout 30 \
    --speed-time 60 --speed-limit 10000 \
    -A "$UA" \
    -o "$part" \
    "$url"
  got=$(stat -c%s "$part")
  if [[ "$got" != "$size" ]]; then
    progress "FAIL size $dest got=${got} expected=${size}"
    fail=$((fail+1))
    continue
  fi
  actual=$(sha256sum "$part" | awk '{print $1}')
  if [[ "$actual" != "$sha" ]]; then
    progress "FAIL sha256 $dest got=${actual} expected=${sha}"
    rm -f "$part"
    fail=$((fail+1))
    continue
  fi
  mv -f "$part" "$out"
  progress "VERIFIED $dest (${got} bytes, sha256 ${actual})"
  ok=$((ok+1))
done

# Convenience names used by staged llama-swap config
ln -sfn nomic-embed-text-v1.5.Q8_0.gguf "${DEST_ROOT}/embed-small/embed.gguf"
ln -sfn gemma-4-26B-A4B-it-heretic.Q8_0.gguf "${DEST_ROOT}/gemma4-heretic/gemma4-26b-a4b-heretic.gguf"
ln -sfn mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf "${DEST_ROOT}/flash-next/mtp-shared-Q8_0.gguf"
# llama.cpp split GGUF: point the un-sharded name at shard 1
ln -sfn Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf "${DEST_ROOT}/flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL.gguf"

# Write SHA256SUMS of real files (not symlinks)
(
  cd "$DEST_ROOT"
  find . -type f -name '*.gguf' | sort | while read -r f; do
    sha256sum "$f"
  done
) > "${DEST_ROOT}/SHA256SUMS"

progress "DOWNLOADS FINISHED ok=${ok} fail=${fail}. SHA256SUMS written."
echo "DONE ok=${ok} fail=${fail}" > "${HOME}/evo-x3/download-done.txt"
