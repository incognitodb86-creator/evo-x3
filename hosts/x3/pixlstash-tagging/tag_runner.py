#!/usr/bin/env python3
"""Unattended resumable PixlStash tagging & face-matching sidecar runner (U44).

Runs Phase A (InsightFace CPU face matching) concurrently in a dedicated thread
alongside N concurrent VLM tagging requests (default N=3) via llama-swap's
gemma4-heretic slot. Uses official PixlStash REST APIs for all reads/writes.
Logs counts and timings only — never image bytes, filenames, tag strings,
captions, face bboxes, or character names.
"""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import datetime, timedelta
import fcntl
from io import BytesIO
import json
import os
import re
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from zoneinfo import ZoneInfo

import httpx

_TAGGER_DIR = os.path.dirname(os.path.abspath(__file__))
if _TAGGER_DIR not in sys.path:
    sys.path.insert(0, _TAGGER_DIR)
import index_map
from PIL import Image

CT_TZ = ZoneInfo("America/Chicago")

PIXLSTASH_URL = "http://127.0.0.1:9537"
LLAMA_SWAP_URL = "http://127.0.0.1:8080"
VLM_MODEL = "joycaption"

PIXL_TOKEN_FILE = "/home/evo/.config/pixlstash/tagger-write.token"
LLM_ENV_FILE = "/home/evo/.config/evo-x3/llm.env"

STATE_DIR = "/home/evo/AI/pixlstash-tagging"
STATE_DB = os.path.join(STATE_DIR, "u42_state.db")

PROGRESS_DIR = "/var/tmp/u42-progress"
PROGRESS_LOG = os.path.join(PROGRESS_DIR, "U42-tagging-progress.log")
PROGRESS_JSON = os.path.join(PROGRESS_DIR, "U42-tagging-progress.json")

LOCK_PATHS = (
    "/home/evo/AI/locks/gpu-render.lock",
    "/home/derekboone/AI/locks/gpu-render.lock",
)
RENDER_PROC_PATTERNS = (
    "run_graph_job",
    "comfyui/main.py",
    "comfyui_auto",
    "queue-remote",
    "remote_comfy",
)

EXPECTED_PICTURE_COUNT = 32964
INSIGHTFACE_STRICT_THRESHOLD = 0.55
VIDEO_FORMATS = frozenset({"mp4", "webm", "mov", "avi", "mkv", "m4v"})
MAX_IMAGE_EDGE = 1280
MAX_NEW_TAGS_PER_PIC = 25
VLM_MAX_TOKENS = 192
PREFETCH_BATCH_SIZE = 200
DEFAULT_VLM_CONCURRENCY = 3
VLM_CONCURRENCY_ENV = "U44_VLM_CONCURRENCY"

GENERIC_PERSON_STOPWORDS = frozenset({
    "woman", "man", "girl", "boy", "person", "people", "female", "male",
    "lady", "gentleman", "model", "actress", "actor", "celebrity", "unknown",
    "none", "n/a", "na", "unidentified", "anonymous", "someone", "subject",
    "adult", "1girl", "1boy", "solo", "human",
})
BOORU_NAMESPACE_SKIP = frozenset({
    "artist", "copyright", "meta", "species", "lore", "rating",
})

# Official JoyCaption Beta One system prompt (fancyfeast/llama-joycaption-beta-one-hf-llava)
# and Booru-like tag list prompts (fpgaminer/joycaption gradio-app/app.py).
SYSTEM_PROMPT = "You are a helpful image captioner."
BOORU_PROMPT = "Write a list of Booru-like tags for this image within 50 words."
BOORU_PERSON_PROMPT = (
    "Write a list of Booru-like tags for this image within 60 words. "
    "If an unnamed face unmistakably belongs to a well-known celebrity or named fictional character, "
    "include character:<name>; otherwise do not guess a name."
)


def now_ct() -> datetime:
    return datetime.now(CT_TZ)


def fmt_ct(dt: datetime | None = None) -> str:
    return (dt or now_ct()).strftime("%Y-%m-%d %H:%M:%S %Z")


def resolve_vlm_concurrency(cli_value: int | None) -> int:
    if cli_value is not None:
        val = cli_value
    else:
        raw_env = os.environ.get(VLM_CONCURRENCY_ENV, "").strip()
        val = int(raw_env) if raw_env else DEFAULT_VLM_CONCURRENCY
    if val < 1 or val > 16:
        raise ValueError(f"vlm_concurrency must be between 1 and 16, got {val}")
    return val


