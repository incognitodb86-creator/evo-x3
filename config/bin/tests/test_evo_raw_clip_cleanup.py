import hashlib
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


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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

        # 1. Valid upscaled run -> candidate (with clip_sha256 + raw_sha256)
        ok_up_data, ok_raw_data = b"upscaled-video-bytes", b"raw-video-bytes-1234"
        self.ok_up = _write(self.runs / "run_ok" / "clip" / "clip.mp4", ok_up_data)
        self.ok_raw = _write(self.runs / "run_ok" / "clip" / "clip_raw.mp4", ok_raw_data)
        _write(self.runs / "run_ok" / "clip" / "still.png", b"png")
        _write(self.runs / "run_ok" / "clip" / "notes.txt", b"txt")
        _write(
            self.runs / "run_ok" / "clip" / "render_ok.json",
            json.dumps({
                "clip": "clip/clip.mp4",
                "clip_sha256": _sha(ok_up_data),
                "upscale": {"raw_clip": "clip/clip_raw.mp4", "raw_sha256": _sha(ok_raw_data)},
            }).encode(),
        )

        # 2. Second valid upscaled run (raw_sha256 omitted -> still valid; used for --apply exact-list check)
        ok2_up_data, ok2_raw_data = b"upscaled-2", b"raw-2-bytes"
        self.ok2_up = _write(self.runs / "run_ok2" / "clip" / "clip.mp4", ok2_up_data)
        self.ok2_raw = _write(self.runs / "run_ok2" / "clip" / "clip_raw.mp4", ok2_raw_data)
        _write(
            self.runs / "run_ok2" / "clip" / "render_ok.json",
            json.dumps({
                "clip": "clip/clip.mp4",
                "clip_sha256": _sha(ok2_up_data),
                "upscale": {"raw_clip": "clip/clip_raw.mp4"},
            }).encode(),
        )

        # 3. No upscale block -> NOT a candidate
        _write(self.runs / "run_no_up" / "clip" / "clip.mp4", b"raw-only")
        self.no_up_raw = _write(self.runs / "run_no_up" / "clip" / "clip_raw.mp4", b"raw-no-up")
        _write(self.runs / "run_no_up" / "clip" / "render_ok.json", json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"raw-only")}).encode())

        # 4. 0-byte upscaled file -> NOT a candidate
        _write(self.runs / "run_zero" / "clip" / "clip.mp4", b"")
        self.zero_raw = _write(self.runs / "run_zero" / "clip" / "clip_raw.mp4", b"raw-zero")
        _write(
            self.runs / "run_zero" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b""), "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )

        # 5. ffprobe fails or duration==0 -> NOT candidates
        _write(self.runs / "run_badprobe" / "badprobe" / "badprobe.mp4", b"corrupt")
        self.bad_raw = _write(self.runs / "run_badprobe" / "badprobe" / "badprobe_raw.mp4", b"raw-bad")
        _write(
            self.runs / "run_badprobe" / "badprobe" / "render_ok.json",
            json.dumps({"clip": "badprobe/badprobe.mp4", "clip_sha256": _sha(b"corrupt"), "upscale": {"raw_clip": "badprobe/badprobe_raw.mp4"}}).encode(),
        )
        _write(self.runs / "run_zerodur" / "zerodur" / "zerodur.mp4", b"zero-dur")
        self.zerodur_raw = _write(self.runs / "run_zerodur" / "zerodur" / "zerodur_raw.mp4", b"raw-zerodur")
        _write(
            self.runs / "run_zerodur" / "zerodur" / "render_ok.json",
            json.dumps({"clip": "zerodur/zerodur.mp4", "clip_sha256": _sha(b"zero-dur"), "upscale": {"raw_clip": "zerodur/zerodur_raw.mp4"}}).encode(),
        )

        # 6. Still job and QNAP-only layout (no render_ok.json) -> NOT candidates
        _write(self.runs / "run_still" / "s1" / "s1.png", b"img")
        self.still_raw = _write(self.runs / "run_still" / "s1" / "s1_raw.mp4", b"not-video-job")
        _write(
            self.runs / "run_still" / "s1" / "render_ok.json",
            json.dumps({"job_type": "still", "clip_sha256": _sha(b"img"), "upscale": {"raw_clip": "s1/s1_raw.mp4"}}).encode(),
        )
        self.qnap_raw = _write(self.runs / "run_qnap" / "clip" / "clip_raw.mp4", b"qnap-only")

        # 7. SHA256 mismatch cases (#5) -> NOT candidates
        _write(self.runs / "run_bad_clip_sha" / "clip" / "clip.mp4", b"up-sha")
        _write(self.runs / "run_bad_clip_sha" / "clip" / "clip_raw.mp4", b"raw-sha")
        _write(
            self.runs / "run_bad_clip_sha" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": "0" * 64, "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )
        _write(self.runs / "run_bad_raw_sha" / "clip" / "clip.mp4", b"up-sha2")
        _write(self.runs / "run_bad_raw_sha" / "clip" / "clip_raw.mp4", b"raw-sha2")
        _write(
            self.runs / "run_bad_raw_sha" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"up-sha2"), "upscale": {"raw_clip": "clip/clip_raw.mp4", "raw_sha256": "f" * 64}}).encode(),
        )

        # 8. Path-traversal, absolute, cross-tag, nested-subdir, _raw.mp4 clip (#3, #8) -> NOT candidates
        _write(self.runs / "run_tricky" / "clip" / "clip.mp4", b"up-tricky")
        _write(self.runs / "run_tricky" / "other" / "other_raw.mp4", b"cross-tag-raw")
        _write(self.runs / "run_tricky" / "clip" / "sub" / "sub_raw.mp4", b"nested-raw")
        _write(
            self.runs / "run_tricky" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"up-tricky"), "upscale": {"raw_clip": "../outside_raw.mp4"}}).encode(),
        )
        _write(self.runs / "run_abs" / "clip" / "clip.mp4", b"up-abs")
        _write(
            self.runs / "run_abs" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"up-abs"), "upscale": {"raw_clip": "/etc/x_raw.mp4"}}).encode(),
        )
        _write(self.runs / "run_xtag" / "clip" / "clip.mp4", b"up-xtag")
        _write(self.runs / "run_xtag" / "other" / "x_raw.mp4", b"xtag")
        _write(
            self.runs / "run_xtag" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"up-xtag"), "upscale": {"raw_clip": "other/x_raw.mp4"}}).encode(),
        )
        _write(self.runs / "run_nested" / "clip" / "clip.mp4", b"up-nested")
        _write(self.runs / "run_nested" / "clip" / "sub" / "clip_raw.mp4", b"nested")
        _write(
            self.runs / "run_nested" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"up-nested"), "upscale": {"raw_clip": "clip/sub/clip_raw.mp4"}}).encode(),
        )
        _write(self.runs / "run_rawclip" / "clip" / "clip_raw.mp4", b"raw-as-clip")
        _write(
            self.runs / "run_rawclip" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip_raw.mp4", "clip_sha256": _sha(b"raw-as-clip"), "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )

        # 9. Hardlink samefile (#4): raw hardlinked to upscaled -> NOT a candidate
        hl_up = _write(self.runs / "run_samefile" / "clip" / "clip.mp4", b"same-inode")
        os.link(hl_up, self.runs / "run_samefile" / "clip" / "clip_raw.mp4")
        _write(
            self.runs / "run_samefile" / "clip" / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"same-inode"), "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )

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
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"good"), "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )
        # Now break stale_up to 0 bytes before --apply to verify re-check blocks deletion
        stale_up.write_bytes(b"")

        ok_raw_size = self.ok_raw.stat().st_size
        apply_list = self.out / "custom-apply.txt"
        apply_list.write_text(
            "\n".join([str(self.ok_raw), str(self.ok_up), str(self.outside), str(stale_raw)]) + "\n",
            encoding="utf-8",
        )
        r2 = self._run("--runs-dir", str(self.runs), "--apply", str(apply_list))
        self.assertEqual(r2.returncode, 1, r2.stdout + r2.stderr)
        self.assertIn(f"DELETED {self.ok_raw}", r2.stdout)
        self.assertIn(f"SKIP {self.ok_up} not_qualified", r2.stdout)
        self.assertIn(f"APPLY deleted=1 bytes={ok_raw_size} skipped=3 failed=0", r2.stdout)
        applied_log = Path(str(apply_list) + ".applied")
        self.assertTrue(applied_log.is_file())
        self.assertIn(f"DELETED {self.ok_raw}", applied_log.read_text(encoding="utf-8"))

        # Only ok_raw was deleted; everything else (including unlisted ok2_raw) survived
        self.assertFalse(self.ok_raw.exists())
        for p in (self.ok_up, self.ok2_raw, self.outside, stale_raw, self.no_up_raw, self.zero_raw, self.bad_raw):
            self.assertTrue(p.exists(), f"Should not have deleted {p}")

        # Clean apply list (all items valid) -> exits 0
        clean_list = self.out / "clean-apply.txt"
        clean_list.write_text(str(self.ok2_raw) + "\n", encoding="utf-8")
        r3 = self._run("--runs-dir", str(self.runs), "--apply", str(clean_list))
        self.assertEqual(r3.returncode, 0, r3.stdout + r3.stderr)
        self.assertFalse(self.ok2_raw.exists())

    def test_hardlink_nlink_bytes_and_qnap_refusal_and_symlinks(self):
        # Hard-linked raw (st_nlink == 2, distinct from upscaled) -> candidate, but freed bytes == 0 (#4)
        hl_run = self.runs / "run_hl_other" / "clip"
        hl_up = _write(hl_run / "clip.mp4", b"hl-upscaled")
        hl_raw = _write(hl_run / "clip_raw.mp4", b"hl-raw-linked-elsewhere")
        other_link = self.root / "comfy_output_copy.mp4"
        os.link(hl_raw, other_link)
        _write(
            hl_run / "render_ok.json",
            json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"hl-upscaled"), "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
        )
        # Symlinked raw, tag, and run (#8) — created when OS permits symlinks
        sym_created = False
        try:
            sym_up = _write(self.runs / "run_sym_raw" / "clip" / "clip.mp4", b"sym-up")
            os.symlink(self.outside, self.runs / "run_sym_raw" / "clip" / "clip_raw.mp4")
            _write(
                self.runs / "run_sym_raw" / "clip" / "render_ok.json",
                json.dumps({"clip": "clip/clip.mp4", "clip_sha256": _sha(b"sym-up"), "upscale": {"raw_clip": "clip/clip_raw.mp4"}}).encode(),
            )
            os.symlink(self.runs / "run_ok", self.runs / "run_sym_run", target_is_directory=True)
            (self.runs / "run_sym_tag").mkdir()
            os.symlink(self.runs / "run_ok" / "clip", self.runs / "run_sym_tag" / "clip", target_is_directory=True)
            sym_created = True
        except OSError:
            pass

        r = self._run("--runs-dir", str(self.runs), "--out-dir", str(self.out), "--no-pixlstash")
        self.assertEqual(r.returncode, 0, r.stderr)
        m = re.search(r"DRY_RUN candidates=(\d+) bytes=(\d+) list=(.+)", r.stdout)
        self.assertIsNotNone(m, r.stdout)
        self.assertEqual(int(m.group(1)), 3)  # ok_raw, ok2_raw, hl_raw (none of the symlinked ones)
        # hl_raw has st_nlink==2 so contributes 0 to freed bytes
        self.assertEqual(int(m.group(2)), self.ok_raw.stat().st_size + self.ok2_raw.stat().st_size)
        if sym_created:
            listed = Path(m.group(3).strip()).read_text(encoding="utf-8")
            self.assertNotIn("run_sym_", listed)

        # Refuse --runs-dir under /mnt/qnap (#7)
        rq = self._run("--runs-dir", "/mnt/qnap/renders/runs", "--out-dir", str(self.out), "--no-pixlstash")
        self.assertEqual(rq.returncode, 2)
        self.assertIn("refused:", rq.stderr)

    def test_pixlstash_dry_run_report_only_ids_and_counts(self):
        inbox = self.root / "pixl-inbox"
        _write(inbox / "_imported" / "run_ok_clip.mp4", b"a")
        _write(inbox / "_imported" / "run_ok_clip_raw.mp4", b"b")
        _write(inbox / "_imported" / "run_ok2_clip.mp4", b"c")
        # Unknown video names (celeb downloads etc.) must NEVER appear in report (#1)
        _write(inbox / "_imported" / "taylor_swift_beach.mp4", b"d")
        _write(inbox / "_imported" / "taylor_swift_beach_raw.mp4", b"e")

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
                    {"id": 105, "format": "mp4", "file_path": "/data/taylor_swift_beach.mp4"},
                    {"id": 106, "format": "mp4", "file_path": "/data/taylor_swift_beach_raw.mp4"},
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
        self.assertNotIn("taylor", r.stdout.lower())
        self.assertNotIn("clip_raw.mp4", r.stdout.split("PIXLSTASH_REPORT", 1)[1])
        m = re.search(r"PIXLSTASH_REPORT (.+)", r.stdout)
        self.assertIsNotNone(m, r.stdout)
        rep = json.loads(m.group(1))
        self.assertEqual(rep["inbox_imported_multi_video_runs"], {"run_ok": 2})
        self.assertEqual(rep["pixlstash_api"]["status"], "ok")
        self.assertEqual(rep["pixlstash_api"]["multi_video_runs"], {"run_ok": {"count": 2, "picture_ids": [101, 102]}})

        # Non-loopback PixlStash URL must be refused without sending token (#6)
        r_ext = self._run(
            "--runs-dir", str(self.runs),
            "--out-dir", str(self.out),
            "--inbox-dir", str(inbox),
            "--pixl-url", "http://example.com:9537",
            "--pixl-token-file", str(tok_file),
        )
        self.assertEqual(r_ext.returncode, 0, r_ext.stderr)
        rep_ext = json.loads(re.search(r"PIXLSTASH_REPORT (.+)", r_ext.stdout).group(1))
        self.assertEqual(rep_ext["pixlstash_api"]["status"], "refused_non_loopback")


if __name__ == "__main__":
    unittest.main()
