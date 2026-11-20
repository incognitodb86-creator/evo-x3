#!/usr/bin/env python3
"""REA: REA-video -> FLUX -> H3Max parody remake orchestrator (`plan` + `status` + `flux` + `build`).

`plan` turns an rea-video decomposition folder (breakdown.json + shots/*.jpg + stems/*.wav) into an H3 batch:
one run dir per shot under <batch_dir>/shots/, each with the source keyframe in `_inputs/`, a
`raw_still_read.json` vision read (18+ gate, fail closed), and a `shot_brief.json` carrying the frame plan,
the H3 camera words, the dialogue and the beat map Hermes needs. The batch gets `parody_cast_lock.json`
and `batch_card.md` (rea_shot_plan, C2); beats come from `onset_beats.json` (rea_onset_probe, C1) when the
REA folder does not ship one.

`status` prints, per shot, which of the pipeline artifacts already exist.

`flux` (C5) turns each shot's Hermes-written `flux_prompt.txt` into a Flux still request under
`<shot_dir>/flux/` (dry run by default; `--queue --yes-derrick` queues it and copies the returned still to
`_inputs/<id>_edited.png`). `build` (C5) runs render_writer_pipeline.py over `hermes_prose.txt` + the edited
still for every ready shot and records the per-shot build reports in `<batch_dir>/build_status.json`.

Usage:
  rea_parody_remake.py plan   <batch_dir> --rea-dir <dir> (--names NAME... | --character FCSydny|FCMegan)
                              [--lane parody|oc] [--aspect 9:16|16:9] [--shots shot_001,shot_002]
  rea_parody_remake.py status <batch_dir>
  rea_parody_remake.py flux   <batch_dir> [--shot ID] [--queue --yes-derrick]
  rea_parody_remake.py build  <batch_dir> [--shot ID]

stdlib + the parody modules only; vision/HTTP happen inside render_writer_pipeline._ensure_still_read_raw.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import build_request as br  # noqa: E402
import flux_still  # noqa: E402
import rea_onset_probe  # noqa: E402
import rea_shot_plan as rsp  # noqa: E402
import render_writer_pipeline as wp  # noqa: E402
import wp_lint  # noqa: E402
import wp_llm  # noqa: E402
import wp_state  # noqa: E402

DEFAULT_RUNS_ROOT = "/home/evo/AI/community/runs"
BATCH_PREFIX = "rea_"
SEED_BASE = 51083601  # the builder's default seed; every shot gets SEED_BASE + index
DIALOGUE_MAX_WORDS = 25
ONSET_NAME = "onset_beats.json"
FLUX_MODE_DEFAULT = "rea_edit"
FLUX_MODE_POSE = "rea_pose"
HYBRID_REFMOD_STRENGTH = 0.85  # the RefMod author's hybrid preset (flux_still.HYBRID_RETENTION at 0.85)
HYBRID_RETENTION = "partially_preserved (0.7)"
BUILD_STATUS_NAME = "build_status.json"
PIPELINE_SCRIPT = PARODY_DIR / "render_writer_pipeline.py"
# status probes, in pipeline order: (label, relative path, build_report key or None)
STATUS_ARTIFACTS = (
    ("raw_still_read", "raw_still_read.json", None),
    ("flux_prompt", "flux_prompt.txt", None),
    ("edited", "_inputs/{sid}_edited.png", None),
    ("prose", "hermes_prose.txt", None),
    ("build", "build_report.json", "build"),
    ("render_ok", "clip/render_ok.json", None),
)


# --- runs root + batch dir validation ---------------------------------------

def runs_root() -> Path:
    """The runs root; REA_RUNS_ROOT overrides it (tests use a tmp root)."""
    return Path(os.environ.get("REA_RUNS_ROOT") or DEFAULT_RUNS_ROOT)


def check_batch_dir(raw: Any) -> Path:
    """Absolute path under the runs root whose last part starts with rea_, or ValueError."""
    s = str(raw or "").strip()
    if not s:
        raise ValueError("batch_dir is empty")
    p = Path(s)
    if not p.is_absolute():
        raise ValueError(f"batch_dir must be absolute, got {s!r}")
    if ".." in p.parts:
        raise ValueError(f"batch_dir must not contain '..', got {s!r}")
    root = runs_root()
    if root not in p.parents:
        raise ValueError(f"batch_dir must be under {root}, got {s!r}")
    if not p.name.startswith(BATCH_PREFIX):
        raise ValueError(f"batch_dir last part must start with {BATCH_PREFIX!r}, got {p.name!r}")
    return p


# --- breakdown ---------------------------------------------------------------

def load_breakdown(rea_dir: Path) -> Dict[str, Any]:
    path = Path(rea_dir) / "breakdown.json"
    if not path.is_file():
        raise FileNotFoundError(f"no breakdown.json in {rea_dir}")
    return json.loads(path.read_text(encoding="utf-8"))


def shot_ids(shot: Dict[str, Any], index: int = 0) -> str:
    return str(shot.get("id") or shot.get("shot_id") or f"shot{index + 1:03d}")


def select_shots(breakdown: Dict[str, Any], only: Optional[Sequence[str]] = None) -> List[Dict[str, Any]]:
    """breakdown["shots"], optionally cut to the --shots ids (in the given order)."""
    shots = list(breakdown.get("shots") or [])
    known = {shot_ids(sh, i): sh for i, sh in enumerate(shots)}
    if not only:
        return shots
    picked: List[Dict[str, Any]] = []
    for raw in only:
        sid = str(raw or "").strip()
        if not sid:
            continue
        if sid not in known:
            raise KeyError(f"unknown shot {sid!r}; breakdown has {', '.join(known) or 'none'}")
        picked.append(known[sid])
    if not picked:
        raise KeyError("--shots listed nothing")
    return picked


def resolve_keyframe(rea_dir: Path, shot: Dict[str, Any], sid: str) -> Optional[Path]:
    """<rea_dir>/shots/<id>_first.jpg, else the shot's own keyframe/first_frame path (relative to rea_dir)."""
    rea = Path(rea_dir)
    cand = rea / "shots" / f"{sid}_first.jpg"
    if cand.is_file():
        return cand
    for key in ("keyframe", "first_frame"):
        val = str(shot.get(key) or "").strip()
        if not val:
            continue
        p = Path(val)
        found = p if p.is_absolute() else (rea / val.replace("\\", "/").lstrip("/"))
        if found.is_file():
            return found
    return None