def read_secret_token(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        token = "<redacted-in-locked-keyfile>"
    if not token:
        raise RuntimeError(f"Empty token file: {path}")
    return token


def read_llm_key(env_path: str) -> str:
    with open(env_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            if key.strip().startswith("LLM_KEY_"):
                cleaned = val.strip().strip('"').strip("'")
                if cleaned:
                    return cleaned
    raise RuntimeError(f"No LLM_KEY_* found in {env_path}")


def check_live_render() -> str | None:
    """Return a non-empty reason string if a live render holds the GPU, else None."""
    # Max Architect 2026-11-16 (Derrick t2056u/t2057u): renders run on AlienPc ComfyUI, not this X3 GPU, so X3 tagging never stops for them.
    return None
    for path in LOCK_PATHS:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                raw = handle.read().strip()
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except BlockingIOError:
                    return f"flock held on {os.path.basename(path)}"
                if raw:
                    match = re.search(r"(\d+)", raw)
                    if match:
                        pid = int(match.group(1))
                        if os.path.exists(f"/proc/{pid}"):
                            return f"live PID {pid} in {os.path.basename(path)}"
        except (FileNotFoundError, PermissionError, OSError):
            continue

    my_pid = os.getpid()
    try:
        for entry in os.scandir("/proc"):
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if pid == my_pid:
                continue
            try:
                with open(os.path.join(entry.path, "cmdline"), "rb") as f:
                    cmd = f.read().replace(b"\x00", b" ").decode("utf-8", "ignore").lower()
            except OSError:
                continue
            for pat in RENDER_PROC_PATTERNS:
                if pat in cmd:
                    return f"live render process pid={pid}"
    except OSError:
        pass
    return None


def init_state_db(path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_pictures (
            picture_id INTEGER PRIMARY KEY,
            status TEXT NOT NULL,
            tags_added INTEGER NOT NULL DEFAULT 0,
            faces_assigned INTEGER NOT NULL DEFAULT 0,
            char_named INTEGER NOT NULL DEFAULT 0,
            error_code TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def get_state_counts(conn: sqlite3.Connection) -> dict[str, int]:
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT
            SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END),
            COALESCE(SUM(tags_added), 0),
            COALESCE(SUM(faces_assigned), 0),
            COALESCE(SUM(char_named), 0)
        FROM processed_pictures
        """
    ).fetchone()
    done, skipped, failed, tags_added, faces_assigned, char_named = [int(x or 0) for x in rows]
    extra_faces = cur.execute("SELECT value FROM meta WHERE key = 'phase_a_faces_assigned'").fetchone()
    insightface_assigned = int(extra_faces[0]) if extra_faces else 0
    return {
        "pictures_done": done,
        "pictures_skipped": skipped,
        "pictures_failed": failed,
        "tags_added": tags_added,
        "faces_assigned_insightface": insightface_assigned,
        "faces_processed": faces_assigned + insightface_assigned,
        "characters_named": char_named,
    }


def load_done_or_skipped_ids(conn: sqlite3.Connection) -> set[int]:
    rows = conn.execute(
        "SELECT picture_id FROM processed_pictures WHERE status IN ('done', 'skipped')"
    ).fetchall()
    return {int(r[0]) for r in rows}


def normalize_tag(raw: str) -> str | None:
    if not isinstance(raw, str):
        return None
    cleaned = raw.strip().lower().replace("_", " ")
    cleaned = re.sub(r"[^a-z0-9 \-/'+.]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned or len(cleaned) < 2 or len(cleaned) > 60:
        return None
    return cleaned


def normalize_person_name(raw: str) -> str | None:
    if not isinstance(raw, str):
        return None
    cleaned = re.sub(r"\s+", " ", raw.strip().lower().replace("_", " "))
    cleaned = re.sub(r"[^a-z0-9 '\-.]", "", cleaned).strip()
    if not cleaned or len(cleaned) < 3 or len(cleaned) > 60:
        return None
    if cleaned in GENERIC_PERSON_STOPWORDS:
        return None
    return cleaned


def parse_vlm_json(text: str) -> tuple[list[str], list[str]]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        stripped = stripped[start : end + 1]
    data = json.loads(stripped)
    if not isinstance(data, dict):
        raise ValueError("Non-dict JSON")
    raw_tags = data.get("tags") or []
    raw_people = data.get("people") or []
    tags = []
    seen = set()
    for t in raw_tags:
        nt = normalize_tag(t)
        if nt and nt not in seen:
            seen.add(nt)
            tags.append(nt)
    people = []
    seen_p = set()
    for p in raw_people:
        np_name = normalize_person_name(p)
        if np_name and np_name not in seen_p:
            seen_p.add(np_name)
            people.append(np_name)
    return tags, people


def parse_vlm_tags(text: str) -> tuple[list[str], list[str]]:
    """Parse JoyCaption comma/newline-separated Booru tags (with JSON fallback)."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    stripped = stripped.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return parse_vlm_json(stripped)

    # Drop a single conversational preamble line ending with ':' (e.g. "Tags:" or "Here are the tags:")
    lines = stripped.splitlines()
    if len(lines) > 1 and lines[0].strip().endswith(":"):
        stripped = "\n".join(lines[1:]).strip()

    tags: list[str] = []
    seen_tags: set[str] = set()
    people: list[str] = []
    seen_people: set[str] = set()

    for part in re.split(r"[,\n]+", stripped):
        cleaned = part.strip().strip("\"'`.*•-")
        if not cleaned:
            continue
        cleaned = re.sub(r"^(?:booru(?:-like)?\s+)?tags?\s*:\s*", "", cleaned, flags=re.IGNORECASE).strip()
        if not cleaned or cleaned.endswith(":"):
            continue
        ns_match = re.match(r"^([a-zA-Z]+)\s*:\s*(.+)$", cleaned)
        if ns_match:
            ns = ns_match.group(1).strip().lower()
            val = ns_match.group(2).strip()
            if ns == "character":
                np_name = normalize_person_name(val)
                if np_name and np_name not in seen_people:
                    seen_people.add(np_name)
                    people.append(np_name)
                continue
            if ns in BOORU_NAMESPACE_SKIP:
                continue
        nt = normalize_tag(cleaned)
        if nt and nt not in seen_tags:
            seen_tags.add(nt)
            tags.append(nt)

    if not tags and not people:
        raise ValueError("Empty tag list")
    return tags, people


def encode_image_b64_jpeg(raw_bytes: bytes) -> str:
    with Image.open(BytesIO(raw_bytes)) as img:
        rgb = img.convert("RGB")
        w, h = rgb.size
        if max(w, h) > MAX_IMAGE_EDGE:
            rgb.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
        buf = BytesIO()
        rgb.save(buf, format="JPEG", quality=88)
        return base64.b64encode(buf.getvalue()).decode("ascii")


def probe_video_duration(video_path: str) -> float | None:
    """Return video duration in seconds via ffprobe, or None if unavailable."""
    for entry, extra in (("format=duration", []), ("stream=duration", ["-select_streams", "v:0"])):
        cmd = [
            "ffprobe",
            "-v",
            "error",
            *extra,
            "-show_entries",
            entry,
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            continue
        for line in proc.stdout.splitlines():
            cleaned = line.strip()
            if cleaned and cleaned.upper() != "N/A":
                try:
                    val = float(cleaned)
                    if val > 0.0:
                        return val
                except ValueError:
                    pass
    return None


def run_ffmpeg_frame(seek_args: list[str], video_path: str, out_path: str) -> bytes | None:
    """Extract a single frame with ffmpeg to out_path and return its bytes."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        *seek_args,
        "-i",
        video_path,
        "-frames:v",
        "1",
        out_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode == 0 and os.path.isfile(out_path) and os.path.getsize(out_path) > 0:
        with open(out_path, "rb") as handle:
            return handle.read()
    return None


def extract_video_frames_ffmpeg(video_bytes: bytes, fmt: str) -> list[bytes]:
    """Extract one middle frame of a video (falling back to start frame) and clean up."""
    safe_fmt = re.sub(r"[^a-z0-9]", "", fmt.lower()) or "mp4"
    with tempfile.TemporaryDirectory(prefix="u49_vid_") as tmpdir:
        video_path = os.path.join(tmpdir, f"input.{safe_fmt}")
        with open(video_path, "wb") as handle:
            handle.write(video_bytes)

        duration = probe_video_duration(video_path)
        if duration is not None and duration > 0.2:
            mid_ts = f"{duration * 0.5:.3f}"
            middle = run_ffmpeg_frame(["-ss", mid_ts], video_path, os.path.join(tmpdir, "frame_mid.png"))
            if middle is not None:
                return [middle]

        fallback = run_ffmpeg_frame(["-ss", "0"], video_path, os.path.join(tmpdir, "frame_0.png"))
        if fallback is None:
            fallback = run_ffmpeg_frame([], video_path, os.path.join(tmpdir, "frame_0.png"))
        return [fallback] if fallback is not None else []


class ProgressReporter:
    def __init__(self, started_ct: datetime, vlm_concurrency: int):
        os.makedirs(PROGRESS_DIR, exist_ok=True)
        os.chmod(PROGRESS_DIR, 0o755)
        self.started_ct = started_ct
        self.vlm_concurrency = vlm_concurrency
        self.write_lock = threading.Lock()
        self.vlm_start_mono: float | None = None
        self.vlm_done_start: int | None = None
        self.vlm_skipped_start: int | None = None
        self.phase_a_start_mono = time.monotonic()
        self.phase_a_faces_start: int | None = None

    def start_vlm_clock(self, initial_done: int, initial_skipped: int = 0) -> None:
        with self.write_lock:
            self.vlm_start_mono = time.monotonic()
            self.vlm_done_start = initial_done
            self.vlm_skipped_start = initial_skipped

    def start_phase_a_clock(self, initial_assigned: int) -> None:
        with self.write_lock:
            self.phase_a_start_mono = time.monotonic()
            self.phase_a_faces_start = initial_assigned

    def write(
        self,
        counts: dict[str, int],
        status: str,
        phase_a_status: str = "running",
        stop_reason: str | None = None,
        append_log: bool = True,
    ) -> None:
        with self.write_lock:
            done = counts["pictures_done"]
            skipped = counts["pictures_skipped"]
            failed = counts["pictures_failed"]
            insight_faces = counts["faces_assigned_insightface"]

            if self.phase_a_faces_start is None:
                self.phase_a_faces_start = insight_faces
            phase_a_session = max(0, insight_faces - self.phase_a_faces_start)
            phase_a_elapsed = max(0.001, time.monotonic() - self.phase_a_start_mono)
            phase_a_rate_per_min = (
                round(phase_a_session / (phase_a_elapsed / 60.0), 2)
                if phase_a_session > 0
                else 0.0
            )

            vlm_session_processed = 0
            vlm_session_skipped = 0
            vlm_sec_per_img: float | None = None
            vlm_rate_per_min: float | None = None
            vlm_eta_str: str | None = None
            remaining_total = max(0, EXPECTED_PICTURE_COUNT - done - skipped)
            remaining_non_skipped = remaining_total

            if self.vlm_start_mono is not None and self.vlm_done_start is not None:
                vlm_session_processed = max(0, done - self.vlm_done_start)
                vlm_session_skipped = max(0, skipped - (self.vlm_skipped_start or 0))
                vlm_elapsed = max(0.001, time.monotonic() - self.vlm_start_mono)
                session_total = vlm_session_processed + vlm_session_skipped
                if session_total >= 20 and vlm_session_processed > 0:
                    non_skip_ratio = vlm_session_processed / session_total
                    remaining_non_skipped = max(0, int(round(remaining_total * non_skip_ratio)))
                if vlm_session_processed > 0:
                    vlm_sec_per_img = round(vlm_elapsed / vlm_session_processed, 2)
                    vlm_rate_per_min = round(vlm_session_processed / (vlm_elapsed / 60.0), 2)
                    eta_sec = int(remaining_non_skipped * vlm_sec_per_img)
                    vlm_eta_str = str(timedelta(seconds=eta_sec))

            now_str = fmt_ct()
            payload = {
                "status": status,
                "pid": os.getpid(),
                "started_at_ct": fmt_ct(self.started_ct),
                "last_update_ct": now_str,
                "total_pictures": EXPECTED_PICTURE_COUNT,
                "pictures_done": done,
                "pictures_skipped": skipped,
                "pictures_failed": failed,
                "tags_added": counts["tags_added"],
                "faces_assigned_insightface": insight_faces,
                "faces_processed": counts["faces_processed"],
                "characters_named": counts["characters_named"],
                "seconds_per_image": vlm_sec_per_img,
                "rate_per_min": vlm_rate_per_min,
                "eta": vlm_eta_str,
                "vlm_concurrency": self.vlm_concurrency,
                "vlm_session_processed": vlm_session_processed,
                "vlm_session_skipped": vlm_session_skipped,
                "remaining_non_skipped": remaining_non_skipped,
                "vlm_seconds_per_image": vlm_sec_per_img,
                "vlm_pictures_per_min": vlm_rate_per_min,
                "vlm_eta": vlm_eta_str,
                "phase_a_status": phase_a_status,
                "phase_a_session_assigned": phase_a_session,
                "phase_a_faces_per_min": phase_a_rate_per_min,
                "stop_reason": stop_reason,
                "resume_command": "sudo -n -iu evo systemctl --user start u42-pixlstash-tagger.service",
            }
            tmp_json = f"{PROGRESS_JSON}.tmp.{threading.get_ident()}"
            with open(tmp_json, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
            os.chmod(tmp_json, 0o644)
            os.replace(tmp_json, PROGRESS_JSON)

            if append_log:
                line = (
                    f"[{now_str}] status={status} done={done}/{EXPECTED_PICTURE_COUNT} "
                    f"skipped={skipped} failed={failed} tags_added={counts['tags_added']} "
                    f"faces_assigned_insightface={insight_faces} "
                    f"faces_processed={counts['faces_processed']} characters_named={counts['characters_named']} "
                    f"sec_per_img={vlm_sec_per_img} eta={vlm_eta_str} "
                    f"vlm_conc={self.vlm_concurrency} vlm_sec_per_img={vlm_sec_per_img} "
                    f"vlm_pic_per_min={vlm_rate_per_min} vlm_eta={vlm_eta_str} "
                    f"phase_a={phase_a_status} phase_a_fpm={phase_a_rate_per_min}"
                )
                if stop_reason:
                    line += f" reason={stop_reason}"
                with open(PROGRESS_LOG, "a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
                os.chmod(PROGRESS_LOG, 0o644)


class Runner:
    def __init__(self, vlm_concurrency: int) -> None:
        self.vlm_concurrency = vlm_concurrency
        self.stop_requested = False
        self.stop_reason: str | None = None
        self.phase_a_status = "starting"
        self.vlm_started = False
        self.db_lock = threading.Lock()
        self.conn = init_state_db(STATE_DB)
        self.pixl_token = "<redacted-in-locked-keyfile>"
        self.llm_key = read_llm_key(LLM_ENV_FILE)
        self.pixl_headers = {"Authorization": f"Bearer {self.pixl_token}"}
        self.llm_headers = {
            "Authorization": "<redacted-in-locked-keyfile>"
            "Content-Type": "application/json",
        }
        self._tls = threading.local()
        self._clients_lock = threading.Lock()
        self._all_clients: list[httpx.Client] = []
        self._precond_lock = threading.Lock()
        self._last_precond_ok_mono = 0.0
        self.reporter = ProgressReporter(now_ct(), vlm_concurrency=vlm_concurrency)

    def get_pixl_client(self) -> httpx.Client:
        client = getattr(self._tls, "pixl_client", None)
        if client is None:
            client = httpx.Client(
                base_url=PIXLSTASH_URL,
                headers=self.pixl_headers,
                timeout=60.0,
            )
            self._tls.pixl_client = client
            with self._clients_lock:
                self._all_clients.append(client)
        return client

    def get_llm_client(self) -> httpx.Client:
        client = getattr(self._tls, "llm_client", None)
        if client is None:
            client = httpx.Client(
                base_url=LLAMA_SWAP_URL,
                headers=self.llm_headers,
                timeout=600.0,
            )
            self._tls.llm_client = client
            with self._clients_lock:
                self._all_clients.append(client)
        return client

    def close_all_clients(self) -> None:
        with self._clients_lock:
            for client in self._all_clients:
                try:
                    client.close()
                except Exception:
                    pass
            self._all_clients.clear()

    def pixl_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        client = self.get_pixl_client()
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                resp = client.request(method, url, **kwargs)
                if resp.status_code in (502, 503) and attempt < 2:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                return resp
            except (httpx.ReadError, httpx.RemoteProtocolError, httpx.ConnectError) as exc:
                last_exc = exc
                if attempt < 2 and not self.stop_requested:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                raise
        assert last_exc is not None
        raise last_exc

    def handle_signal(self, signum: int, _frame) -> None:
        self.stop_requested = True
        self.stop_reason = f"signal_{signum}"

    def check_preconditions(self, force_count_check: bool = False) -> bool:
        render_busy = check_live_render()
        if render_busy:
            self.stop_requested = True
            self.stop_reason = f"live_render:{render_busy}"
            return False
        now_m = time.monotonic()
        with self._precond_lock:
            if not force_count_check and (now_m - self._last_precond_ok_mono) < 15.0:
                return True
            try:
                resp = self.pixl_request("GET", "/api/v1/pictures/count", timeout=15.0)
                resp.raise_for_status()
                count = int(resp.json().get("count", -1))
                if count < 1:  # Max 2026-11-16: library grows from Grok Downloader imports; only stop if PixlStash looks empty
                    self.stop_requested = True
                    self.stop_reason = f"picture_count_mismatch:{count}"
                    return False
                self._last_precond_ok_mono = time.monotonic()
            except Exception as exc:
                self.stop_requested = True
                self.stop_reason = f"pixlstash_unreachable:{type(exc).__name__}"
                return False
        return True

    def current_status(self) -> str:
        return "running" if self.vlm_started else "running_insightface"

    def run_phase_a_loop(self) -> None:
        """Continuously match unassigned faces to named characters on CPU alongside VLM."""
        with self.db_lock:
            done_flag = self.conn.execute(
                "SELECT value FROM meta WHERE key = 'phase_a_completed'"
            ).fetchone()
            init_counts = get_state_counts(self.conn)
        if done_flag and done_flag[0] == "1":
            self.phase_a_status = "completed"
            return

        self.phase_a_status = "running"
        self.reporter.start_phase_a_clock(init_counts["faces_assigned_insightface"])
        already_owned_faces: set[int] = set()
        attempted_faces_by_char: dict[int, set[int]] = {}

        try:
            while not self.stop_requested:
                if not self.check_preconditions():
                    break
                resp = self.pixl_request("GET", "/api/v1/characters?include_counts=true")
                resp.raise_for_status()
                characters = resp.json()
                pass_assigned = 0

                for char in characters:
                    if self.stop_requested:
                        break
                    cid = int(char["id"])
                    attempted_for_char = attempted_faces_by_char.setdefault(cid, set())

                    while not self.stop_requested:
                        if not self.check_preconditions():
                            return
                        sr = self.pixl_request(
                            "POST",
                            "/api/v1/pictures/face-search",
                            params={
                                "source_character_id": cid,
                                "exclude_character_id": cid,
                                "top_n": 500,
                                "combine": "mean",
                            },
                            timeout=120.0,
                        )
                        sr.raise_for_status()
                        matches = sr.json()
                        candidates = [
                            m for m in matches
                            if float(m.get("likeness") or 0.0) >= INSIGHTFACE_STRICT_THRESHOLD
                            and m.get("face_id") is not None
                            and int(m["face_id"]) not in already_owned_faces
                            and int(m["face_id"]) not in attempted_for_char
                        ]
                        if not candidates:
                            break

                        assignments = []
                        seen_faces_in_batch: set[int] = set()
                        faces_cache_by_pid: dict[int, list[dict]] = {}

                        for m in candidates:
                            if self.stop_requested:
                                break
                            pid = int(m["picture_id"])
                            fid = int(m["face_id"])
                            attempted_for_char.add(fid)
                            if fid in seen_faces_in_batch or fid in already_owned_faces:
                                continue

                            faces = faces_cache_by_pid.get(pid)
                            if faces is None:
                                fr = self.pixl_request("GET", f"/api/v1/pictures/{pid}/faces")
                                if fr.status_code != 200:
                                    faces = []
                                else:
                                    faces = fr.json().get("faces", [])
                                faces_cache_by_pid[pid] = faces
                                for f in faces:
                                    if f.get("character_id") is not None and f.get("id") is not None:
                                        already_owned_faces.add(int(f["id"]))

                            target = next((f for f in faces if f.get("id") == fid), None)
                            if (
                                target is None
                                or target.get("character_id") is not None
                                or int(target.get("face_index", -1)) < 0
                            ):
                                continue
                            seen_faces_in_batch.add(fid)
                            assignments.append({"picture_id": pid, "face_id": fid})

                        if not assignments:
                            break

                        round_assigned = 0
                        for i in range(0, len(assignments), 50):
                            if self.stop_requested:
                                break
                            chunk = assignments[i : i + 50]
                            ar = self.pixl_request(
                                "POST",
                                f"/api/v1/characters/{cid}/faces",
                                json={"face_assignments": chunk},
                            )
                            if ar.status_code == 200:
                                assigned_ids = ar.json().get("face_ids") or []
                                for afid in assigned_ids:
                                    already_owned_faces.add(int(afid))
                                assigned_now = len(assigned_ids)
                                round_assigned += assigned_now
                                pass_assigned += assigned_now
                                if assigned_now > 0:
                                    with self.db_lock:
                                        cur_val = self.conn.execute(
                                            "SELECT value FROM meta WHERE key = 'phase_a_faces_assigned'"
                                        ).fetchone()
                                        new_val = (int(cur_val[0]) if cur_val else 0) + assigned_now
                                        self.conn.execute(
                                            "INSERT OR REPLACE INTO meta (key, value) VALUES ('phase_a_faces_assigned', ?)",
                                            (str(new_val),),
                                        )
                                        self.conn.commit()
                                        counts = get_state_counts(self.conn)
                                    self.reporter.write(
                                        counts,
                                        self.current_status(),
                                        phase_a_status=self.phase_a_status,
                                        append_log=True,
                                    )

                        if round_assigned == 0:
                            break

                if self.stop_requested:
                    break
                if pass_assigned == 0:
                    with self.db_lock:
                        self.conn.execute(
                            "INSERT OR REPLACE INTO meta (key, value) VALUES ('phase_a_completed', '1')"
                        )
                        self.conn.commit()
                        counts = get_state_counts(self.conn)
                    self.phase_a_status = "completed"
                    self.reporter.write(
                        counts,
                        self.current_status(),
                        phase_a_status=self.phase_a_status,
                        append_log=True,
                    )
                    break
                time.sleep(0.25)
        except Exception as exc:
            self.phase_a_status = f"error:{type(exc).__name__}"

    def stream_all_picture_stubs(self) -> list[tuple[int, str]]:
        stubs: list[tuple[int, str]] = []
        offset = 0
        while True:
            r = self.pixl_request(
                "GET",
                "/api/v1/pictures/stream",
                params={
                    "batch_limit": 2000,
                    "offset": offset,
                    "fields": "id,format",
                    "descending": "false",
                },
                timeout=60.0,
            )
            r.raise_for_status()
            body = r.json()
            for pic in body.get("pictures", []):
                stubs.append((int(pic["id"]), str(pic.get("format") or "jpeg").lower()))
            if body.get("done"):
                break
            next_off = body.get("next_offset")
            if next_off is None or int(next_off) <= offset:
                break
            offset = int(next_off)
        return stubs

    def fetch_existing_tags_batch(self, pids: list[int]) -> dict[int, set[str]]:
        out: dict[int, set[str]] = {pid: set() for pid in pids}
        for i in range(0, len(pids), 200):
            chunk = pids[i : i + 200]
            r = self.pixl_request(
                "POST",
                "/api/v1/pictures/tags/bulk_fetch",
                json={"picture_ids": chunk},
            )
            r.raise_for_status()
            for item in r.json():
                pid = int(item["id"])
                out[pid] = {
                    str(t.get("tag") or "").strip().lower()
                    for t in (item.get("tags") or [])
                    if t.get("tag")
                }
        return out

    def get_face_counts(self, pid: int) -> tuple[int, int]:
        fr = self.pixl_request("GET", f"/api/v1/pictures/{pid}/faces")
        if fr.status_code != 200:
            return 0, 0
        total = 0
        unassigned = 0
        for f in fr.json().get("faces", []):
            if int(f.get("face_index", -1)) >= 0:
                total += 1
                if f.get("character_id") is None:
                    unassigned += 1
        return total, unassigned

    def count_unassigned_faces(self, pid: int) -> int:
        _, unassigned = self.get_face_counts(pid)
        return unassigned

    def fetch_image_bytes(self, pid: int, fmt: str) -> tuple[bytes | None, str | None]:
        if fmt in VIDEO_FORMATS:
            img_resp = self.pixl_request("GET", f"/api/v1/pictures/thumbnails/{pid}.webp")
        else:
            try:
                img_resp = self.pixl_request("GET", f"/api/v1/pictures/{pid}.{fmt}")
                if img_resp.status_code in (400, 404, 500):
                    img_resp = self.pixl_request("GET", f"/api/v1/pictures/thumbnails/{pid}.webp")
            except httpx.HTTPError:
                img_resp = self.pixl_request("GET", f"/api/v1/pictures/thumbnails/{pid}.webp")

        if img_resp.status_code == 404:
            return None, "HTTP_404"
        img_resp.raise_for_status()
        return img_resp.content, None

    def query_vlm_for_image(
        self, raw_bytes: bytes, unassigned_faces: int
    ) -> tuple[list[str], list[str]]:
        """Encode one image or frame and query JoyCaption in native Booru-like tag mode."""
        b64_img = encode_image_b64_jpeg(raw_bytes)
        user_text = BOORU_PROMPT if unassigned_faces == 0 else BOORU_PERSON_PROMPT
        llm_payload = {
            "model": VLM_MODEL,
            "max_tokens": "<redacted-in-locked-keyfile>"
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                        },
                        {"type": "text", "text": user_text},
                    ],
                },
            ],
        }
        lr = self.get_llm_client().post("/v1/chat/completions", json=llm_payload)
        lr.raise_for_status()
        content = (
            lr.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return parse_vlm_tags(content)

    def process_one_picture(
        self, pid: int, fmt: str, existing_tags: set[str]
    ) -> tuple[int, str, int, int, int, str | None]:
        if self.stop_requested:
            return (pid, "abort", 0, 0, 0, None)

        # 1. Check faces: skip if >=1 face and all faces already have character_id
        total_faces, unassigned_faces = self.get_face_counts(pid)
        if total_faces >= 1 and unassigned_faces == 0:
            return (pid, "skipped", 0, 0, 0, "face_matched")

        if fmt in VIDEO_FORMATS:
            # 2a. Fetch original video, extract one middle frame to temp dir, tag
            vid_resp = self.pixl_request("GET", f"/api/v1/pictures/{pid}.{fmt}", timeout=120.0)
            if vid_resp.status_code == 404:
                return (pid, "skipped", 0, 0, 0, "HTTP_404")
            vid_resp.raise_for_status()
            frame_bytes_list = extract_video_frames_ffmpeg(vid_resp.content, fmt)
            if not frame_bytes_list:
                return (pid, "skipped", 0, 0, 0, "ffmpeg_no_frames")

            vlm_tags: list[str] = []
            seen_tags: set[str] = set()
            vlm_people: list[str] = []
            seen_people: set[str] = set()
            for frame_bytes in frame_bytes_list:
                if self.stop_requested:
                    return (pid, "abort", 0, 0, 0, None)
                frame_tags, frame_people = self.query_vlm_for_image(frame_bytes, unassigned_faces)
                for tag in frame_tags:
                    if tag not in seen_tags:
                        seen_tags.add(tag)
                        vlm_tags.append(tag)
                for person in frame_people:
                    if person not in seen_people:
                        seen_people.add(person)
                        vlm_people.append(person)
        else:
            # 2b. Fetch image (fallback when original fetch errors)
            raw_bytes, skip_reason = self.fetch_image_bytes(pid, fmt)
            if skip_reason is not None or raw_bytes is None:
                return (pid, "skipped", 0, 0, 0, skip_reason or "HTTP_404")

            if self.stop_requested:
                return (pid, "abort", 0, 0, 0, None)

            # 3. Query gemma4-heretic (slot sampling settings in llama-swap.yaml; thinking disabled for throughput)
            vlm_tags, vlm_people = self.query_vlm_for_image(raw_bytes, unassigned_faces)

        if self.stop_requested:
            return (pid, "abort", 0, 0, 0, None)

        tags_to_add = [t for t in vlm_tags if t not in existing_tags][:MAX_NEW_TAGS_PER_PIC]
        tags_added = 0
        for tag in tags_to_add:
            tr = self.pixl_request("POST", f"/api/v1/pictures/{pid}/tags", json={"tag": tag})
            if tr.status_code == 200:
                tags_added += 1
                existing_tags.add(tag)

        # 4. TOCTOU-safe face re-check immediately before writing any person tag:
        # InsightFace Phase A runs concurrently and always wins; VLM may only name faces
        # that STILL have character_id=None at write time, without inventing gallery entries.
        char_named = 0
        reported_unassigned = unassigned_faces
        if unassigned_faces > 0 and vlm_people:
            live_unassigned = self.count_unassigned_faces(pid)
            reported_unassigned = live_unassigned
            if live_unassigned > 0:
                for person in vlm_people[:live_unassigned]:
                    ptag = f"person {person}"
                    if ptag not in existing_tags:
                        tr = self.pixl_request(
                            "POST",
                            f"/api/v1/pictures/{pid}/tags",
                            json={"tag": ptag},
                        )
                        if tr.status_code == 200:
                            tags_added += 1
                            char_named += 1
                            existing_tags.add(ptag)
                            for mapped_char in index_map.map_person_to_characters(person):
                                ctag = f"character {mapped_char}"
                                ctag_lower = ctag.lower()
                                if ctag_lower not in existing_tags:
                                    cr = self.pixl_request(
                                        "POST",
                                        f"/api/v1/pictures/{pid}/tags",
                                        json={"tag": ctag},
                                    )
                                    if cr.status_code == 200:
                                        tags_added += 1
                                        existing_tags.add(ctag_lower)

        return (pid, "done", tags_added, reported_unassigned, char_named, None)

    def run(self) -> int:
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        with self.db_lock:
            init_counts = get_state_counts(self.conn)
        self.reporter.write(init_counts, "starting", phase_a_status=self.phase_a_status, append_log=True)

        if not self.check_preconditions(force_count_check=True):
            self.reporter.write(
                init_counts,
                "stopped",
                phase_a_status=self.phase_a_status,
                stop_reason=self.stop_reason,
            )
            self.close_all_clients()
            return 0

        # Launch Phase A (InsightFace on CPU) in a background thread concurrent with VLM tagging
        phase_a_thread = threading.Thread(
            target=self.run_phase_a_loop,
            name="phase-a-insightface",
            daemon=True,
        )
        phase_a_thread.start()

        try:
            stubs = self.stream_all_picture_stubs()
            done_ids = load_done_or_skipped_ids(self.conn)
            pending = [(pid, fmt) for (pid, fmt) in stubs if pid not in done_ids]

            with self.db_lock:
                vlm_init_counts = get_state_counts(self.conn)
            self.vlm_started = True
            index_map.get_mapper()
            self.reporter.start_vlm_clock(
                vlm_init_counts["pictures_done"],
                vlm_init_counts["pictures_skipped"],
            )

            first_logged = False
            completed_since_log = 0
            pending_idx = 0
            total_pending = len(pending)
            tags_cache: dict[int, set[str]] = {}
            in_flight_target = max(self.vlm_concurrency * 2, self.vlm_concurrency + 1)
            active_futures: dict[Future, int] = {}

            with ThreadPoolExecutor(max_workers=self.vlm_concurrency) as pool:
                while (pending_idx < total_pending or active_futures) and not self.stop_requested:
                    if not self.check_preconditions():
                        break

                    # Prefetch existing tags in chunks of PREFETCH_BATCH_SIZE
                    while (
                        not self.stop_requested
                        and pending_idx < total_pending
                        and len(active_futures) < in_flight_target
                    ):
                        pid, fmt = pending[pending_idx]
                        if pid not in tags_cache:
                            chunk_end = min(total_pending, pending_idx + PREFETCH_BATCH_SIZE)
                            chunk_pids = [p for p, _ in pending[pending_idx:chunk_end]]
                            tags_cache.update(self.fetch_existing_tags_batch(chunk_pids))
                        existing = tags_cache.pop(pid, set())
                        fut = pool.submit(self.process_one_picture, pid, fmt, existing)
                        active_futures[fut] = pid
                        pending_idx += 1

                    if not active_futures:
                        break

                    done_futs, _ = wait(
                        active_futures.keys(),
                        timeout=2.0,
                        return_when=FIRST_COMPLETED,
                    )
                    for fut in done_futs:
                        pid = active_futures.pop(fut)
                        try:
                            r_pid, status, t_add, f_proc, c_named, err = fut.result()
                        except httpx.HTTPStatusError as exc:
                            r_pid, status, t_add, f_proc, c_named, err = (
                                pid,
                                "failed",
                                0,
                                0,
                                0,
                                f"HTTP_{exc.response.status_code}",
                            )
                        except Exception as exc:
                            r_pid, status, t_add, f_proc, c_named, err = (
                                pid,
                                "failed",
                                0,
                                0,
                                0,
                                type(exc).__name__,
                            )

                        if status == "abort":
                            continue

                        with self.db_lock:
                            self.conn.execute(
                                """
                                INSERT OR REPLACE INTO processed_pictures
                                (picture_id, status, tags_added, faces_assigned, char_named, error_code, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (r_pid, status, t_add, f_proc, c_named, err, fmt_ct()),
                            )
                            self.conn.commit()
                            counts = get_state_counts(self.conn)

                        completed_since_log += 1
                        if not first_logged or completed_since_log >= 10:
                            first_logged = True
                            completed_since_log = 0
                            self.reporter.write(
                                counts,
                                "running",
                                phase_a_status=self.phase_a_status,
                                append_log=True,
                            )
                        else:
                            self.reporter.write(
                                counts,
                                "running",
                                phase_a_status=self.phase_a_status,
                                append_log=False,
                            )

                # On stop request, cancel queued tasks and drain active ones cleanly
                if self.stop_requested and active_futures:
                    for fut in list(active_futures.keys()):
                        fut.cancel()
                    done_futs, _ = wait(active_futures.keys(), timeout=30.0)
                    for fut in done_futs:
                        pid = active_futures.pop(fut)
                        if fut.cancelled():
                            continue
                        try:
                            r_pid, status, t_add, f_proc, c_named, err = fut.result()
                        except Exception:
                            continue
                        if status == "abort":
                            continue
                        with self.db_lock:
                            self.conn.execute(
                                """
                                INSERT OR REPLACE INTO processed_pictures
                                (picture_id, status, tags_added, faces_assigned, char_named, error_code, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (r_pid, status, t_add, f_proc, c_named, err, fmt_ct()),
                            )
                            self.conn.commit()

            phase_a_thread.join(timeout=15.0 if self.stop_requested else None)
            with self.db_lock:
                final_counts = get_state_counts(self.conn)
            if self.stop_requested:
                self.reporter.write(
                    final_counts,
                    "stopped",
                    phase_a_status=self.phase_a_status,
                    stop_reason=self.stop_reason,
                )
            else:
                self.reporter.write(
                    final_counts,
                    "completed",
                    phase_a_status=self.phase_a_status,
                    stop_reason="all_pictures_processed",
                )
            return 0
        finally:
            self.close_all_clients()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="U44 PixlStash concurrent tagging & face-matching runner")
    parser.add_argument(
        "--vlm-concurrency",
        type=int,
        default=None,
        help=f"Number of concurrent VLM requests (env {VLM_CONCURRENCY_ENV}, default {DEFAULT_VLM_CONCURRENCY})",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    vlm_concurrency = resolve_vlm_concurrency(args.vlm_concurrency)
    runner = Runner(vlm_concurrency=vlm_concurrency)
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
