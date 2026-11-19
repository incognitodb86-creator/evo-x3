"""Offline regression tests for AlienPc ComfyUI hardening (templates, frame snapping, LOST_PROMPT, remote harvest, argv check)."""
from __future__ import annotations

import email.utils
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PARODY_DIR = SCRIPTS_DIR / "parody"
TEMPLATES_DIR = SCRIPTS_DIR.parent / "templates"
for _p in (str(SCRIPTS_DIR), str(PARODY_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import comm
import fill_request as fr
import make_b2_request as mbr
import remote_comfy as rc


class TestTemplatesBeta7Invariants(unittest.TestCase):
    def test_all_eight_video_templates_use_beta7_shift12_vsa_and_audio_mux(self):
        # Plain loop, not subTest: the Ralph gate needs the pytest summary to end in "skipped(, 6 errors)? in".
        for name, path in fr.TEMPLATES.items():
            g = json.loads(path.read_text(encoding="utf-8"))
            msg = f"template {name}"
            self.assertEqual(g["unet"]["inputs"]["unet_name"], "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors", msg)
            self.assertEqual(g["m_shift"]["inputs"]["shift_video"], 12.0, msg)
            self.assertEqual(g["m_shift"]["inputs"]["shift_audio"], 3.0, msg)
            self.assertEqual(g["m_vsa"]["inputs"]["selection"], "vsa", msg)
            self.assertEqual(g["m_vsa"]["inputs"]["selection.keep_percent"], 10, msg)
            self.assertEqual(g["m_vsa"]["inputs"]["dense_blocks"], "0,1", msg)
            self.assertEqual(g["m_vsa"]["inputs"]["start_percent"], 0.0, msg)
            self.assertEqual(g["s0_sched"]["inputs"]["steps"], 8, msg)
            self.assertEqual(g["dec_a"]["class_type"], "VAEDecodeAudio", msg)
            self.assertEqual(g["mkvid"]["inputs"]["audio"], ["dec_a", 0], msg)
            if "ref_image_size" in g["c0"]["inputs"]:
                expected_ref_size = "max" if name == "oc_ref" else "match"
                self.assertEqual(g["c0"]["inputs"]["ref_image_size"], expected_ref_size, msg)
            if "refmods" in g:
                self.assertEqual(g["refmods"]["class_type"], "MiniMaxH3RefModsLoader", msg)
                self.assertNotIn("max_frames", g["refmods"]["inputs"], msg)


class TestFrameSnappingAndFillRequestGuards(unittest.TestCase):
    def test_make_b2_request_snaps_120_to_124_by_default(self):
        self.assertEqual(mbr.snap_h3_frames(1), 5)
        self.assertEqual(mbr.snap_h3_frames(5), 5)
        self.assertEqual(mbr.snap_h3_frames(120), 124)
        self.assertEqual(mbr.snap_h3_frames(124), 124)
        self.assertEqual(mbr.snap_h3_frames(240), 243)
        with tempfile.TemporaryDirectory() as d:
            rc_code = mbr.main([
                "--arm-dir", d,
                "--prompt", "two adult women (18+) walking on the beach",
                "--seed", "42",
                "--image", "community/test.png",
                "--prefix", "community/test/clip",
                "--frames", "120",
            ])
            self.assertEqual(rc_code, 0)
            g = json.load(open(os.path.join(d, "request.api.json"), encoding="utf-8"))
            self.assertEqual(g["c0"]["inputs"]["length"], 124)

    def test_fill_request_catches_out_of_range_frames_and_caps_refmods_to_8(self):
        prompt = (
            "subject_definitions:\n<Subject 1> is an adult woman, 25 years old; she is (S1).\n\n"
            "summary:\nAn adult woman walks on the beach.\n\n"
            "retention_analysis:\n<Subject 1>: fully_preserved - face and hair.\n\n"
            "detailed_description:\n[Shot 1] (S1) walks across warm sand at sunset as waves lap gently."
        )
        with tempfile.TemporaryDirectory() as d:
            bad = fr.fill_request(prompt, Path(d) / "over_cap", frames=300, dry_run=True)
            self.assertEqual(bad["status"], "NOT_READY")
            self.assertIn("exceeds the single-clip ceiling", bad["reason"])

            stems = [f"mod_stem_{i}" for i in range(1, 11)]
            ok = fr.fill_request(prompt, Path(d) / "nine_mods", refmod_stems=stems, frames=120, dry_run=True)
            self.assertEqual(ok["status"], "READY")
            self.assertEqual(ok["frames"], 124)
            self.assertEqual(len(ok["refmods"]["stems"]), 8)
            self.assertIn("refmod_slots_truncated:10->8", ok.get("warnings", []))


class TestLostPromptAndArgvGate(unittest.TestCase):
    def test_comm_run_aborts_after_3_lost_prompt_misses(self):
        out = {}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(comm, "submit", return_value="pid-lost"), \
             mock.patch.object(comm, "fetch", return_value=comm.PENDING) as m_fetch, \
             mock.patch.object(comm, "_in_comfy_queue", return_value=False), \
             mock.patch.object(comm, "log"):
            res = comm.run({}, "clip", {}, d, poll=0.0, timeout=60, out=out)
        self.assertIsNone(res)
        self.assertEqual(out.get("outcome"), "evicted")
        self.assertIn("LOST_PROMPT", out.get("note", ""))
        # 3 loop polls x 2 fetch calls (initial + race re-check) = 6 calls, never spinning to timeout
        self.assertEqual(m_fetch.call_count, 6)

    def test_comm_run_recovers_if_history_populates_right_after_queue_drain(self):
        side = {"file": "clip.mp4"}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(comm, "submit", return_value="pid-race"), \
             mock.patch.object(comm, "fetch", side_effect=[comm.PENDING, side]), \
             mock.patch.object(comm, "_in_comfy_queue", return_value=False), \
             mock.patch.object(comm, "log"):
            res = comm.run({}, "clip", {}, d, poll=0.0, timeout=60, out={})
        self.assertEqual(res, side)

    def test_check_launch_argv_warns_or_raises(self):
        st_bad = {"system": {"argv": ["main.py", "--listen", "127.0.0.1", "--disable-pinned-memory"]}}
        with mock.patch.object(comm, "log"):
            missing = comm.check_launch_argv(st_bad, require_ck=False)
            self.assertEqual(missing, ["--use-ck-attention"])
            with self.assertRaises(RuntimeError):
                comm.check_launch_argv(st_bad, require_ck=True)


class TestRemoteViewHarvestAndBusyWait(unittest.TestCase):
    def test_remote_view_harvest_recovers_single_landed_mp4(self):
        with tempfile.TemporaryDirectory() as d:
            def fake_urlopen(url, timeout=15):
                if "_00002_" in url:
                    raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
                raise AssertionError(f"unexpected urlopen {url}")

            def fake_dl(subf, fname, dst, timeout=300, not_before=None):
                if fname == "clip_00001_.mp4":
                    Path(dst).write_bytes(b"MP4DATA")
                    return 7
                raise urllib.error.HTTPError(fname, 404, "Not Found", {}, None)

            with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen), \
                 mock.patch.object(rc, "download", side_effect=fake_dl):
                got = rc.remote_view_harvest("community/run42/clip", d)
            self.assertIsNotNone(got)
            self.assertTrue(Path(got).is_file())
            self.assertTrue(got.endswith("clip_00001_.mp4"))

    def _view_resp(self, last_modified):
        class _Resp:
            status = 200
            headers = {"Last-Modified": last_modified} if last_modified else {}
            def __init__(self): self._b = io.BytesIO(b"MP4DATA")
            def read(self, n=-1): return self._b.read(n)
            def __enter__(self): return self
            def __exit__(self, *a): return False
        return _Resp()

    def _harvest_with_mtime(self, mtime, since):
        def fake_urlopen(url, timeout=15):
            if "_00002_" in url:
                raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
            if "clip_00001_.mp4" in url:
                return self._view_resp(None if mtime is None else email.utils.formatdate(mtime, usegmt=True))
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen):
            got = rc.remote_view_harvest("community/run42/clip", d, since=since)
            return got, (Path(got).read_bytes() if got else None)

    def test_remote_view_harvest_adopts_file_written_during_attempt(self):
        t_att = 1_800_000_000
        got, data = self._harvest_with_mtime(t_att + 400, t_att)
        self.assertTrue(got and got.endswith("clip_00001_.mp4"))
        self.assertEqual(data, b"MP4DATA")

    def test_remote_view_harvest_refuses_earlier_attempt_output(self):
        t_att = 1_800_000_000
        self.assertEqual(self._harvest_with_mtime(t_att - 30, t_att), (None, None))

    def test_remote_view_harvest_refuses_undated_output(self):
        self.assertEqual(self._harvest_with_mtime(None, 1_800_000_000), (None, None))

    def test_remote_view_harvest_skips_ambiguous_multi_output_prefix(self):
        class _Resp200:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *a): return False

        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(rc.urllib.request, "urlopen", return_value=_Resp200()), \
             mock.patch.object(rc, "download") as m_dl:
            self.assertIsNone(rc.remote_view_harvest("community/run42/clip", d))
            m_dl.assert_not_called()


if __name__ == "__main__":
    unittest.main()
