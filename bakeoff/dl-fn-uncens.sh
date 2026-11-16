#!/bin/bash
# Download orcarouter IQ4_XS (Peonist-recommended) + mmproj.
# Token is read from /etc/evo-x3/hf.env into the process environment only. Never printed, never on the command line.
set -euo pipefail
D=/srv/bakeoff/fn-uncens-iq4xs
mkdir -p "$D"
cd "$D"
REV=98eb3357afd966c25cadd082c7f830eafde7aa52
REPO=orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF
FILES=(
  Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00001-of-00003.gguf
  Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00002-of-00003.gguf
  Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00003-of-00003.gguf
  mmproj-Qwen3.8-Flash-Next-Uncensored-F16.gguf
  Qwen3.8-Flash-Next-Uncensored-MTP-draft.gguf
)
# expected sizes (bytes) from the HF tree at $REV
cat > SIZES.expected <<'S'
44766155936  Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00001-of-00003.gguf
44735995008  Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00002-of-00003.gguf
7971004256  Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00003-of-00003.gguf
907543296  mmproj-Qwen3.8-Flash-Next-Uncensored-F16.gguf
4135893632  Qwen3.8-Flash-Next-Uncensored-MTP-draft.gguf
S
# Load token without printing. Fail clearly if the repo is still gated for this account.
eval "$(sudo python3 -c '
import os, shlex, pathlib, subprocess, sys
raw = subprocess.check_output(["cat","/etc/evo-x3/hf.env"], text=True)
tok=None
for line in raw.splitlines():
    if line.startswith("HF_TOKEN="):
        tok=line.split("=",1)[1].strip().strip("\"'\''")
if not tok:
    print("echo NO_HF_TOKEN >&2; exit 2")
    sys.exit(0)
print("export HF_TOKEN=" + shlex.quote(tok))
')"
# Probe the gate before spending an hour. Token stays in the environment, not argv.
python3 - <<'PY'
import os, urllib.request, urllib.error, sys
tok=os.environ["HF_TOKEN"]
url="https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF/resolve/98eb3357afd966c25cadd082c7f830eafde7aa52/Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00001-of-00003.gguf"
req=urllib.request.Request(url, headers={"Authorization":"Bearer "+tok, "Range":"bytes=0-16"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("GATE_OK", r.status, "len", r.headers.get("content-length") or r.headers.get("content-range"))
except urllib.error.HTTPError as e:
    print("GATE_BLOCKED", e.code, (e.headers.get("x-error-code") or ""), file=sys.stderr)
    print("Visit https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF as Incognitodb and accept access.", file=sys.stderr)
    sys.exit(3)
PY
# Prefer huggingface_hub if present; otherwise aria2 with a 0600 header file.
if python3 -c "import huggingface_hub" 2>/dev/null; then
  export HF_HUB_ENABLE_HF_TRANSFER=1
  python3 - <<'PY'
import os
from huggingface_hub import hf_hub_download
repo="orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF"
rev="98eb3357afd966c25cadd082c7f830eafde7aa52"
dest="/srv/bakeoff/fn-uncens-iq4xs"
files=[
  "Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00001-of-00003.gguf",
  "Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00002-of-00003.gguf",
  "Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00003-of-00003.gguf",
  "mmproj-Qwen3.8-Flash-Next-Uncensored-F16.gguf",
  "Qwen3.8-Flash-Next-Uncensored-MTP-draft.gguf",
]
for f in files:
    print("DL_START", f, flush=True)
    hf_hub_download(repo_id=repo, revision=rev, filename=f, local_dir=dest)
    print("DL_DONE", f, flush=True)
PY
else
  HDR=$(mktemp)
  chmod 600 "$HDR"
  printf 'Authorization: Bearer %s\n' "$HF_TOKEN" > "$HDR"
  : > "$D/list.aria"
  for f in "${FILES[@]}"; do
    printf '%s\n  out=%s\n' "https://huggingface.co/${REPO}/resolve/${REV}/${f}" "$f" >> "$D/list.aria"
  done
  aria2c -i "$D/list.aria" -d "$D" -x 16 -s 16 -j 1 -c --file-allocation=none --console-log-level=warn --header-file="$HDR" || {
    # aria2 may not support --header-file on this build; fall back to python
    rm -f "$HDR"
    echo "ARIA_HEADER_FILE_UNSUPPORTED_OR_FAILED; use huggingface_hub" >&2
    exit 4
  }
  rm -f "$HDR"
fi
echo "======= size check ======="
ok=1
while read -r sz name; do
  got=$(stat -c %s "$D/$name" 2>/dev/null || echo 0)
  if [ "$got" = "$sz" ]; then
    echo "SIZE_OK $name $got"
  else
    echo "SIZE_BAD $name expected=$sz got=$got"
    ok=0
  fi
done < "$D/SIZES.expected"
# drop token from this shell
unset HF_TOKEN
[ "$ok" = 1 ] && echo "FN_UNCENS_DL_OK $(date '+%F %T %Z')" || { echo "FN_UNCENS_DL_FAIL $(date '+%F %T %Z')"; exit 5; }