# --- dialogue / beats --------------------------------------------------------

def dialogue_for(breakdown: Dict[str, Any], shot: Dict[str, Any], start: float, end: float) -> str:
    """The breakdown ASR text that falls inside the shot window, cut to 25 words."""
    parts: List[str] = []
    shot_lines = shot.get("asr") or shot.get("speech") or shot.get("dialogue")
    if isinstance(shot_lines, str):
        parts.append(shot_lines)
    elif isinstance(shot_lines, list):
        parts.extend(str(x.get("text", "")) if isinstance(x, dict) else str(x) for x in shot_lines)
    if not parts:
        for line in ((breakdown.get("speech") or {}).get("lines") or []):
            if not isinstance(line, dict):
                continue
            ls, le = line.get("start"), line.get("end")
            if ls is None or le is None:
                continue
            try:
                ls, le = float(ls), float(le)
            except (TypeError, ValueError):
                continue
            if ls < end and le > start:
                parts.append(str(line.get("text") or ""))
    words = " ".join(t for t in parts if t).split()
    return " ".join(words[:DIALOGUE_MAX_WORDS])


def sfx_for(shot: Dict[str, Any]) -> List[str]:
    raw = shot.get("sfx")
    if not raw:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, (list, tuple)):
        return [str(x.get("text", x)) if isinstance(x, dict) else str(x) for x in raw]
    return []


def onset_source(rea_dir: Path, batch_dir: Path) -> Optional[Path]:
    """The onset map to read: the REA folder's own file wins, then the one this plan generated."""
    for cand in (Path(rea_dir) / ONSET_NAME, Path(batch_dir) / ONSET_NAME):
        if cand.is_file():
            return cand
    return None


def ensure_onsets(rea_dir: Path, batch_dir: Path, breakdown: Dict[str, Any], log=None) -> None:
    """No onset_beats.json in the REA folder but stems/music.wav (or original.wav)? Probe into the batch dir."""
    rea, batch = Path(rea_dir), Path(batch_dir)
    if (rea / ONSET_NAME).is_file():
        return
    wav = next((rea / "stems" / n for n in ("music.wav", "original.wav")
                if (rea / "stems" / n).is_file()), None)
    if wav is None:
        return
    shots = [{"id": shot_ids(sh, i), "start": sh.get("start"), "end": sh.get("end")}
             for i, sh in enumerate(breakdown.get("shots") or [])]
    result = rea_onset_probe.probe(str(wav), shots=shots)
    wp_state.atomic_write(batch / ONSET_NAME, json.dumps(result, indent=2, ensure_ascii=False))
    if log:
        log("rea_onsets", {"source": str(wav), "bpm": result.get("bpm"),
                           "onsets": len(result.get("onsets") or [])})


