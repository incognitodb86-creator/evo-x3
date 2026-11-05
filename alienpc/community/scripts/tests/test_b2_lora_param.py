# F2a (cleanup 2026-11-05, card item 2) regression tests for make_b2_request --lora/--strength.
# Offline: no HTTP, no GPU, no ComfyUI. The graph the parameterized path builds must equal the per-face
# FC_*.api.json files it replaces (C:\AI\_archive\2026-11-05-cleanup\7\faces\, node id + class_type +
# LoRA inputs), and --lora none must build the plain b2 graph with no LoraLoader node.
import json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # C:\AI\community\scripts
sys.path.insert(0, ROOT)
import make_b2_request as mbr

# The archived per-face copies (retired by cleanup phase 2); one is enough to prove the wiring.
FC_DIR = r"C:\AI\_archive\2026-11-05-cleanup\7\faces"
FC_FILE = os.path.join(FC_DIR, "FC_ARIANA.api.json")
LORA = "FC_ARIANA_h3_face_v1.safetensors"
BASE = dict(prompt="two adult women (18+), no pose change", seed=1, image="community/X.png",
            prefix="community/_selftest/x", frames=22)


def nodes(g):
    return {k: g[k]["class_type"] for k in g}


class TestB2LoraParam(unittest.TestCase):
    def setUp(self):
        with open(mbr.TEMPLATE, encoding="utf-8") as f:
            self.b2 = json.load(f)

    def test_lora_injects_the_face_lora_on_the_model_chain(self):
        g = mbr.build(self.b2, lora=LORA, strength=0.7, **BASE)
        self.assertIn("lora", g)
        self.assertEqual(g["lora"]["class_type"], "LoraLoader")
        self.assertEqual(g["lora"]["inputs"]["lora_name"], LORA)
        self.assertEqual(g["lora"]["inputs"]["strength_model"], 0.7)
        self.assertEqual(g["lora"]["inputs"]["model"], ["unet", 0])
        self.assertEqual(g["lora"]["inputs"]["clip"], ["clip", 0])
        self.assertEqual(g["m_attn"]["inputs"]["model"], ["lora", 0], "the model chain must go through the LoRA")

    def test_strength_is_applied(self):
        self.assertEqual(mbr.build(self.b2, lora=LORA, strength=0.35, **BASE)["lora"]["inputs"]["strength_model"], 0.35)

    def test_lora_none_is_the_plain_b2_graph(self):
        g = mbr.build(self.b2, lora=None, **BASE)
        self.assertNotIn("lora", g)
        self.assertEqual(nodes(g), nodes(self.b2), "--lora none must not change the b2 node set")
        self.assertEqual(g["m_attn"]["inputs"]["model"], ["unet", 0])
        # only the documented per-run fields may differ from the template
        changed = {k for k in set(g) | set(self.b2) if g.get(k) != self.b2.get(k)}
        self.assertEqual(changed, {"c0", "img", "noise", "save"})

    def test_cli_lora_none_builds_the_plain_graph(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(mbr.main(["--arm-dir", d, "--prompt", BASE["prompt"], "--seed", "1",
                                      "--image", BASE["image"], "--prefix", BASE["prefix"],
                                      "--frames", "22", "--lora", "none"]), 0)
            g = json.load(open(os.path.join(d, "request.api.json"), encoding="utf-8"))
        self.assertEqual(nodes(g), nodes(self.b2))

    @unittest.skipUnless(os.path.isfile(FC_FILE), "archived FC_*.api.json copy not present")
    def test_generated_graph_matches_the_fc_file_it_replaces(self):
        fc = json.load(open(FC_FILE, encoding="utf-8"))
        g = mbr.build(self.b2, lora=LORA, strength=0.7, **BASE)
        self.assertEqual(nodes(g), nodes(fc), "node set must equal the retired per-face template")
        self.assertEqual(g["lora"]["inputs"], fc["lora"]["inputs"], "LoRA node wiring must match")
        self.assertEqual(g["m_attn"]["inputs"]["model"], fc["m_attn"]["inputs"]["model"])


if __name__ == "__main__":
    unittest.main()
