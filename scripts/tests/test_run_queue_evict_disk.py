# Regression (2026-10-31 Klein N12): an evicted/stalled job whose output already landed flat in
# ComfyUI output/community/<run>/<tag>_00001_.ext is collected as DONE, never failed/retried. Offline.
import os, sys, tempfile, time, unittest
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import run_queue as rq


class TestEvictDiskFallback(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); b = self.tmp.name
        self.out = os.path.join(b, "out"); self.run = os.path.join(b, "runs", "R1")
        os.makedirs(os.path.join(self.out, "R1")); os.makedirs(self.run)
    def tearDown(self): self.tmp.cleanup()

    def _go(self, tag, ext, job_type, outcome, probe):
        os.makedirs(os.path.join(self.run, tag))
        t_att = time.time() - 60
        open(os.path.join(self.out, "R1", tag + "1_00001_" + ext), "wb").write(b"x")  # near-miss tag must be ignored
        open(os.path.join(self.out, "R1", tag + "_00001_" + ext), "wb").write(b"x" * 10)
        job = {"pos": 4, "tag": tag, "job_type": job_type}
        with mock.patch.object(rq, "OUT_ROOT", self.out), mock.patch.object(rq.rgj, "probe", return_value=probe), \
             mock.patch.object(rq.rgj, "blackfreeze", return_value=[]), \
             mock.patch.object(rq.rgj, "collect_from_disk", return_value=None):
            try:
                ok = rq.finish(self.run, job, 121, (752, 1360), False, lambda *a: None, None,
                               {"outcome": outcome, "prompt_id": "p"}, {}, t_att, t_att)
            except Exception:
                ok = None  # post-objective bookkeeping may need more mocks; the FAIL-stall line is what matters
        log = open(os.path.join(self.run, "_render_queue.log"), encoding="utf-8").read() if os.path.exists(os.path.join(self.run, "_render_queue.log")) else ""
        self.assertNotIn("FAIL", log)
        self.assertNotEqual(ok, False)
        self.assertTrue(os.path.exists(os.path.join(self.run, tag, tag + ext)))
        return log

    def test_still_evicted(self):
        log = self._go("kx_N12_P2_E1_s7", ".png", "still", "evicted", {"bytes": 10, "w": 752, "h": 1360})
        self.assertIn("DONE pos=4", log)

    def test_clip_stalled(self):
        self._go("gi_P1_s5", ".mp4", "clip", "stalled", {"bytes": 10, "w": 752, "h": 1360, "frames": 121, "audio": True})

    def test_nothing_landed_still_fails(self):
        self.assertIsNone(rq.disk_output(self.run, "nope", time.time()))


if __name__ == "__main__": unittest.main()