def beats_for(src: Optional[Path], shot: Dict[str, Any], sid: str) -> List[float]:
    """Per-shot absolute beat times from the onset map, else the shot's own beats."""
    if src is not None:
        try:
            data = json.loads(Path(src).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        for entry in data.get("shots") or []:
            if isinstance(entry, dict) and str(entry.get("id") or "") == sid:
                return [float(b) for b in entry.get("beats") or []]
    return [float(b) for b in (shot.get("beats") or [])]


# --- 18+ gate ----------------------------------------------------------------

def gate_18plus(read: Any, sid: str) -> Optional[str]:
    """Adult-only floor on the raw still read; returns the offending text, or None when it passes.

    Fail closed: a youth/under-18 cue in the read, or anything the builder's own 18+ check rejects."""
    text = json.dumps(read, ensure_ascii=False)
    for rx in (wp_lint.YOUTH_RE, wp_lint.UNDER18_AGE_RE):
        m = rx.search(text)
        if m:
            return m.group(0)
    try:
        br._check_writer_18plus(text, {"still_read": read})
    except Exception as exc:  # WriterNotReady and anything else the check raises
        return str(exc)
    return None


# --- vision read plumbing ----------------------------------------------------

def _wp_bundle(log) -> tuple:
    """(client, cfg) from render_writer_pipeline's config loader; a missing config file is not fatal offline."""
    try:
        cfg = wp.load_config()
    except (OSError, ValueError):
        cfg = {}
    cfg = dict(cfg)
    cfg.setdefault("model_alias", "writer")
    return wp_llm.Client(cfg, log), cfg


# --- plan --------------------------------------------------------------------

def plan(batch_dir: Path, rea_dir: Path, names: Optional[Sequence[str]] = None,
         character: Optional[str] = None, lane: str = "parody", aspect: str = "9:16",
         shots: Optional[Sequence[str]] = None, log=None) -> int:
    """Build the batch skeleton. Prints the final line and returns the exit code."""
    log = log or (lambda *a, **k: None)
    batch, rea = Path(batch_dir), Path(rea_dir)
    try:
        breakdown = load_breakdown(rea)
    except (OSError, ValueError) as exc:
        print(f"NOT_READY breakdown {rea}/breakdown.json: {exc}")
        return 3
    try:
        selected = select_shots(breakdown, shots)
    except KeyError as exc:
        print(f"NOT_READY shots: {exc}")
        return 3

    # keyframes first: one missing frame means the whole batch is not ready, before any vision call
    frames: Dict[str, Path] = {}
    for i, shot in enumerate(selected):
        sid = shot_ids(shot, i)
        kf = resolve_keyframe(rea, shot, sid)
        if kf is None:
            print(f"NOT_READY keyframe {sid}: {rea / 'shots' / (sid + '_first.jpg')}")
            return 3
        frames[sid] = kf

    ensure_onsets(rea, batch, breakdown, log)
    onset_src = onset_source(rea, batch)
    client, cfg = _wp_bundle(log)

    views: List[Dict[str, Any]] = []
    briefs: List[Dict[str, Any]] = []
    for i, shot in enumerate(selected):
        sid = shot_ids(shot, i)
        view = rsp.shot_view(shot, i)
        beats = beats_for(onset_src, shot, sid)
        shot_dir = batch / "shots" / sid
        still = shot_dir / "_inputs" / f"{sid}_first.jpg"
        still.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(frames[sid]), str(still))

        read = wp._ensure_still_read_raw(shot_dir, str(still), None, client, cfg, log)
        produced = shot_dir / "still_read.json"
        if produced.exists():
            # the H3 build writes its own still_read.json for the edited still later on
            produced.rename(shot_dir / "raw_still_read.json")

        blocked = gate_18plus(read, sid)
        if blocked is not None:
            (shot_dir / "clip_NOT_READY.txt").write_text(
                f"NOT_READY 18+ gate {sid}: {blocked}\n", encoding="utf-8")
            print(f"NOT_READY 18+ gate {sid}: {blocked}")
            return 3

        brief = {
            "shot_id": sid,
            "seconds": view["seconds"],
            "parts": rsp.plan_frames(view["seconds"], beats, view["shot_start"]),
            "camera_h3_vocab": rsp.camera_vocab(view["camera"]),
            "dialogue": dialogue_for(breakdown, shot, view["shot_start"],
                                     view["shot_start"] + view["seconds"]),
            "sfx": sfx_for(shot),
            "beats": beats,
            "seed": SEED_BASE + i,
        }
        wp_state.atomic_write(shot_dir / "shot_brief.json", json.dumps(brief, indent=2, ensure_ascii=False))
        views.append({"shot_id": sid, "seconds": view["seconds"], "start": view["shot_start"],
                      "shot_start": view["shot_start"], "beats": beats, "camera": view["camera"]})
        briefs.append(brief)

    try:
        cast_lock = rsp.build_cast_lock(names, character, lane, aspect, views)
    except ValueError as exc:
        print(f"NOT_READY cast: {exc}")
        return 3
    wp_state.atomic_write(batch / "parody_cast_lock.json", json.dumps(cast_lock, indent=2, ensure_ascii=False))
    rsp.write_batch_card(batch, cast_lock, views)

    total_parts = sum(len(b["parts"]) for b in briefs)
    print(f"READY plan {batch} shots={len(briefs)} parts={total_parts}")
    return 0


