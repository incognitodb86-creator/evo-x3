import csv
import os
import shutil
import tempfile
import unittest

import _synth
import flux_edit_guard as G
import flux_edit_pick as P

ANG = ["profile", "side", "three-quarter", "front"]


class Fixture:
    """Synthetic approved folder: flat-colour PNGs only. chars A..F, plus E10, _dropped, REALX (real-named)."""

    def __init__(self, n_portrait=24, n_land=10, n_multi=4, extra=None):
        self.d = tempfile.mkdtemp()
        self.app = os.path.join(self.d, "approved")
        self.ann = []
        seed = 0
        chars = ["A", "B", "C", "D", "F"]
        for cid in chars + ["E10", "_dropped", "REALX"]:
            os.makedirs(os.path.join(self.app, cid))
        for i in range(n_portrait + n_land):
            cid = chars[i % len(chars)]
            w, h = (768, 1344) if i < n_portrait else (1344, 768)
            self.add(cid, f"s{i:02d}.png", w, h, cid, "single", ANG[i % 4], seed := seed + 1)
        for i in range(n_multi):
            cid = chars[i % len(chars)]
            other = chars[(i + 1) % len(chars)]
            self.add(cid, f"m{i:02d}.png", 768, 1344, f"{cid};{other}", "multi", "side", seed := seed + 1)
        for cid in chars:  # one head-ref-only still each (odd size: never a body)
            self.add(cid, "headsrc.png", 512, 512, cid, "single", "front", seed := seed + 1)
        for cid in ("E10", "_dropped", "REALX"):
            self.add(cid, "x.png", 768, 1344, cid, "single", "front", seed := seed + 1)
        self.write_ann()
        self.real = os.path.join(self.d, "real_named.txt")
        open(self.real, "w").write("REALX\n")
        self.prior = os.path.join(self.d, "prior.txt")
        open(self.prior, "w").write("# sha256,path\n")
        self.out = os.path.join(self.d, "inputs")

    def add(self, cid, fn, w, h, chars, cast, angle, seed, annotate=True):
        p = _synth.make(os.path.join(self.app, cid, fn), w, h, seed)
        if annotate:
            self.ann.append({"path": f"{cid}/{fn}", "characters": chars, "cast": cast,
                             "target": chars.split(";")[0], "angle": angle, "adult": "Y"})
        return p

    def write_ann(self):
        self.annp = os.path.join(self.d, "annotations.csv")
        with open(self.annp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["path", "characters", "cast", "target", "angle", "adult"])
            w.writeheader()
            w.writerows(self.ann)

    def run(self, out=None):
        return P.run(self.app, self.annp, self.real, self.prior, out or self.out)

    def rows(self, name="picks.csv", out=None):
        with open(os.path.join(out or self.out, name), newline="") as f:
            return list(csv.DictReader(f))

    def cleanup(self):
        shutil.rmtree(self.d, ignore_errors=True)


