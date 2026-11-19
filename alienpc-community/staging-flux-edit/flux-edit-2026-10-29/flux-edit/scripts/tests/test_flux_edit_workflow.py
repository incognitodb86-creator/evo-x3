import json
import os
import shutil
import tempfile
import unittest

import flux_edit_guard as G
import flux_edit_workflow as W
import tpl_check
import tpl_fill
from tpl_fill import _jl, _wr
import pathlib

SEED = 432262096973493


def b(arm="L", **kw):
    a = dict(arm=arm, body_image="flux_edit/body1.png", head_image="flux_edit/head1.png", seed=SEED,
             lora_name=W.PINS["lora"]["name"], prefix="flux_edit/p01_bfs_L_s1")
    a.update(kw)
    return W.build(**a)


def node(g, title):
    return [n for n in g.values() if n["_meta"]["title"] == title][0]


class Workflow(unittest.TestCase):
    def test_template_files_match_generator(self):
        d = os.path.join(W.TEMPLATES, W.NAME, W.VERSION)
        for fn, txt in W.template_files().items():
            self.assertEqual(pathlib.Path(d, fn).read_text(encoding="utf-8"), txt, fn)
        tpl_fill.verify_index(W.TEMPLATES, W.NAME, W.VERSION)

    def test_image_order_body1_head2(self):
        g = b()
        self.assertEqual(node(g, "picture1_body")["inputs"]["image"], "flux_edit/body1.png")
        self.assertEqual(node(g, "picture2_head")["inputs"]["image"], "flux_edit/head1.png")
        body_id = [k for k, n in g.items() if n["_meta"]["title"] == "picture1_body"][0]
        enc_body = node(g, "enc_body")["inputs"]["pixels"][0]
        self.assertEqual(enc_body, body_id)
        self.assertEqual(node(g, "body_size")["inputs"]["image"][0], body_id)  # unscaled body sets size (R8)
        # ref1 (first ReferenceLatent on positive) must take the body latent
        enc_body_id = [k for k, n in g.items() if n["_meta"]["title"] == "enc_body"][0]
        self.assertEqual(node(g, "ref1_pos_body")["inputs"]["latent"][0], enc_body_id)
        self.assertEqual(node(g, "ref2_pos_head")["inputs"]["conditioning"][0],
                         [k for k, n in g.items() if n["_meta"]["title"] == "ref1_pos_body"][0])

    def test_arms_parameterised(self):
        exp = {"L": ("lcm", 4, 1.0), "E": ("euler", 4, 1.0), "CTRL": ("lcm", 4, 0.0), "E8": ("euler", 8, 1.0),
               "L-FULL": ("lcm", 4, 1.0)}
        for arm, (s, st, lo) in exp.items():
            g = b(arm)
            self.assertEqual(node(g, "sampler")["inputs"]["sampler_name"], s)
            self.assertEqual(node(g, "scheduler")["inputs"]["steps"], st)
            self.assertEqual(node(g, "lora")["inputs"]["strength_model"], lo)
            self.assertEqual(node(g, "guider")["inputs"]["cfg"], 1.0)
            self.assertEqual(node(g, "noise")["inputs"]["noise_seed"], SEED)

    def test_only_core_classes_and_constant_prompt(self):
        g = b()
        self.assertEqual({n["class_type"] for n in g.values()}, set(W.CORE_CLASSES))
        self.assertEqual(node(g, "positive")["inputs"]["text"], W.PROMPT)
        self.assertEqual(node(g, "positive")["inputs"]["text"], node(b("E"), "positive")["inputs"]["text"])

    def test_pins_vae_unet(self):
        g = b()
        self.assertEqual(node(g, "vae")["inputs"]["vae_name"], "flux2-vae.safetensors")
        self.assertEqual(node(g, "unet")["inputs"]["unet_name"], "FLUX-KLEIN-9B-FP8-NSFW.safetensors")

    def test_lora_option_pick(self):
        name = W.PINS["lora"]["name"]
        self.assertEqual(W.pick_lora_option(["x.safetensors", "sub\\" + name]), "sub\\" + name)
        for opts in ([], ["TripleView.safetensors"], [name, "a/" + name]):
            with self.assertRaises(SystemExit):
                W.pick_lora_option(opts)

    def test_lora_file_pin(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, W.PINS["lora"]["name"])
        _wr(p, "wb", b"x" * 10)
        with self.assertRaises(SystemExit):  # size mismatch
            W.check_lora_file(p)
        q = os.path.join(d, "other.safetensors")
        _wr(q, "wb", b"x")
        with self.assertRaises(SystemExit):
            W.check_lora_file(q)


