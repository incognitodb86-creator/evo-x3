import http.server
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "evo-raw-clip-cleanup"


def _write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _make_ffprobe_stub(bin_dir: Path) -> None:
    stub_py = bin_dir / "ffprobe_stub.py"
    stub_py.write_text(
        "import os, sys\n"
        "p = sys.argv[-1]\n"
        "name = os.path.basename(p)\n"
        "if 'badprobe' in name:\n"
        "    sys.exit(1)\n"
        "if 'zerodur' in name:\n"
        "    print('0.0')\n"
        "    sys.exit(0)\n"
        "print('5.250000')\n",
        encoding="utf-8",
    )
    if os.name == "nt":
        cmd = bin_dir / "ffprobe.cmd"
        cmd.write_text(f'@echo off\r\n"{sys.executable}" "{stub_py}" %*\r\n', encoding="utf-8")
    else:
        sh = bin_dir / "ffprobe"
        sh.write_text(f'#!/usr/bin/env sh\nexec "{sys.executable}" "{stub_py}" "$@"\n', encoding="utf-8")
        sh.chmod(sh.stat().st_mode | stat.S_IXUSR)


class _PixlHandler(http.server.BaseHTTPRequestHandler):
    expected_token = ""
    pages: list[dict] = []

    def do_GET(self):
        if self.headers.get("Authorization") != f"Bearer {self.expected_token}":
            self.send_response(401)
            self.end_headers()
            return
        if not self.path.startswith("/api/v1/pictures/stream"):
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps(self.pages[0]).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


