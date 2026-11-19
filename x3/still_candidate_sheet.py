#!/usr/bin/env python3
"""Build a labelled 2x3 contact sheet from PixlStash fresh search hits (plan-v32 P4.5, ST1)."""
from __future__ import annotations

import argparse
import io
import json
import os
import random
import secrets
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable
from PIL import Image, ImageDraw

PIXL_BASE = "http://127.0.0.1:9537"
TOKEN_FILE = Path.home() / ".config/pixlstash/render-read.token"
DEFAULT_RUNS_DIR = Path("/home/evo/AI/community/runs")
DEFAULT_PIXL_LIB = "/home/evo/AI/5slock/libraries/"
DEFAULT_RECENT_PICKS = 20
SEARCH_LIMIT = 60
TOP_POOL = 18
SHEET_SIZE = 6


def _token() -> str:
    tok = os.environ.get("PIXL_KEY", "").strip()
    if tok:
        return tok
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


def _get_json(path: str, tok: str):
    req = urllib.request.Request(f"{PIXL_BASE}{path}", headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def _get_bytes(path: str, tok: str) -> bytes:
    req = urllib.request.Request(f"{PIXL_BASE}{path}", headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def _norm_still_ref(val: str | int | None) -> str:
    s = str(val or "").strip().replace("\\", "/")
    if not s:
        return ""
    if s.startswith(DEFAULT_PIXL_LIB):
        s = s[len(DEFAULT_PIXL_LIB):]
    return s.lstrip("/")


def load_recent_picks(runs_dir: Path | None = DEFAULT_RUNS_DIR, limit: int = DEFAULT_RECENT_PICKS) -> set[str]:
    """Read the last `limit` runs/*/pick.json 'still' values (newest mtime first)."""
    if runs_dir is None or limit <= 0 or not runs_dir.is_dir():
        return set()
    pick_files = [p for p in runs_dir.glob("*/pick.json") if p.is_file()]
    pick_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    recent: set[str] = set()
    for pf in pick_files:
        if len(recent) >= limit:
            break
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        norm = _norm_still_ref(data.get("still"))
        if norm:
            recent.add(norm)
    return recent


def _parse_excludes(exclude: Iterable[str | int] | None) -> set[str]:
    out: set[str] = set()
    if not exclude:
        return out
    for raw in exclude:
        for part in str(raw).split(","):
            norm = _norm_still_ref(part)
            if norm:
                out.add(norm)
    return out


def _matches_refs(pic: dict, refs: set[str]) -> bool:
    if not refs:
        return False
    pid = str(pic.get("id", "")).strip()
    if pid and pid in refs:
        return True
    fp = _norm_still_ref(pic.get("file_path"))
    if not fp:
        return False
    if fp in refs:
        return True
    suffix = "/" + fp
    return any(r.endswith(suffix) for r in refs)


def build_sheet(
    query: str,
    out_path: Path,
    character_id: int | None = None,
    min_likeness: float = 0.55,
    *,
    exclude: Iterable[str | int] | None = None,
    page: int = 1,
    recent_n: int = DEFAULT_RECENT_PICKS,
    runs_dir: Path | None = DEFAULT_RUNS_DIR,
    seed: int | None = None,
) -> list[dict]:
    tok = _token()
    params = {"query": query, "limit": str(SEARCH_LIMIT)}
    if character_id is not None:
        params["character_id"] = str(character_id)
    hits = _get_json("/api/v1/pictures/search?" + urllib.parse.urlencode(params), tok)
    if not isinstance(hits, list):
        hits = hits.get("pictures", []) if isinstance(hits, dict) else []

    filtered = [
        p for p in hits
        if not p.get("is_video")
        and (character_id is None or (p.get("likeness_score") or 0.0) >= min_likeness)
    ]
    if not filtered:
        filtered = [p for p in hits if not p.get("is_video")]

    ranked_all = sorted(
        filtered,
        key=lambda p: (
            round(float(p.get("score") or 0.0), 4),
            float(p.get("smart_score") or 0.0),
            float(p.get("likeness_score") or 0.0),
        ),
        reverse=True,
    )

    recent_refs = load_recent_picks(runs_dir, limit=recent_n)
    exclude_refs = _parse_excludes(exclude)

    fresh: list[dict] = []
    recent_excluded: list[dict] = []
    explicit_excluded: list[dict] = []
    for pic in ranked_all:
        if _matches_refs(pic, exclude_refs):
            explicit_excluded.append(pic)
        elif _matches_refs(pic, recent_refs):
            recent_excluded.append(pic)
        else:
            fresh.append(pic)

    rng_seed = seed if seed is not None else secrets.randbits(32)
    rng = random.Random(rng_seed)
    page_num = max(1, int(page))

    if not exclude_refs and page_num > 1:
        offset = (page_num - 1) * SHEET_SIZE
        primary_fresh = fresh[offset : offset + TOP_POOL]
        overflow_fresh = fresh[offset + TOP_POOL :] + fresh[:offset]
    else:
        primary_fresh = fresh[:TOP_POOL]
        overflow_fresh = fresh[TOP_POOL:]

    if len(primary_fresh) >= SHEET_SIZE:
        ranked = rng.sample(primary_fresh, SHEET_SIZE)
    else:
        ranked = rng.sample(primary_fresh, len(primary_fresh))
        need = SHEET_SIZE - len(ranked)
        if need > 0 and overflow_fresh:
            ranked.extend(overflow_fresh[:need])
            need = SHEET_SIZE - len(ranked)
        if need > 0:
            fallback = recent_excluded + explicit_excluded
            ranked.extend(fallback[:need])

    cell_w, cell_h, pad, cap_h = 360, 360, 12, 34
    cols, rows = 3, 2
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * pad, rows * (cell_h + cap_h) + (rows + 1) * pad), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)

    summary = []
    for idx, pic in enumerate(ranked):
        pid = pic["id"]
        r_i, c_i = divmod(idx, cols)
        x0 = pad + c_i * (cell_w + pad)
        y0 = pad + r_i * (cell_h + cap_h + pad)
        raw = _get_bytes(f"/api/v1/pictures/thumbnails/{pid}.webp", tok)
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((cell_w, cell_h))
        sheet.paste(im, (x0 + (cell_w - im.width) // 2, y0 + (cell_h - im.height) // 2))
        like = pic.get("likeness_score")
        smart = pic.get("smart_score")
        like_s = f"{like:.2f}" if isinstance(like, (int, float)) else "-"; smart_s = f"{smart:.2f}" if isinstance(smart, (int, float)) else "-"; label = f"#{idx+1} id={pid} like={like_s} smart={smart_s}"
        draw.text((x0 + 4, y0 + cell_h + 6), label[:48], fill=(240, 240, 240))
        summary.append({
            "rank": idx + 1,
            "id": pid,
            "file_path": pic.get("file_path"),
            "score": pic.get("score"),
            "smart_score": smart,
            "likeness_score": like,
            "seed": rng_seed,
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--character-id", type=int, default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--exclude", action="append", default=[], help="Comma-separated picture IDs or paths to exclude")
    ap.add_argument("--page", type=int, default=1, help="1-based page for fresh candidate slice")
    ap.add_argument("--recent-n", type=int, default=DEFAULT_RECENT_PICKS, help="Exclude last N runs/*/pick.json stills")
    ap.add_argument("--runs-dir", default=str(DEFAULT_RUNS_DIR), help="Runs directory containing */pick.json")
    ap.add_argument("--seed", type=int, default=None, help="Optional RNG seed to rebuild a previous sheet")
    ap.add_argument("--min-likeness", type=float, default=0.55)
    args = ap.parse_args()
    res = build_sheet(
        args.query,
        Path(args.out),
        character_id=args.character_id,
        min_likeness=args.min_likeness,
        exclude=args.exclude,
        page=args.page,
        recent_n=args.recent_n,
        runs_dir=Path(args.runs_dir) if args.runs_dir else None,
        seed=args.seed,
    )
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
