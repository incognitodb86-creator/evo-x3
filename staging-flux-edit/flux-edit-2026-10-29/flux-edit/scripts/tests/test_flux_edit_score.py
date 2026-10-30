import csv
import inspect
import json
import os
import pathlib
import shutil
import tempfile
import unittest

from PIL import Image

import flux_edit_guard as G
import flux_edit_score as S
from _synth import make
from test_flux_edit_run import Env

SCRIPTS = pathlib.Path(__file__).resolve().parents[1]
_RUN = None


def window1():
    """One mocked window-1 run (synthetic images only), shared read-only by the sheet tests."""
    global _RUN
    if _RUN is None:
        e = Env()
        assert e.driver().run() == "COMPLETE"
        e.mock.close()
        _RUN = e
    return _RUN


def tearDownModule():
    if _RUN is not None:
        shutil.rmtree(_RUN.d, ignore_errors=True)


def rows(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


class Sheets(unittest.TestCase):
    def setUp(self):
        self.e = window1()
        self.out = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.out, True)

    def build(self, run_dirs=None, **kw):
        e = self.e
        return S.build_sheets(run_dirs or [e.run_dir], e.inputs, e.app, e.allow, self.out, **kw)

    def test_blind_layout_and_orig_arm(self):
        key = self.build()
        self.assertEqual(len(key), 30 * 7)  # 3 arms x 2 seeds + ORIG
        self.assertEqual(len({k["code"] for k in key}), len(key))
        self.assertEqual(sum(k["arm"] == "ORIG" for k in key), 30)
        self.assertEqual(sorted(os.listdir(os.path.join(self.out, "sheets"))), [f"p{i:02d}.png" for i in range(1, 31)])
        rv = rows(os.path.join(self.out, "review_blank.csv"))
        self.assertEqual(list(rv[0]), ["code", "panel", *S.CHECKS])
        blob = open(os.path.join(self.out, "review_blank.csv")).read()
        for arm in ("CTRL", "ORIG", "_bfs_", "432262096973493"):
            self.assertNotIn(arm, blob)
        with Image.open(os.path.join(self.out, "sheets", "p01.png")) as im:
            self.assertFalse(any(k for k in im.info if k not in ("dpi",)), im.info)
        self.assertTrue(os.path.isfile(os.path.join(self.out, "key_NOT_FOR_SCORER", "key.csv")))

    def test_order_is_shuffled_not_arm_sorted(self):
        key = self.build()
        orders = {tuple(k["arm"] for k in key if k["panel"] == p) for p in ("p01", "p02", "p03", "p04", "p05")}
        self.assertGreater(len(orders), 1)

    def test_show_original_off_by_default(self):
        self.assertIs(inspect.signature(S.build_sheets).parameters["show_original"].default, False)
        self.build()
        with Image.open(os.path.join(self.out, "sheets", "p01.png")) as im:
            w0 = im.width
        self.build(show_original=True)
        with Image.open(os.path.join(self.out, "sheets", "p01.png")) as im:
            self.assertGreater(im.width, w0)

    def test_r6_excludes_non_real_rows(self):
        rd = os.path.join(self.out, "run_copy")
        shutil.copytree(self.e.run_dir, rd)
        with open(os.path.join(rd, "status.log"), "a") as f:
            f.write("2026-10-29 00:00:00 CLIP_SKIP p01_bfs_L_s432262096973493 test\n")
            f.write("2026-10-29 00:00:00 JOB error p02_bfs_E_s20261028 test\n")
        key = self.build(run_dirs=[rd])
        self.assertEqual(len(key), 30 * 7 - 2)
        self.assertFalse(any(k["panel"] == "p01" and k["arm"] == "L" and k["seed"] == "432262096973493" for k in key))

    def test_guard_unlisted_output_stops(self):
        rd = os.path.join(self.out, "run_copy")
        shutil.copytree(self.e.run_dir, rd)
        make(os.path.join(rd, "phaseA_bfs", "p03_bfs_E_s20261028.png"), 64, 64, seed=99)
        with self.assertRaises(G.GuardStop):
            self.build(run_dirs=[rd])
        self.assertFalse(os.path.exists(os.path.join(self.out, "key_NOT_FOR_SCORER", "key.csv")))


class Tally(unittest.TestCase):
    def mk(self, usable):
        """usable: {arm: set(panel)}; panels p01..p30, odd panels 9:16/single, even 16:9/multi."""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        key, rev = [], []
        n = 0
        for i in range(1, 31):
            p = f"p{i:02d}"
            asp, cast = ("9:16", "single") if i % 2 else ("16:9", "multi")
            for arm, seeds in (("ORIG", ["-"]), ("L", ["a", "b"]), ("E", ["a", "b"])):
                for s in seeds:
                    n += 1
                    code = f"C{n:04d}"
                    key.append({"code": code, "panel": p, "arm": arm, "seed": s, "file": "x", "aspect": asp, "cast": cast})
                    ok = p in usable.get(arm, set()) and s in ("-", "b")  # only one seed passes
                    rev.append(dict({"code": code, "panel": p}, **{c: "Y" if ok else "N" for c in S.CHECKS}))
        for name, data in (("key.csv", key), ("review.csv", rev)):
            with open(os.path.join(d, name), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(data[0]))
                w.writeheader()
                w.writerows(data)
        return os.path.join(d, "review.csv"), os.path.join(d, "key.csv")

    def test_counts_bar_and_paired(self):
        pp = lambda *ix: {f"p{i:02d}" for i in ix}  # noqa: E731
        r, k = self.mk({"L": pp(1, 2, 3, 4, 5, 6), "E": pp(1, 2, 3, 4, 5), "ORIG": pp(1, 9)})
        rep = S.tally(r, k)
        L, E = rep["arms"]["L"], rep["arms"]["E"]
        self.assertEqual((L["usable_panels"], L["reaches_bar"]), (6, "yes"))
        self.assertEqual((E["usable_panels"], E["reaches_bar"]), (5, "no"))
        self.assertEqual(L["per_aspect"], {"9:16": 3, "16:9": 3})
        self.assertEqual(L["per_cast"], {"single": 3, "multi": 3})
        self.assertEqual(rep["paired"]["L_vs_ORIG"], {"both": 1, "only_L": 5, "only_ORIG": 1, "neither": 23})
        self.assertEqual(rep["paired"]["E_vs_L"]["only_L"], 1)
        self.assertEqual(rep["bar"], "6/30")
        txt = json.dumps(rep).upper()
        self.assertNotIn("KEEP", txt)
        self.assertNotIn("PASS", txt)
        self.assertIn("NOT GATING", txt)

    def test_unscored_or_unknown_code_raises(self):
        r, k = self.mk({})
        rv = rows(r)
        rv[0]["identity"] = ""
        with open(r, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rv[0]))
            w.writeheader()
            w.writerows(rv)
        with self.assertRaises(ValueError):
            S.tally(r, k)

    def test_wilson(self):
        lo, hi = S.wilson(6, 30)
        self.assertAlmostEqual(lo, 0.0951, places=3)
        self.assertAlmostEqual(hi, 0.3730, places=3)
        self.assertEqual(S.wilson(0, 0), (0.0, 0.0))

    def test_reads_through_guard(self):
        src = (SCRIPTS / "flux_edit_score.py").read_text()
        self.assertIn("import flux_edit_guard", src)
        self.assertIn('check_image(p, "read"', src)


if __name__ == "__main__":
    unittest.main()
