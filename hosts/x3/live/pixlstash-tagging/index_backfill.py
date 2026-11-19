#!/usr/bin/env python3
"""Idempotent backfill of `character <Character>` tags from `person <Name>` tags.

Uses index_map to resolve `person <Name>` tags against the community parody INDEX
and aliases, skipping installed OC keys and existing character tags.
Logs and prints counts only — never tag strings, person names, or character names.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import httpx

import index_map

PIXLSTASH_URL = "http://127.0.0.1:9537"
PIXL_TOKEN_FILE = "/home/evo/.config/pixlstash/tagger-write.token"
UNMATCHED_OUT_PATH = "/home/evo/AI/pixlstash-tagging/unmatched-person-names.txt"
BULK_FETCH_CHUNK = 200
STREAM_BATCH_LIMIT = 5000


def read_secret_token(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        token = "<redacted-in-locked-keyfile>"
    if not token:
        raise RuntimeError(f"Empty token file: {path}")
    return token


def stream_picture_ids_for_tag(client: httpx.Client, tag_str: str) -> list[int]:
    pids: list[int] = []
    seen: set[int] = set()
    offset = 0
    while True:
        resp = client.get(
            "/api/v1/pictures/stream",
            params={
                "tag": tag_str,
                "fields": "id",
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
                pids.append(pid)
        if body.get("done"):
            break
        next_off = body.get("next_offset")
        if next_off is None or int(next_off) <= offset:
            break
        offset = int(next_off)
    return pids


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


def write_unmatched_file(path: str, entries: list[tuple[str, int]]) -> None:
    entries_sorted = sorted(entries, key=lambda kv: (-kv[1], kv[0].lower()))
    tmp_path = f"{path}.tmp.{os.getpid()}"
    fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for name, count in entries_sorted:
                handle.write(f"{name}\t{count}\n")
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, path)
        os.chmod(path, 0o600)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def run_backfill(dry_run: bool) -> dict[str, int | bool]:
    token = "<redacted-in-locked-keyfile>"
    mapper = index_map.get_mapper()

    counts: dict[str, int | bool] = {
        "dry_run": dry_run,
        "person_tags_seen": 0,
        "matched": 0,
        "unmatched": 0,
        "oc_skipped": 0,
        "pictures_checked": 0,
        "already_present": 0,
        "character_tags_would_add": 0,
        "character_tags_added": 0,
        "failures": 0,
    }
    unmatched_entries: list[tuple[str, int]] = []

    with httpx.Client(
        base_url=PIXLSTASH_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60.0,
    ) as client:
        tags_resp = client.get("/api/v1/tags")
        tags_resp.raise_for_status()
        all_tags = tags_resp.json()

        person_items = [
            item
            for item in all_tags
            if str(item.get("tag") or "").lower().startswith("person ")
        ]
        counts["person_tags_seen"] = len(person_items)

        for item in person_items:
            tag_str = str(item.get("tag") or "")
            tag_count = int(item.get("count") or 0)
            person_name = tag_str[len("person ") :].strip()
            if not person_name:
                counts["unmatched"] = int(counts["unmatched"]) + 1
                continue

            if mapper.is_oc_name(person_name):
                counts["oc_skipped"] = int(counts["oc_skipped"]) + 1
                continue

            char_names = mapper.map_person_to_characters(person_name)
            if not char_names:
                counts["unmatched"] = int(counts["unmatched"]) + 1
                unmatched_entries.append((person_name, tag_count))
                continue

            counts["matched"] = int(counts["matched"]) + 1
            pids = stream_picture_ids_for_tag(client, tag_str)
            if not pids:
                continue

            existing_by_pid = fetch_existing_tags_batch(client, pids)
            counts["pictures_checked"] = int(counts["pictures_checked"]) + len(pids)

            for pid in pids:
                existing = existing_by_pid.get(pid, set())
                for char_name in char_names:
                    ctag = f"character {char_name}"
                    ctag_lower = ctag.lower()
                    if ctag_lower in existing:
                        counts["already_present"] = int(counts["already_present"]) + 1
                        continue
                    if dry_run:
                        counts["character_tags_would_add"] = int(counts["character_tags_would_add"]) + 1
                        existing.add(ctag_lower)
                    else:
                        added = False
                        for attempt in range(5):
                            try:
                                post_resp = client.post(
                                    f"/api/v1/pictures/{pid}/tags",
                                    json={"tag": ctag},
                                )
                                if post_resp.status_code == 200:
                                    counts["character_tags_added"] = int(counts["character_tags_added"]) + 1
                                    existing.add(ctag_lower)
                                    added = True
                                    time.sleep(0.05)
                                    break
                                if post_resp.status_code in (429, 502, 503) and attempt < 4:
                                    retry_after = float(post_resp.headers.get("Retry-After", 0) or 0)
                                    time.sleep(max(retry_after, 1.5 * (attempt + 1)))
                                    continue
                                break
                            except httpx.HTTPError:
                                if attempt < 4:
                                    time.sleep(1.0 * (attempt + 1))
                                    continue
                        if not added:
                            counts["failures"] = int(counts["failures"]) + 1

    write_unmatched_file(UNMATCHED_OUT_PATH, unmatched_entries)
    return counts


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill character tags from person tags via community INDEX."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute counts and write unmatched-person-names.txt without adding tags.",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    summary = run_backfill(dry_run=args.dry_run)
    print(json.dumps(summary, indent=2))
    return 1 if int(summary["failures"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