class Picker(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()

    def tearDown(self):
        self.fx.cleanup()

    def test_happy_path_counts_and_quotas(self):
        self.fx.run()
        rows = self.fx.rows()
        bodies = [r for r in rows if r["role"] == "body"]
        self.assertEqual(len(bodies), 30)
        self.assertEqual(sum(r["role"] == "canary" for r in rows), 1)
        self.assertGreaterEqual(sum(r["aspect"] == "9:16" for r in bodies), 3)
        self.assertGreaterEqual(sum(r["aspect"] == "16:9" for r in bodies), 3)
        self.assertGreaterEqual(sum(r["cast"] == "multi" for r in bodies), 1)
        self.assertGreaterEqual(sum(r["cast"] == "single" for r in bodies), 1)
        self.assertTrue(all(len(r["sha256"]) == 64 and r["class"] == "approved" for r in rows))
        self.assertEqual(len({r["sha256"] for r in rows}), 31)
        canary = [r for r in rows if r["role"] == "canary"][0]
        self.assertEqual(canary["angle"], "front")

    def test_excluded_ids_never_picked(self):
        self.fx.run()
        for r in self.fx.rows() + [{"path": h["source_path"]} for h in self.fx.rows("head_refs.csv")]:
            self.assertFalse(r["path"].split("/")[0] in ("E10", "_dropped", "REALX"), r["path"])
        rej = {r["path"] for r in self.fx.rows("rejected.csv")}
        self.assertTrue({"E10/", "_dropped/", "REALX/"} <= rej)

    def test_seeded_deterministic(self):
        self.fx.run()
        a = open(os.path.join(self.fx.out, "picks.csv")).read()
        out2 = os.path.join(self.fx.d, "inputs2")
        self.fx.run(out2)
        self.assertEqual(a, open(os.path.join(out2, "picks.csv")).read())

    def test_head_refs_not_bodies_and_hashed(self):
        self.fx.run()
        picked = {r["sha256"] for r in self.fx.rows()}
        heads = self.fx.rows("head_refs.csv")
        targets = {r["target"] for r in self.fx.rows()}
        self.assertEqual({h["character"] for h in heads}, targets)
        for h in heads:
            self.assertNotIn(h["source_sha256"], picked)
            self.assertEqual(h["crop_box"], "PENDING_MA")

    def test_multi_with_excluded_costar_rejected(self):
        self.fx.add("A", "with_e10.png", 768, 1344, "A;E10", "multi", "side", 999)
        self.fx.write_ann()
        self.fx.run()
        rej = {r["path"]: r["reason"] for r in self.fx.rows("rejected.csv")}
        self.assertIn("A/with_e10.png", rej)
        self.assertNotIn("A/with_e10.png", {r["path"] for r in self.fx.rows()})

    def test_missing_annotation_is_unsure_and_stops(self):
        self.fx.add("A", "unannotated.png", 768, 1344, "A", "single", "side", 998, annotate=False)
        with self.assertRaises(P.PickStop) as cm:
            self.fx.run()
        self.assertIn("UNSURE", str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(self.fx.out, "picks.csv")))

    def test_inconsistent_annotation_stops(self):
        self.fx.ann[0]["cast"] = "multi"  # one character but multi
        self.fx.write_ann()
        with self.assertRaises(P.PickStop):
            self.fx.run()

    def test_prior_run_sha_and_path_rejected(self):
        first = os.path.join(self.fx.app, "A", "s00.png")
        sha = G.sha256_file(first)
        open(self.fx.prior, "a").write(f"{sha},C:/x/loop1017/bodies/zzz.png\n,B/s01.png\n")
        self.fx.run()
        rej = {r["path"]: r["reason"] for r in self.fx.rows("rejected.csv")}
        self.assertEqual(rej.get("A/s00.png"), "used in 10-17 run")
        self.assertEqual(rej.get("B/s01.png"), "used in 10-17 run")
        self.assertNotIn(sha, {r["sha256"] for r in self.fx.rows()})

    def test_required_lists_missing_stop(self):
        os.remove(self.fx.prior)
        with self.assertRaises(P.PickStop):
            self.fx.run()


class PickerShortfall(unittest.TestCase):
    def test_fewer_than_30_stops_with_count(self):
        fx = Fixture(n_portrait=20, n_land=5, n_multi=2)
        try:
            with self.assertRaises(P.PickStop) as cm:
                fx.run()
            self.assertIn("eligible bodies", str(cm.exception))
            self.assertFalse(os.path.exists(os.path.join(fx.out, "picks.csv")))
        finally:
            fx.cleanup()

    def test_no_16_9_quota_stops(self):
        fx = Fixture(n_portrait=34, n_land=0)
        try:
            with self.assertRaises(P.PickStop) as cm:
                fx.run()
            self.assertIn("quota", str(cm.exception))
        finally:
            fx.cleanup()


class Crop(unittest.TestCase):
    def test_crop_deterministic_bounds_and_note(self):
        d = tempfile.mkdtemp()
        src = _synth.make(os.path.join(d, "s.png"), 400, 300, 5)
        a = P.crop_head(src, (10, 10, 100, 120), os.path.join(d, "a.png"))
        b = P.crop_head(src, (10, 10, 100, 120), os.path.join(d, "b.png"))
        self.assertEqual(a[:3], b[:3])
        self.assertEqual(a[:2], (100, 120))
        self.assertIn("NEEDS_DEREK", a[3])
        self.assertIn("not a gate", a[3])
        with self.assertRaises(P.PickStop):
            P.crop_head(src, (350, 10, 100, 100), os.path.join(d, "c.png"))
        shutil.rmtree(d)

    def test_verify_picks_missing_file_stops(self):
        fx = Fixture()
        try:
            fx.run()
            p = os.path.join(fx.out, "picks.csv")
            self.assertEqual(len(P.verify_picks(p, fx.app)), 31)
            os.remove(os.path.join(fx.app, fx.rows()[1]["path"]))
            with self.assertRaises(P.PickStop):
                P.verify_picks(p, fx.app)
        finally:
            fx.cleanup()


if __name__ == "__main__":
    unittest.main()
