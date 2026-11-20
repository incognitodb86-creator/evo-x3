#!/usr/bin/env python3
"""Pick diverse render-ready stills from PixlStash (contact sheet and/or MEDIA: symlinks).

Smart Score (1.0-5.0 upstream scale) is strictly a quality floor (>= 2.2 by default; None passes so
brand-new unscored Flux/imported stills stay visible) and is NEVER the primary sort.
Character/Smart-Set queries use GET /api/v1/pictures (never character_id on /pictures/search, which
hits SQLite bind limits on >32k libraries), filter by requested orientation + min_short_edge, dedup
stacks (1 pick per stack_id), exclude recent runs/*/pick.json picks, and stratify across recent
imports, strong matches, and random-fresh candidates.
"""
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
from typing import Iterable, Sequence
from PIL import Image, ImageDraw

PIXL_BASE = "http://127.0.0.1:9537"
TOKEN_FILE = Path.home() / ".config/pixlstash/render-read.token"
DEFAULT_RUNS_DIR = Path("/home/evo/AI/community/runs")
DEFAULT_PIXL_LIB = "/home/evo/AI/5slock/libraries/"
DEFAULT_RECENT_PICKS = 30
DEFAULT_MIN_SMART_SCORE = 2.2
DEFAULT_MIN_LIKENESS = 0.55
DEFAULT_MIN_SHORT_EDGE = 768
FETCH_LIMIT = 120
RECENT_IMPORT_LIMIT = 40
TOP_STRONG_POOL = 12
SHEET_SIZE = 6

PIC_FIELDS = "id,file_path,format,width,height,score,smart_score,likeness_score,stack_id,imported_at"


def _token() -> str:
    tok = os.environ.get("PIXL_KEY", "").strip()
    if tok:
        return tok
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


def _auth_header(tok: str) -> dict[str, str]:
    return {"Authorization": "Bear" + f"er {tok}"}


def _get_json(path: str, tok: str):
    req = urllib.request.Request(f"{PIXL_BASE}{path}", headers=_auth_header(tok))
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def _get_bytes(path: str, tok: str) -> bytes:
    req = urllib.request.Request(f"{PIXL_BASE}{path}", headers=_auth_header(tok))
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def _unwrap_pictures(data) -> list[dict]:
    if isinstance(data, list):
        return [p for p in data if isinstance(p, dict)]
    if isinstance(data, dict):
        for k in ("pictures", "items", "results"):
            if isinstance(data.get(k), list):
                return [p for p in data[k] if isinstance(p, dict)]
    return []


def _norm_still_ref(val: str | int | None) -> str:
    s = str(val or "").strip().replace("\\", "/")
    if not s:
        return ""
    if s.startswith(DEFAULT_PIXL_LIB):
        s = s[len(DEFAULT_PIXL_LIB):]
    return s.lstrip("/")


def _is_video(pic: dict) -> bool:
    if pic.get("is_video"):
        return True
    fmt = str(pic.get("format") or "").strip().upper()
    if fmt in {"MP4", "WEBM", "MOV", "MKV", "AVI"}:
        return True
    fp = str(pic.get("file_path") or "").lower()
    return fp.endswith((".mp4", ".webm", ".mov", ".mkv", ".avi"))


def _passes_smart_floor(pic: dict, min_smart_score: float) -> bool:
    """Smart Score is a quality floor only; None passes so newly imported unscored stills are never hidden."""
    if min_smart_score <= 0:
        return True
    val = pic.get("smart_score")
    if val is None:
        return True
    try:
        return float(val) >= float(min_smart_score)
    except (TypeError, ValueError):
        return True


def _norm_aspect(aspect: str | None) -> str:
    s = (aspect or "any").strip().lower()
    if s in ("9:16", "portrait", "vertical"):
        return "9:16"
    if s in ("16:9", "landscape", "horizontal", "widescreen"):
        return "16:9"
    return "any"


