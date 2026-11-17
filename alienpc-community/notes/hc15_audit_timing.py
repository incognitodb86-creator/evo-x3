"""HC15 per-segment render timing, read out of ComfyUI's own records (no GPU, read-only).

Durable rows: runs/hc15_*/*[.id].mp4.json + objective.json carry the wall seconds each clip took, and
ComfyUI/user/comfyui*.log* carries "Prompt executed in HH:MM:SS" lines = whole-prompt cost on this 16 GB card.
Per-SEGMENT rows: ComfyUI's Prompt log (ComfyUI/Prompt_<start>.log[.N]) writes one JSON line per executed prompt
with "prompt_id" and a dict whose keys are the sampling segment frame lengths and whose values are that
segment's seconds, plus an "audio" key. That is the only place on this box where a segment's cost is recorded,
and it is what the fix_plan item asks for ("Time each segment").

HONEST STATE 2026-10-24 18:30 CT: the Prompt_*.log files for the HC15 window (16:45-17:27 CT) were read this
pass and printed segment seconds (124 f @10 steps = 179.00 s, 141 f window @10 steps = 267.00 s, audio decode
35.57 s - quoted in notes/hc15_start_fidelity_audit.md), then ComfyUI rotated them away; by 18:55 CT
find -name 'Prompt_*' under the install returns 0 files. This tool therefore prints PROMPT_LOGS_ABSENT and
leaves segments=null, and the audit marks those numbers transcript-captured. Re-run it while a Prompt log exists
to refresh timing.json.

Reproduce:  "C:/Program Files/Python312/python.exe" C:/AI/community/notes/hc15_audit_timing.py
Writes:     C:/AI/community/notes/hc15_audit/timing.json
Community timing rows:
  https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md  (reference configuration = 8-12 steps, "slower")
  https://github.com/mostlygeek/llama-swap/blob/main/docs/comfyui.md  (swap semantics around a render)
  https://github.com/Comfy-Org/ComfyUI/issues/15337  (1344x768 H3 audio-OOM report on a 16 GB RTX 5080 laptop)
"""
import glob
import json
import os
import re

W = r"C:\AI\community"
ROOT = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
PROMPT_GLOBS = [os.path.join(ROOT, "Prompt_*.log*"), os.path.join(ROOT, "user", "Prompt_*.log*"),
                os.path.join(ROOT, "user", "*", "Prompt_*.log*"), os.path.join(ROOT, "*", "Prompt_*.log*")]
LOG_GLOBS = [os.path.join(ROOT, "user", "comfyui*.log*")]
AUD = os.path.join(W, "notes", "hc15_audit")
OUT = os.path.join(AUD, "timing.json")


def clips():
    rows = {}
    for p in sorted(glob.glob(os.path.join(W, "runs", "hc15_*", "*.mp4.json"))):
        d = json.load(open(p, encoding="utf-8"))
        obj = json.load(open(os.path.join(os.path.dirname(p), "objective.json"), encoding="utf-8"))
        a = obj["attempts"][0]
        rows[d["prompt_id"]] = dict(run=d["run"], mp4_secs=d["secs"], frames=a["frames"],
                                    finished=d.get("finished"), file=p)
    return rows


def prompt_logs():
    files = set()
    for g in PROMPT_GLOBS:
        files |= set(glob.glob(g))
    return sorted(files)


def parse_logs(files, prompt_ids):
    hits = {}
    for f in files:
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = re.search(r'"prompt_id":\s*"([0-9a-f-]{36})"', line)
                if not m or m.group(1) not in prompt_ids:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                seg = {k: v for k, v in rec.get("prompt", {}).items() if isinstance(v, (int, float))}
                cur = hits.get(m.group(1))
                if cur is None or (rec.get("timestamp") or 0) > (cur["timestamp"] or 0):
                    hits[m.group(1)] = dict(file=f, timestamp=rec.get("timestamp"), segments=seg)
    return hits


def executed_lines():
    """Durable whole-prompt costs: [timestamp] Prompt executed in HH:MM:SS, from every comfyui*.log*."""
    out = []
    for f in glob.glob(os.path.join(ROOT, "user", "comfyui*.log*")):
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "Prompt executed in" in line:
                    m = re.search(r"\[([0-9-]+ [0-9:.]+)\].*Prompt executed in ([0-9:]+)", line)
                    if m:
                        out.append(dict(file=os.path.basename(f), at=m.group(1), elapsed=m.group(2)))
    vram = []
    for f in glob.glob(os.path.join(ROOT, "user", "comfyui_10004*.log*")):
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "Total VRAM" in line:
                    vram.append(dict(file=os.path.basename(f), line=line.strip()))
    return out, vram


def main():
    os.makedirs(AUD, exist_ok=True)
    idx = clips()
    files = prompt_logs()
    hits = parse_logs(files, set(idx)) if files else {}
    executed, vram = executed_lines()
    rows = []
    for pid, c in sorted(idx.items(), key=lambda kv: kv[1]["run"]):
        h = hits.get(pid, {})
        seg = h.get("segments") or None
        samp = sum(v for k, v in (seg or {}).items() if k != "audio")
        rows.append(dict(run=c["run"], prompt_id=pid, frames=c["frames"], wall_secs=c["mp4_secs"],
                         finished=c["finished"], segments=seg,
                         sampling_secs=round(samp, 2) if seg else None,
                         log_sum=round(sum((seg or {}).values()), 2) if seg else None,
                         overhead_secs=round(c["mp4_secs"] - sum((seg or {}).values()), 2) if seg else None,
                         segment_shapes="x".join(k for k in (seg or {}) if k != "audio") or None,
                         log=h.get("file")))
    doc = dict(rows=rows, prompt_log_files=files, prompt_logs_present=bool(files),
               executed_lines=executed, vram_lines=vram,
               per_clip_secs={r["run"]: r["wall_secs"] for r in rows})
    open(OUT, "w", encoding="utf-8").write(json.dumps(doc, indent=1))
    for r in rows:
        print(json.dumps(r))
    print("EXECUTED_LINES %s" % json.dumps(executed[-6:]))
    print("VRAM %s" % json.dumps(vram[:2]))
    print("PROMPT_LOGS_ABSENT" if not files else "PROMPT_LOGS %d files" % len(files))
    print("TIMING_JSON %s rows=%d with_segments=%d wall_only=%d"
          % (OUT, len(rows), sum(1 for r in rows if r["segments"]), sum(1 for r in rows if not r["segments"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
