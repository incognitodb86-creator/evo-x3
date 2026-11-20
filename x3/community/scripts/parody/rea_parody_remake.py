#!/usr/bin/env python3
"""REA C4: REA-video -> FLUX -> H3Max parody remake orchestrator (`plan` + `status`).

`plan` turns an rea-video decomposition folder (breakdown.json + shots/*.jpg + stems/*.wav) into an H3 batch:
one run dir per shot under <batch_dir>/shots/, each with the source keyframe in `_inputs/`, a
`raw_still_read.json` vision read (18+ gate, fail closed), and a `shot_brief.json` carrying the frame plan,
the H3 camera words, the dialogue and the beat map Hermes needs. The batch gets `parody_cast_lock.json`
and `batch_card.md` (rea_shot_plan, C2); beats come from `onset_beats.json` (rea_onset_probe, C1) when the
REA folder does not ship one.

`status` prints, per shot, which of the pipeline artifacts already exist.

Usage:
  rea_parody_remake.py plan   <batch_dir> --rea-dir <dir> (--names NAME... | --character FCSydny|FCMegan)
                              [--lane parody|oc] [--aspect 9:16|16:9] [--shots shot_001,shot_002]
  rea_parody_remake.py status <batch_dir>

stdlib + the parody modules only; vision/HTTP happen inside render_writer_pipeline._ensure_still_read_raw.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import build_request as br  # noqa: E402
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

    args = ap.parse_args(argv)
    try:
        batch = check_batch_dir(args.batch_dir)
    except ValueError as exc:
        print(f"NOT_READY batch_dir {exc}")
        return 2

    if args.cmd == "status":
        return status(batch)

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
