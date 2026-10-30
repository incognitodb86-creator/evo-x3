import ast
import json
import os
import pathlib
import tempfile
import unittest

import _synth
import adult_stub
import flux_edit_guard as G

SCRIPTS = pathlib.Path(__file__).resolve().parents[1]
COMM_MIRROR = os.environ.get("FLUX_EDIT_COMM_MIRROR", "/workspace/cos/community/comm.py")


def graph(text, prefix="flux_edit/x"):
    return {"5": {"class_type": "CLIPTextEncode", "inputs": {"text": text}},
            "24": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix}, "_meta": {"title": "Save"}}}


class GuardText(unittest.TestCase):
    def test_adult_prompt_passes(self):
        self.assertTrue(G.check_graph(graph("head_swap: start with Picture 1 as the base image, adult woman")))

    def test_keyword_in_text_stops(self):
        with self.assertRaises(G.GuardStop):
            G.check_graph(graph("a teen on a beach"))

    def test_keyword_in_other_string_stops(self):
        with self.assertRaises(G.GuardStop):
            G.check_graph(graph("adult woman", prefix="out/schoolgirl_set"))
        g = graph("adult woman")
        g["24"]["_meta"]["title"] = "note: minors"
        with self.assertRaises(G.GuardStop):
            G.check_graph(g)

    def test_nested_list_string_stops(self):
        g = graph("adult")
        g["5"]["inputs"]["extra"] = ["ok", {"deep": "kids"}]
        with self.assertRaises(G.GuardStop):
            G.check_graph(g)

    def test_exception_words_pass(self):
        self.assertTrue(G.check_graph(graph("cowgirl pose, his girlfriend, old-school look")))

    def test_malformed_graph_stops(self):
        for bad in (None, {}, "x"):
            with self.assertRaises(G.GuardStop):
                G.check_graph(bad)

    @unittest.skipUnless(os.path.isfile(COMM_MIRROR), "comm.py mirror absent")
    def test_parity_with_comm_mirror_lists(self):
        tree = ast.parse(pathlib.Path(COMM_MIRROR).read_text(encoding="utf-8"))
        vals = {}
        for n in tree.body:
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("EXC", "BAD"):
                vals[n.targets[0].id] = ast.literal_eval(n.value)
        self.assertEqual(vals["EXC"], G.EXC)
        self.assertEqual(vals["BAD"], G.BAD)


class GuardImages(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.al = os.path.join(self.d, "allow.jsonl")
        self.a = _synth.make(os.path.join(self.d, "a.png"), 64, 64, 1)
        self.b = _synth.make(os.path.join(self.d, "b.png"), 64, 64, 2)
        self.sa, self.sb = G.sha256_file(self.a), G.sha256_file(self.b)

    def test_listed_approved_passes(self):
        G.AllowListWriter(self.al).add(self.sa, "approved", src_path="a.png")
        self.assertEqual(G.check_image(self.a, "klein", G.AllowList(self.al)), self.sa)

    def test_not_on_list_stops(self):
        G.AllowListWriter(self.al).add(self.sa, "approved")
        with self.assertRaises(G.GuardStop):
            G.check_image(self.b, "klein", G.AllowList(self.al))

    def test_missing_list_stops(self):
        with self.assertRaises(G.GuardStop):
            G.AllowList(os.path.join(self.d, "nope.jsonl"))

    def test_derived_with_unlisted_parent_stops(self):
        G.AllowListWriter(self.al).add(self.sb, "derived", parents=["f" * 64])
        with self.assertRaises(G.GuardStop):
            G.check_image(self.b, "klein", G.AllowList(self.al))

    def test_derived_with_listed_parent_passes(self):
        w = G.AllowListWriter(self.al)
        w.add(self.sa, "approved")
        w.add(self.sb, "derived", parents=[self.sa])
        G.check_image(self.b, "klein", G.AllowList(self.al))

    def test_pose_skeleton_in_klein_graph_stops_but_read_ok(self):
        G.AllowListWriter(self.al).add(self.sa, "pose_skeleton")
        with self.assertRaises(G.GuardStop):
            G.check_image(self.a, "klein", G.AllowList(self.al))
        G.check_image(self.a, "read", G.AllowList(self.al))

    def test_unknown_class_refused_and_hand_edit_stops(self):
        with self.assertRaises(G.GuardStop):
            G.AllowListWriter(self.al).add(self.sa, "pose_source")
        G.AllowListWriter(self.al).add(self.sa, "approved")
        rows = [json.loads(x) for x in open(self.al)]
        rows[0]["cls"] = "derived"  # hand edit
        with open(self.al, "w") as f:
            f.write(json.dumps(rows[0]) + "\n")
        with self.assertRaises(G.GuardStop):
            G.AllowList(self.al)
        # hand-appended line without a valid chain
        os.remove(self.al)
        G.AllowListWriter(self.al).add(self.sa, "approved")
        with open(self.al, "a") as f:
            f.write(json.dumps({"sha256": self.sb, "cls": "approved", "parents": [], "path": "", "chain": "x"}) + "\n")
        with self.assertRaises(G.GuardStop):
            G.AllowList(self.al)

    def test_detector_unsure_error_other_stop(self):
        G.AllowListWriter(self.al).add(self.sa, "approved")
        al = G.AllowList(self.al)
        G.check_image(self.a, "klein", al, detector=adult_stub.make("adult"))
        for det in (adult_stub.make("unsure"), adult_stub.make(None), adult_stub.make(exc=RuntimeError("boom"))):
            with self.assertRaises(G.GuardStop):
                G.check_image(self.a, "klein", al, detector=det)

    def test_unknown_kind_stops(self):
        G.AllowListWriter(self.al).add(self.sa, "approved")
        with self.assertRaises(G.GuardStop):
            G.check_image(self.a, "dwpose", G.AllowList(self.al))


class GuardStatic(unittest.TestCase):
    def run_path_sources(self):
        return {p.name: p.read_text(encoding="utf-8") for p in SCRIPTS.glob("*.py")}

    def test_run_path_never_imports_stub(self):
        for name, src in self.run_path_sources().items():
            self.assertNotIn("adult_stub", src, name)

    def test_only_driver_writes_allow_list(self):
        for name, src in self.run_path_sources().items():
            if name in ("flux_edit_guard.py", "flux_edit_run.py"):
                continue
            self.assertNotIn("AllowListWriter", src, name)


if __name__ == "__main__":
    unittest.main()
