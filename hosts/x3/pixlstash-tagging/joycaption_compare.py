#!/usr/bin/env python3
"""Compare JoyCaption Beta One tags and descriptions on PixlStash `jc-test` pictures.

Reads PixlStash and llama-swap keys from existing secret files on disk.
Never prints picture IDs, image bytes, tags, captions, or secrets — counts and timings only.
"""

from __future__ import annotations

import argparse
import base64
import glob
from io import BytesIO
import json
import os
import re
import sys
import time

import httpx
from PIL import Image

PIXLSTASH_URL = "http://127.0.0.1:9537"
LLAMA_SWAP_URL = "http://127.0.0.1:8080"
JOYCAPTION_MODEL = "joycaption"
TRIGGER_TAG = "jc-test"

PIXL_TOKEN_CANDIDATES = (
    "/home/evo/.config/pixlstash/tagger-write.token",
)
PIXL_TOKEN_GLOB = "/home/evo/.config/pixlstash/*.token"
LLM_ENV_CANDIDATES = (
    "/home/evo/.config/evo-x3/llm.env",
    "/etc/evo-x3/llm.env",
)

OUT_DIR = "/home/evo/AI/pixlstash-tagging/jc-compare"
VIDEO_FORMATS = frozenset({"mp4", "webm", "mov", "avi", "mkv", "m4v"})
MAX_IMAGE_EDGE = 1280
MAX_JC_TAGS = 40
STREAM_BATCH_LIMIT = 5000
BULK_FETCH_CHUNK = 200

DANBOORU_PROMPT = (
    "Generate only comma-separated Danbooru tags. Only add general tags. "
    "Include counts (1girl), appearance, clothing, accessories, pose, "
    "expression, actions, background."
)
DESCRIPTIVE_PROMPT = "Write a long detailed description for this image."
SYSTEM_PROMPT = "You are a helpful image captioner."


def read_pixl_token() -> str:
    candidates = list(PIXL_TOKEN_CANDIDATES)
    for path in sorted(glob.glob(PIXL_TOKEN_GLOB)):
        if path not in candidates:
            candidates.append(path)
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                token = handle.read().strip()
            if token:
                return token
        except OSError:
            continue
    raise RuntimeError("No readable PixlStash token file found")


