# (b)(c)(d) regression tests, brief 2026-11-02-2010 (Derek GO 8:19 PM CT). Offline: no HTTP, no GPU, no ComfyUI.
import csv, hashlib, json, os, sys, tempfile, time, unittest
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import comm
import run_queue as rq


class TestLlmGate(unittest.TestCase):  # (b)
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.lock = os.path.join(self.tmp.name, "gpu-render.lock")
    def tearDown(self): self.tmp.cleanup()

    def test_no_lock_allows(self):
        comm.llm_gate(self.lock, alive=lambda p: True)

    def test_live_foreign_lock_refuses(self):
        open(self.lock, "w").write("4242 2026-11-02T20:30:00 run_queue h3_firstframe_ab_20261102\n")
        with self.assertRaises(comm.GpuBusy):
            comm.llm_gate(self.lock, alive=lambda p: True, me=1)

    def test_dead_pid_is_stale(self):
        open(self.lock, "w").write("4242 x run_queue r\n")
        comm.llm_gate(self.lock, alive=lambda p: False, me=1)

    def test_own_lock_allows(self):
        open(self.lock, "w").write("77 x judge_vlm\n")
        comm.llm_gate(self.lock, alive=lambda p: True, me=77)

    def test_llm_never_posts_when_busy(self):
        open(self.lock, "w").write("4242 x run_queue r\n")
        with mock.patch.object(comm, "GPU_LOCK_FILE", self.lock), mock.patch.object(comm, "_pid_alive", lambda p: True), \
             mock.patch.object(comm, "http") as h:
            with self.assertRaises(comm.GpuBusy):
                comm.llm("sys", "user")
            h.assert_not_called()


class TestPromptIdsAndHarvest(unittest.TestCase):  # (c)
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); b = self.tmp.name
        self.C = os.path.join(b, "ComfyUI"); self.run = os.path.join(b, "runs", "R1"); self.tag = "c1_kf"
        os.makedirs(os.path.join(self.run, self.tag)); os.makedirs(os.path.join(self.C, "output"))
        self.g = {"save": {"class_type": "SaveVideo", "inputs": {"filename_prefix": "community/R1/%s/%s" % (self.tag, self.tag)}}}
        json.dump(self.g, open(os.path.join(self.run, self.tag, "request.api.json"), "w"))
        self.job = {"pos": 1, "tag": self.tag}
    def tearDown(self): self.tmp.cleanup()

    def test_expected_prefix(self):
        self.assertEqual(rq.expected_prefix(self.g), "community/R1/c1_kf/c1_kf")

    def test_save_pid_written_at_submit(self):
        rq.save_pid(self.run, self.tag, "pid-1", rq.expected_prefix(self.g), False)
        d = json.load(open(os.path.join(self.run, rq.PIDS_FILE)))
        self.assertEqual(d[self.tag]["prompt_id"], "pid-1")
        self.assertEqual(d[self.tag]["expected_prefix"], "community/R1/c1_kf/c1_kf")

    def _patched(self):
        return [mock.patch.object(comm, "C", self.C), mock.patch.object(rq, "OUT_ROOT", os.path.join(self.C, "output", "community")),
                mock.patch.object(rq, "ACTIONS", os.path.join(self.tmp.name, "actions.log"))]

    def test_nested_layout_evicted_history_harvested_from_disk(self):
        rq.save_pid(self.run, self.tag, "pid-ev", rq.expected_prefix(self.g), False)
        nested = os.path.join(self.C, "output", "community", "R1", self.tag); os.makedirs(nested)
        open(os.path.join(nested, self.tag + "_00001_.mp4"), "wb").write(b"v" * 10)
        open(os.path.join(nested, self.tag + "1_00001_.mp4"), "wb").write(b"x")  # near-miss tag ignored
        ps = self._patched()
        for p in ps: p.start()
        try:
            with mock.patch.object(comm, "fetch", return_value=comm.PENDING), \
                 mock.patch.object(rq, "finish", return_value=True) as fin:
                todo, adopted, done = rq.harvest(self.run, [self.job], 124, (768, 1344), lambda *a: None, queue_ids=set())
        finally:
            for p in ps: p.stop()
        self.assertEqual(todo, []); self.assertEqual(adopted, {}); self.assertEqual(done, [self.job])
        self.assertEqual(fin.call_args[0][7]["outcome"], "evicted")
        log = open(os.path.join(self.run, "_render_queue.log"), encoding="utf-8").read()
        self.assertIn("HARVEST pos=1 tag=c1_kf prompt_id=pid-ev collected from disk", log)

    def test_prefix_output_finds_nested_file(self):
        nested = os.path.join(self.C, "output", "community", "R1", self.tag); os.makedirs(nested)
        f = os.path.join(nested, self.tag + "_00002_.mp4"); open(f, "wb").write(b"v")
        with mock.patch.object(comm, "C", self.C):
            self.assertEqual(rq.prefix_output("community/R1/c1_kf/c1_kf", time.time() - 60), f)

    def test_still_queued_is_adopted_not_resubmitted(self):
        rq.save_pid(self.run, self.tag, "pid-q", rq.expected_prefix(self.g), False)
        ps = self._patched()
        for p in ps: p.start()
        try:
            with mock.patch.object(comm, "fetch") as fe:
                todo, adopted, done = rq.harvest(self.run, [self.job], 124, (768, 1344), lambda *a: None, queue_ids={"pid-q"})
        finally:
            for p in ps: p.stop()
        self.assertEqual(todo, []); self.assertIn("pid-q", adopted); fe.assert_not_called()

    def test_nothing_anywhere_is_resubmitted(self):
        rq.save_pid(self.run, self.tag, "pid-x", rq.expected_prefix(self.g), False)
        ps = self._patched()
        for p in ps: p.start()
        try:
            with mock.patch.object(comm, "fetch", return_value=comm.PENDING):
                todo, adopted, done = rq.harvest(self.run, [self.job], 124, (768, 1344), lambda *a: None, queue_ids=set())
        finally:
            for p in ps: p.stop()
        self.assertEqual(todo, [self.job]); self.assertEqual(done, [])

    def test_no_record_means_submit(self):
        todo, adopted, done = rq.harvest(self.run, [self.job], 124, (768, 1344), lambda *a: None, queue_ids=set())
        self.assertEqual(todo, [self.job])

    def test_mark_collected(self):
        p = os.path.join(self.tmp.name, "gpu-render.collected"); comm.mark_collected(pid=55, path=p)
        self.assertTrue(open(p).read().startswith("55 "))


