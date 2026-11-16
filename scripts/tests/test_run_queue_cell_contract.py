"""B2-10 (2026-11-06): the queue enforces the long-clip plan's clip-cell tag form.

The plan fixes the clip cell dir name of a 3-clip run: c<2 digits>_s<seed> (cNN_sNNNNNNNN).
The rule belongs in the tool that reads a run's order file, and that tool is run_queue.py.
A run turns the rule on by declaring "cell_contract": true in its order file; prepare() then
refuses any tag outside the form, and the clip is not submitted. Order files that do not
declare the contract keep the old behaviour, so no other run changes.
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run_queue

SEED = 51083601
CELL = "c01_s%d" % SEED
# 35 tag forms a long-clip run must never see: the one-run arm dir names of the B2-7 shape,
# the CLI's own tag, short/long seed fields, case, path forms, batch dir names, plain words.
NON_CELLS = [
    "clip1_b2_int8HQ_p1lora0_p2lora1", "clip2_b2_learnedHQ_p1lora0_p2lora1",
    "clip3_b2_learnedHQ_p1lora035_p2lora065", "clip", "c1_s%d" % SEED,
    "c001_s%d" % SEED, "c01_s51083", "c01_s%d_extra" % SEED, "C01_s%d" % SEED,
    "c01_%d" % SEED, "c01-s%d" % SEED, "batch1_18", "batch2_17", "c01_s%d/clip" % SEED,
    "cell01", "c01_s00000", "c99_s%d_" % SEED, " c01_s%d" % SEED, "c01_s%d " % SEED,
    "prompt", "logs", "_render_order", "__pycache__", "1", "01", "c0_s1", "c__s__",
    "c01_s%sx" % SEED, "c01_s%s." % SEED, "*c01_s%d" % SEED, "c01_s%d." % SEED,
    "parent", "run", "job", "tag",
]


class CellContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = self.tmp.name
        self._old = run_queue._CELL_CONTRACT
        self.addCleanup(setattr, run_queue, "_CELL_CONTRACT", self._old)
        # qlog() appends to the shared notes/actions.log; a test must not write there
        for _m in (run_queue, run_queue.comm, run_queue.rgj):
            _saved = dict(vars(_m))
            self.addCleanup(lambda _m=_m, _s=_saved: (vars(_m).clear(), vars(_m).update(_s)))
        # qlog() appends to the shared notes/actions.log; a test must not write there
        run_queue.ACTIONS = os.path.join(self.run, "actions.log")

    def _log(self):
        p = os.path.join(self.run, "_render_queue.log")
        return open(p, encoding="utf-8").read() if os.path.exists(p) else ""

    def _prepare(self, tag, contract=True):
        run_queue._CELL_CONTRACT = contract
        job = {"pos": 1, "tag": tag, "arm": "parody", "scene": "S01_B1", "seed": SEED}
        return run_queue.prepare(self.run, job, 0, lambda m: None)

    def test_the_plan_35_cell_dirs_all_match_the_form(self):
        names = ["c%02d_s%d" % (i, SEED) for i in range(1, 36)]
        self.assertEqual(35, sum(1 for n in names if run_queue.CELL_RE.match(n)))

    def test_35_non_cell_tags_are_rejected_and_never_submitted(self):
        self.assertEqual(35, len(NON_CELLS))
        for tag in NON_CELLS:
            self.assertIsNone(self._prepare(tag), "tag %r must be rejected" % tag)
        log = self._log()
        self.assertEqual(35, log.count("cell_contract=true: this run's tags must be clip cell dirs"))
        self.assertNotIn("START pos=", log, "a rejected tag must never reach the START line")

    def test_a_cell_tag_gets_past_the_tag_check(self):
        os.makedirs(os.path.join(self.run, CELL))
        self.assertIsNone(self._prepare(CELL))  # next check: the bundle's graph file
        log = self._log()
        self.assertIn("START pos=1 tag=%s" % CELL, log)
        self.assertIn("no graph", log)
        self.assertNotIn("cell_contract", log)

    def test_a_run_that_does_not_declare_the_contract_is_unchanged(self):
        os.makedirs(os.path.join(self.run, "clip"))
        self.assertIsNone(self._prepare("clip", contract=False))
        log = self._log()
        self.assertIn("START pos=1 tag=clip", log)
        self.assertNotIn("cell_contract", log)

    def test_main_takes_the_contract_from_the_order_file(self):
        names = ["c%02d_s%d" % (i, SEED) for i in range(1, 36)]
        order = {"cell_contract": True,
                 "order": [{"pos": i, "tag": t} for i, t in enumerate(names + ["clip1_b2_int8HQ"], 1)]}
        qf = os.path.join(self.run, "_render_order.json")
        json.dump(order, open(qf, "w", encoding="utf-8"))
        argv = ["run_queue.py", "--run-dir", self.run, "--queue", qf, "--dry-run"]
        old = sys.argv
        sys.argv = argv
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = run_queue.main()
        finally:
            sys.argv = old
        self.assertEqual(0, rc)
        out = buf.getvalue()
        self.assertIn("cell_contract=true: 35/36 tags are clip cell dirs", out)
        self.assertIn("these would FAIL: clip1_b2_int8HQ", out)
        self.assertFalse(os.path.exists(os.path.join(self.run, "_render_queue.log")),
                         "a dry run writes no queue log, no lock, no GPU and no HTTP call")

    def test_main_without_the_flag_prints_no_contract_line(self):
        order = {"order": [{"pos": 1, "tag": "clip"}]}
        qf = os.path.join(self.run, "_render_order.json")
        json.dump(order, open(qf, "w", encoding="utf-8"))
        old = sys.argv
        sys.argv = ["run_queue.py", "--run-dir", self.run, "--queue", qf, "--dry-run"]
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = run_queue.main()
        finally:
            sys.argv = old
        self.assertEqual(0, rc)
        self.assertNotIn("cell_contract", buf.getvalue())
        self.assertFalse(run_queue._CELL_CONTRACT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