def read_llm_key() -> str:
    for env_path in LLM_ENV_CANDIDATES:
        try:
            with open(env_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    k = key.strip()
                    if k == "LLAMA_SWAP_KEY" or k.startswith("LLM_KEY_"):
                        cleaned = val.strip().strip('"').strip("'")
                        if cleaned:
                            return cleaned
        except OSError:
            continue
    raise RuntimeError("No readable LLM key file found")


def stream_tagged_pictures(client: httpx.Client, tag: str) -> list[tuple[int, str]]:
    pictures: list[tuple[int, str]] = []
    seen: set[int] = set()
    offset = 0
    while True:
        resp = client.get(
            "/api/v1/pictures/stream",
            params={
                "tag": tag,
                "fields": "id,format",
                "batch_limit": STREAM_BATCH_LIMIT,
                "offset": offset,
                "descending": "false",
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        body = resp.json()
        for pic in body.get("pictures", []):
            pid = int(pic["id"])
            if pid not in seen:
                seen.add(pid)
                fmt = str(pic.get("format") or "jpeg").lower()
                pictures.append((pid, fmt))
        if body.get("done"):
            break
        next_off = body.get("next_offset")
        if next_off is None or int(next_off) <= offset:
            break
        offset = int(next_off)
    return pictures


def fetch_existing_tags_batch(client: httpx.Client, pids: list[int]) -> dict[int, set[str]]:
    out: dict[int, set[str]] = {pid: set() for pid in pids}
    for i in range(0, len(pids), BULK_FETCH_CHUNK):
        chunk = pids[i : i + BULK_FETCH_CHUNK]
        resp = client.post(
            "/api/v1/pictures/tags/bulk_fetch",
            json={"picture_ids": chunk},
            timeout=60.0,
        )
        resp.raise_for_status()
        for item in resp.json():
            pid = int(item["id"])
            out[pid] = {
                str(t.get("tag") or "").strip().lower()
                for t in (item.get("tags") or [])
                if t.get("tag")
            }
    return out


def fetch_image_bytes(client: httpx.Client, pid: int, fmt: str) -> bytes:
    if fmt in VIDEO_FORMATS:
        resp = client.get(f"/api/v1/pictures/thumbnails/{pid}.webp", timeout=60.0)
    else:
        try:
            resp = client.get(f"/api/v1/pictures/{pid}.{fmt}", timeout=60.0)
            if resp.status_code in (400, 404, 500):
                resp = client.get(f"/api/v1/pictures/thumbnails/{pid}.webp", timeout=60.0)
        except httpx.HTTPError:
            resp = client.get(f"/api/v1/pictures/thumbnails/{pid}.webp", timeout=60.0)
    resp.raise_for_status()
    return resp.content


def encode_image_b64_jpeg(raw_bytes: bytes) -> str:
    with Image.open(BytesIO(raw_bytes)) as img:
        rgb = img.convert("RGB")
        w, h = rgb.size
        if max(w, h) > MAX_IMAGE_EDGE:
            rgb.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
        buf = BytesIO()
        rgb.save(buf, format="JPEG", quality=88)
        return base64.b64encode(buf.getvalue()).decode("ascii")


def query_joycaption(llm_client: httpx.Client, b64_img: str, prompt: str, max_tokens: int) -> str:
    payload = {
        "model": JOYCAPTION_MODEL,
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            },
        ],
    }
    resp = llm_client.post("/v1/chat/completions", json=payload, timeout=300.0)
    resp.raise_for_status()
    content = (
        resp.json()
        .get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    return str(content).strip()


def parse_danbooru_tags(raw_text: str, limit: int = MAX_JC_TAGS) -> list[str]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    tags: list[str] = []
    seen: set[str] = set()
    for part in re.split(r"[,\n]+", text):
        cleaned = part.strip().lower()
        cleaned = cleaned.strip("\"'`.*•-")
        if cleaned.startswith("jc "):
            cleaned = cleaned[3:].strip()
        cleaned = re.sub(r"\s+", "_", cleaned)
        cleaned = re.sub(r"[^a-z0-9_()\-'/+.]", "", cleaned)
        cleaned = cleaned.strip("_")
        if not cleaned or len(cleaned) < 2 or len(cleaned) > 60:
            continue
        prefixed = f"jc {cleaned}"
        if prefixed not in seen:
            seen.add(prefixed)
            tags.append(prefixed)
            if len(tags) >= limit:
                break
    return tags


def write_description_file(out_dir: str, pid: int, description: str) -> None:
    os.makedirs(out_dir, mode=0o700, exist_ok=True)
    os.chmod(out_dir, 0o700)
    out_path = os.path.join(out_dir, f"{pid}.txt")
    tmp_path = os.path.join(out_dir, f".{pid}.txt.tmp.{os.getpid()}")
    fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(description.rstrip() + "\n")
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, out_path)
        os.chmod(out_path, 0o600)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def is_picture_done(out_dir: str, pid: int) -> bool:
    path = os.path.join(out_dir, f"{pid}.txt")
    try:
        return os.path.isfile(path) and os.path.getsize(path) > 0
    except OSError:
        return False


def run_compare(dry_run: bool, force: bool) -> dict[str, int | float | bool | None]:
    pixl_token = read_pixl_token()
    llm_key = read_llm_key()

    pixl_headers = {"Authorization": f"Bearer {pixl_token}"}
    llm_headers = {
        "Authorization": f"Bearer {llm_key}",
        "Content-Type": "application/json",
    }

    pictures_found = 0
    skipped_already_done = 0
    done = 0
    failed = 0
    total_elapsed = 0.0

    with (
        httpx.Client(base_url=PIXLSTASH_URL, headers=pixl_headers, timeout=60.0) as pixl_client,
        httpx.Client(base_url=LLAMA_SWAP_URL, headers=llm_headers, timeout=300.0) as llm_client,
    ):
        stubs = stream_tagged_pictures(pixl_client, TRIGGER_TAG)
        pictures_found = len(stubs)

        pending: list[tuple[int, str]] = []
        for pid, fmt in stubs:
            if not force and is_picture_done(OUT_DIR, pid):
                skipped_already_done += 1
            else:
                pending.append((pid, fmt))

        if dry_run or not pending:
            return {
                "dry_run": dry_run,
                "pictures_found": pictures_found,
                "skipped_already_done": skipped_already_done,
                "pending": len(pending),
                "done": 0,
                "failed": 0,
                "seconds_per_picture": None,
            }

        existing_by_pid = fetch_existing_tags_batch(
            pixl_client, [pid for pid, _ in pending]
        )

        for pid, fmt in pending:
            t0 = time.monotonic()
            try:
                raw_bytes = fetch_image_bytes(pixl_client, pid, fmt)
                b64_img = encode_image_b64_jpeg(raw_bytes)

                raw_tags_text = query_joycaption(
                    llm_client, b64_img, DANBOORU_PROMPT, max_tokens=512
                )
                jc_tags = parse_danbooru_tags(raw_tags_text, limit=MAX_JC_TAGS)
                if not jc_tags:
                    raise RuntimeError("No tags parsed")

                desc_text = query_joycaption(
                    llm_client, b64_img, DESCRIPTIVE_PROMPT, max_tokens=768
                )
                if not desc_text:
                    raise RuntimeError("Empty description")

                existing = existing_by_pid.get(pid, set())
                for jtag in jc_tags:
                    if jtag.lower() in existing:
                        continue
                    resp = pixl_client.post(
                        f"/api/v1/pictures/{pid}/tags",
                        json={"tag": jtag},
                    )
                    if resp.status_code != 200:
                        raise RuntimeError(f"Tag POST HTTP {resp.status_code}")
                    existing.add(jtag.lower())

                write_description_file(OUT_DIR, pid, desc_text)
                done += 1
            except Exception:
                failed += 1
            finally:
                total_elapsed += time.monotonic() - t0

    processed = done + failed
    sec_per_pic = round(total_elapsed / processed, 2) if processed > 0 else None
    return {
        "dry_run": dry_run,
        "pictures_found": pictures_found,
        "skipped_already_done": skipped_already_done,
        "pending": len(pending),
        "done": done,
        "failed": failed,
        "seconds_per_picture": sec_per_pic,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run JoyCaption Beta One tag + description comparison on PixlStash `jc-test` pictures."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count matching pictures without querying JoyCaption or writing tags/files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-run even if jc-compare/<picture_id>.txt already exists.",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    summary = run_compare(dry_run=args.dry_run, force=args.force)
    print(json.dumps(summary, indent=2))
    return 1 if int(summary["failed"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
