#!/usr/bin/bash
# Batch runner for the render writer pipeline: one JSON manifest in, N clips out.
# 2026-11-16 render-chat audit fix: the model must not hand-write batch shell (heredoc
# escaping bug cost ~8 min in test_batch_11b). Manifest fields map 1:1 to
# render_writer_pipeline.py flags; commands are built with shlex in python, so
# quotes, $( ), unicode and spaces in asks are safe by construction.
#
# Usage: run_batch.sh <manifest.json> [--dry-run] [--queue]
#   --dry-run  print the exact per-clip commands, run nothing
#   --queue    append --queue --yes-derrick to every clip; REQUIRES an "approval"
#              string in the manifest recording Derrick's yes for this batch
# Env overrides: PY (python), PIPELINE (render_writer_pipeline.py path) — for tests.
# Background a real batch: nohup bash run_batch.sh manifest.json > batch.out 2>&1 &
set -uo pipefail

MANIFEST=${1:?usage: run_batch.sh <manifest.json> [--dry-run] [--queue]}
shift
DRY=0; QUEUE=0
for a in "$@"; do case "$a" in
  --dry-run) DRY=1;;
  --queue) QUEUE=1;;
  *) echo "unknown arg: $a" >&2; exit 2;;
esac; done

PY=${PY:-/home/evo/AI/render/x3/.venv/bin/python3}
PIPELINE=${PIPELINE:-/home/evo/AI/community/scripts/parody/render_writer_pipeline.py}
[ -f "$MANIFEST" ] || { echo "manifest not found: $MANIFEST" >&2; exit 2; }

# Build one shlex-quoted command per clip (json -> argv), tab-separated with the clip dir.
CMDS=$(Q="$QUEUE" "$PY" - "$MANIFEST" "$PY" "$PIPELINE" <<'PYX'
import json, os, shlex, sys
manifest, py, pipeline = sys.argv[1], sys.argv[2], sys.argv[3]
m = json.load(open(manifest, encoding="utf-8"))
run_dir = m.get("run_dir")
if not run_dir:
    sys.exit("manifest needs run_dir")
if os.environ.get("Q") == "1" and not m.get("approval"):
    sys.exit("--queue refused: manifest has no \"approval\" string with Derrick's yes")
for i, c in enumerate(m.get("clips", []), 1):
    cid = str(c.get("id", i))
    clip_dir = os.path.join(run_dir, f"clip_{cid}")
    argv = [py, pipeline, clip_dir,
            "--ask", c["ask"], "--still", c["still"]]
    for key, flag in (("position", "--position"), ("character", "--character"),
                      ("template", "--template"), ("still_mode", "--still-mode"),
                      ("size", "--size"), ("aspect", "--aspect"),
                      ("frames", "--frames"), ("still_read", "--still-read"),
                      ("continue", "--continue"), ("scene", "--scene")):
        if c.get(key) not in (None, ""):
            argv += [flag, str(c[key])]
    if c.get("names"):
        argv += ["--names"] + [str(n) for n in c["names"]]
    argv += [str(x) for x in c.get("extra", [])]
    if os.environ.get("Q") == "1":
        argv += ["--queue", "--yes-derrick"]
    print(f"{clip_dir}\t{shlex.join(argv)}")
PYX
) || { echo "manifest error: see message above" >&2; exit 2; }

if [ "$DRY" = 1 ]; then
  echo "$CMDS" | while IFS=$'\t' read -r dir cmd; do echo "DRY: $cmd"; done
  exit 0
fi

PASS=0; FAIL=0; FAILED_IDS=""
while IFS=$'\t' read -r dir cmd; do
  cid=$(basename "$dir")
  mkdir -p "$dir"
  echo "=== $cid  $(date '+%H:%M:%S')"
  if eval "$cmd" > "$dir/_clip.log" 2>&1; then
    echo "OK   $cid (log $dir/_clip.log)"; PASS=$((PASS+1))
  else
    echo "FAIL $cid rc=$? (log $dir/_clip.log)"
    tail -3 "$dir/_clip.log" 2>/dev/null | sed 's/^/     | /'
    FAIL=$((FAIL+1)); FAILED_IDS="$FAILED_IDS $cid"
  fi
done <<< "$CMDS"

echo "----------------------------------------"
echo "batch done: $PASS ok, $FAIL fail${FAILED_IDS:+ — failed:$FAILED_IDS}"
[ "$FAIL" = 0 ]
