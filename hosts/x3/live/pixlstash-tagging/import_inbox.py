#!/usr/bin/env python3
"""Import media in /home/evo/AI/pixl-inbox into PixlStash (Max, Nov 16 2026, Derrick t2002s7376; ST3b caps).
Imported files move to _imported/, explicit failures to _failed/, timed-out or unstarted files stay in the inbox for
the next pass. Prints counts and timings only (never filenames or tokens). Token read from file, never printed.
Usage: sudo -u evo python3 /home/evo/AI/pixlstash-tagging/import_inbox.py"""
from __future__ import annotations

import json
import mimetypes
import os
import shutil
import time
import urllib.request
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover (non-POSIX test host)
    fcntl = None  # type: ignore[assignment]

INBOX = os.environ.get("PIXL_INBOX", "/home/evo/AI/pixl-inbox")
API = os.environ.get("PIXL_IMPORT_API", "http://127.0.0.1:9537/api/v1/pictures/import")
TOKEN_FILE = "<redacted-in-locked-keyfile>"
BATCH_SIZE = max(1, int(os.environ.get("PIXL_IMPORT_BATCH_SIZE", "10")))
MAX_SECONDS = max(1.0, float(os.environ.get("PIXL_IMPORT_MAX_SECONDS", "900")))
BATCH_MAX_SECONDS = max(1.0, float(os.environ.get("PIXL_IMPORT_BATCH_SECONDS", "300")))
POLL_INTERVAL = max(0.05, float(os.environ.get("PIXL_IMPORT_POLL_SECONDS", "3")))
EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".mov")


def _build_multipart(inbox: str, batch: list[str]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    for f in batch:
        ct = mimetypes.guess_type(f)[0] or "application/octet-stream"
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{f}"\r\n'
            f"Content-Type: {ct}\r\n\r\n".encode("utf-8")
        )
        with open(os.path.join(inbox, f), "rb") as fh:
            parts.append(fh.read())
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), boundary


def _acquire_inbox_lock(inbox: str):
    """Non-blocking exclusive flock on <inbox>/.import_inbox.lock (review #7). Returns open fd or None if busy."""
    if fcntl is None:
        return -1
    lock_path = os.path.join(inbox, ".import_inbox.lock")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    return fd


def _release_inbox_lock(fd) -> None:
    if fcntl is None or fd is None or fd < 0:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def run_import(
    inbox: str = INBOX,
    api: str = API,
    token: "<redacted-in-locked-keyfile>"
    batch_size: int = BATCH_SIZE,
    max_seconds: float = MAX_SECONDS,
    batch_max_seconds: float = BATCH_MAX_SECONDS,
    poll_interval: float = POLL_INTERVAL,
) -> dict:
    start = time.monotonic()
    overall_deadline = start + max_seconds
    lock_fd = _acquire_inbox_lock(inbox)
    if lock_fd is None:
        return {
            "files": 0,
            "batches": 0,
            "imported": 0,
            "duplicate": 0,
            "failed": 0,
            "timed_out": 0,
            "remaining": 0,
            "elapsed_s": round(time.monotonic() - start, 2),
            "stopped_reason": "locked",
        }
    try:
        if token is None:
            with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
                token = "<redacted-in-locked-keyfile>"
        headers = {"Authorization": "Bearer " + token}

        files = sorted(
            f for f in os.listdir(inbox)
            if f.lower().endswith(EXT) and os.path.isfile(os.path.join(inbox, f))
        )
        tot = {
            "files": len(files),
            "batches": 0,
            "imported": 0,
            "duplicate": 0,
            "failed": 0,
            "timed_out": 0,
            "remaining": len(files),
            "elapsed_s": 0.0,
            "stopped_reason": "done",
        }
        if not files:
            tot["elapsed_s"] = round(time.monotonic() - start, 2)
            return tot

        os.makedirs(os.path.join(inbox, "_imported"), exist_ok=True)
        os.makedirs(os.path.join(inbox, "_failed"), exist_ok=True)

        processed = 0
        for i in range(0, len(files), batch_size):
            now = time.monotonic()
            if now >= overall_deadline:
                tot["stopped_reason"] = "overall_timeout"
                break
            batch = files[i : i + batch_size]
            tot["batches"] += 1
            batch_deadline = min(overall_deadline, now + batch_max_seconds)
            body, boundary = _build_multipart(inbox, batch)

            post_timeout = max(5.0, min(batch_max_seconds, batch_deadline - time.monotonic()))
            try:
                req = urllib.request.Request(
                    api,
                    data=body,
                    method="POST",
                    headers={**headers, "Content-Type": "multipart/form-data; boundary=" + boundary},
                )
                with urllib.request.urlopen(req, timeout=post_timeout) as resp:
                    tid = json.load(resp)["task_id"]
            except Exception:
                # Leave unfinished files in inbox for the next pass.
                tot["timed_out"] += len(batch)
                tot["stopped_reason"] = "post_error"
                break

            status_obj = None
            while True:
                if time.monotonic() >= batch_deadline:
                    break
                poll_timeout = max(5.0, min(60.0, batch_deadline - time.monotonic()))
                try:
                    sreq = urllib.request.Request(f"{api}/status?task_id={tid}", headers=headers)
                    with urllib.request.urlopen(sreq, timeout=poll_timeout) as sresp:
                        s = json.load(sresp)
                except Exception:
                    s = {}
                if s.get("status") in ("completed", "failed", "error", "cancelled"):
                    status_obj = s
                    break
                rem = batch_deadline - time.monotonic()
                if rem <= 0:
                    break
                time.sleep(min(poll_interval, rem))

            if status_obj is None:
                # Per-batch or overall cap hit: leave this batch in inbox for the next pass.
                tot["timed_out"] += len(batch)
                tot["stopped_reason"] = "overall_timeout" if time.monotonic() >= overall_deadline else "batch_timeout"
                break

            tot["imported"] += status_obj.get("imported_count") or 0
            tot["duplicate"] += status_obj.get("duplicate_count") or 0
            ok = status_obj.get("status") == "completed"
            if not ok:
                tot["failed"] += len(batch)
            dest_dir = os.path.join(inbox, "_imported" if ok else "_failed")
            for f in batch:
                shutil.move(os.path.join(inbox, f), os.path.join(dest_dir, f))
            processed += len(batch)

        tot["remaining"] = len(files) - processed
        tot["elapsed_s"] = round(time.monotonic() - start, 2)
        return tot
    finally:
        _release_inbox_lock(lock_fd)


if __name__ == "__main__":
    print(json.dumps(run_import()))