class Fill(unittest.TestCase):
    def test_unknown_missing_out_of_range(self):
        with self.assertRaises(tpl_fill.TplError):
            b(arm="ZZ")
        with self.assertRaises(tpl_fill.TplError):
            W.build("L", "a.png", "b.png", -1, W.PINS["lora"]["name"], "p")
        g = _jl(os.path.join(W.TEMPLATES, W.NAME, W.VERSION, "workflow_api.json"))
        with self.assertRaises(tpl_fill.TplError):
            tpl_fill.fill_graph(g, W.SCHEMA, {"SEED": 1})
        p = dict(W.ARMS["L"], BODY_IMAGE="a.png", HEAD_IMAGE="b.png", SEED=1, LORA_NAME=W.PINS["lora"]["name"],
                 PREFIX="p", EXTRA=1)
        with self.assertRaises(tpl_fill.TplError):
            tpl_fill.fill_graph(g, W.SCHEMA, p)
        with self.assertRaises(tpl_fill.TplError):
            b(lora_name="TripleView.safetensors")
        with self.assertRaises(tpl_fill.TplError):
            b(body_image="../../etc/x;rm")  # pattern rejects ; and spaces
        with self.assertRaises(tpl_fill.TplError):
            b(prefix="${PREFIX}")

    def test_blocked_word_via_param_stops(self):
        with self.assertRaises(G.GuardStop):
            b(prefix="flux_edit/teen_set")

    def test_no_leftover_placeholder(self):
        self.assertNotIn("${", json.dumps(b()))

    def test_changed_frozen_file_fails_index(self):
        tmp = tempfile.mkdtemp()
        root = os.path.join(tmp, "templates")
        shutil.copytree(W.TEMPLATES, root)
        f = os.path.join(root, W.NAME, W.VERSION, "workflow_api.json")
        _wr(f, "a", " ")
        with self.assertRaises(tpl_fill.TplError):
            W.build("L", "a.png", "b.png", 1, W.PINS["lora"]["name"], "p", templates_root=root)
        self.assertTrue(any(p.startswith("INDEX") for p in tpl_check.check(root, W.NAME, W.VERSION)))


class Check(unittest.TestCase):
    def test_clean_with_core_fallback_but_baseline_missing_blocks(self):
        ps = tpl_check.check(W.TEMPLATES, W.NAME, W.VERSION, core_fallback=W.CORE_CLASSES)
        self.assertEqual(tpl_check.blocking(ps), [])
        ps = tpl_check.check(W.TEMPLATES, W.NAME, W.VERSION)
        self.assertIn("BASELINE_MISSING pins/object_info baseline not captured", ps)

    def _mutated(self, fn):
        tmp = tempfile.mkdtemp()
        root = os.path.join(tmp, "templates")
        shutil.copytree(W.TEMPLATES, root)
        p = os.path.join(root, W.NAME, W.VERSION, "workflow_api.json")
        g = _jl(p)
        fn(g)
        _wr(p, "w", json.dumps(g))
        return tpl_check.check(root, W.NAME, W.VERSION, core_fallback=W.CORE_CLASSES)

    def test_forbidden_pack_uuid_vae(self):
        ps = self._mutated(lambda g: g.update({"99": {"class_type": "ApplyPulidFlux2", "inputs": {}}}))
        self.assertTrue(any(p.startswith("FORBIDDEN_PACK") for p in ps))
        ps = self._mutated(lambda g: g.update({"98": {"class_type": "1b2c3d4e-0000-1111-2222-333344445555",
                                                     "inputs": {}}}))
        self.assertTrue(any(p.startswith("SUBGRAPH_UUID") for p in ps))
        ps = self._mutated(lambda g: g["4"]["inputs"].update(vae_name="flux2-vae-128ch.safetensors"))
        self.assertTrue(any(p.startswith("VAE_NOT_PINNED") for p in ps))
        ps = self._mutated(lambda g: g["7"]["inputs"].update(image="${NOT_DECLARED}"))
        self.assertTrue(any(p.startswith("UNDECLARED") for p in ps))

    def test_model_sha_mismatch(self):
        d = tempfile.mkdtemp()
        for m in W.PINS.values():
            _wr(os.path.join(d, m["name"]), "wb", b"not the model")
        ps = tpl_check.check(W.TEMPLATES, W.NAME, W.VERSION, core_fallback=W.CORE_CLASSES, models_dir=d)
        self.assertIn(f"MODEL_SHA_MISMATCH {W.PINS['lora']['name']}", ps)


if __name__ == "__main__":
    unittest.main()