# --- shared shot plumbing ------------------------------------------------------

def _load_json_obj(path: Path) -> Dict[str, Any]:
    """A JSON object, or {} when missing/corrupt/not-an-object (never raises)."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _shot_dirs(batch: Path, only: Optional[str] = None) -> List[Path]:
    """The shot dirs to run a stage over; `only` selects a single shot id (KeyError when unknown)."""
    if only:
        d = batch / "shots" / str(only)
        if not d.is_dir():
            raise KeyError(f"unknown shot {only!r}")
        return [d]
    return sorted((batch / "shots").glob("shot_*"))


def _lock_override(lock: Dict[str, Any], sid: str) -> Dict[str, Any]:
    for o in lock.get("shot_overrides") or []:
        if isinstance(o, dict) and str(o.get("shot_id") or "") == sid:
            return o
    return {}


def flux_mode_for(brief: Dict[str, Any], lock: Dict[str, Any], sid: str) -> str:
    """shot_brief flux_mode, else the cast lock's, else rea_edit; a new_pose shot override forces rea_pose."""
    ovr = _lock_override(lock, sid)
    if ovr.get("new_pose") is True or str(ovr.get("flux_mode") or "").strip().lower() == "new_pose":
        return FLUX_MODE_POSE
    return str(brief.get("flux_mode") or lock.get("flux_mode") or FLUX_MODE_DEFAULT)


# --- flux (C5) -----------------------------------------------------------------

