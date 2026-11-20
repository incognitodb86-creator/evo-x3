"""Render writer pipeline state: dialogue blacklist, cloned phrases, scene state, logs (Max Architect 3, 2026-11-13)."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from build_request import R11_HAND
from wp_lint import norm, WORD_RE, clone_hash

WHITELIST = ("inside her", "inside her mouth", "fully sheathed", "hips flush", "flush against", "buried in her", "deep in her",
             "sheathed", "aside", "to one side", "primary motion", "per second", "every second", "every half second", "cycle",
             "strokes a second", "stroke a second", "beats a second", "beat a second", "tempo", "bpm", "at first",
             "as it builds", "by the end", "as the clip ends", "on the last frame",
             # required wordings & structural syntax the rules themselves prescribe (never a clone)
             "his hand on her throat", "s3 's left hand", "s3 s left hand", "he does x she does y",
             "the camera is a", "the camera holds a", "medium two shot", "two shot at", "at hip height",
             "at chest height", "at eye level", "keeping her face", "keeping his face", "keeping both faces",
             "keeping the join", "says in a", "says in a low", "in a low voice", "in a soft voice",
             "his penis", "her vagina", "her anus", "her mouth", "her vulva", "from behind", "until his hips",
             "his hips are", "her buttocks", "against her buttocks", "where it stays", "hands and knees",
             "on her back", "on all fours", "wet skin slaps", "on every stroke",
             "shot 1 the camera is", "the camera is", "camera is a", "says in a", "stays buried in",
             "stays deep in", "flush against her", "pushes into her", "drives into her", "slides into her",
             "sinks into her", "thrusts into her", "to one side at her hip")


_STRIP_TAG_RE = re.compile(r"(?i)</?d>|\[(?:English|Shot\s+\d+)\]")
_CLONE_STOP = frozenset({
    "a", "an", "the", "and", "or", "as", "at", "by", "for", "from", "in", "into", "is", "are",
    "it", "its", "of", "on", "to", "until", "with", "he", "she", "his", "her", "hers", "they",
    "their", "them", "s1", "s2", "s3", "d", "english", "shot", "stays", "where", "every",
})


def now_ct() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CT")


def atomic_write(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    for i in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:  # Windows: a reader holds the file for a moment
            time.sleep(0.2 * (i + 1))
    os.replace(tmp, path)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---- dialogue blacklist (FIFO, cap 20, atomic) ------------------------------------------------------------------------
def load_blacklist(path: Path, log=None) -> List[Dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        for ln in path.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            r = json.loads(ln)
            if not isinstance(r, dict) or not isinstance(r.get("line"), str):
                raise ValueError("row without a line string")
            rows.append(r)
        return rows
    except Exception as e:  # corrupt: keep the bad file in _archive, rebuild empty, warn (never block)
        arch = path.parent / "_archive"
        arch.mkdir(exist_ok=True)
        bad = arch / f"{path.name}.corrupt-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.move(str(path), str(bad))
        atomic_write(path, "")
        if log:
            log("blacklist_corrupt_rebuilt", {"error": f"{type(e).__name__}: {e}", "moved_to": str(bad)})
        return []


def update_blacklist(path: Path, new_lines: Iterable[str], run: str, cap: int = 20, log=None) -> List[Dict[str, Any]]:
    rows = load_blacklist(path, log)
    have = {norm(r["line"]) for r in rows}
    for l in new_lines:
        if norm(l) and norm(l) not in have:
            rows.append({"line": l, "run": run, "ts": now_ct()})
            have.add(norm(l))
    rows = rows[-cap:]
    atomic_write(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    return rows


# ---- recent outputs (for 6-gram clone detection) -----------------------------------------------------------------------
def append_recent(path: Path, run: str, dd: str, cap: int = 20) -> None:
    rows = []
    if Path(path).exists():
        for ln in Path(path).read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(ln))
            except ValueError:
                continue
    rows.append({"run": run, "dd": dd, "ts": now_ct()})
    rows = rows[-cap:]
    atomic_write(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def load_recent(path: Path) -> List[str]:
    out = []
    if Path(path).exists():
        for ln in Path(path).read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(ln)["dd"])
            except (ValueError, KeyError):
                continue
    return out


# ---- cloned phrases --------------------------------------------------------------------------------------------------
_QUOTED_RE = re.compile(r"[\"\u201c]([^\"\u201d\n]{3,200})[\"\u201d]")


def _strip_whitelist(p: str) -> str:
    t = " " + norm(p) + " "
    for w in sorted(WHITELIST, key=len, reverse=True):
        t = t.replace(" " + w + " ", " ")
    return " ".join(t.split())



_EXAMPLES_BLOCK_RE = re.compile(r"(?im)^EXAMPLES\b[\s\S]*?(?=^SHAPE\b|\Z)")
_WORKED_EXAMPLE_RE = re.compile(r"(?im)^##\s*Worked example\b[\s\S]*?(?=^##\s|\Z)")


def default_wording_example_paths() -> List[Path]:
    """Return skill reference files containing worked prompt examples to include in the 6-gram clone gate."""
    p = Path(__file__).resolve().parents[2] / "skills" / "h3-prompting" / "references" / "wording.md"
    return [p] if p.is_file() else []


def _r11_hand_sixgrams() -> frozenset:
    """Six-word runs of the required verbatim R11 hand-lock clause; never flagged as cloned."""
    w = WORD_RE.findall(norm(R11_HAND))
    return frozenset(" ".join(w[i:i + 6]) for i in range(max(0, len(w) - 5)))


_R11_HAND_EXCLUDED = _r11_hand_sixgrams()
_R11_HAND_NORM = norm(R11_HAND)


def _is_r11_hand_phrase(phrase: str) -> bool:
    pn = norm(phrase)
    return bool(pn) and (pn in _R11_HAND_EXCLUDED or pn == _R11_HAND_NORM)


def _sixgrams_from_text(text: str) -> List[str]:
    w = WORD_RE.findall(norm(_STRIP_TAG_RE.sub(" ", text or "")))
    out: List[str] = []
    for g in {" ".join(w[i:i + 6]) for i in range(max(0, len(w) - 5))}:
        if g in _R11_HAND_EXCLUDED:
            continue
        rem = [tok for tok in _strip_whitelist(g).split() if tok not in _CLONE_STOP]
        if len(rem) >= 3:
            out.append(g)
    return out


def example_sixgrams(prompt_text: str) -> List[str]:
    """Distinctive 6-grams from EXAMPLES / Worked example blocks (structural phrases are whitelisted)."""
    chunks: List[str] = []
    for rx in (_EXAMPLES_BLOCK_RE, _WORKED_EXAMPLE_RE):
        for m in rx.finditer(prompt_text or ""):
            chunks.append(m.group(0))
    if not chunks:
        return []
    out: List[str] = []
    for c in chunks:
        out.extend(_sixgrams_from_text(c))
    return out


def build_cloned(prompt_text: str, recent: List[str], extra_texts: Optional[Sequence[str]] = None) -> List[str]:
    """Every quoted string of >=4 words in the prompt, plus every 6-gram the prompt shares with >=2 of the last 20
    outputs, plus worked examples from writer_prompt and h3-prompting/references/wording.md."""
    out: List[str] = []
    for m in _QUOTED_RE.finditer(prompt_text):
        q = norm(m.group(1))
        if len(q.split()) >= 4 and len(_strip_whitelist(q).split()) >= 3:
            out.append(q)
    # 6-word runs from the EXAMPLES / Worked example blocks are a clone gate even on a first copy
    # (quoted strings above already cover dialogue; this catches unquoted narrative).
    out.extend(example_sixgrams(prompt_text))
    if extra_texts is None:
        extra_texts = [p.read_text(encoding="utf-8") for p in default_wording_example_paths()]
    for et in extra_texts:
        eg = example_sixgrams(et)
        out.extend(eg if eg else _sixgrams_from_text(et))
    pw = WORD_RE.findall(norm(_STRIP_TAG_RE.sub(" ", prompt_text)))
    pgrams = {" ".join(pw[i:i + 6]) for i in range(max(0, len(pw) - 5))}
    counts: Dict[str, int] = {}
    for dd in recent[-20:]:
        w = WORD_RE.findall(norm(_STRIP_TAG_RE.sub(" ", dd)))
        for g in {" ".join(w[i:i + 6]) for i in range(max(0, len(w) - 5))} & pgrams:
            counts[g] = counts.get(g, 0) + 1
    for g, c in counts.items():
        if c >= 2:
            rem = [tok for tok in _strip_whitelist(g).split() if tok not in _CLONE_STOP]
            if len(rem) >= 3:
                out.append(g)
    seen, uniq = set(), []
    for p in out:
        if _is_r11_hand_phrase(p):
            continue
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def refresh_cloned(cloned_path: Path, prompt_text: str, prompt_sha: str, recent: List[str]) -> List[str]:
    phrases = build_cloned(prompt_text, recent)
    hashed = list(dict.fromkeys(clone_hash(p) for p in phrases if norm(p)))
    header = f"# auto-generated {now_ct()} from writer prompt sha256 {prompt_sha}; recent outputs {len(recent)}\n"
    atomic_write(cloned_path, header + "".join(h + "\n" for h in hashed))
    return hashed


# ---- logs ------------------------------------------------------------------------------------------------------------
class Log:
    def __init__(self, log_dir: Path, retention_days: int = 14, cap_mb: int = 50):
        self.dir = Path(log_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / f"pipeline_{datetime.datetime.now().strftime('%Y%m%d')}.jsonl"
        self.prune(retention_days, cap_mb)

    def prune(self, days: int, cap_mb: int) -> None:
        """14-day / 50 MB retention: old logs move to logs\\_archive (never deleted)."""
        arch = self.dir / "_archive"
        files = sorted(self.dir.glob("pipeline_*.jsonl"), key=lambda p: p.stat().st_mtime)
        cutoff = time.time() - days * 86400
        total = sum(p.stat().st_size for p in files)
        for p in files:
            if p == self.path:
                continue
            if p.stat().st_mtime < cutoff or total > cap_mb * 1024 * 1024:
                arch.mkdir(exist_ok=True)
                total -= p.stat().st_size
                shutil.move(str(p), str(arch / p.name))

    def __call__(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        row = {"ts": now_ct(), "event": event}
        row.update(data or {})
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


# ---- scene state -----------------------------------------------------------------------------------------------------
def scene_path(runs_root: Path, scene_id: str) -> Path:
    return Path(runs_root) / "_scenes" / re.sub(r"[^\w.-]+", "_", scene_id) / "scene_state.json"


def load_scene(p: Path) -> List[Dict[str, Any]]:
    if not Path(p).exists():
        return []
    try:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        return d.get("clips", []) if isinstance(d, dict) else []
    except ValueError:
        return []


def reset_scene(p: Path, scene_id: str) -> None:
    """Clip 1 of a scene starts a fresh scene_state (PM acc4 #3). Old file is moved to _archive, never deleted."""
    p = Path(p)
    if p.exists():
        arch = p.parent / "_archive"
        arch.mkdir(parents=True, exist_ok=True)
        dest = arch / f"{p.stem}-{now_ct().replace(':', '')}{p.suffix}"
        n = 1
        while dest.exists():
            dest = arch / f"{p.stem}-{now_ct().replace(':', '')}-{n}{p.suffix}"
            n += 1
        p.rename(dest)
    atomic_write(p, json.dumps({"scene_id": scene_id, "updated": now_ct(), "clips": []}, indent=2, ensure_ascii=False))


def append_scene(p: Path, scene_id: str, entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    clips = [c for c in load_scene(p) if c.get("clip_id") != entry.get("clip_id")]
    clips.append(entry)
    atomic_write(Path(p), json.dumps({"scene_id": scene_id, "updated": now_ct(), "clips": clips}, indent=2, ensure_ascii=False))
    return clips


def archive_old_scenes(runs_root: Path, days: int = 30) -> List[str]:
    root = Path(runs_root) / "_scenes"
    moved = []
    if not root.exists():
        return moved
    cutoff = time.time() - days * 86400
    for d in root.iterdir():
        if d.is_dir() and d.name != "_archive":
            f = d / "scene_state.json"
            if f.exists() and f.stat().st_mtime < cutoff:
                (root / "_archive").mkdir(exist_ok=True)
                shutil.move(str(d), str(root / "_archive" / d.name))
                moved.append(d.name)
    return moved
