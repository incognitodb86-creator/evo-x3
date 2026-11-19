#!/usr/bin/env python3
"""Build a labelled 2x3 contact sheet from PixlStash top-6 ranked search hits (plan-v32 P4.5)."""
from __future__ import annotations

import argparse
import io
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

PIXL_BASE = "http://127.0.0.1:9537"
TOKEN_FILE = Path.home() / ".config/pixlstash/render-read.token"


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


def build_sheet(query: str, out_path: Path, character_id: int | None = None, min_likeness: float = 0.55) -> list[dict]:
    tok = _token()
    params = {"query": query, "limit": "30"}
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

    ranked = sorted(
        filtered,
        key=lambda p: (
            round(float(p.get("score") or 0.0), 4),
            float(p.get("smart_score") or 0.0),
            float(p.get("likeness_score") or 0.0),
        ),
        reverse=True,
    )[:6]

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
        summary.append({"rank": idx + 1, "id": pid, "file_path": pic.get("file_path"), "score": pic.get("score"), "smart_score": smart, "likeness_score": like})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--character-id", type=int, default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    res = build_sheet(args.query, Path(args.out), character_id=args.character_id)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