def flux(batch: Path, only: Optional[str] = None, queue: bool = False, yes_derrick: bool = False) -> int:
    """Build (and with --queue run) the Flux still for every shot that has a Hermes flux_prompt.txt.

    One shot at a time: a failed or skipped shot is reported and the next shot still runs; the queue only
    drops the returned still into `_inputs/<id>_edited.png`. Hermes owns retries (it may rewrite the prompt);
    this stage never loops.
    """
    if queue and not yes_derrick:
        print("NOT_READY flux: --queue requires --yes-derrick")
        return 3
    batch = Path(batch)
    lock = _load_json_obj(batch / "parody_cast_lock.json")
    if not lock:
        print(f"NOT_READY flux cast lock: {batch}/parody_cast_lock.json")
        return 2
    try:
        shot_dirs = _shot_dirs(batch, only)
    except KeyError as exc:
        print(f"NOT_READY flux: {exc}")
        return 3

    canvas = list(lock.get("canvas") or [768, 1344])[:2]
    width, height = int(canvas[0]), int(canvas[1])
    flux_id = dict(lock.get("flux_identity") or {})
    h3 = dict(lock.get("h3_identity") or {})
    refmod = str(flux_id.get("refmod") or "").strip()
    names = [str(n).strip() for n in (h3.get("names") or []) if str(n).strip()]
    character = str(h3.get("character") or "").strip() or None
    hybrid = bool(lock.get("hybrid"))
    loras: List[Dict[str, Any]] = []
    if hybrid and str(flux_id.get("lora") or "").strip():
        loras = [{"name": str(flux_id["lora"]), "strength": float(flux_id.get("lora_strength") or 0.60)}]

    done = failed = 0
    for shot_dir in shot_dirs:
        sid = shot_dir.name
        if (shot_dir / "clip_NOT_READY.txt").is_file():
            continue
        prompt_file = shot_dir / "flux_prompt.txt"
        if not prompt_file.is_file():
            print(f"NOT_READY {sid} flux_prompt.txt missing")
            failed += 1
            continue
        brief = _load_json_obj(shot_dir / "shot_brief.json")
        kwargs: Dict[str, Any] = {
            "refmods": [refmod] if refmod else [],
            "loras": loras,
            "image": str(shot_dir / "_inputs" / f"{sid}_first.jpg"),
            "width": width,
            "height": height,
            "seed": int(brief.get("seed") or SEED_BASE),
            "character": character,
            "names": names or None,
            "dry_run": not queue,
        }
        if hybrid:
            kwargs["refmod_strength"] = HYBRID_REFMOD_STRENGTH
            kwargs["retention"] = HYBRID_RETENTION
        rep = flux_still.build_flux_still(shot_dir / "flux", prompt_file.read_text(encoding="utf-8").strip(),
                                          flux_mode_for(brief, lock, sid), **kwargs)
        if not isinstance(rep, dict) or str(rep.get("status")) != "READY":
            reason = str(rep.get("reason") or "?") if isinstance(rep, dict) else "?"
            print(f"NOT_READY flux {sid}: {reason}")
            failed += 1
            continue
        if queue:
            qres = flux_still.queue_flux_still(shot_dir / "flux") or {}
            still = str(qres.get("still") or "")
            if int(qres.get("rc") or 0) != 0 or not still or not Path(still).is_file():
                print(f"NOT_READY queue {sid}: {str(qres.get('stderr') or 'no still returned').strip()[:200]}")
                failed += 1
                continue
            dst = shot_dir / "_inputs" / f"{sid}_edited.png"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(still, str(dst))
            print(f"EDITED {sid} {dst}")
        done += 1
    print(f"READY flux {batch} shots={done} failed={failed}")
    return 3 if failed else 0


# --- build (C5) ----------------------------------------------------------------

def build(batch: Path, only: Optional[str] = None) -> int:
    """Run render_writer_pipeline.py (--prose-file, never --queue/--yes-derrick/--fix-once) per ready shot.

    A shot is ready when it has `_inputs/<id>_edited.png`, `hermes_prose.txt` and no clip_NOT_READY.txt.
    Each shot's `build_report.json` is recorded as {id, status, reason} in `<batch_dir>/build_status.json`;
    a NOT_READY shot prints `STUCK <id> <reason>` for Hermes to rewrite the prose once and rerun this stage.
    """
    batch = Path(batch)
    lock = _load_json_obj(batch / "parody_cast_lock.json")
    if not lock:
        print(f"NOT_READY build cast lock: {batch}/parody_cast_lock.json")
        return 2
    try:
        shot_dirs = _shot_dirs(batch, only)
    except KeyError as exc:
        print(f"NOT_READY build: {exc}")
        return 3

    h3 = dict(lock.get("h3_identity") or {})
    names = [str(n).strip() for n in (h3.get("names") or []) if str(n).strip()]
    character = str(h3.get("character") or "").strip() or None
    aspect = str(lock.get("aspect") or "9:16")

    records: List[Dict[str, Any]] = []
    stuck = 0
    for shot_dir in shot_dirs:
        sid = shot_dir.name
        if (shot_dir / "clip_NOT_READY.txt").is_file():
            continue
        edited = shot_dir / "_inputs" / f"{sid}_edited.png"
        prose = shot_dir / "hermes_prose.txt"
        if not edited.is_file() or not prose.is_file():
            continue
        brief = _load_json_obj(shot_dir / "shot_brief.json")
        parts = brief.get("parts") or _lock_override(lock, sid).get("parts") or []
        frames = parts[0].get("frames") if parts and isinstance(parts[0], dict) else None
        cmd = [sys.executable, str(PIPELINE_SCRIPT), str(shot_dir),
               "--prose-file", str(prose),
               "--still", str(edited),
               "--still-mode", "guide",
               "--position", str(brief.get("position") or "talk"),
               "--ask", f"rea remake {sid}"]
        if frames is not None:
            cmd += ["--frames", str(int(frames))]
        cmd += ["--aspect", aspect]
        if names and str(lock.get("lane") or "parody") != "oc":
            cmd += ["--names", *names]
        elif character:
            cmd += ["--character", character]
        elif names:
            cmd += ["--names", *names]
        proc = subprocess.run(cmd, cwd=str(PARODY_DIR), capture_output=True, text=True)
        report = _load_json_obj(shot_dir / "build_report.json")
        if report:
            st = str(report.get("status") or "?")
            reason = str(report.get("reason") or "")
        else:
            st = "NOT_READY"
            reason = f"no build_report.json (rc={getattr(proc, 'returncode', '?')})"
        records.append({"id": sid, "status": st, "reason": reason})
        if st == "NOT_READY":
            stuck += 1
            print(f"STUCK {sid} {reason}")
    wp_state.atomic_write(batch / BUILD_STATUS_NAME, json.dumps(records, indent=2, ensure_ascii=False))
    print(f"READY build {batch} shots={len(records)} stuck={stuck}")
    return 3 if stuck else 0


