# Unit tests for scripts/queue/flux_phase_gate.py (FLX-01, plan v3 section 3)
import csv, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(os.path.dirname(HERE), "queue")
if QUEUE not in sys.path:
    sys.path.insert(0, QUEUE)

import flux_phase_gate as g

def write_scores(d, n, hands_no=0):
    with open(os.path.join(d, "scores.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id"] + list(g.CHECKS) + ["face_sim", "s_per_image", "notes"])
        for i in range(n):
            flags = ["yes"] * len(g.CHECKS)
            if i < hands_no:
                flags[g.CHECKS.index("Hands")] = "no"
            w.writerow([i] + flags + ["0.8", "", ""])

class TestFluxPhaseGate(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.d = self.t.name
    def tearDown(self):
        self.t.cleanup()
    def rc(self, *args):
        return g.main(["--run-dir", self.d] + list(args))

    def test_missing_csv_fails_rc2_and_writes_gate(self):
        self.assertEqual(self.rc("--phase", "2"), 2)
        txt = open(os.path.join(self.d, "_gate.txt"), encoding="utf-8").read()
        self.assertIn("GATE FAIL: scores.csv missing", txt)
        self.assertIn(os.path.join(self.d, "scores.csv"), txt)
    def test_report_only_rc0_even_when_failing(self):
        self.assertEqual(self.rc("--phase", "1", "--report-only"), 0)
    def test_too_few_rows_fails(self):
        write_scores(self.d, 60)
        self.assertEqual(self.rc("--phase", "2"), 2)
    def test_enough_rows_passes_phase2(self):
        write_scores(self.d, 61)
        self.assertEqual(self.rc("--phase", "2"), 0)
    def test_phase3_needs_winner(self):
        write_scores(self.d, 5)
        self.assertEqual(self.rc("--phase", "3", "--jobs", "5"), 2)
        open(os.path.join(self.d, "winner.txt"), "w").write("S2\n")
        self.assertEqual(self.rc("--phase", "3", "--jobs", "5"), 0)
    def test_phase4_hands_bar(self):
        write_scores(self.d, 30, hands_no=5)
        self.assertEqual(self.rc("--phase", "4"), 0)
        write_scores(self.d, 30, hands_no=6)
        self.assertEqual(self.rc("--phase", "4"), 2)
    def test_derrick_bar_phases_never_pass(self):
        write_scores(self.d, 10)
        self.assertEqual(self.rc("--phase", "5", "--jobs", "10"), 2)
    def test_missing_run_dir_fails(self):
        self.assertEqual(g.main(["--phase", "2", "--run-dir", os.path.join(self.d, "nope")]), 2)

if __name__ == "__main__":
    unittest.main()
