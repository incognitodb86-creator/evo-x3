#!/usr/bin/env python3
"""REA: REA-video -> FLUX -> H3Max parody remake orchestrator
(`plan` + `status` + `flux` + `build` + `queue` + `assemble`).

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

`queue` (C7) hands every built-and-READY shot to AlienPc with `queue-remote.sh`, one shot at a time, and waits for
that shot's 2x `clip/render_ok.json` before starting the next one; the per-shot outcomes go to
`<batch_dir>/queue_status.json`. `assemble` (C7) concatenates the 2x clips of the DONE shots in shot order with hard
cuts, trims the padded shots back, matches every clip's color to the first clip (`rea_color_match`) and writes
`<batch_dir>/final_2x.mp4` (`--bgm` mixes the REA stems music under the dialogue, `--publish` copies the master to
`/srv/renders`).

Usage:
  rea_parody_remake.py plan   <batch_dir> --rea-dir <dir> (--names NAME... | --character FCSydny|FCMegan)
                              [--lane parody|oc] [--aspect 9:16|16:9] [--shots shot_001,shot_002]
  rea_parody_remake.py status <batch_dir>
  rea_parody_remake.py flux   <batch_dir> [--shot ID] [--queue --yes-derrick]
  rea_parody_remake.py build  <batch_dir> [--shot ID]
  rea_parody_remake.py queue  <batch_dir> --yes-derrick [--shot ID]
  rea_parody_remake.py assemble <batch_dir> [--bgm] [--publish]

stdlib + the parody modules only; vision/HTTP happen inside render_writer_pipeline._ensure_still_read_raw,
ffmpeg/ffprobe happen inside rea_color_match.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import build_request as br  # noqa: E402
import flux_still  # noqa: E402
import rea_color_match as rcm  # noqa: E402
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
# queue (C7): the AlienPc submitter, the watch on its 2x output, and the per-shot outcome file
QUEUE_REMOTE_SCRIPT = "/home/evo/AI/render/x3/queue-remote.sh"  # REA_QUEUE_REMOTE overrides (tests)
QUEUE_STATUS_NAME = "queue_status.json"
QUEUE_POLL_SEC = 15.0  # REA_QUEUE_POLL_SEC overrides (tests)
QUEUE_TIMEOUT_SEC = 40 * 60.0  # REA_QUEUE_TIMEOUT_SEC overrides (tests)
RENDER_OK_REL = "clip/render_ok.json"
DEFAULT_CLIP_REL = "clip/clip.mp4"
# assemble (C7)
MASTER_NAME = "final_2x.mp4"
PUBLISH_DIR = "/srv/renders"  # REA_PUBLISH_DIR overrides (tests)
BGM_DB = -14.0
COLOR_SAMPLES = 5  # frames sampled per clip, the rea_color_match default
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
    cast_lock["rea_dir"] = str(rea)  # assemble --bgm reads <rea_dir>/stems/music.wav out of this
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


def _load_records(path: Path) -> List[Dict[str, Any]]:
    """The per-shot records of a *_status.json file: a list of dicts, or [] when missing/corrupt."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if isinstance(data, dict):
        data = data.get("shots") or data.get("records") or []
    return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []


def _all_shot_dirs(batch: Path, lock: Optional[Dict[str, Any]] = None) -> List[Path]:
    """Every shot directory under <batch>/shots/, honoring cast-lock shot_overrides order first."""
    shots_root = Path(batch) / "shots"
    if not shots_root.is_dir():
        return []
    present = {p.name: p for p in sorted(shots_root.iterdir()) if p.is_dir()}
    ordered: List[Path] = []
    seen: set[str] = set()
    cfg = lock if lock is not None else _load_json_obj(Path(batch) / "parody_cast_lock.json")
    for ovr in (cfg.get("shot_overrides") or []):
        sid = str(ovr.get("shot_id") or "") if isinstance(ovr, dict) else ""
        if sid and sid in present and sid not in seen:
            ordered.append(present[sid])
            seen.add(sid)
    for sid, path in present.items():
        if sid not in seen:
            ordered.append(path)
    return ordered