# --- status ------------------------------------------------------------------

def _build_status(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "corrupt"
    if isinstance(data, dict):
        for key in ("status", "pick", "result"):
            if data.get(key):
                return str(data[key])
    return "?"


def status(batch_dir: Path) -> int:
    """One line per shot listing which pipeline artifacts exist. Prints nothing when there are no shots."""
    batch = Path(batch_dir)
    shot_dirs = sorted((batch / "shots").glob("shot_*"))
    if not shot_dirs:
        print(f"DONE status {batch} shots=0")
        return 0
    for shot_dir in shot_dirs:
        sid = shot_dir.name
        cells = []
        for label, rel, is_build in STATUS_ARTIFACTS:
            path = shot_dir / rel.format(sid=sid)
            if is_build:
                cells.append(f"{label}={_build_status(path) if path.is_file() else 'none'}")
            else:
                cells.append(f"{label}={'yes' if path.is_file() else 'no'}")
        print(f"{sid} " + " ".join(cells))
    return 0


# --- CLI ---------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="rea_parody_remake.py",
                                 description="REA-video -> FLUX -> H3Max parody remake orchestrator")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("plan", help="build the batch skeleton (reads, briefs, cast lock, batch card)")
    pl.add_argument("batch_dir")
    pl.add_argument("--rea-dir", required=True, help="rea-video decomposition folder")
    pl.add_argument("--names", nargs="+", default=None, help='parody cast, e.g. --names "Sydney Sweeney as Star"')
    pl.add_argument("--character", default=None, help="OC lane character (FCSydny|FCMegan)")
    pl.add_argument("--lane", choices=("parody", "oc"), default="parody")
    pl.add_argument("--aspect", choices=("9:16", "16:9"), default="9:16")
    pl.add_argument("--shots", default=None, help="comma-separated shot ids (default: every breakdown shot)")

    st = sub.add_parser("status", help="list which artifacts each shot already has")
    st.add_argument("batch_dir")

    fx = sub.add_parser("flux", help="build (and with --queue run) the Flux still for each shot's flux_prompt.txt")
    fx.add_argument("batch_dir")
    fx.add_argument("--shot", default=None, help="only this shot id")
    fx.add_argument("--queue", action="store_true", help="queue on AlienPc ComfyUI (requires --yes-derrick)")
    fx.add_argument("--yes-derrick", action="store_true", help="Derrick approved the prompts; required with --queue")

    bd = sub.add_parser("build", help="run render_writer_pipeline over hermes_prose.txt + the edited still")
    bd.add_argument("batch_dir")
    bd.add_argument("--shot", default=None, help="only this shot id")

    args = ap.parse_args(argv)
    try:
        batch = check_batch_dir(args.batch_dir)
    except ValueError as exc:
        print(f"NOT_READY batch_dir {exc}")
        return 2

    if args.cmd == "status":
        return status(batch)
    if args.cmd == "flux":
        return flux(batch, only=args.shot, queue=args.queue, yes_derrick=args.yes_derrick)
    if args.cmd == "build":
        return build(batch, only=args.shot)

    names = [n for n in (args.names or []) if str(n).strip()]
    if names and args.character:
        print("NOT_READY cast: pass --names or --character, not both")
        return 2
    if not names and not args.character:
        print("NOT_READY cast: plan needs --names or --character")
        return 2
    only = [s for s in re.split(r"[,\s]+", args.shots or "") if s]
    return plan(batch, Path(args.rea_dir), names=names or None, character=args.character,
                lane=args.lane, aspect=args.aspect, shots=only or None)


if __name__ == "__main__":
    raise SystemExit(main())