def _matches_aspect(pic: dict, aspect: str) -> bool:
    if aspect == "any":
        return True
    w, h = pic.get("width"), pic.get("height")
    if not (isinstance(w, (int, float)) and isinstance(h, (int, float)) and w > 0 and h > 0):
        return False
    return (h > w) if aspect == "9:16" else (w > h)


def _passes_min_short_edge(pic: dict, min_short_edge: int) -> bool:
    if min_short_edge <= 0:
        return True
    w, h = pic.get("width"), pic.get("height")
    if not (isinstance(w, (int, float)) and isinstance(h, (int, float)) and w > 0 and h > 0):
        return True  # don't drop records that omit dimensions
    return min(int(w), int(h)) >= int(min_short_edge)


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


def _dedup_stacks(pics: Sequence[dict]) -> list[dict]:
    """Keep at most one picture per stack_id (and deduplicate by picture id)."""
    seen_ids: set[str] = set()
    seen_stacks: set[str] = set()
    out: list[dict] = []
    for p in pics:
        pid = str(p.get("id", ""))
        if pid and pid in seen_ids:
            continue
        sid = p.get("stack_id")
        if sid is not None and str(sid).strip() != "":
            skey = str(sid).strip()
            if skey in seen_stacks:
                continue
            seen_stacks.add(skey)
        if pid:
            seen_ids.add(pid)
        out.append(p)
    return out


def _build_pictures_url(
    *,
    character_id: int | None,
    set_id: int | None,
    tags: Sequence[str],
    rejected_tags: Sequence[str],
    sort: str,
    limit: int,
) -> str:
    params: list[tuple[str, str]] = [
        ("format", "JPEG"),
        ("format", "PNG"),
        ("fields", PIC_FIELDS),
        ("sort", sort),
        ("limit", str(limit)),
    ]
    if character_id is not None:
        params.append(("character_id", str(character_id)))
    if set_id is not None:
        params.append(("set_id", str(set_id)))
    for t in tags:
        if t.strip():
            params.append(("tag", t.strip()))
    for rt in rejected_tags:
        if rt.strip():
            params.append(("rejected_tag", rt.strip()))
    return "/api/v1/pictures?" + urllib.parse.urlencode(params)


def _fetch_candidates(
    tok: str,
    *,
    query: str | None,
    character_id: int | None,
    set_id: int | None,
    tags: Sequence[str],
    rejected_tags: Sequence[str],
    fetch_limit: int = FETCH_LIMIT,
) -> tuple[list[dict], set[str]]:
    """Fetch primary candidates and recent-import IDs without hitting >32k SQLite bind limits."""
    recent_import_ids: set[str] = set()
    q = (query or "").strip()

    if character_id is not None or set_id is not None or tags or rejected_tags:
        # Character / Smart-Set / tag queries ALWAYS use /api/v1/pictures (never character_id on /pictures/search).
        primary_sort = "CHARACTER_LIKENESS" if character_id is not None else "IMPORTED_AT"
        primary_url = _build_pictures_url(
            character_id=character_id,
            set_id=set_id,
            tags=tags,
            rejected_tags=rejected_tags,
            sort=primary_sort,
            limit=fetch_limit,
        )
        hits = _unwrap_pictures(_get_json(primary_url, tok))

        if primary_sort != "IMPORTED_AT":
            recent_url = _build_pictures_url(
                character_id=character_id,
                set_id=set_id,
                tags=tags,
                rejected_tags=rejected_tags,
                sort="IMPORTED_AT",
                limit=RECENT_IMPORT_LIMIT,
            )
            try:
                recent_hits = _unwrap_pictures(_get_json(recent_url, tok))
            except Exception:
                recent_hits = []
            seen = {str(p.get("id")) for p in hits}
            for rp in recent_hits:
                rpid = str(rp.get("id"))
                recent_import_ids.add(rpid)
                if rpid not in seen:
                    hits.append(rp)
                    seen.add(rpid)
        else:
            for rp in hits[:RECENT_IMPORT_LIMIT]:
                recent_import_ids.add(str(rp.get("id")))

        # Optional free-text boost if query was also supplied with character_id/set_id.
        if q:
            q_tokens = [tok_w for tok_w in q.lower().split() if len(tok_w) >= 3]
            if q_tokens:
                boosted: list[dict] = []
                for p in hits:
                    hay = f"{p.get('file_path', '')} {' '.join(str(x) for x in (p.get('tags') or []))}".lower()
                    matched = sum(1 for w in q_tokens if w in hay)
                    if matched:
                        p = dict(p)
                        p["score"] = round(float(p.get("score") or 0.0) + matched / len(q_tokens), 4)
                    boosted.append(p)
                hits = boosted
        return hits, recent_import_ids

    if not q:
        raise ValueError("Provide --query, --character-id, --set-id, or --tag")
    params = {"query": q, "limit": str(fetch_limit)}
    hits = _unwrap_pictures(_get_json("/api/v1/pictures/search?" + urllib.parse.urlencode(params), tok))
    return hits, recent_import_ids