class TestClipShaBackfill(unittest.TestCase):  # (d)
    def test_backfill_fills_only_empty(self):
        # F6b: the tests moved to C:\AI\lib\tests, so ".." is now C:\AI\lib and has no notes folder. The
        # helper this test imports (h3_lora_ab_judge_check.py) lives in the community work tree, which is
        # where it always lived; that path is added, then the import is exactly as before.
        for cand in (os.path.join(os.path.dirname(os.path.dirname(HERE)), "notes"),
                     r"C:\AI\community\notes"):
            if os.path.isdir(cand) and cand not in sys.path:
                sys.path.insert(0, cand)
        import h3_lora_ab_judge_check as jc
        with tempfile.TemporaryDirectory() as b:
            runs = os.path.join(b, "runs"); os.makedirs(os.path.join(runs, "c1")); os.makedirs(os.path.join(runs, "c2"))
            open(os.path.join(runs, "c1", "c1.mp4"), "wb").write(b"one"); open(os.path.join(runs, "c2", "c2.mp4"), "wb").write(b"two")
            key = os.path.join(b, "key.csv")
            with open(key, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=["pack_id", "cell", "clip_sha256", "bytes"]); w.writeheader()
                w.writerow({"pack_id": "a01", "cell": "c1", "clip_sha256": "", "bytes": 3})
                w.writerow({"pack_id": "a02", "cell": "c2", "clip_sha256": "keep", "bytes": 3})
            self.assertEqual(jc.backfill_clip_sha(key, runs), 1)
            rows = list(csv.DictReader(open(key, encoding="utf-8")))
            self.assertEqual(rows[0]["clip_sha256"], hashlib.sha256(b"one").hexdigest())
            self.assertEqual(rows[1]["clip_sha256"], "keep")
            self.assertEqual(jc.sha256_file(os.path.join(runs, "c2", "c2.mp4")), hashlib.sha256(b"two").hexdigest())


if __name__ == "__main__": unittest.main()
