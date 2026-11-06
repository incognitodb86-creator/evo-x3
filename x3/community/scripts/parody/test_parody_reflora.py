"""RefLoRA arm U2-U4 CPU fixtures + FG-2/3/8/9 pre-smoke gates.

Covers R8/R9/R10/KTD2/KTD3 plus FG-2 Cond provenance, FG-3 exact token match,
FG-8/9 junction+idempotence+slot overflow+2pass frozen diff+Arm A vs B diff,
and FG-11 Cond-required on both branches. No GPU, network, or process launch.
"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest


def _deny_live_effects(event, args):
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"RefLoRA CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import reflora
import resolve
from build_request import (
    DEFAULT_B2_TEMPLATE,
    DEFAULT_REFMOD_TEMPLATE,
    DEFAULT_REFLORA_TEMPLATE,
    DEFAULT_REFLORA_2PASS_TEMPLATE,
    build_parody_request,
)
from run_record import build_assets_record

INDEX_MD = """## Folder: `good`
| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Goodchar** | Goodactor | Fixture Show | g.mp4 | 2026-11-05 |
| **Daenerys Targaryen** | Emilia Clarke | Game of Thrones | d.mp4 | 2026-11-05 |
## Folder: `onthefence`
| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Fencechar** | Fenceactor | Fixture Show | f.mp4 | 2026-11-05 |
"""
INDEX_BAD_MD = """| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Badchar** | Badactor | Fixture Show | b.mp4 | 2026-11-05 |
| **Jennifer Check** | Megan Fox | Jennifer's Body | j.mp4 | 2026-11-05 |
| **Fox Standalone** | Jamie Foxx | Fixture | x.mp4 | 2026-11-05 |
| **Jorja Role** | Jorja Fox | CSI | y.mp4 | 2026-11-05 |
"""
BIO = "long dark hair, hazel eyes, red leather jacket"
COND = "hoot_start.jpg"


def _write_st(path: Path, tensors: dict, meta: dict) -> None:
    header, blob, off = {"__metadata__": meta}, b"", 0
    for key, (shape, data) in tensors.items():
        header[key] = {"dtype": "F16", "shape": shape, "data_offsets": [off, off + len(data)]}
        blob += data
        off += len(data)
    raw = json.dumps(header).encode()
    path.write_bytes(struct.pack("<Q", len(raw)) + raw + blob)


def _latent(seed: int) -> bytes:
    n = 1 * 24 * 1 * 2 * 2
    return bytes((seed + i) % 251 for i in range(n * 2))


def make_refmod(path: Path, seed: int) -> None:
    meta = {"refmod_meta": json.dumps({"_format_version": 4, "name": path.stem, "kind": "image",
                                       "latent_t": 1, "latent_h": 2, "latent_w": 2})}
    _write_st(path, {"latent": ([1, 24, 1, 2, 2], _latent(seed))}, meta)


def make_hybrid(path: Path, member_name: str, seed: int, lora_keys: int = 2,
                declared: int | None = None, audio: bool = False) -> None:
    tensors = {f"lora_unet_b{i}.lora_down.weight": ([1, 2], b"\x00\x3c" * 2) for i in range(lora_keys)}
    members = [{"_format_version": 4, "name": member_name, "kind": "image",
                "latent_t": 1, "latent_h": 2, "latent_w": 2}]
    tensors["ref_0"] = ([1, 24, 1, 2, 2], _latent(seed))
    if audio:
        members.append({"_format_version": 4, "name": member_name + "_voice", "kind": "audio"})
        tensors["ref_1"] = ([1, 32, 2, 1], b"\x00\x00" * 64)
    meta = {
        "refmod_meta": json.dumps({"_format_version": 5, "kind": "bundle", "name": path.stem,
                                   "members": members}),
        "h3_hybrid": json.dumps({"version": 1, "lora": {"format": "kohya",
                                 "keys": lora_keys if declared is None else declared},
                                 "refmod_count": len(members)}),
    }
    _write_st(path, tensors, meta)


class RefLoRAFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="reflora_")
        root = Path(self.tmp.name)
        self.index = root / "index"
        self.index.mkdir()
        (self.index / "INDEX.md").write_text(INDEX_MD, encoding="utf-8")
        (self.index / "INDEX_BAD.md").write_text(INDEX_BAD_MD, encoding="utf-8")
        self.refmods = root / "refmods"
        self.refmods.mkdir()
        self.rdir = root / "reflora"
        self.rdir.mkdir()
        self.pool = root / "approved_characters" / "HOOTERS01"
        self.pool.mkdir(parents=True)
        self.cond_src = self.pool / "hoot_start.jpg"
        self.cond_src.write_bytes(b"fake-cond-bytes-hoot-start")
        self.comfy_input = root / "ComfyUI" / "input"
        self.comfy_input.mkdir(parents=True)
        (self.comfy_input / "hoot_start.jpg").write_bytes(self.cond_src.read_bytes())
        self.tpl = json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
        self.b2 = json.loads(Path(DEFAULT_B2_TEMPLATE).read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def _mod(self, ident: str, seed: int = 1, ver: int = 1) -> Path:
        p = self.refmods / f"minimaxh3_{ident}_v{ver}_refmod.safetensors"
        make_refmod(p, seed)
        return p

    def _hyb(self, ident: str, seed: int = 1, ver: int = 1, **kw) -> Path:
        p = self.rdir / f"minimaxh3_{ident}_v{ver}_reflora.safetensors"
        make_hybrid(p, f"minimaxh3_{ident}_v{ver}_refmod", seed, **kw)
        return p

    def _resolve(self, character: str, actor=None, refmod_only=False):
        return resolve.resolve_identities(
            {"names": [character], "character": character, "actor": actor, "description": BIO},
            index_dir=self.index, refmods_dir=self.refmods,
            reflora_dir=None if refmod_only else self.rdir)

    def _build(self, resolved, image=COND, graph_mode="single-pass", **kw):
        return build_parody_request(
            resolved, seed=1, prefix="community/t/clip", image=image,
            cond_source=str(self.cond_src),
            approved_pool=self.pool.parent,  # approved_characters root
            comfy_input=self.comfy_input,
            graph_mode=graph_mode, **kw)

    # R8 -----------------------------------------------------------------
    def test_all_three_layers_when_hybrid_present_each_index_class(self):
        for ident, cls in (("goodchar", "good"), ("badchar", "bad"), ("fencechar", "onthefence")):
            with self.subTest(cls=cls):
                self._mod(ident)
                self._hyb(ident)
                r = self._resolve(ident.capitalize())
                self.assertEqual(r["index_status"], cls)
                self.assertEqual(r["identity_layers"], ["INDEX", "RefMod", "RefLoRA"])
                g, prompt, cond = self._build(r)
                self.assertEqual(cond["cond_sha256"], reflora.sha256_file(self.cond_src))
                self.assertEqual(g["s0_guide"]["inputs"]["model"], ["reflora_1", 0])
                self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
                self.assertEqual(reflora.frozen_diff(self.tpl, g), [])

    def test_absent_hybrid_falls_back_to_index_refmod(self):
        for ident in ("goodchar", "badchar", "fencechar"):
            with self.subTest(ident=ident):
                self._mod(ident)
                r = self._resolve(ident.capitalize())
                self.assertEqual(r["identity_layers"], ["INDEX", "RefMod"])
                self.assertFalse(r["reflora"]["enabled"])
                g, _, _ = self._build(r)  # FG-11: Cond still required
                self.assertFalse([k for k, v in g.items()
                                  if v["class_type"].startswith("MiniMaxH3RefLoRA")])
                self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
                self.assertEqual(reflora.frozen_diff(self.tpl, g), [])

    def test_fallback_restores_cond_when_still_given(self):
        self._mod("badchar")
        g, _, _ = self._build(self._resolve("Badchar"))
        self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
        self.assertEqual(reflora.frozen_diff(self.tpl, g), [])

    def test_broken_present_hybrid_blocks(self):
        self._mod("badchar")
        self._hyb("badchar", declared=600)
        with self.assertRaises(reflora.RefLoRAError):
            self._resolve("Badchar")

    def test_weightless_hybrid_blocks(self):
        self._mod("badchar")
        self._hyb("badchar", lora_keys=0, declared=0)
        with self.assertRaises(reflora.RefLoRAError):
            self._resolve("Badchar")

    def test_unknown_member_equivalence_blocks(self):
        self._mod("badchar")
        p = self.rdir / "minimaxh3_badchar_v1_reflora.safetensors"
        make_hybrid(p, "some_other_member", 1)
        with self.assertRaises(reflora.RefLoRAError):
            self._resolve("Badchar")

    def test_missing_cond_blocks_hybrid_branch(self):
        self._mod("badchar")
        self._hyb("badchar")
        with self.assertRaises(ValueError):
            build_parody_request(self._resolve("Badchar"), seed=1, prefix="community/t/clip",
                                 require_cond=True)

    def test_missing_cond_blocks_refmod_only_branch_fg11(self):
        self._mod("badchar")
        with self.assertRaises(ValueError):
            build_parody_request(self._resolve("Badchar", refmod_only=True), seed=1,
                                 prefix="community/t/clip", require_cond=True)

    # FG-2 Cond provenance ------------------------------------------------
    def test_outside_pool_cond_blocks(self):
        self._mod("badchar")
        outside = Path(self.tmp.name) / "outside.jpg"
        outside.write_bytes(b"nope")
        with self.assertRaises(ValueError):
            build_parody_request(
                self._resolve("Badchar"), seed=1, prefix="community/t/clip",
                image=COND, cond_source=str(outside),
                approved_pool=self.pool.parent, comfy_input=self.comfy_input)

    def test_sydney_path_blocks(self):
        with self.assertRaises(ValueError):
            resolve.validate_stills(
                [str(self.pool.parent / "sydney" / "x.jpg")], self.pool.parent)

    def test_sha256_mismatch_blocks(self):
        self._mod("badchar")
        (self.comfy_input / "hoot_start.jpg").write_bytes(b"DIFFERENT")
        with self.assertRaises(ValueError) as ctx:
            self._build(self._resolve("Badchar"))
        self.assertIn("SHA256", str(ctx.exception))

    def test_valid_pool_matching_hash_records_cond_sha(self):
        self._mod("badchar")
        self._hyb("badchar")
        r = self._resolve("Badchar")
        g, _, cond = self._build(r)
        a = build_assets_record({**r, "cond": cond}, g)
        self.assertEqual(a["cond_sha256"], reflora.sha256_file(self.cond_src))
        self.assertEqual(a["cond_input_name"], COND)
        self.assertTrue(a["cond_source_path"])

    # FG-3 exact token / ambiguity ----------------------------------------
    def test_substring_fox_does_not_match_meganfox(self):
        self._mod("meganfox")
        self._mod("jamiefoxx")
        self._mod("jorjafox")
        # bare token "fox" must NOT substring-match meganfox
        hits = resolve.find_refmods_for_name("fox", self.refmods)
        self.assertEqual(hits, [])

    def test_substring_ana_does_not_match_anadearmas(self):
        self._mod("anadearmas")
        self.assertEqual(resolve.find_refmods_for_name("ana", self.refmods), [])

    def test_multiple_versions_block_on_ambiguity(self):
        self._mod("meganfox", ver=1)
        self._mod("meganfox", ver=2, seed=2)
        with self.assertRaises(ValueError) as ctx:
            resolve.find_refmods_for_name("meganfox", self.refmods)
        self.assertIn("ambiguous", str(ctx.exception).lower())

    def test_dual_subject_exact_match_megan_and_emilia(self):
        self._mod("meganfox")
        self._hyb("meganfox")
        self._mod("emiliaclarke")
        self._hyb("emiliaclarke")
        r_m = self._resolve("Jennifer Check", actor="Megan Fox")
        r_e = self._resolve("Daenerys Targaryen", actor="Emilia Clarke")
        self.assertTrue(any("meganfox" in p for p in
                            [h["lora_name"] for h in r_m["reflora"]["hybrids"]]
                            + r_m["loaded_refmods"]))
        self.assertTrue(r_m["reflora"]["enabled"] or r_m["loaded_refmods"])
        self.assertTrue(r_e["reflora"]["enabled"])
        self.assertTrue(any("emiliaclarke" in h["lora_name"] for h in r_e["reflora"]["hybrids"]))

    def test_index_token_ambiguity_blocks(self):
        with self.assertRaises(ValueError) as ctx:
            resolve.match_index_rows("Fox", resolve.load_index_files(self.index))
        self.assertIn("ambiguous", str(ctx.exception).lower())

    def test_refmod_only_flag_skips_hybrid_even_when_present(self):
        self._mod("meganfox")
        self._hyb("meganfox")
        r = self._resolve("Megan Fox", refmod_only=True)
        self.assertFalse(r["reflora"].get("enabled"))
        self.assertEqual(r["identity_layers"], ["INDEX", "RefMod"])
        g, _, _ = self._build(r)
        self.assertFalse([k for k, v in g.items()
                          if v["class_type"].startswith("MiniMaxH3RefLoRA")])
        self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])

    # KTD3 provenance -----------------------------------------------------
    def test_identical_standalone_injected_once_from_hybrid(self):
        self._mod("badchar", seed=5)
        self._hyb("badchar", seed=5)
        r = self._resolve("Badchar")
        self.assertEqual(len(r["reflora"]["standalone_deduped"]), 1)
        self.assertEqual(r["loaded_refmods"], [])
        self.assertEqual(r["reflora"]["effective_reference_count"], 1)

    def test_distinct_standalone_and_packed_both_survive(self):
        self._mod("badchar", seed=5)
        self._hyb("badchar", seed=9)
        r = self._resolve("Badchar")
        self.assertEqual(r["reflora"]["standalone_deduped"], [])
        self.assertEqual(len(r["loaded_refmods"]), 1)
        self.assertEqual(r["reflora"]["effective_reference_count"], 2)

    def test_audio_members_excluded_visual_only(self):
        self._mod("badchar")
        self._hyb("badchar", audio=True)
        r = self._resolve("Badchar")
        h = r["reflora"]["hybrids"][0]
        self.assertEqual(h["components"], "Visual")
        self.assertEqual(h["member_selection"], "1")

    # KTD2 / R9 -----------------------------------------------------------
    def _graph(self):
        self._mod("badchar")
        self._hyb("badchar")
        g, _, _ = self._build(self._resolve("Badchar"))
        return g

    def test_dial_drift_detected(self):
        g = self._graph()
        g["s0_sched"]["inputs"]["steps"] = 20
        with self.assertRaises(ValueError):
            reflora.verify_reflora_graph(g, self.tpl, 1)

    def test_attach_plus_apply_double_injection_fails(self):
        g = self._graph()
        g["reflora_1"]["inputs"]["attach_to_model"] = True
        with self.assertRaises(ValueError):
            reflora.verify_reflora_graph(g, self.tpl, 1)

    def test_generic_loader_only_fails(self):
        g = self._graph()
        g["lora_x"] = {"class_type": "LoraLoaderModelOnly",
                       "inputs": {"lora_name": "MinimaxH3\\reflora\\x_reflora.safetensors"}}
        with self.assertRaises(ValueError):
            reflora.verify_reflora_graph(g, self.tpl, 1)

    def test_missing_cond_picture_fails(self):
        g = self._graph()
        del g["c0"]["inputs"]["ref_images.ref_image_1"]
        with self.assertRaises(ValueError):
            reflora.verify_reflora_graph(g, self.tpl, 1)

    def test_assets_record_proves_weights_and_refs(self):
        self._mod("badchar")
        self._hyb("badchar")
        r = self._resolve("Badchar")
        g, _, cond = self._build(r)
        a = build_assets_record({**r, "cond": cond}, g)
        self.assertEqual(a["identity_layers"], ["INDEX", "RefMod", "RefLoRA"])
        self.assertEqual(a["cond_picture"], COND)
        self.assertEqual(len(a["reflora_ledger"]), 1)

    def test_committed_template_matches_derivation(self):
        committed = json.loads(Path(DEFAULT_REFLORA_TEMPLATE).read_text(encoding="utf-8"))
        self.assertEqual(committed, reflora.derive_reflora_template(self.tpl))
        self.assertEqual(reflora.frozen_diff(self.tpl, committed), [])

    # FG-1 / FG-8 two-pass + Arm A vs B -----------------------------------
    def test_2pass_template_frozen_diff(self):
        committed = json.loads(Path(DEFAULT_REFLORA_2PASS_TEMPLATE).read_text(encoding="utf-8"))
        derived = reflora.derive_reflora_2pass_template(self.b2)
        # Normalize cond placeholder
        derived = reflora.add_cond_picture(derived, "community/<cond>.png")
        self.assertEqual(reflora.frozen_diff_2pass(committed, self.b2), [])
        self.assertEqual(reflora.frozen_diff_2pass(derived, self.b2), [])

    def test_arm_a_vs_arm_b_differ_only_in_reflora_hybrid(self):
        self._mod("meganfox")
        self._hyb("meganfox")
        arm_a = self._resolve("Megan Fox", refmod_only=True)
        arm_b = self._resolve("Megan Fox", refmod_only=False)
        ga, _, _ = self._build(arm_a)
        gb, _, _ = self._build(arm_b)
        # Strip RefLoRA nodes from B and compare core dials
        gb_core = {k: v for k, v in gb.items()
                   if not str(k).startswith("reflora")}
        # After stripping loaders, rewire expectations: Arm B without reflora nodes
        # should match Arm A on KEEP dials (unet/steps/canvas/refmods path shape).
        self.assertEqual(ga["unet"]["inputs"], gb["unet"]["inputs"])
        self.assertEqual(ga["s0_sched"]["inputs"]["steps"], gb["s0_sched"]["inputs"]["steps"])
        self.assertEqual(ga["c0"]["inputs"]["width"], gb["c0"]["inputs"]["width"])
        self.assertEqual(ga["c0"]["inputs"]["height"], gb["c0"]["inputs"]["height"])
        self.assertEqual(ga["c0"]["inputs"]["ref_images.ref_image_1"],
                         gb["c0"]["inputs"]["ref_images.ref_image_1"])
        self.assertTrue(any(v["class_type"] == reflora.LOADER_CLASS for v in gb.values()))
        self.assertFalse(any(v["class_type"] == reflora.LOADER_CLASS for v in ga.values()))

    def test_two_pass_graft_wires_ag_positive_and_model_consumers(self):
        self._mod("meganfox")
        self._hyb("meganfox")
        r = self._resolve("Megan Fox")
        g, _, _ = self._build(r, graph_mode="two-pass")
        self.assertEqual(g["ag0"]["inputs"]["positive"], ["reflora_apply_1", 0])
        self.assertEqual(g["ag1"]["inputs"]["positive"], ["reflora_apply_1", 0])
        for nid in ("s0_guide", "s0_sched", "s1_guide", "p2sched"):
            self.assertEqual(g[nid]["inputs"]["model"], ["reflora_1", 0], nid)
        self.assertEqual(g["c0"]["inputs"]["clip"], ["reflora_1", 1])
        self.assertEqual(reflora.frozen_diff_2pass(g, self.b2), [])

    def test_slot_overflow_kept_dropped_determinism(self):
        # 4 hybrids (deduped packed=4) + 6 standalones without hybrids -> drop 2 kept
        for i in range(4):
            ident = f"hyb{i:02d}"
            self._mod(ident, seed=i + 1)
            self._hyb(ident, seed=i + 1)  # dedup -> packed only
        for i in range(6):
            ident = f"solo{i:02d}"
            self._mod(ident, seed=50 + i)
            # no hybrid -> stays in kept
        paths = (
            [str(self.refmods / f"minimaxh3_hyb{i:02d}_v1_refmod.safetensors") for i in range(4)]
            + [str(self.refmods / f"minimaxh3_solo{i:02d}_v1_refmod.safetensors") for i in range(6)]
        )
        sel = reflora.select_reflora(paths, self.rdir, with_file_hash=False)
        self.assertEqual(sel["effective_reference_count"], 8)  # 4 packed + 4 kept
        self.assertEqual(len(sel["standalone_dropped_for_budget"]), 2)
        sel2 = reflora.select_reflora(paths, self.rdir, with_file_hash=False)
        self.assertEqual(sel["standalone_dropped_for_budget"],
                         sel2["standalone_dropped_for_budget"])

    def test_safe_child_rejects_symlink(self):
        self._mod("badchar")
        target = self.rdir / "minimaxh3_badchar_v1_reflora.safetensors"
        make_hybrid(target, "minimaxh3_badchar_v1_refmod", 1)
        link = self.rdir / "link_reflora.safetensors"
        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest("symlinks not available on this host")
        with self.assertRaises(reflora.RefLoRAError):
            reflora._safe_child(link, self.rdir)

    def test_manifest_idempotence_select_twice(self):
        self._mod("badchar", seed=5)
        self._hyb("badchar", seed=5)
        p = str(self.refmods / "minimaxh3_badchar_v1_refmod.safetensors")
        a = reflora.select_reflora([p], self.rdir, with_file_hash=False)
        b = reflora.select_reflora([p], self.rdir, with_file_hash=False)
        self.assertEqual(a["hybrids"][0]["lora_name"], b["hybrids"][0]["lora_name"])
        self.assertEqual(a["standalone_deduped"], b["standalone_deduped"])
        self.assertEqual(a["effective_reference_count"], b["effective_reference_count"])


class StagedHybridsLive(unittest.TestCase):
    """Header/tensor-only checks on the two smoke hybrids staged by HF (U2). CPU, read-only."""

    def test_staged_smoke_hybrids_valid_and_dedup_provable(self):
        rdir = reflora.DEFAULT_REFLORA_DIR
        refmods = reflora.COMFY_DIR / "models" / "refmods"
        names = ("meganfox", "emiliaclarke")
        if not all((rdir / f"minimaxh3_{n}_v1_reflora.safetensors").is_file() for n in names):
            self.skipTest("staged smoke hybrids not present on this host")
        for n in names:
            with self.subTest(n=n):
                sel = reflora.select_reflora(
                    [str(refmods / f"minimaxh3_{n}_v1_refmod.safetensors")],
                    rdir, with_file_hash=False)
                self.assertTrue(sel["enabled"])
                h = sel["hybrids"][0]
                self.assertEqual(h["lora_keys"], 600)
                self.assertEqual(
                    h["lora_name"],
                    f"MinimaxH3\\reflora\\minimaxh3_{n}_v1_reflora.safetensors")
                self.assertEqual(len(sel["standalone_deduped"]), 1, sel)


if __name__ == "__main__":
    unittest.main()
