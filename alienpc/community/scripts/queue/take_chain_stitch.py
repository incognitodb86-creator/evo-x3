r"""take_chain_stitch.py - stitch one take-chain run into a single film (CPU only, no GPU, no lock).

Built for the approved plan C:\AI\community\plans\2026-11-03-1955-fc-take-chain-10-plan.md (Stitch section):
hard cuts by the video concat demuxer + a 60 ms audio crossfade at each seam. Reusable for any future
take chain: every cell must share codec, canvas, fps, sample rate and channels, which this script proves
with ffprobe before it writes anything.

Usage:
  python take_chain_stitch.py RUN_DIR [--xfade 0.06] [--name fc_take_chain] [--grid] [--no-key]

Writes, all inside RUN_DIR\_stitch\:
  concat_list.txt        the concat-demuxer list (video-only path)
  _video_only.mp4        video stream, copied bit-for-bit, no audio
  _audio.m4a             the crossfaded audio bed
  <name>.mp4             the film (video copied + audio re-encoded, apad to video length)
  key.csv                one row per cell: cell, seed, prompt_sha256, clip_sha256, frames, size, bytes
  review_grid.png        one labelled mid-frame per cell (chat review; his rule: chat never gets an mp4)

Prints one PROOF line per output (ffprobe facts) and exits 0 only when the film's duration matches the
sum of the cells. Known, by-design cost of the crossfade: the audio bed is (n-1)*xfade shorter than
the video, so the audio leads the video by that much at the last cell; the bed is room tone + breath,
not lip-sync, which is what the plan chose.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

CELL_RE = re.compile(r"^c\d{2}_s\d+$")
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"


def sh(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def probe(path: Path) -> dict:
    """Stream facts of one mp4: video codec/canvas/fps/pix_fmt + audio codec/rate/channels + duration."""
    r = sh([
        FFPROBE, "-v", "error",
        "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels",
        "-show_entries", "format=duration",
        "-of", "json", str(path),
    ])
    if r.returncode:
        raise SystemExit(f"ffprobe failed rc={r.returncode} {path}: {r.stderr.strip()[:300]}")
    data = json.loads(r.stdout)
    out = {"duration": float(data["format"]["duration"]), "path": path}
    for s in data["streams"]:
        if s.get("codec_type") == "video":
            out.update({k: s.get(k) for k in ("codec_name", "width", "height", "r_frame_rate", "pix_fmt")})
        elif s.get("codec_type") == "audio":
            out.update({k: s.get(k) for k in ("codec_name", "sample_rate", "channels")})
    for k in ("codec_name", "width", "height", "r_frame_rate", "pix_fmt", "sample_rate", "channels"):
        if out.get(k) is None:
            raise SystemExit(f"cannot read {k} on {path}")
    return out


def cells(run_dir: Path) -> list[dict]:
    """Every ordered cell: dir with a name like cNN_sSEED, its mp4 and its render_ok.json."""
    found = []
    for d in sorted(p for p in run_dir.iterdir() if p.is_dir() and CELL_RE.match(p.name) and not p.name.startswith("_")):
        clip = d / f"{d.name}.mp4"
        ok = d / "render_ok.json"
        if not clip.exists():
            raise SystemExit(f"MISSING CLIP in {d.name} - refusing to stitch a partial chain")
        meta = json.loads(ok.read_text(encoding="utf-8")) if ok.exists() else {}
        found.append({"cell": d.name, "clip": clip, "meta": meta})
    if len(found) < 2:
        raise SystemExit(f"need at least 2 cells, found {len(found)} in {run_dir}")
    return found


def uniform(cs: list[dict]) -> list[dict]:
    provs = [probe(c["clip"]) for c in cs]
    keys = ("codec_name", "width", "height", "r_frame_rate", "pix_fmt", "sample_rate", "channels")
    base = {k: provs[0][k] for k in keys}
    for p in provs:
        if {k: p[k] for k in keys} != base:
            raise SystemExit(f"cells are not uniform: {base} vs { {k: p[k] for k in keys} } on {p['path']}")
    for p in provs:
        print(f"PROOF cell={p['path'].parent.name} dur={p['duration']:.3f} " + " ".join(f"{k}={base[k]}" for k in keys))
    return provs


def write_key(run_dir: Path, cs: list[dict], out_dir: Path) -> Path:
    path = out_dir / "key.csv"
    cols = ["cell", "seed", "frames", "prompt_sha256", "clip_sha256", "w", "h", "bytes", "rendered_at", "clip_rel"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for c in cs:
            m = c["meta"]
            w.writerow([
                c["cell"], m.get("seed"), m.get("frames"), m.get("prompt_sha256"), m.get("clip_sha256"),
                m.get("w"), m.get("h"), m.get("bytes"), m.get("rendered_at"),
                f"{c['cell']}/{c['clip'].name}",
            ])
    print(f"PROOF key.csv rows={len(cs)} path={path}")
    return path


def build_film(cs: list[dict], provs: list[dict], out_dir: Path, name: str, xfade: float) -> Path:
    lst = out_dir / "concat_list.txt"
    lst.write_text("".join(f"file '{p['path'].as_posix()}'\n" for p in provs), encoding="utf-8")

    vonly = out_dir / "_video_only.mp4"
    r = sh([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-map", "0:v:0", "-c:v", "copy", "-an", str(vonly)])
    if r.returncode:
        raise SystemExit(f"video concat failed rc={r.returncode}: {r.stderr.strip()[:500]}")

    # input 0 is the concatenated video; inputs 1..n are the cells, used for their audio only
    inputs: list[str] = ["-i", str(vonly)]
    for p in provs:
        inputs += ["-i", str(p["path"])]
    parts, prev = [], "[1:a]"
    for i in range(1, len(provs)):
        label = f"a{i:02d}"
        parts.append(f"{prev}[{i + 1}:a]acrossfade=d={xfade:g}:c1=tri:c2=tri[{label}]")
        prev = f"[{label}]"
    af = ";".join(parts) + f";{prev}apad[aout]"
    film = out_dir / f"{name}.mp4"
    r = sh([FFMPEG, "-y", "-loglevel", "error"] + inputs +
           ["-filter_complex", af, "-map", "0:v:0", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart", str(film)])
    if r.returncode:
        raise SystemExit(f"mux failed rc={r.returncode}: {r.stderr.strip()[:500]}")
    return film


def grid(cs: list[dict], out_dir: Path, cell_w: int = 300, at: float = 5.0) -> Path:
    """One labelled mid-frame per cell tiled into a single review image."""
    from PIL import Image, ImageDraw
    frames = []
    for c in cs:
        tmp = out_dir / f"_mid_{c['cell']}.png"
        r = sh([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{at:g}", "-i", str(c["clip"]),
                "-frames:v", "1", str(tmp)])
        if r.returncode or not tmp.exists():
            raise SystemExit(f"mid-frame extract failed for {c['cell']}: {r.stderr.strip()[:300]}")
        frames.append((c["cell"], Image.open(tmp).convert("RGB"), tmp))
    w = cell_w
    h = int(frames[0][1].height * w / frames[0][1].width)
    cols = min(5, len(frames))
    rows = (len(frames) + cols - 1) // cols
    pad, label_h = 6, 20
    sheet = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + label_h + pad) + pad), (16, 16, 16))
    dr = ImageDraw.Draw(sheet)
    for i, (name, img, tmp) in enumerate(frames):
        cx, cy = pad + (i % cols) * (w + pad), pad + (i // cols) * (h + label_h + pad)
        sheet.paste(img.resize((w, h)), (cx, cy + label_h))
        dr.text((cx + 2, cy + 4), f"{name}  t={at:g}s", fill=(240, 240, 240))
    out = sheet
    out_path = out_dir / "review_grid.png"
    out.save(out_path)
    for _, _, tmp in frames:
        tmp.unlink(missing_ok=True)
    print(f"PROOF review_grid path={out_path} size={out.size} cells={len(frames)} t={at}")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--xfade", type=float, default=0.06, help="audio crossfade seconds per seam (plan default 0.060)")
    ap.add_argument("--name", default="fc_take_chain", help="film filename stem")
    ap.add_argument("--grid", action="store_true", help="also build review_grid.png")
    ap.add_argument("--no-key", action="store_true")
    a = ap.parse_args()

    run_dir = Path(a.run_dir).resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"not a directory: {run_dir}")
    out_dir = run_dir / "_stitch"
    out_dir.mkdir(exist_ok=True)

    cs = cells(run_dir)
    provs = uniform(cs)
    if not a.no_key:
        write_key(run_dir, cs, out_dir)
    film = build_film(cs, provs, out_dir, a.name, a.xfade)

    want = sum(p["duration"] for p in provs)
    got = probe(film)
    drift = (len(provs) - 1) * a.xfade  # n-1 seams
    ok = abs(got["duration"] - want) < 0.35
    print(f"PROOF film path={film} dur={got['duration']:.3f} want={want:.3f} delta={got['duration'] - want:+.3f} "
          f"video={got['width']}x{got['height']}@{got['r_frame_rate']} audio={got['codec_name']} "
          f"{got['sample_rate']}Hz ch={got['channels']} bytes={film.stat().st_size}")
    print(f"NOTE audio bed is {drift:.3f} s shorter than video by design ((n-1)*xfade); apad fills the tail; "
          f"the bed is room tone + breath, not lip-sync")
    if a.grid:
        grid(cs, out_dir)
    print(f"STITCH {'OK' if ok else 'FAIL'} cells={len(cs)} xfade={a.xfade:g}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