def _shot_dirs(batch: Path, only: Optional[str] = None, lock: Optional[Dict[str, Any]] = None) -> List[Path]:
    """The shot dirs to run a stage over; `only` selects a single shot id (KeyError when unknown)."""
    if only:
        d = batch / "shots" / str(only)
        if not d.is_dir():
            raise KeyError(f"unknown shot {only!r}")
        return [d]
    return _all_shot_dirs(batch, lock=lock)


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
        mode = flux_mode_for(brief, lock, sid)
        src_frame = str(shot_dir / "_inputs" / f"{sid}_first.jpg")
        kwargs: Dict[str, Any] = {
            "refmods": [refmod] if refmod else [],
            "loras": loras,
            "image": str(brief.get("identity_image") or lock.get("identity_image") or src_frame) if mode == FLUX_MODE_POSE else src_frame,
            "width": width,
            "height": height,
            "seed": int(brief.get("seed") or SEED_BASE),
            "character": character,
            "names": names or None,
            "dry_run": not queue,
        }
        if mode == FLUX_MODE_POSE:
            kwargs["pose_image"] = src_frame
        if hybrid:
            kwargs["refmod_strength"] = HYBRID_REFMOD_STRENGTH
            kwargs["retention"] = HYBRID_RETENTION
        rep = flux_still.build_flux_still(shot_dir / "flux", prompt_file.read_text(encoding="utf-8").strip(),
                                          mode, **kwargs)
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


# --- queue (C7) ----------------------------------------------------------------

def queue_remote_script() -> Path:
    """The AlienPc submitter; REA_QUEUE_REMOTE overrides it (tests point at a stub path)."""
    return Path(os.environ.get("REA_QUEUE_REMOTE") or QUEUE_REMOTE_SCRIPT)


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name) or default)
    except (TypeError, ValueError):
        return default


def queue_wait_params() -> tuple:
    """(poll_sec, timeout_sec) of the 2x watch; REA_QUEUE_POLL_SEC / REA_QUEUE_TIMEOUT_SEC override both."""
    poll = _env_float("REA_QUEUE_POLL_SEC", QUEUE_POLL_SEC)
    timeout = _env_float("REA_QUEUE_TIMEOUT_SEC", QUEUE_TIMEOUT_SEC)
    return (poll if poll > 0 else QUEUE_POLL_SEC,
            timeout if timeout >= 0 else QUEUE_TIMEOUT_SEC)


def publish_dir() -> Path:
    """Where `--publish` copies the master; REA_PUBLISH_DIR overrides it (tests use a tmp dir)."""
    return Path(os.environ.get("REA_PUBLISH_DIR") or PUBLISH_DIR)


def clip_path_for(shot_dir: Path, render_ok: Optional[Dict[str, Any]] = None) -> Path:
    """A shot's 2x clip: render_ok.json "clip" (relative to the shot dir), default `clip/clip.mp4`."""
    data = render_ok if render_ok is not None else _load_json_obj(shot_dir / RENDER_OK_REL)
    raw = str(data.get("clip") or "").strip() or DEFAULT_CLIP_REL
    p = Path(raw)
    return p if p.is_absolute() else shot_dir / p


