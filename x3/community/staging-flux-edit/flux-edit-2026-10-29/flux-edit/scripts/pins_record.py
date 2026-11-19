"""U11 helper: record what custom-node code a run used (read-only).

If a cm-cli snapshot JSON is given it is copied in verbatim (sha256 noted). Otherwise each folder under
custom_nodes/ is read with `git rev-parse HEAD` (non-git folders are listed as "not_git"). Nothing is installed,
updated or fetched. Output: one JSON file next to the run (pins.json)."""
import argparse
import datetime
import hashlib
import json
import os
import subprocess


def git_head(path):
    try:
        r = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"status": "error", "detail": str(e)}
    if r.returncode != 0:
        return {"status": "not_git"}
    return {"status": "git", "head": r.stdout.strip()}


def record(custom_nodes_dir=None, snapshot=None):
    out = {"recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    if snapshot:
        with open(snapshot, "rb") as f:
            raw = f.read()
        out["source"] = "cm-cli snapshot"
        out["snapshot_sha256"] = hashlib.sha256(raw).hexdigest()
        out["snapshot"] = json.loads(raw)
        return out
    if not custom_nodes_dir or not os.path.isdir(custom_nodes_dir):
        raise SystemExit(f"custom_nodes dir not found: {custom_nodes_dir}")
    out["source"] = "git rev-parse HEAD per custom_nodes folder"
    out["nodes"] = {n: git_head(os.path.join(custom_nodes_dir, n)) for n in sorted(os.listdir(custom_nodes_dir))
                    if os.path.isdir(os.path.join(custom_nodes_dir, n)) and not n.startswith((".", "__"))}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--custom-nodes")
    ap.add_argument("--snapshot")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rec = record(a.custom_nodes, a.snapshot)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(f"wrote {a.out}")
