"""Canonical last-frame chain harness for writer-runs (keep-comfy-part1, 2026-11-15).

Copy of runs/overnight_5min_rough_20261115_v2/chain_queue.py (that finished run is never edited),
parameterized by --run-dir / --scene-read and carrying the keep-comfy chain mode:
- every queued writer-run passes --keep-comfy-process, so run_queue.py frees ComfyUI's models
  (POST /free) at batch close but keeps the comfyui_auto PROCESS alive (no ~40 s wake per clip);
- during the gaps between batches (still_read vision + writer builds, waiting on a render) this
  harness pings llama-swap GET /comfyui/system_stats every PING_SEC so the model's ttl (300 s idle
  in /home/derekboone/AI/director/config/llama-swap.yaml) cannot expire mid-chain. /system_stats is in
  upstream.ignorePaths, so the ping never WAKES a stopped process (run_graph_job.wake uses GET
  /comfyui/ for that); it only resets the idle timer of a running one. A chain starts on the
  start still: the first queued batch wakes comfyui_auto through the normal run_queue wake path.

Defaults are the finished v2 scene (start still GI183, v2 position/frame table, S2 look, c18-c20
mouth guard); a new scene passes --run-dir plus its own --scene-read and, when it differs,
--meta-file / --start-still / --s2-look. Builder b81b04f Fix A/B in effect: --scene-read on every
continued clip, --inherited-garments from the previous clip's tracked end state. The v1
stale-garment auto-correction (W5 override without evidence) stays REMOVED: any W5 override needs
a frame-crop evidence file and is not done by this harness.
Uses fill_request.py, run_queue (gpu_lock per clip) and
render_writer_pipeline.chain_start_still / build_request.vision_read. No pipeline edits.
One fixed seed (writer-run default 51083601). Stops at the first NOT_READY or failed clip.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

PY = sys.executable
SCRIPTS = Path(__file__).resolve().parent.parent
SUBMIT = SCRIPTS / "parody" / "fill_request.py"
PARODY = SUBMIT.parent
for _p in (str(SCRIPTS), str(PARODY)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The finished v2 scene, kept as the default so an old command line still works.
STILL0 = str(SCRIPTS.parents[1] / "render" / "stills" / "approved_characters" / "GROK_IMAGINE_2026-10-19b" / "GI183.jpg")
S2 = ("a fictional adult man aged 31, athletic, naturally muscular build with real weight in his "
      "chest and thighs, light tan skin, short dark hair and dark stubble")
SEED = 51083601  # writer-run default seed, fixed for every clip (build_report.json records it)
WAIT_SEC = 45 * 60
PING_SEC = 60          # << comfyui_auto ttl 300 s (llama-swap.yaml); keep the gap under the ttl
GUARD = {18, 19, 20}   # v2 mouth-height guard clips (c18-c20)

META = {
    1: ("talk", 243), 2: ("talk", 243), 3: ("talk", 243), 4: ("talk", 243), 5: ("talk", 243),
    6: ("blowjob", 158), 7: ("blowjob", 243), 8: ("blowjob", 243),
    9: ("doggy", 158), 10: ("doggy", 243), 11: ("doggy", 243),
    12: ("missionary", 158), 13: ("missionary", 243), 14: ("missionary", 243),
    15: ("standing_mf", 158), 16: ("standing_mf", 243), 17: ("standing_mf", 243),
    18: ("blowjob", 158), 19: ("blowjob", 243), 20: ("blowjob", 243),
    21: ("standing_mf", 158), 22: ("standing_mf", 243), 23: ("standing_mf", 243),
    24: ("missionary", 158), 25: ("missionary", 243), 26: ("missionary", 243),
    27: ("prone_bone", 158), 28: ("prone_bone", 243), 29: ("prone_bone", 243),
    30: ("finish", 158), 31: ("finish", 243), 32: ("talk", 209),
}
assert sum(f for _, f in META.values()) == 6977


class Chain:
    """Per-run state (dir, logs, scene files); every helper below is a method so nothing is hard-wired."""

    def __init__(self, root: Path, scene_read: Path, still0: str, s2: str, meta: dict, guard: set):
        self.root = Path(root)
        self.scene_read = Path(scene_read)
        self.still0 = still0
        self.s2 = s2
        self.meta = {int(k): (v[0], int(v[1])) for k, v in meta.items()}
        self.guard = set(guard)
        self.n = max(self.meta)
        self.log_path = self.root / "_chain.log"

    def now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S CT")

    def log(self, msg: str) -> None:
        line = f"{self.now()} {msg}"
        print(line, flush=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def status(self, **kw) -> None:
        kw["at"] = self.now()
        (self.root / "_chain_status.json").write_text(json.dumps(kw, indent=2), encoding="utf-8")

    # ---- comfyui_auto keep-alive (ttl 300 s, llama-swap.yaml) ------------------------------------------------
    def ping(self) -> None:
        """GET /comfyui/system_stats through llama-swap: resets the ttl idle timer of a RUNNING
        comfyui_auto; it is in upstream.ignorePaths so it never wakes a stopped process and never
        blocks. Logged once per gap by keepalive(); failures are logged, never fatal."""
        import run_graph_job as rgj
        try:
            urllib.request.urlopen(rgj.COMFY + "/system_stats", timeout=10).read()
        except Exception as e:
            self.log(f"keepalive ping note {type(e).__name__}: {str(e)[:120]}")

    def keepalive(self, fn, *args, **kw):
        """Run fn (a step of the gap: writer build, vision read, batch wait) while pinging every
        PING_SEC so the chain never leaves comfyui_auto idle past its ttl."""
        stop = []

        def loop():
            while not stop:
                self.ping()
                for _ in range(PING_SEC * 4):  # sleep in 0.25 s slices so the thread ends fast
                    if stop:
                        break
                    time.sleep(0.25)

        import threading
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        try:
            return fn(*args, **kw)
        finally:
            stop.append(True)
            t.join(timeout=15)

    # ---- per-clip helpers -----------------------------------------------------------------------------------
    def clip_dir(self, i: int) -> Path:
        return self.root / f"clip_{i:02d}"

    def ask_of(self, d: Path) -> str:
        text = (d / "writer_output.txt").read_text(encoding="utf-8")
        if "summary:" in text and "retention_analysis:" in text:
            a = text.split("summary:", 1)[1].split("retention_analysis:", 1)[0].strip()
            if a:
                return a
        return f"chain {self.root.name} {d.name}"

    def garments_of(self, d: Path):
        p = d / "build_report.json"
        if not p.exists():
            return None
        try:
            b = json.loads(p.read_text(encoding="utf-8"))
            g = ((b.get("build") or {}).get("state") or {}).get("garments")
            return g if isinstance(g, dict) and g else None
        except Exception:
            return None

    def writer_run(self, d: Path, pos: str, frames: int, still: str, continued: bool, garments, queue: bool) -> dict:
        cmd = [
            PY, str(SUBMIT), str(d),
            "--ask", self.ask_of(d), "--position", pos, "--still", still,
            "--character", "FCSydny", "--frames", str(frames),
        ]
        if queue:
            cmd.append("--queue")
        t0 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PARODY), timeout=240 if not queue else 200)
        if queue and p.returncode == 0:
            q_cmd = [PY, "-u", str(SCRIPTS / "run_queue.py"), "--run-dir", str(d), "--frames", str(frames), "--detach"]
            # chain mode (keep-comfy-part1): the queued batch keeps comfyui_auto's process alive;
            # this harness carries it across the gaps with ping(). Only on the queued call.
            q_cmd.append("--keep-comfy-process")
            p = subprocess.run(q_cmd, capture_output=True, text=True, cwd=str(SCRIPTS.parent), timeout=200)
        sec = round(time.time() - t0, 2)
        st, reason, seed = "UNKNOWN", "", None
        br_path = d / "build_report.json"
        if br_path.exists():
            try:
                rep = json.loads(br_path.read_text(encoding="utf-8"))
                st = rep.get("status") or st
                reason = rep.get("reason") or ""
                seed = rep.get("seed")
            except Exception as e:
                reason = f"build_report parse: {e}"
        out = ((p.stdout or "") + (p.stderr or "")).strip()
        self.log(f"{d.name} writer-run queue={queue} rc={p.returncode} status={st} seed={seed} sec={sec} reason={reason} out={out[-400:]}")
        if seed is not None and int(seed) != SEED:
            return {"rc": p.returncode, "status": "SEED_MISMATCH", "reason": f"seed {seed} != {SEED}"}
        return {"rc": p.returncode, "status": st, "reason": reason}

    def closed_count(self, logp: Path) -> int:
        if not logp.exists():
            return 0
        return logp.read_text(encoding="utf-8", errors="replace").count("BATCH closed rc=")

    def wait_batch(self, d: Path) -> int:
        logp = d / "_render_queue.log"
        before = self.closed_count(logp)
        self.log(f"{d.name} wait batch (closed already={before})")
        t0 = time.time()
        while time.time() - t0 < WAIT_SEC:
            if self.closed_count(logp) > before:
                text = logp.read_text(encoding="utf-8", errors="replace")
                line = [ln for ln in text.splitlines() if "BATCH closed rc=" in ln][-1]
                rc = int(line.split("BATCH closed rc=", 1)[1].split()[0])
                self.log(f"{d.name} {line.strip()}")
                return rc
            time.sleep(8)
        self.log(f"{d.name} WAIT TIMEOUT after {WAIT_SEC}s")
        return 99

    def vision_chat(self, messages):
        global _CLIENT
        if _CLIENT is None:
            from render_writer_pipeline import load_config
            from wp_llm import Client
            _CLIENT = Client(load_config(), lambda e, dd=None: self.log(f"pipeline {e} {dd or ''}"))
        return _CLIENT.chat(messages, {"temperature": 0.2, "top_k": 20, "top_p": 0.9}, 7, 1024, purpose="vision_read")

    def prep_next_still(self, prev: Path, nxt: Path) -> str:
        from render_writer_pipeline import chain_start_still
        import build_request as br

        still = chain_start_still(prev, self.still0, nxt, lambda e, dd=None: self.log(f"pipeline {e} {dd or ''}"))
        read = br.vision_read(still, self.vision_chat)
        doc = {"read": read, "source": still, "how": "chain last-frame vision_read (pose/framing/facing/people only; cast+set from scene_read, garments from tracked state)"}
        (nxt / "still_read.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"{nxt.name} still_read from last frame people={read.get('people')} garments={read.get('garments')} pose={read.get('pose')}")
        return still

    def frame_at(self, mp4: Path, out: Path, sseof: float = None, frac: float = None) -> bool:
        ff = shutil.which("ffmpeg") or "ffmpeg"
        if sseof is not None:
            args = [ff, "-y", "-sseof", str(-abs(sseof)), "-i", str(mp4), "-frames:v", "1", str(out)]
        else:
            fp = shutil.which("ffprobe") or "ffprobe"
            r = subprocess.run([fp, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                               capture_output=True, text=True, timeout=60)
            dur = float((r.stdout or "0").strip() or 0)
            args = [ff, "-y", "-ss", f"{dur * frac:.3f}", "-i", str(mp4), "-frames:v", "1", str(out)]
        r = subprocess.run(args, capture_output=True, timeout=120)
        return r.returncode == 0 and out.exists()

    def mouth_guard(self, d: Path, i: int) -> bool:
        """True = OK to continue. Checks rendered frames; c18 last frame, c19/c20 mid + last."""
        import base64, io
        from PIL import Image
        import build_request as br
        mp4 = d / "clip" / "clip.mp4"
        points = [("last", dict(sseof=0.1))] if i == 18 else [("mid", dict(frac=0.5)), ("last", dict(sseof=0.1))]
        results = {}
        for name, kw in points:
            png = d / f"guard_{name}.png"
            if not self.frame_at(mp4, png, **kw):
                self.log(f"{d.name} GUARD frame extract failed ({name})")
                results[name] = None
                continue
            buf = io.BytesIO()
            Image.open(png).convert("RGB").save(buf, "PNG")
            url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
            try:
                reply = self.vision_chat([{"role": "user", "content": [{"type": "text", "text": GUARD_Q},
                                                                       {"type": "image_url", "image_url": {"url": url}}]}])
                res = br._parse_json_reply(reply)
            except Exception as e:
                res = {"error": f"{type(e).__name__}: {e}"}
            results[name] = res
            self.log(f"{d.name} GUARD {name} {res}")
        (d / "mouth_guard.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

        def ok(r):
            return isinstance(r, dict) and (r.get("her_mouth_at_his_groin_height") is True or r.get("mouth_on_penis") is True)
        good = [ok(r) for r in results.values()]
        # Stop when no checked frame shows her mouth at his groin height / on his penis.
        return any(good)

    # ---- the chain ------------------------------------------------------------------------------------------------
    def main(self, start: int) -> int:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"{self.now()} chain_queue start={start} seed={SEED} root={self.root} still0={self.still0} "
                    f"scene_read={self.scene_read} keep_comfy_process=True\n")
        print(f"{self.now()} chain_queue start={start} seed={SEED}", flush=True)
        results = [f"clip_{j:02d}" for j in range(1, start)]
        prev = self.clip_dir(start - 1) if start > 1 else None
        still = self.still0
        garments = self.garments_of(prev) if prev else None
        for i in range(start, self.n + 1):
            tag = f"clip_{i:02d}"
            d = self.clip_dir(i)
            pos, frames = self.meta[i]
            continued = i > 1
            if i > 1:
                have = (d / "start_still_from_prev.png").exists() and (d / "still_read.json").exists()
                if i == start and have:
                    still = str(d / "start_still_from_prev.png")
                    self.log(f"{tag} resume reuse last-frame still and still_read garments={garments}")
                else:
                    # the vision-read gap: keep comfyui_auto's ttl timer reset while Gemma reads
                    still = self.keepalive(self.prep_next_still, prev, d)
                    garments = self.garments_of(prev)
                    self.log(f"{tag} inherited garments={garments} still={still}")
            dry = self.keepalive(self.writer_run, d, pos, frames, still, continued, garments, queue=False)
            if dry["status"] != "READY":
                self.log(f"STOP at {tag} dry-run {dry['status']}: {dry['reason']}")
                self.status(stopped=tag, why="dry-run NOT_READY", reason=dry["reason"], finished_ok=results)
                return 2
            q = self.keepalive(self.writer_run, d, pos, frames, still, continued, garments, queue=True)
            if q["status"] != "READY":
                self.log(f"STOP at {tag} queue-build {q['status']}: {q['reason']}")
                self.status(stopped=tag, why="queue-build NOT_READY", reason=q["reason"], finished_ok=results)
                return 2
            rc = self.keepalive(self.wait_batch, d)
            t = (d / "_render_queue.log").read_text(encoding="utf-8", errors="replace") if (d / "_render_queue.log").exists() else ""
            ok = rc == 0 and "BATCH closed rc=0" in t and (d / "clip" / "clip.mp4").exists()
            if not ok:
                self.log(f"STOP at {tag} batch rc={rc} objective_ok={ok}")
                self.status(stopped=tag, why=f"batch rc={rc} FAILED", finished_ok=results)
                return 3
            results.append(tag)
            self.log(f"{tag} OBJECTIVE ok ({len(results)}/{self.n})")
            if i in self.guard and not self.mouth_guard(d, i):
                self.log(f"STOP at {tag} c18-c20 mouth-height guard: her mouth does not line up with him at the low bed edge (see {tag}\\mouth_guard.json, guard_*.png)")
                self.status(stopped=tag, why="c18-c20 mouth-height guard", finished_ok=results,
                            fix="Prompt maker one-line swap: he kneels on the floor in c18-c20")
                return 4
            self.status(stopped=None, running_next=f"clip_{i+1:02d}" if i < self.n else None, finished_ok=results)
            prev = d
        self.status(stopped=None, why=f"all {self.n} OBJECTIVE ok", finished_ok=results)
        self.log(f"ALL {self.n} DONE")
        return 0


_CLIENT = None

GUARD_Q = (
    "This is one frame from an adult (18+) fictional film scene with one woman and one man in a bedroom "
    "with a low bed. Answer ONLY with JSON: {\"woman_on_all_fours_or_kneeling_on_bed\": true|false, "
    "\"man_standing_on_floor\": true|false, \"her_mouth_at_his_groin_height\": true|false, "
    "\"mouth_on_penis\": true|false, \"note\": \"<one short sentence on the height relation between her mouth and his groin>\"}"
)


def parse_meta_file(path: str) -> dict:
    """A scene's clip table: JSON {"1": ["talk", 243], ...} (list form [pos, frames] is not used)."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not raw:
        raise SystemExit("--meta-file must be a JSON object {clip index: [position, frames]}")
    return raw


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="chain_queue.py", description=__doc__.splitlines()[0],
                                 epilog="Defaults are the finished overnight_5min_rough_20261115_v2 scene.")
    ap.add_argument("--run-dir", required=True, help="chain run dir (clip_XX subdirs, _chain.log here)")
    ap.add_argument("--scene-read", default=None, help="clip-1 vision read every continued clip keeps its cast and set from (default: <run-dir>/scene_read.start.json)")
    ap.add_argument("--start-still", default=STILL0, help="clip-1 start still")
    ap.add_argument("--s2-look", default=S2, help="S2 description for every clip")
    ap.add_argument("--meta-file", default=None, help='JSON object {"1": ["talk", 243], ...} (default: the v2 table)')
    ap.add_argument("--guard", default="18,19,20", help="comma-separated clip indices to run the mouth-height guard on (empty = none)")
    ap.add_argument("--start", type=int, default=1, help="resume at this clip")
    a = ap.parse_args(argv)
    root = Path(a.run_dir)
    scene_read = Path(a.scene_read) if a.scene_read else root / "scene_read.start.json"
    guard = {int(g) for g in re.split(r"[,\s]+", a.guard.strip()) if g}
    meta = parse_meta_file(a.meta_file) if a.meta_file else META
    ch = Chain(root, scene_read, a.start_still, a.s2_look, meta, guard)
    return ch.main(a.start)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"FATAL {type(e).__name__}: {e}")
        raise