def _stratified_sample(
    fresh: list[dict],
    recent_import_ids: set[str],
    limit: int,
    rng: random.Random,
    *,
    page: int = 1,
    has_explicit_excludes: bool = False,
) -> list[dict]:
    """Stratified selection across floor-passing fresh pool: recent imports + strong matches + random-fresh."""
    if len(fresh) <= limit:
        out = list(fresh)
        rng.shuffle(out)
        return out

    page_num = max(1, int(page))
    if not has_explicit_excludes and page_num > 1:
        offset = (page_num - 1) * limit
        pool = fresh[offset:] + fresh[:offset]
    else:
        pool = list(fresh)

    chosen: list[dict] = []
    chosen_ids: set[str] = set()
    chosen_stacks: set[str] = set()

    def _can_take(p: dict) -> bool:
        pid = str(p.get("id", ""))
        if pid in chosen_ids:
            return False
        sid = p.get("stack_id")
        if sid is not None and str(sid).strip() != "" and str(sid).strip() in chosen_stacks:
            return False
        return True

    def _take_from(bucket: list[dict], count: int) -> None:
        avail = [p for p in bucket if _can_take(p)]
        if not avail or count <= 0:
            return
        k = min(count, len(avail))
        for p in rng.sample(avail, k):
            chosen.append(p)
            chosen_ids.add(str(p.get("id", "")))
            sid = p.get("stack_id")
            if sid is not None and str(sid).strip() != "":
                chosen_stacks.add(str(sid).strip())

    n_recent = min(2, max(0, limit // 3)) if recent_import_ids else 0
    n_strong = min(2, max(1, limit // 3))

    # 1. Recent imports stratum (or newest imported_at)
    if n_recent > 0:
        recent_bucket = [p for p in pool if str(p.get("id", "")) in recent_import_ids]
        _take_from(recent_bucket[: max(8, n_recent * 4)], n_recent)

    # 2. Strong likeness / relevance stratum (never sorted by smart_score)
    strong_bucket = pool[: max(TOP_STRONG_POOL, limit * 2)]
    _take_from(strong_bucket, min(n_strong, limit - len(chosen)))

    # 3. Random-fresh across the wider floor-passing pool
    _take_from(pool, limit - len(chosen))
    return chosen


def _create_media_symlinks(
    items: Sequence[dict],
    media_dir: Path,
    pixl_lib: Path = Path(DEFAULT_PIXL_LIB),
) -> list[str]:
    media_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for item in items:
        fp = _norm_still_ref(item.get("file_path"))
        if not fp:
            continue
        ext = Path(fp).suffix.lstrip(".") or "jpg"
        link = media_dir / f"pixl_{item['id']}.{ext}"
        target = pixl_lib / fp
        if link.is_symlink() or link.exists():
            link.unlink()
        os.symlink(str(target), str(link))
        item["media_path"] = str(link)
        lines.append(f"MEDIA:{link}")
    return lines


def build_sheet(
    query: str | None = None,
    out_path: Path | None = None,
    character_id: int | None = None,
    min_likeness: float = DEFAULT_MIN_LIKENESS,
    *,
    set_id: int | None = None,
    tags: Sequence[str] = (),
    rejected_tags: Sequence[str] = (),
    min_smart_score: float = DEFAULT_MIN_SMART_SCORE,
    aspect: str = "any",
    min_short_edge: int = DEFAULT_MIN_SHORT_EDGE,
    limit: int = SHEET_SIZE,
    exclude: Iterable[str | int] | None = None,
    page: int = 1,
    recent_n: int = DEFAULT_RECENT_PICKS,
    runs_dir: Path | None = DEFAULT_RUNS_DIR,
    seed: int | None = None,
    media_dir: Path | None = None,
    pixl_lib: Path = Path(DEFAULT_PIXL_LIB),
) -> list[dict]:
    tok = _token()
    hits, recent_import_ids = _fetch_candidates(
        tok,
        query=query,
        character_id=character_id,
        set_id=set_id,
        tags=tags,
        rejected_tags=rejected_tags,
    )

    non_video = [p for p in hits if not _is_video(p)]

    # 1. Character likeness floor (fallback to all non-video if likeness empties)
    if character_id is not None:
        like_ok = [p for p in non_video if (p.get("likeness_score") or 0.0) >= min_likeness]
        pool = like_ok if like_ok else list(non_video)
    else:
        pool = list(non_video)

    # 2. Smart Score floor ONLY (None passes; NEVER sorted by smart_score)
    smart_ok = [p for p in pool if _passes_smart_floor(p, min_smart_score)]
    smart_floor_fallback = False
    if smart_ok:
        pool = smart_ok
    else:
        smart_floor_fallback = True

    # 3. Minimum short edge filter (if dimensions are present)
    edge_ok = [p for p in pool if _passes_min_short_edge(p, min_short_edge)]
    if edge_ok:
        pool = edge_ok

    # 4. Requested orientation filter (falls back with needs_reframe=True so Hermes calls Flux reframe)
    want_aspect = _norm_aspect(aspect)
    needs_reframe = False
    if want_aspect != "any":
        aspect_ok = [p for p in pool if _matches_aspect(p, want_aspect)]
        if aspect_ok:
            pool = aspect_ok
        else:
            needs_reframe = True

    # Rank by likeness / relevance ONLY — NEVER by smart_score!
    ranked_all = sorted(
        pool,
        key=lambda p: (
            round(float(p.get("score") or 0.0), 4),
            round(float(p.get("likeness_score") or 0.0), 4),
            str(p.get("imported_at") or ""),
        ),
        reverse=True,
    )
    ranked_all = _dedup_stacks(ranked_all)

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
    want_n = max(1, int(limit))

    chosen = _stratified_sample(
        fresh,
        recent_import_ids,
        want_n,
        rng,
        page=page,
        has_explicit_excludes=bool(exclude_refs),
    )
    if len(chosen) < want_n:
        need = want_n - len(chosen)
        chosen_ids = {str(p.get("id", "")) for p in chosen}
        for fb in (recent_excluded + explicit_excluded):
            if need <= 0:
                break
            if str(fb.get("id", "")) not in chosen_ids:
                chosen.append(fb)
                chosen_ids.add(str(fb.get("id", "")))
                need -= 1

    summary: list[dict] = []
    for idx, pic in enumerate(chosen):
        summary.append({
            "rank": idx + 1,
            "id": pic["id"],
            "file_path": pic.get("file_path"),
            "width": pic.get("width"),
            "height": pic.get("height"),
            "stack_id": pic.get("stack_id"),
            "score": pic.get("score"),
            "smart_score": pic.get("smart_score"),
            "likeness_score": pic.get("likeness_score"),
            "needs_reframe": needs_reframe,
            "smart_floor_fallback": smart_floor_fallback,
            "seed": rng_seed,
        })

    if out_path is not None:
        cell_w, cell_h, pad, cap_h = 360, 360, 12, 34
        cols = min(3, max(1, len(chosen)))
        rows = max(1, (len(chosen) + cols - 1) // cols)
        sheet = Image.new(
            "RGB",
            (cols * cell_w + (cols + 1) * pad, rows * (cell_h + cap_h) + (rows + 1) * pad),
            (24, 24, 28),
        )
        draw = ImageDraw.Draw(sheet)
        for idx, pic in enumerate(chosen):
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
            like_s = f"{like:.2f}" if isinstance(like, (int, float)) else "-"
            smart_s = f"{smart:.2f}" if isinstance(smart, (int, float)) else "-"
            w, h = pic.get("width"), pic.get("height")
            dim_s = f" {int(w)}x{int(h)}" if isinstance(w, (int, float)) and isinstance(h, (int, float)) else ""
            rf_s = " [reframe]" if needs_reframe else ""
            label = f"#{idx+1} id={pid} like={like_s} ss={smart_s}{dim_s}{rf_s}"
            draw.text((x0 + 4, y0 + cell_h + 6), label[:52], fill=(240, 240, 240))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out_path)

    if media_dir is not None:
        _create_media_symlinks(summary, media_dir, pixl_lib=pixl_lib)

    return summary


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pick diverse PixlStash stills (Smart Score >= 2.2 floor, never sort).")
    ap.add_argument("--query", default=None, help="Free-text search query (optional if --character-id/--set-id/--tag set)")
    ap.add_argument("--character-id", type=int, default=None, help="PixlStash character_id (uses /api/v1/pictures)")
    ap.add_argument("--set-id", type=int, default=None, help="PixlStash Smart Picture Set ID")
    ap.add_argument("--tag", action="append", default=[], help="Required tag (repeatable)")
    ap.add_argument("--rejected-tag", action="append", default=[], help="Excluded tag (repeatable)")
    ap.add_argument("--out", default=None, help="Output 2x3 contact sheet PNG path")
    ap.add_argument("--media-dir", default=None, help="Create space-free symlinks here and emit MEDIA: lines")
    ap.add_argument("--limit", type=int, default=SHEET_SIZE, help="Number of stills to pick (default 6)")
    ap.add_argument("--min-smart-score", type=float, default=DEFAULT_MIN_SMART_SCORE,
                    help="Smart Score quality floor (default 2.2; None always passes; 0 disables)")
    ap.add_argument("--min-likeness", type=float, default=DEFAULT_MIN_LIKENESS)
    ap.add_argument("--aspect", default="any", choices=("any", "9:16", "16:9", "portrait", "landscape"))
    ap.add_argument("--min-short-edge", type=int, default=DEFAULT_MIN_SHORT_EDGE)
    ap.add_argument("--exclude", action="append", default=[], help="Comma-separated picture IDs or paths to exclude")
    ap.add_argument("--page", type=int, default=1, help="1-based page for fresh candidate slice")
    ap.add_argument("--recent-n", type=int, default=DEFAULT_RECENT_PICKS, help="Exclude last N runs/*/pick.json stills")
    ap.add_argument("--runs-dir", default=str(DEFAULT_RUNS_DIR), help="Runs directory containing */pick.json")
    ap.add_argument("--seed", type=int, default=None, help="Optional RNG seed to rebuild a previous sheet")
    args = ap.parse_args(argv)

    if not args.out and not args.media_dir:
        ap.error("Specify at least one of --out or --media-dir")

    res = build_sheet(
        args.query,
        Path(args.out) if args.out else None,
        character_id=args.character_id,
        min_likeness=args.min_likeness,
        set_id=args.set_id,
        tags=args.tag,
        rejected_tags=args.rejected_tag,
        min_smart_score=args.min_smart_score,
        aspect=args.aspect,
        min_short_edge=args.min_short_edge,
        limit=args.limit,
        exclude=args.exclude,
        page=args.page,
        recent_n=args.recent_n,
        runs_dir=Path(args.runs_dir) if args.runs_dir else None,
        seed=args.seed,
        media_dir=Path(args.media_dir) if args.media_dir else None,
    )
    if args.media_dir:
        for item in res:
            if item.get("media_path"):
                print(f"MEDIA:{item['media_path']}")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