def wait_for_render_ok(shot_dir: Path, poll_sec: Optional[float] = None,
                       timeout_sec: Optional[float] = None) -> Dict[str, Any]:
    """Watch <shot_dir>/clip/render_ok.json for an upscale object; {"status","clip","reason"}.

    Poll-count loop (sleeps between checks, never wall clock), so a mocked time.sleep collapses a 40 minute
    wait into a few iterations. DONE only when the file exists and carries an "upscale" object: a render_ok.json
    from a render without the 2x pass is not a finished shot.
    """
    poll, timeout = queue_wait_params()
    if poll_sec is not None:
        poll = float(poll_sec)
    if timeout_sec is not None:
        timeout = float(timeout_sec)
    ok_path = shot_dir / RENDER_OK_REL
    checks = max(1, int(timeout // poll))
    for i in range(checks):
        data = _load_json_obj(ok_path)
        if isinstance(data.get("upscale"), dict):
            return {"status": "DONE", "clip": str(clip_path_for(shot_dir, data)), "reason": ""}
        if i + 1 < checks:
            time.sleep(poll)
    return {"status": "FAIL", "clip": None,
            "reason": f"no {RENDER_OK_REL} with an upscale object within {timeout:g}s"}


def _write_queue_status(batch: Path, records: Dict[str, Dict[str, Any]], shot_names: Sequence[str]) -> None:
    """Save {id, status, clip} per shot in shot order (ids this batch no longer has stay at the end)."""
    known = set(shot_names)
    ordered = [records[sid] for sid in shot_names if sid in records]
    ordered += [r for sid, r in records.items() if sid not in known]
    wp_state.atomic_write(batch / QUEUE_STATUS_NAME, json.dumps(ordered, indent=2, ensure_ascii=False))


def queue(batch: Path, only: Optional[str] = None, yes_derrick: bool = False) -> int:
    """Queue every built shot on AlienPc, one at a time, and watch for its 2x clip.

    A shot is queueable when its `build_status.json` entry says READY and it has no `clip_NOT_READY.txt`, and a
    shot whose `queue_status.json` entry already says DONE is never queued again. `queue-remote.sh` detaches the
    render, so this stage waits for the shot's 2x render_ok.json before starting the next shot: one GPU job at a
    time, and a FAIL (submit error or timeout) is recorded and the next shot still runs.
    """
    if not yes_derrick:
        print("NOT_READY queue: --yes-derrick is required")
        return 3
    batch = Path(batch)
    try:
        shot_dirs = _shot_dirs(batch, only)
    except KeyError as exc:
        print(f"NOT_READY queue: {exc}")
        return 3
    built_file = batch / BUILD_STATUS_NAME
    if not built_file.is_file():
        print(f"NOT_READY queue {built_file}: run build first")
        return 2
    built = {str(r.get("id") or ""): str(r.get("status") or "") for r in _load_records(built_file)}
    records: Dict[str, Dict[str, Any]] = {str(r.get("id") or ""): r
                                         for r in _load_records(batch / QUEUE_STATUS_NAME) if r.get("id")}
    all_shots = [p.name for p in _all_shot_dirs(batch)]
    script = str(queue_remote_script())
    queued = failed = 0

    for shot_dir in shot_dirs:
        sid = shot_dir.name
        if str(records.get(sid, {}).get("status") or "") == "DONE":
            print(f"SKIP queue {sid} already DONE")
            continue
        if (shot_dir / "clip_NOT_READY.txt").is_file():
            print(f"SKIP queue {sid} clip_NOT_READY.txt")
            continue
        if built.get(sid) != "READY":
            print(f"SKIP queue {sid} build_status={built.get(sid) or 'none'}")
            continue
        queued += 1
        print(f"QUEUED {sid} {script}")
        proc = subprocess.run(["bash", script, str(shot_dir), "--yes-derrick"],
                              capture_output=True, text=True)
        rc = int(getattr(proc, "returncode", 0) or 0)
        if rc != 0:
            err = (str(getattr(proc, "stderr", "") or "").strip()
                   or str(getattr(proc, "stdout", "") or "").strip())
            res: Dict[str, Any] = {"status": "FAIL", "clip": None,
                                   "reason": f"queue-remote.sh rc={rc} {err[:160]}".strip()}
        else:
            res = wait_for_render_ok(shot_dir)
        records[sid] = {"id": sid, "status": res["status"], "clip": res["clip"]}
        _write_queue_status(batch, records, all_shots)
        if res["status"] == "DONE":
            print(f"DONE clip {sid} {res['clip']}")
        else:
            failed += 1
            print(f"FAIL clip {sid} {res['reason']}")

    print(f"READY queue {batch} queued={queued} failed={failed}")
    return 3 if failed else 0


# --- assemble (C7) -------------------------------------------------------------

def shot_trim_frames(brief: Dict[str, Any], lock: Dict[str, Any], sid: str) -> Optional[int]:
    """Real frames a shot's clip must keep: the sum of its parts' trim_to_frames, or None when unpadded.

    The graph renders every part on the 17n+5 grid, so a shot whose parts were padded (or split across beats)
    renders more frames than the source footage had; the master trims the clip back to the real length.
    """
    parts = brief.get("parts") or _lock_override(lock, sid).get("parts") or []
    parts = [p for p in parts if isinstance(p, dict)]
    if not parts:
        return None
    rendered = sum(int(p.get("frames") or 0) for p in parts)
    real = sum(int(p.get("trim_to_frames") or p.get("frames") or 0) for p in parts)
    return real if rendered > real > 0 else None


def bgm_path_for(batch: Path, lock: Optional[Dict[str, Any]] = None) -> Optional[Path]:
    """`<rea-dir>/stems/music.wav` for --bgm: the rea_dir recorded in the cast lock, else batch_meta.json."""
    meta = _load_json_obj(batch / "batch_meta.json")
    for src in (lock or {}, meta):
        raw = str(src.get("rea_dir") or src.get("rea-dir") or "").strip()
        if not raw:
            continue
        wav = Path(raw) / "stems" / "music.wav"
        if wav.is_file():
            return wav
    return None


def assemble(batch: Path, bgm: bool = False, publish: bool = False) -> int:
    """Cut the DONE shots' 2x clips into `<batch_dir>/final_2x.mp4` (hard cuts, color matched to the first clip).

    Shot order is the order of `shots/`; the clips come from each shot's render_ok.json (default
    `clip/clip.mp4`), padded shots are trimmed back to their planned frames, and every clip after the first gets a
    lutrgb transfer toward the first clip's channel stats. One ffmpeg call does the whole master.
    """
    batch = Path(batch)
    lock = _load_json_obj(batch / "parody_cast_lock.json")
    done = {str(r.get("id") or "") for r in _load_records(batch / QUEUE_STATUS_NAME)
            if str(r.get("status") or "") == "DONE"}
    if not done:
        print(f"NOT_READY assemble {batch}: no DONE shots in {QUEUE_STATUS_NAME}, run queue first")
        return 2

    clips: List[Dict[str, Any]] = []
    ref_stats: Optional[Any] = None
    for shot_dir in _all_shot_dirs(batch, lock=lock):
        sid = shot_dir.name
        if sid not in done:
            continue
        clip = clip_path_for(shot_dir)
        if not clip.is_file():
            print(f"NOT_READY assemble {sid}: no 2x clip {clip}")
            return 2
        stats = rcm.channel_stats(rcm.sample_frames(str(clip), n=COLOR_SAMPLES))
        if ref_stats is None:
            ref_stats = stats
            lut = None
        else:
            lut = rcm.transfer_expr(stats, ref_stats)
        clips.append({"path": str(clip),
                      "trim_to_frames": shot_trim_frames(_load_json_obj(shot_dir / "shot_brief.json"), lock, sid),
                      "lut": lut})
    if not clips:
        print(f"NOT_READY assemble {batch}: the {len(done)} DONE ids have no shots/ folder")
        return 2

    bgm_wav: Optional[Path] = None
    if bgm:
        bgm_wav = bgm_path_for(batch, lock)
        if bgm_wav is None:
            print(f"NOT_READY assemble bgm: no stems/music.wav for {batch.name} "
                  f"(cast lock or batch_meta.json needs rea_dir)")
            return 2

    out = batch / MASTER_NAME
    cmd = rcm.build_master_cmd(clips, str(out), bgm=str(bgm_wav) if bgm_wav else None, bgm_db=BGM_DB)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    rc = int(getattr(proc, "returncode", 0) or 0)
    if rc != 0 or not out.is_file():
        err = str(getattr(proc, "stderr", "") or "").strip()
        print(f"NOT_READY assemble ffmpeg rc={getattr(proc, 'returncode', '?')} {err[:200]}")
        return 2
    print(f"MASTER {out} clips={len(clips)} luts={sum(1 for c in clips if c['lut'])}")

    if publish:
        pub = publish_dir()
        if pub.is_dir() and os.access(str(pub), os.W_OK):
            dest = pub / f"{batch.name}_{MASTER_NAME}"
            shutil.copy2(str(out), str(dest))
            print(f"PUBLISHED {dest}")
        else:
            print(f"note: --publish skipped, {pub} is not writable")

    print(f"DONE assemble {out}")
    print(f"MEDIA:{out}")
    return 0


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
    shot_dirs = _all_shot_dirs(batch)
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

    qq = sub.add_parser("queue", help="queue every READY shot on AlienPc and wait for its 2x clip, one at a time")
    qq.add_argument("batch_dir")
    qq.add_argument("--shot", default=None, help="only this shot id")
    qq.add_argument("--yes-derrick", action="store_true",
                    help="Derrick approved this batch for the render queue; required")

    asm = sub.add_parser("assemble", help="cut the DONE shots' 2x clips into final_2x.mp4 (hard cuts, color matched)")
    asm.add_argument("batch_dir")
    asm.add_argument("--bgm", action="store_true",
                     help=f"mix <rea-dir>/stems/music.wav at {BGM_DB:g} dB under the dialogue")
    asm.add_argument("--publish", action="store_true",
                     help=f"copy the master to {PUBLISH_DIR}/<batch>_{MASTER_NAME} when that folder is writable")

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
    if args.cmd == "queue":
        return queue(batch, only=args.shot, yes_derrick=args.yes_derrick)
    if args.cmd == "assemble":
        return assemble(batch, bgm=args.bgm, publish=args.publish)

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