class TestEvoRawClipCleanup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.runs = self.root / "runs"
        self.out = self.root / "out"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        _make_ffprobe_stub(self.bin)
        self.env = os.environ.copy()
        self.env["PATH"] = str(self.bin) + os.pathsep + self.env.get("PATH", "")

        # 1. Valid upscaled run -> candidate
        self.ok_up = _write(self.runs / "run_ok" / "clip" / "clip.mp4", b"upscaled-video-bytes")
        self.ok_raw = _write(self.runs / "run_ok" / "clip" / "clip_raw.mp4", b"raw-video-bytes-1234")
        _write(self.runs / "run_ok" / "clip" / "still.png", b"png")
        _write(self.runs / "run_ok" / "clip" / "notes.txt", b"txt")
        _write(
            self.runs / "run_ok" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )

        # 2. Second valid upscaled run (used to verify --apply only deletes listed paths)
        self.ok2_up = _write(self.runs / "run_ok2" / "clip" / "clip.mp4", b"upscaled-2")
        self.ok2_raw = _write(self.runs / "run_ok2" / "clip" / "clip_raw.mp4", b"raw-2-bytes")
        _write(
            self.runs / "run_ok2" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )

        # 3. No upscale block -> NOT a candidate
        _write(self.runs / "run_no_up" / "clip" / "clip.mp4", b"raw-only")
        self.no_up_raw = _write(self.runs / "run_no_up" / "clip" / "clip_raw.mp4", b"raw-no-up")
        _write(self.runs / "run_no_up" / "clip" / "render_ok.json", json.dumps({"clip": "clip/clip.mp4"}).encode())

        # 4. 0-byte upscaled file -> NOT a candidate
        _write(self.runs / "run_zero" / "clip" / "clip.mp4", b"")
        self.zero_raw = _write(self.runs / "run_zero" / "clip" / "clip_raw.mp4", b"raw-zero")
        _write(
            self.runs / "run_zero" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )

        # 5. ffprobe fails or duration==0 -> NOT candidates
        _write(self.runs / "run_badprobe" / "badprobe" / "badprobe.mp4", b"corrupt")
        self.bad_raw = _write(self.runs / "run_badprobe" / "badprobe" / "badprobe_raw.mp4", b"raw-bad")
        _write(
            self.runs / "run_badprobe" / "badprobe" / "render_ok.json",
            json.dumps({"clip": "badprobe/badprobe.mp4", "upscale": {"raw_clip": "badprobe/badprobe_raw.mp4"}}).encode(),
        )
        _write(self.runs / "run_zerodur" / "zerodur" / "zerodur.mp4", b"zero-dur")
        self.zerodur_raw = _write(self.runs / "run_zerodur" / "zerodur" / "zerodur_raw.mp4", b"raw-zerodur")
        _write(
            self.runs / "run_zerodur" / "zerodur" / "render_ok.json",
            json.dumps({"clip": "zerodur/zerodur.mp4", "upscale": {"raw_clip": "zerodur/zerodur_raw.mp4"}}).encode(),
        )

        # 6. Still job and QNAP-only layout (no render_ok.json) -> NOT candidates
        _write(self.runs / "run_still" / "s1" / "s1.png", b"img")
        self.still_raw = _write(self.runs / "run_still" / "s1" / "s1_raw.mp4", b"not-video-job")
        _write(
            self.runs / "run_still" / "s1" / "render_ok.json",
            json.dumps({"job_type": "still", "upscale": {"raw_clip": "s1/s1_raw.mp4"}}).encode(),
        )
        self.qnap_raw = _write(self.runs / "run_qnap" / "clip" / "clip_raw.mp4", b"qnap-only")

        # Outside file that must never be touched
        self.outside = _write(self.root / "outside_raw.mp4", b"keep-me")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_dry_run_and_apply_recheck(self):
        r = self._run("--runs-dir", str(self.runs), "--out-dir", str(self.out), "--no-pixlstash")
        self.assertEqual(r.returncode, 0, r.stderr)
        m = re.search(r"DRY_RUN candidates=(\d+) bytes=(\d+) list=(.+)", r.stdout)
        self.assertIsNotNone(m, r.stdout)
        self.assertEqual(int(m.group(1)), 2)
        expected_bytes = self.ok_raw.stat().st_size + self.ok2_raw.stat().st_size
        self.assertEqual(int(m.group(2)), expected_bytes)

        list_file = Path(m.group(3).strip())
        self.assertTrue(list_file.is_file())
        listed = {Path(x).resolve() for x in list_file.read_text(encoding="utf-8").splitlines() if x.strip()}
        self.assertEqual(listed, {self.ok_raw.resolve(), self.ok2_raw.resolve()})

        # Dry run deleted nothing
        for p in (self.ok_raw, self.ok2_raw, self.ok_up, self.no_up_raw, self.zero_raw, self.bad_raw, self.zerodur_raw, self.still_raw, self.qnap_raw):
            self.assertTrue(p.exists())

        # Build an apply list with: 1 valid listed raw clip, 1 tampered upscaled clip, 1 outside file, 1 stale raw clip
        stale_up = _write(self.runs / "run_stale" / "clip" / "clip.mp4", b"good")
        stale_raw = _write(self.runs / "run_stale" / "clip" / "clip_raw.mp4", b"stale-raw")
        _write(
            self.runs / "run_stale" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )
        # Now break stale_up to 0 bytes before --apply to verify re-check blocks deletion
        stale_up.write_bytes(b"")

        apply_list = self.out / "custom-apply.txt"
        apply_list.write_text(
            "\n".join([str(self.ok_raw), str(self.ok_up), str(self.outside), str(stale_raw)]) + "\n",
            encoding="utf-8",
        )
        r2 = self._run("--runs-dir", str(self.runs), "--apply", str(apply_list))
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertIn(f"APPLY deleted=1 bytes={self.ok_raw.stat().st_size if self.ok_raw.exists() else 20} skipped=3", r2.stdout)

        # Only ok_raw was deleted; everything else (including unlisted ok2_raw) survived
        self.assertFalse(self.ok_raw.exists())
        for p in (self.ok_up, self.ok2_raw, self.outside, stale_raw, self.no_up_raw, self.zero_raw, self.bad_raw):
            self.assertTrue(p.exists(), f"Should not have deleted {p}")

    def test_pixlstash_dry_run_report_only_ids_and_counts(self):
        inbox = self.root / "pixl-inbox"
        _write(inbox / "_imported" / "run_ok_clip.mp4", b"a")
        _write(inbox / "_imported" / "run_ok_clip_raw.mp4", b"b")
        _write(inbox / "_imported" / "run_ok2_clip.mp4", b"c")

        secret = "tok-never-print-98765"
        tok_file = _write(self.root / "pixl.token", (secret + "\n").encode())

        _PixlHandler.expected_token = secret
        _PixlHandler.pages = [
            {
                "done": True,
                "pictures": [
                    {"id": 101, "format": "mp4", "file_path": "/data/run_ok_clip_raw.mp4"},
                    {"id": 102, "format": "mp4", "file_path": "/data/run_ok_clip.mp4"},
                    {"id": 103, "format": "mp4", "file_path": "/data/run_ok2_clip.mp4"},
                    {"id": 104, "format": "png", "file_path": "/data/run_ok_still.png"},
                ],
            }
        ]
        srv = http.server.HTTPServer(("127.0.0.1", 0), _PixlHandler)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            url = f"http://127.0.0.1:{srv.server_address[1]}"
            r = self._run(
                "--runs-dir", str(self.runs),
                "--out-dir", str(self.out),
                "--inbox-dir", str(inbox),
                "--pixl-url", url,
                "--pixl-token-file", str(tok_file),
            )
        finally:
            srv.shutdown()
            srv.server_close()

        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(secret, r.stdout)
        self.assertNotIn("clip_raw.mp4", r.stdout.split("PIXLSTASH_REPORT", 1)[1])
        m = re.search(r"PIXLSTASH_REPORT (.+)", r.stdout)
        self.assertIsNotNone(m, r.stdout)
        rep = json.loads(m.group(1))
        self.assertEqual(rep["inbox_imported_multi_video_runs"], {"run_ok": 2})
        self.assertEqual(rep["pixlstash_api"]["status"], "ok")
        self.assertEqual(rep["pixlstash_api"]["multi_video_runs"], {"run_ok": {"count": 2, "picture_ids": [101, 102]}})


if __name__ == "__main__":
    unittest.main()
