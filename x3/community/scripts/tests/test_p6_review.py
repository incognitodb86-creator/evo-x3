# Unit tests for p6_review.py parts that need no model and no GPU: ffmpeg frame extraction, CPU metrics, judge-reply parsing,
# guard parsing, ranking aggregation, verdicts, checkshots. Synthetic clips come from ffmpeg lavfi (tiny, CPU only).
# run: python -m pytest C:\AI\community\scripts\tests\test_p6_review.py -q      (never touches llama-swap / ComfyUI)
import json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import p6_review as R

def lavfi(out, src, vf=None, secs=4):
    cmd = [R.FFMPEG, "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", src, "-t", str(secs)] + (["-vf", vf] if vf else []) + ["-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", out]
    subprocess.run(cmd, check=True, capture_output=True); return out

class Clips(unittest.TestCase):
    _audit_blocked = None

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="p6rev_")
        S = "testsrc2=size=192x336:rate=24"
        try:
            cls.smooth = lavfi(os.path.join(cls.d, "smooth.mp4"), S, "hue=s=0.35")
            cls.flicker = lavfi(os.path.join(cls.d, "flicker.mp4"), S, "eq=brightness='0.12*mod(n,2)':eval=frame")
            cls.burn = lavfi(os.path.join(cls.d, "burn.mp4"), S, "hue=s=0.35,eq=saturation='1+0.8*t':eval=frame")
            cls.frozen = lavfi(os.path.join(cls.d, "frozen.mp4"), "color=c=gray:size=192x336:rate=24")
            a = lavfi(os.path.join(cls.d, "a.mp4"), S, secs=2); b = lavfi(os.path.join(cls.d, "b.mp4"), "smptebars=size=192x336:rate=24", secs=2)
            lst = os.path.join(cls.d, "l.txt"); open(lst, "w").write(f"file '{a}'\nfile '{b}'\n")
            cls.cut = os.path.join(cls.d, "cut.mp4")
            subprocess.run([R.FFMPEG, "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cls.cut], check=True, capture_output=True)
        except RuntimeError as exc:
            if "U3 CPU fixture blocked" not in str(exc):
                raise
            cls._audit_blocked = str(exc)

    def setUp(self):
        if self._audit_blocked:
            import pytest
            pytest.xfail(
                f"Blocked by parody/test_c2v_context.py process-wide sys.addaudithook in combined pytest run ({self._audit_blocked})"
            )

    def test_extract_frames_and_sheet(self):
        fr = R.extract_frames(self.smooth, 0.0, 4.0, 6, self.d, "t", width=96)
        self.assertEqual(len(fr), 6)
        ts = [t for _, t in fr]; self.assertEqual(ts, sorted(ts)); self.assertTrue(0.25 <= ts[0] and ts[-1] <= 3.75)
        sheet = R.contact_sheet(fr, os.path.join(self.d, "s.jpg"), cols=3)
        from PIL import Image
        w, h = Image.open(sheet).size; self.assertEqual(w, 96 * 3); self.assertEqual(h % 2, 0)

    def test_probe(self):
        p = R.probe(self.smooth); self.assertEqual((p["w"], p["h"]), (192, 336)); self.assertAlmostEqual(p["dur"], 4.0, delta=0.1); self.assertAlmostEqual(p["fps"], 24.0)

    def test_metrics_flicker(self):
        a, b = R.compute_metrics(self.smooth), R.compute_metrics(self.flicker)
        self.assertGreater(b["lum_flicker"], 4 * max(a["lum_flicker"], 0.1)); self.assertLess(b["objective_score"], a["objective_score"])

    def test_metrics_burn(self):
        a, b = R.compute_metrics(self.smooth), R.compute_metrics(self.burn)
        self.assertGreater(b["sat_drift_max"], 0.15); self.assertLess(abs(a["sat_drift_max"]), 0.05); self.assertGreater(b["objective_penalties"]["burn_sat_drift"], 0)

    def test_metrics_freeze(self):
        m = R.compute_metrics(self.frozen); self.assertGreater(m["freeze_frac"], 0.9); self.assertGreater(m["objective_penalties"]["freeze"], 1.0)

    def test_metrics_cut_and_seam(self):
        m = R.compute_metrics(self.cut, seams=[2.0], spans=[(0, 2), (2, 4)])
        self.assertEqual(len(m["shots"]), 0)   # both 2 s halves are < 3 s -> no drift shots
        n = R.compute_metrics(self.cut); self.assertEqual(n["cuts_detected"], 1); self.assertAlmostEqual(n["cut_times"][0], 2.0, delta=0.1)
        self.assertGreater(n["seam_ratio"] if n["seam_ratio"] else 0, -1)  # no seams given -> 0
        self.assertGreater(R.compute_metrics(self.cut, seams=[2.0])["seam_ratio"], 3.0)

class Pure(unittest.TestCase):
    def test_parse_reply(self):
        txt = 'Sure.\n```json\n{"scores":{"motion_quality":12,"artifacts":"4"},"reasons":{"artifacts":"hands"},"flags":["body_horror","nonsense"]}\n```'
        c = R.norm_abs(R.parse_json_reply(txt))
        self.assertEqual(c["scores"]["motion_quality"], 10); self.assertEqual(c["scores"]["artifacts"], 4); self.assertIsNone(c["scores"]["burn_exposure"])
        self.assertEqual(c["flags"], ["body_horror"])
        with self.assertRaises(ValueError): R.parse_json_reply("no json here")
        p = R.norm_pair({"winner": "b", "dims": {"artifacts": "A", "motion_quality": "x"}})
        self.assertEqual(p["winner"], "B"); self.assertEqual(p["dims"]["artifacts"], "A"); self.assertEqual(p["dims"]["motion_quality"], "TIE")

    def test_guard_parse(self):
        self.assertEqual(R.parse_guard(0, "IDLE\n", {1}), (True, "IDLE"))
        ok, why = R.parse_guard(1, "BUSY: render script p6_review.py (pid 4242)", {4242}); self.assertTrue(ok)
        ok, why = R.parse_guard(1, "note: x\nBUSY: render script p6_review.py (pid 4242); ComfyUI :10002 queue running=1 pending=0", {4242})
        self.assertFalse(ok); self.assertIn("ComfyUI", why); self.assertNotIn("4242", why)
        self.assertFalse(R.parse_guard(1, "BUSY: render script batch_queue.py (pid 42420)", {4242})[0])   # pid match is exact
        self.assertFalse(R.parse_guard(2, "BUSY: guard error (x)", {1})[0])
        self.assertFalse(R.parse_guard(0, "", {1})[0])

    def test_gpu_util_parse(self):
        self.assertEqual(R.parse_util(["5, 15475\n", "15, 15000\n"]), (10.0, 15475.0))
        self.assertEqual(R.parse_util(["garbage"]), (100.0, 0.0)); self.assertEqual(R.parse_util([]), (100.0, 0.0))

    def test_inside_agent(self):
        tab = {10: (5, "python p6_review.py rank"), 5: (3, "powershell -File ralph.ps1"), 3: (0, "explorer.exe"),
               20: (15, "python -c import p6_review"), 15: (12, "powershell.exe -Command x"), 12: (0, 'node "C:/x/@earendil-works/pi-coding-agent/dist/cli.js" --print')}
        self.assertFalse(R.inside_agent(tab, 10)); self.assertTrue(R.inside_agent(tab, 20))
        self.assertFalse(R.inside_agent({1: (1, "loop")}, 1))   # self-parent loop terminates

    def test_guard_runner_failclosed(self):
        def boom(*a, **k): raise OSError("no powershell")
        self.assertFalse(R.run_guard(runner=boom)[0])

    def test_pair_outcome(self):
        A, B, TIE = {"winner": "A"}, {"winner": "B"}, {"winner": "TIE"}
        self.assertEqual(R.pair_outcome(A, B), (1.0, True))      # x first as A wins, then x as B wins
        self.assertEqual(R.pair_outcome(B, A), (0.0, True))
        self.assertEqual(R.pair_outcome(A, A), (0.5, False))     # position bias -> split
        self.assertEqual(R.pair_outcome(TIE, TIE), (0.5, False))
        self.assertEqual(R.pair_outcome(None, A), (0.5, False))

    def test_bradley_terry_order(self):
        names = ["a", "b", "c"]
        res = [("a", "b", 1.0), ("a", "c", 1.0), ("b", "c", 1.0), ("a", "b", 1.0), ("b", "c", 0.5)]
        p, field = R.bradley_terry(names, res)
        self.assertGreater(p["a"], p["b"]); self.assertGreater(p["b"], p["c"]); self.assertTrue(all(0 < v < 1 for v in field.values()))
        p2, f2 = R.bradley_terry(names, [("a", "b", 0.5), ("b", "c", 0.5), ("a", "c", 0.5)])
        self.assertAlmostEqual(f2["a"], 0.5, places=3)

    def test_aggregate_and_flags(self):
        def card(v, flags=()): return {"scores": {k: v for k in R.DIM_KEYS}, "flags": list(flags)}
        per, absv, weak = R.aggregate_abs([card(8), card(4, ["severe_burn"])], card(6))
        self.assertAlmostEqual(per["artifacts"], 0.6 * 6 + 0.4 * 6); self.assertAlmostEqual(weak, 4.0); self.assertAlmostEqual(absv, 0.7 * 6 + 0.3 * 4)
        self.assertEqual(R.count_flags([card(8, ["severe_burn"]), card(8)], card(8)), [])          # one window is not enough
        self.assertEqual(R.count_flags([card(8, ["frozen"]), card(8, ["frozen"])], card(8, ["identity_break"])), ["frozen", "identity_break"])
        self.assertEqual(R.aggregate_abs([None], None), ({k: None for k in R.DIM_KEYS}, None, None))

    def test_composite_and_rank(self):
        self.assertAlmostEqual(R.composite(8, 6, 10, []), 0.4 * 8 + 0.4 * 6 + 0.2 * 10)
        self.assertAlmostEqual(R.composite(8, 6, 10, ["a", "b", "c"]), 0.4 * 8 + 0.4 * 6 + 0.2 * 10 - 1.5)
        self.assertAlmostEqual(R.composite(None, None, 7.5, []), 7.5)
        rows = [{"name": "x", "composite": 7.0, "pairwise": 5, "abs": 6}, {"name": "y", "composite": 7.0, "pairwise": 6, "abs": 5},
                {"name": "z", "composite": None}, {"name": "w", "composite": 8.0}]
        self.assertEqual([r["name"] for r in R.rank_rows(rows)], ["w", "y", "x", "z"])

    def test_verdict(self):
        P = {"composite": 7.0, "flags": []}
        self.assertEqual(R.verdict(P, {"composite": 7.3, "flags": []}, True), "PROMOTE")
        self.assertEqual(R.verdict(P, {"composite": 7.3, "flags": []}, False), "KEEP_PARENT")
        self.assertEqual(R.verdict(P, {"composite": 7.8, "flags": []}, False), "PROMOTE")
        self.assertEqual(R.verdict(P, {"composite": 9.0, "flags": ["frozen"]}, True), "KEEP_PARENT")
        self.assertEqual(R.verdict(P, {"composite": None, "flags": []}, True), "NO_DATA")

    def test_judge_retry_with_fake_chat(self):
        replies = iter(["garbage", '{"scores":{"artifacts":7}}'])
        j = R.Judge("qwen3vl_judge", chat=lambda *a: next(replies))
        c = j.ask([R.T("x")], R.norm_abs); self.assertEqual(c["scores"]["artifacts"], 7); self.assertEqual((j.calls, j.failures), (2, 0))
        j2 = R.Judge("qwen3vl_judge", chat=lambda *a: "nope"); self.assertIsNone(j2.ask([R.T("x")], R.norm_abs)); self.assertEqual(j2.failures, 1)

    def test_windows_of(self):
        c = {"segments": [{"t0": 0, "t1": 20, "beats": ["a", "b"]}, {"t0": 20, "t1": 40, "beats": ["c", "d"]}]}
        w = R.windows_of(c); self.assertEqual([(x[0], x[1], x[2], x[3]) for x in w], [(0, 0, 10, "a"), (0, 10, 20, "b"), (1, 20, 30, "c"), (1, 30, 40, "d")])

    def test_checkshots(self):
        if not R.APPROVED: self.skipTest("comm.py not importable here")
        d = tempfile.mkdtemp(); jid = "p7_unittest_probe"
        good = [{"id": jid + "_seg2", "image": "POOL", "image_note": R.P7_IMAGE_NOTE, "beat": "She walks to the window.", "chunks": ["She smiles."],
                 "chunk_secs": 10, "mode": "r2v", "arm": "long_r2v", "secs": 10, "seed": 51080001, "w": 768, "h": 1344, "steps": 12, "antiburn": 0.5}]
        p = os.path.join(d, jid + ".json"); json.dump(good, open(p, "w"))
        bad = R.check_shots(p, jid); self.assertEqual(len(bad), 1); self.assertIn("shots file must be", bad[0])   # outside shots dir
        orig = R.SHOTS; R.SHOTS = d
        try:
            self.assertEqual(R.check_shots(p, jid), [])
            worse = [dict(good[0], steps=30, loras=[["x", 1]], image="NEW", w=1024)]; json.dump(worse, open(p, "w"))
            msgs = " ".join(R.check_shots(p, jid))
            for frag in ("steps", "loras", "approved", "768x1344"): self.assertIn(frag, msgs)
            # pool-20261021: P7 is fixed on POOL - D15, a D15 subject note or D15 subject words in the beat are refused
            json.dump([dict(good[0], image="D15")], open(p, "w"))
            self.assertTrue(any("must be POOL" in m for m in R.check_shots(p, jid)))
            json.dump([dict(good[0], image_note="adult woman with long dark hair in a high bun")], open(p, "w"))
            self.assertTrue(any("image_note must be exactly" in m for m in R.check_shots(p, jid)))
            json.dump([dict(good[0], beat="Topless in her black bikini bottoms she walks to the window.")], open(p, "w"))
            self.assertTrue(any("D15 subject" in m for m in R.check_shots(p, jid)))
            json.dump(good, open(p, "w")); self.assertEqual(R.check_shots(p, jid), [])
            self.assertTrue(R.check_shots(p, "../evil"))
        finally: R.SHOTS = orig

class JudgeFix(unittest.TestCase):
    # judge-20261021: pairwise identity anchor per video; a review with 0 usable judge replies is not ok
    def test_pair_refs(self):
        txt, refs = R.pair_refs("ref_D15.jpg", "ref_D15.jpg"); self.assertEqual(refs, ["ref_D15.jpg"]); self.assertIn("Image 3 = video B", txt)
        txt, refs = R.pair_refs("ref_D15.jpg", "ref_POOL.jpg"); self.assertEqual(refs, ["ref_D15.jpg", "ref_POOL.jpg"])
        self.assertIn("own reference", txt); self.assertIn("Image 4 = video B", txt)
        self.assertEqual(R.pair_refs("ref_POOL.jpg", "ref_D15.jpg")[1], ["ref_POOL.jpg", "ref_D15.jpg"])   # follows A/B order on swap
        for a, b in (("ref_D15.jpg", None), (None, "ref_POOL.jpg"), (None, None)):
            txt, refs = R.pair_refs(a, b); self.assertEqual(refs, []); self.assertTrue(txt.startswith("Image 1 = video A frames"))

    def test_judge_unusable(self):
        m = lambda asks, fails, used=True: {"model_used": used, "asks": asks, "judge_failures": fails}
        self.assertFalse(R.judge_unusable(m(8, 0))); self.assertFalse(R.judge_unusable(m(8, 2)))
        self.assertTrue(R.judge_unusable(m(8, 3))); self.assertTrue(R.judge_unusable(m(5, 5))); self.assertTrue(R.judge_unusable(m(0, 0)))
        self.assertFalse(R.judge_unusable(m(0, 0, used=False))); self.assertFalse(R.judge_unusable(None))

if __name__ == "__main__":
    unittest.main()
