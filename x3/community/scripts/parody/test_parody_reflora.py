"""RefLoRA arm U2-U4 CPU fixtures + FG-2/3/8/9 pre-smoke gates.

Covers R8/R9/R10/KTD2/KTD3 plus FG-2 Cond provenance, FG-3 exact token match,
FG-8/9 junction+idempotence+slot overflow+2pass frozen diff+Arm A vs B diff,
FG-11 Cond-required on both branches, the B2-4 per-pass parody dials, and the B2-5
no-start-photo named-celeb graph (no LoadImage, no AddGuide, conditioning-only identity).
No GPU, network, or process launch.
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
    BETA7_UNET_ALLOWLIST,
    DEFAULT_B2_TEMPLATE,
    DEFAULT_PARODY_2PASS_TEMPLATE,
    DEFAULT_REFMOD_TEMPLATE,
    DEFAULT_REFLORA_TEMPLATE,
    DEFAULT_REFLORA_2PASS_TEMPLATE,
    DEFAULT_UNET,
    build_parody_request,
    validate_unet_name,
    verify_keep_dials,
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
# B2-6: the adult age lives in the author-supplied bio (the paste has no canon-age clause), so
# every fixture bio states an 18+ age; the builder refuses a bio that does not.
BIO = "a woman of 28 years, long dark hair, hazel eyes, red leather jacket"
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


    def test_builder_fails_closed_on_a_missing_class(self):
        """B2-3: a class the saved object_info capture does not list blocks the build on CPU."""
        self._mod("badchar")
        bad = json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
        bad["save"]["class_type"] = "NotARealNodeXYZ"
        bad_tpl = self._bad_template(bad)
        with self.assertRaises(ValueError) as ctx:
            self._build(self._resolve("Badchar"), template_path=bad_tpl)
        msg = str(ctx.exception)
        self.assertIn("save", msg)
        self.assertIn("NotARealNodeXYZ", msg)
        self.assertIn("offline class check", msg)

    def _bad_template(self, graph) -> Path:
        p = self.comfy_input.parent / "tpl_bad.api.json"
        p.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        return p

    def test_two_pass_build_blocked_by_a_capture_without_the_upscaler(self):
        """B2-3 (c) at the builder: the U5 two-pass arm, where the pack was not loaded.

        The graph is clean (it passes the KEEP guard); the capture is the thing that lacks the
        class, exactly as at U5 submit time. The build must fail closed naming lsu3 and the pack.
        """
        if not (reflora.CUSTOM_NODES_DIR / reflora.OFFLINE_PACK_UPSCALER).is_dir():
            self.skipTest("the upscaler pack is not present on this host")
        newest = reflora._saved_captures()
        if not newest or "MinimaxH3LatentUpscaler3D" not in json.loads(
                newest[0][1].read_text(encoding="utf-8")):
            self.skipTest("no saved capture lists the upscaler class")
        tpl = json.loads(Path(DEFAULT_B2_TEMPLATE).read_text(encoding="utf-8"))
        classes = sorted({n["class_type"] for n in tpl.values()})
        classes.remove("MinimaxH3LatentUpscaler3D")
        old = self.comfy_input.parent / "object_info_20261101.json"
        old.write_text(json.dumps({c: {"input": {}} for c in classes}), encoding="utf-8")
        self._mod("badchar")
        with self.assertRaises(ValueError) as ctx:
            self._build(self._resolve("Badchar", refmod_only=True), graph_mode="two-pass",
                        objinfo_dump=old)
        msg = str(ctx.exception)
        self.assertIn("lsu3: unknown class MinimaxH3LatentUpscaler3D", msg)
        self.assertIn(reflora.OFFLINE_PACK_UPSCALER, msg)
        self.assertIn("pack disabled", msg)

    def test_builder_passes_against_the_fresh_capture(self):
        """Control: the real templates are all renderable against the freshest capture."""
        if not reflora.DEFAULT_OBJINFO_DUMP.is_file():
            self.skipTest(f"no {reflora.DEFAULT_OBJINFO_DUMP} capture on this host")
        self._mod("badchar")
        g, _, _ = self._build(self._resolve("Badchar"))
        self.assertEqual(reflora.offline_class_check(g), [])

    # B2-4 two-pass PARODY graph: per-pass RefLoRA dials, pass 1 voice-protected ------------
    PARODY_HYB = {"lora_name": "MinimaxH3" + chr(92) + "reflora" + chr(92)
                  + "minimaxh3_badchar_v1_reflora.safetensors", "members": "all"}

    def _parody(self, **dials):
        g = reflora.derive_parody_2pass_graph(self.b2, self.PARODY_HYB, **dials)
        reflora.verify_parody_2pass_graph(g, self.b2, **dials)
        return g

    def test_parody_pass1_model_link_is_raw_at_zero(self):
        """pass1_lora_strength 0.0: pass 1 keeps the raw base model chain (voice protection)."""
        g = self._parody()
        self.assertNotIn(reflora.PARODY_P1_LOADER, g)
        for nid in ("s0_guide", "s0_sched"):
            self.assertEqual(g[nid]["inputs"]["model"], ["m_shift", 0], nid)
        self.assertEqual(g[reflora.PARODY_P2_LOADER]["inputs"]["lora_strength"], 1.0)

    def test_parody_pass1_model_link_is_a_loader_at_035(self):
        """A pass-1 dial above 0.0 inserts a pass-1 MiniMaxH3RefLoRALoader on that line only."""
        g = self._parody(pass1_lora_strength=0.35)
        for nid in ("s0_guide", "s0_sched"):
            self.assertEqual(g[nid]["inputs"]["model"], [reflora.PARODY_P1_LOADER, 0], nid)
        self.assertEqual(g[reflora.PARODY_P1_LOADER]["class_type"], reflora.LOADER_CLASS)
        self.assertEqual(g[reflora.PARODY_P1_LOADER]["inputs"]["lora_strength"], 0.35)
        self.assertEqual(g[reflora.PARODY_P2_LOADER]["inputs"]["lora_strength"], 1.0)

    def test_parody_pass2_loader_carries_the_pass2_dial_with_apply_route(self):
        """The pass-2 loader takes the pass-2 strength, attach_to_model False, Visual, clip given."""
        g = self._parody(pass2_lora_strength=0.6)
        for nid in ("s1_guide", "p2sched"):
            self.assertEqual(g[nid]["inputs"]["model"], [reflora.PARODY_P2_LOADER, 0], nid)
        inp = g[reflora.PARODY_P2_LOADER]["inputs"]
        self.assertEqual(inp["lora_strength"], 0.6)
        self.assertIs(inp["attach_to_model"], False)
        self.assertEqual(inp["components"], "Visual")
        self.assertEqual(inp["clip"], ["clip", 0])
        self.assertEqual(g[reflora.PARODY_REF_LOADER]["inputs"]["lora_strength"], 0.0)
        self.assertNotIn("clip", g[reflora.PARODY_REF_LOADER]["inputs"])
        self.assertEqual(g["c0"]["inputs"]["clip"], ["clip", 0])

    def test_parody_one_conditioning_injection_feeds_both_guides(self):
        """Exactly one RefMod Apply + one RefLoRA Apply (no second Apply), feeding ag0 AND ag1."""
        g = self._parody(pass1_lora_strength=0.35)
        by_class: dict = {}
        for nid, node in g.items():
            by_class.setdefault(node["class_type"], []).append(nid)
        self.assertEqual(by_class["MiniMaxH3RefModApply"], ["refapply"])
        self.assertEqual(by_class[reflora.APPLY_CLASS], [reflora.PARODY_REF_APPLY])
        self.assertEqual(g["refapply"]["inputs"]["retention"], 1.0)
        self.assertEqual(g[reflora.PARODY_REF_APPLY]["inputs"]["conditioning"], ["refapply", 0])
        self.assertEqual(g[reflora.PARODY_REF_APPLY]["inputs"]["mods"],
                         [reflora.PARODY_REF_LOADER, 2])
        for nid in ("ag0", "ag1"):
            self.assertEqual(g[nid]["inputs"]["positive"], [reflora.PARODY_REF_APPLY, 0], nid)

    def test_parody_keeps_the_keep_graph_and_audio_from_pass1(self):
        """KEEP dials byte-identical to b2.api.json, audio decoded from pass 1, 384x672/124f."""
        for dials in ({}, {"pass1_lora_strength": 0.35}, {"pass2_lora_strength": 0.6}):
            with self.subTest(**dials):
                g = self._parody(**dials)
                self.assertEqual(reflora.frozen_diff_2pass(g, self.b2), [])
                self.assertEqual(g["dec_a"]["inputs"]["samples"], ["s0_sep", 1])
                self.assertEqual(g["lsu3"]["inputs"], self.b2["lsu3"]["inputs"])
                self.assertEqual((g["c0"]["inputs"]["height"], g["c0"]["inputs"]["width"],
                                  g["c0"]["inputs"]["length"]), (672, 384, 124))
                verify_keep_dials(g, two_pass=True)

    def test_parody_shape_verifier_fails_closed(self):
        """The guard must reject a pass-1 loader at the 0.0 dial and a second Apply."""
        g = self._parody()
        g["s0_guide"]["inputs"]["model"] = [reflora.PARODY_P2_LOADER, 0]
        with self.assertRaises(ValueError) as ctx:
            reflora.verify_parody_2pass_graph(g, self.b2)
        self.assertIn("s0_guide", str(ctx.exception))
        g2 = self._parody()
        g2["reflora_apply_2"] = dict(g2[reflora.PARODY_REF_APPLY])
        with self.assertRaises(ValueError) as ctx:
            reflora.verify_parody_2pass_graph(g2, self.b2)
        self.assertIn("reflora_apply_2", str(ctx.exception))

    def test_committed_parody_template_matches_derivation(self):
        """No drift: templates/b2_parody_2pass.api.json == the generated default-dial graph."""
        committed = json.loads(Path(DEFAULT_PARODY_2PASS_TEMPLATE).read_text(encoding="utf-8"))
        self.assertEqual(committed, reflora.derive_parody_2pass_template(self.b2))
        self.assertEqual(reflora.frozen_diff_2pass(committed, self.b2), [])
        self.assertEqual(reflora.offline_class_check(committed), [])

    def test_builder_two_pass_parody_uses_the_template_and_records_the_dials(self):
        """--graph-mode two-pass-parody: template graph + the run's LoRA name + dials in records."""
        self._mod("badchar")
        self._hyb("badchar")
        r = self._resolve("Badchar")
        g, prompt, cond = self._build(r, graph_mode="two-pass-parody", frames=124)
        self.assertEqual(g["s0_guide"]["inputs"]["model"], ["m_shift", 0])
        self.assertEqual(g["s1_guide"]["inputs"]["model"], [reflora.PARODY_P2_LOADER, 0])
        want = r["reflora"]["hybrids"][0]["lora_name"]
        self.assertEqual({n["inputs"]["reflora_name"] for n in g.values()
                          if n["class_type"] == reflora.LOADER_CLASS}, {want})
        self.assertEqual({n["inputs"]["members"] for n in g.values()
                          if n["class_type"] == reflora.LOADER_CLASS},
                         {r["reflora"]["hybrids"][0]["member_selection"]})
        # KTD3: a packed hybrid dedups its standalone RefMod, so no slot is loaded (the identity
        # rides the RefLoRA loader's members); the slots stay "(none)" exactly as in the old arm B.
        self.assertEqual([g["refmods"]["inputs"][f"mod_{i}"] for i in range(1, 9)],
                         ["(none)"] * 8)
        self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
        # the template path is not a raw file copy: make_b2_build must set THIS run's per-run fields
        # (prompt/seed/prefix/frames), the five fields b2.README documents; the file's placeholders
        # (seed 51083002, the terrace example prompt) must not survive into a request.
        self.assertEqual(g["noise"]["inputs"]["noise_seed"], 1)
        self.assertEqual(g["save"]["inputs"]["filename_prefix"], "community/t/clip")
        self.assertEqual(g["c0"]["inputs"]["prompt"], prompt)
        self.assertEqual(g["c0"]["inputs"]["length"], 124)
        dials = r["reflora"]["parody_dials"]
        self.assertEqual((dials["pass1_lora_strength"], dials["pass2_lora_strength"]), (0.0, 1.0))
        a = build_assets_record({**r, "cond": cond}, g)
        self.assertEqual(a["reflora"]["parody_dials"], dials)
        self.assertEqual(a["dials"]["unet"], DEFAULT_UNET)
        self.assertEqual(sorted(tuple(n["model_line"]) for n in a["reflora_ledger"]),
                         [(), ("p2sched", "s1_guide")])

    def test_builder_two_pass_dials_imply_the_parody_graph(self):
        """--graph-mode two-pass plus per-pass dials is the brief's command shape (B2-7)."""
        self._mod("badchar")
        self._hyb("badchar")
        r = self._resolve("Badchar")
        g, _, _ = self._build(r, graph_mode="two-pass", pass1_lora_strength=0.35,
                              pass2_lora_strength=1.0)
        self.assertEqual(g["s0_guide"]["inputs"]["model"], [reflora.PARODY_P1_LOADER, 0])
        self.assertEqual(g[reflora.PARODY_P1_LOADER]["inputs"]["lora_strength"], 0.35)
        self.assertEqual(g["reflora_apply_1"]["inputs"]["mods"], [reflora.PARODY_REF_LOADER, 2])
        self.assertEqual(r["reflora"]["parody_dials"]["pass1_lora_strength"], 0.35)
        # the record names which model line each loader drives (the per-pass dials in records)
        led = {n["node"]: (n["lora_strength"], tuple(n["model_line"]))
               for n in reflora.reflora_ledger(g)}
        self.assertEqual(led[reflora.PARODY_P1_LOADER], (0.35, ("s0_guide", "s0_sched")))
        self.assertEqual(led[reflora.PARODY_P2_LOADER], (1.0, ("p2sched", "s1_guide")))
        self.assertEqual(led[reflora.PARODY_REF_LOADER], (0.0, ()))

    def test_builder_two_pass_refmod_only_still_uses_the_keep_graph(self):
        """Existing default: plain --graph-mode two-pass without dials keeps the old shape."""
        self._mod("badchar")
        r = self._resolve("Badchar", refmod_only=True)
        g, _, _ = self._build(r, graph_mode="two-pass")
        self.assertEqual(g["s0_guide"]["inputs"]["model"], ["m_shift", 0])
        self.assertFalse([k for k, v in g.items()
                          if v["class_type"].startswith("MiniMaxH3RefLoRA")])
        self.assertEqual(reflora.frozen_diff_2pass(g, self.b2), [])

    # B2-4 --unet: the A/B model swap, two beta7 checkpoints only --------------------------
    LEARNED_HQ = "10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors"
    NOT_A_UNET = "NotARealUnet.safetensors"

    def test_unet_allowlist_accepts_exactly_the_two_beta7_checkpoints(self):
        self.assertEqual(validate_unet_name(BETA7_UNET_ALLOWLIST[0]), DEFAULT_UNET)
        self.assertEqual(validate_unet_name(self.LEARNED_HQ), self.LEARNED_HQ)
        for bad in (self.NOT_A_UNET, "", "sub" + chr(92) + self.LEARNED_HQ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate_unet_name(bad)

    def test_builder_default_unet_is_the_int8hq_checkpoint(self):
        self._mod("badchar")
        g, _, _ = self._build(self._resolve("Badchar"))
        self.assertEqual(g["unet"]["inputs"]["unet_name"],
                         "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors")
        self.assertEqual(g["unet"]["inputs"], self.tpl["unet"]["inputs"])
        verify_keep_dials(g)

    def test_builder_unet_override_passes_the_keep_guard(self):
        self._mod("badchar")
        r = self._resolve("Badchar")
        g, _, _ = self._build(r, unet_name=self.LEARNED_HQ)
        self.assertEqual(g["unet"]["inputs"]["unet_name"], self.LEARNED_HQ)
        verify_keep_dials(g)
        self.assertEqual(r["reflora"]["unet_name"], self.LEARNED_HQ)
        self.assertEqual(r["reflora"]["unet_allowlist"], list(BETA7_UNET_ALLOWLIST))

    def test_builder_rejects_a_third_unet_before_writing(self):
        self._mod("badchar")
        with self.assertRaises(ValueError) as ctx:
            self._build(self._resolve("Badchar"), unet_name=self.NOT_A_UNET)
        self.assertIn("UNET dial drifted", str(ctx.exception))
        self.assertIn(self.NOT_A_UNET, str(ctx.exception))

    def test_keep_guard_rejects_a_unet_outside_the_allowlist(self):
        g = json.loads(Path(DEFAULT_B2_TEMPLATE).read_text(encoding="utf-8"))
        g["unet"]["inputs"]["unet_name"] = self.NOT_A_UNET
        with self.assertRaises(ValueError) as ctx:
            verify_keep_dials(g, two_pass=True)
        self.assertIn("UNET dial drifted", str(ctx.exception))


class NoPhotoParodyGraph(unittest.TestCase):
    """B2-5: a named-celeb clip with NO start photo (CPU only, no HTTP, no GPU, no lock).

    The graph shape is the pack's own no-first-frame example: no LoadImage, no MiniMaxH3AddGuide,
    the ONE RefMod/RefLoRA conditioning injection feeding both guiders. A supplied photo must still
    hit the approved_characters + SHA256 gate (FG-2/FG-11).
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="nophoto_")
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

    def _no_photo(self, character="Badchar", refmod_only=False, image=None, cond_source=None, **kw):
        """The item's command shape: --graph-mode two-pass-parody with NO Cond flags at all."""
        self._mod(character.lower())
        if not refmod_only:
            self._hyb(character.lower())
        return build_parody_request(
            self._resolve(character, refmod_only=refmod_only),
            seed=1, prefix="community/t/clip", image=image, cond_source=cond_source,
            approved_pool=self.pool.parent, comfy_input=self.comfy_input,
            graph_mode="two-pass-parody", **kw)

    @staticmethod
    def _dangling(graph):
        """Every link that points at a node id the graph does not carry (must always be [])."""
        bad = []
        for nid, node in graph.items():
            for key, val in (node.get("inputs") or {}).items():
                if isinstance(val, list) and len(val) == 2 and isinstance(val[0], str) \
                        and val[0] not in graph:
                    bad.append(f"{nid}.{key} -> {val[0]}")
        return sorted(bad)

    def test_no_photo_parody_drops_the_picture_and_both_addguides(self):
        """No Cond flags: no LoadImage, no MiniMaxH3AddGuide, no Picture input, links resolve."""
        for dials in ({}, {"pass1_lora_strength": 0.35, "pass2_lora_strength": 1.0}):
            with self.subTest(**dials):
                g, prompt, cond = self._no_photo(**dials)
                by_class: dict = {}
                for nid, node in g.items():
                    by_class.setdefault(node["class_type"], []).append(nid)
                self.assertNotIn("LoadImage", by_class)
                self.assertNotIn("MiniMaxH3AddGuide", by_class)
                self.assertNotIn("ref_images.ref_image_1", g["c0"]["inputs"])
                for nid in ("s0_guide", "s1_guide"):
                    self.assertEqual(g[nid]["inputs"]["conditioning"],
                                     [reflora.PARODY_REF_APPLY, 0], nid)
                self.assertEqual(self._dangling(g), [])
                # the identity feed is the one RefMod -> RefLoRA conditioning injection, both passes
                self.assertEqual(g["refapply"]["inputs"]["conditioning"], ["c0", 0])
                self.assertEqual(g[reflora.PARODY_REF_APPLY]["inputs"]["conditioning"],
                                 ["refapply", 0])
                self.assertEqual(g[reflora.PARODY_REF_APPLY]["inputs"]["mods"],
                                 [reflora.PARODY_REF_LOADER, 2])
                reflora.verify_parody_2pass_graph(
                    g, self.b2, cond_wired=False,
                    pass1_lora_strength=dials.get("pass1_lora_strength", reflora.PASS1_LORA_STRENGTH),
                    pass2_lora_strength=dials.get("pass2_lora_strength", reflora.PASS2_LORA_STRENGTH))
                self.assertEqual(reflora.frozen_diff_no_photo(g, self.b2), [])
                verify_keep_dials(g, two_pass=True, cond_wired=False)
                self.assertNotIn("<Picture 1>", prompt)
                self.assertEqual(prompt.count("<Video 1>"), 1)
                self.assertIsNone(cond["cond_input_name"])
                self.assertIsNone(cond["cond_sha256"])

    def test_no_photo_parody_accepts_the_beta7_model_swap(self):
        """The A/B beta7 UNet swap is the allowlist guard's business, not the frozen template's."""
        other = [u for u in BETA7_UNET_ALLOWLIST
                 if u != self.b2["unet"]["inputs"].get("unet_name")][0]
        g, _, _ = self._no_photo(unet_name=other)
        self.assertEqual(g["unet"]["inputs"]["unet_name"], other)
        verify_keep_dials(g, two_pass=True, cond_wired=False)
        self.assertEqual(
            [p for p in reflora.frozen_diff_no_photo(g, self.b2)
             if not p.startswith("dial drift: unet.unet_name:")], [])

    def test_no_photo_identity_is_the_name_and_description_in_subject_definitions(self):
        """Identity rides the prompt's INDEX name + bio description, never a picture label."""
        g, prompt, _ = self._no_photo()
        self.assertIn("subject_definitions:\n<Subject 1> is the woman in <Video 1>.", prompt)
        self.assertIn("<Subject 1> Badchar,", prompt)
        for cue in BIO.split(", "):
            self.assertIn(cue, prompt)
        self.assertNotIn("<Picture", prompt)
        self.assertEqual(self._dangling(g), [])

    def test_no_photo_verifier_fails_closed(self):
        """A LoadImage, a c0 Picture input, or the with-photo shape must not pass the no-photo guard."""
        g, _, _ = self._no_photo()
        g["img"] = {"_meta": {"title": "x"}, "class_type": "LoadImage",
                    "inputs": {"image": "outside.png"}}
        g["c0"]["inputs"]["ref_images.ref_image_1"] = ["img", 0]
        with self.assertRaises(ValueError) as ctx:
            reflora.verify_parody_2pass_graph(g, self.b2, cond_wired=False)
        msg = str(ctx.exception)
        self.assertIn("LoadImage", msg)
        self.assertIn("ref_images.ref_image_1", msg)
        g2, _, _ = self._no_photo()
        with self.assertRaises(ValueError) as ctx:
            reflora.verify_parody_2pass_graph(g2, self.b2)
        self.assertIn("ag0", str(ctx.exception))
        g3, _, _ = self._no_photo()
        g3["s1_guide"]["inputs"]["conditioning"] = [reflora.PARODY_P2_LOADER, 0]
        with self.assertRaises(ValueError) as ctx:
            reflora.verify_parody_2pass_graph(g3, self.b2, cond_wired=False)
        self.assertIn("s1_guide", str(ctx.exception))

    def test_keep_guard_relaxes_only_for_the_no_photo_shape(self):
        """verify_keep_dials must still demand the AddGuides when a photo is wired."""
        g, _, _ = self._no_photo()
        with self.assertRaises(ValueError) as ctx:
            verify_keep_dials(g, two_pass=True)
        self.assertIn("ag0", str(ctx.exception))

    def test_no_photo_lane_still_gates_a_supplied_photo(self):
        """--image with a Cond outside approved_characters still raises (FG-2/FG-11 unchanged)."""
        self._mod("badchar")
        self._hyb("badchar")
        outside = Path(self.tmp.name) / "outside.jpg"
        outside.write_bytes(b"nope")
        with self.assertRaises(ValueError) as ctx:
            self._no_photo(image=COND, cond_source=str(outside))
        self.assertIn("approved_characters", str(ctx.exception))

    def test_a_pool_photo_in_the_parody_lane_keeps_the_addguide_shape(self):
        """A gated photo: AddGuide + Picture wiring and <Picture 1> stay exactly as they were."""
        g, prompt, cond = self._no_photo(image=COND, cond_source=str(self.cond_src))
        self.assertEqual(g["img"]["class_type"], "LoadImage")
        self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
        for nid in ("ag0", "ag1"):
            self.assertEqual(g[nid]["inputs"]["positive"], [reflora.PARODY_REF_APPLY, 0], nid)
        for nid, guide in (("s0_guide", "ag0"), ("s1_guide", "ag1")):
            self.assertEqual(g[nid]["inputs"]["conditioning"], [guide, 0], nid)
        reflora.verify_parody_2pass_graph(g, self.b2)
        self.assertIn("<Picture 1>", prompt)
        self.assertEqual(cond["cond_sha256"], reflora.sha256_file(self.cond_src))
        self.assertEqual(self._dangling(g), [])

    def test_records_describe_the_built_graph_for_both_shapes(self):
        """Records: no-photo says no start_photo and names the guiders; a gated photo keeps B2-4."""
        self._mod("badchar")
        self._hyb("badchar")
        resolved = self._resolve("Badchar")
        build_parody_request(resolved, seed=1, prefix="community/t/clip", image=None,
                             cond_source=None, approved_pool=self.pool.parent,
                             comfy_input=self.comfy_input, graph_mode="two-pass-parody")
        pd = resolved["reflora"]["parody_dials"]
        self.assertFalse(pd["start_photo"])
        self.assertIn("s0_guide + s1_guide", pd["conditioning_injection"])
        self.assertNotIn("ag0 + ag1", pd["conditioning_injection"])
        resolved2 = self._resolve("Badchar")
        _, _, cond2 = build_parody_request(resolved2, seed=1, prefix="community/t/clip",
                                           image=COND, cond_source=str(self.cond_src),
                                           approved_pool=self.pool.parent,
                                           comfy_input=self.comfy_input,
                                           graph_mode="two-pass-parody")
        pd2 = resolved2["reflora"]["parody_dials"]
        self.assertTrue(pd2["start_photo"])
        self.assertIn("ag0 + ag1", pd2["conditioning_injection"])
        self.assertEqual(cond2["cond_sha256"], reflora.sha256_file(self.cond_src))

    def test_no_photo_never_takes_the_stage_cond_copy(self):
        """--stage-cond with no photo takes NO shutil.copy2 path (the WinError 32 defect)."""
        g, _, cond = self._no_photo(stage_cond=True)
        self.assertIsNone(cond["cond_input_name"])
        self.assertIsNone(cond["cond_sha256"])
        self.assertFalse(cond.get("staged"))
        self.assertNotIn("LoadImage", {n["class_type"] for n in g.values()})
        self.assertEqual(reflora.frozen_diff_no_photo(g, self.b2), [])

    def test_other_graph_modes_still_require_a_cond(self):
        """require=False is scoped to the no-photo parody lane; every other mode still blocks."""
        self._mod("badchar")
        self._hyb("badchar")
        for mode in ("single-pass", "two-pass"):
            with self.subTest(graph_mode=mode):
                with self.assertRaises(ValueError) as ctx:
                    build_parody_request(
                        self._resolve("Badchar"), seed=1, prefix="community/t/clip",
                        image=None, cond_source=None, approved_pool=self.pool.parent,
                        comfy_input=self.comfy_input, graph_mode=mode)
                self.assertIn("requires Cond", str(ctx.exception))

    def test_no_photo_parody_refmod_only_wires_both_guiders_and_blocks_when_empty(self):
        """RefMod-only 2-pass no-photo wires refapply -> s0_guide + s1_guide; zero RefMods blocks."""
        self._mod("badchar")
        g, prompt, cond = self._no_photo(refmod_only=True)
        self.assertIsNone(cond["cond_input_name"])
        self.assertNotIn("LoadImage", {n["class_type"] for n in g.values()})
        self.assertNotIn(reflora.LOADER_CLASS, {n["class_type"] for n in g.values()})
        self.assertEqual(g["refmods"]["inputs"]["mod_1"], "minimaxh3_badchar_v1_refmod")
        self.assertEqual(g["s0_guide"]["inputs"]["conditioning"], ["refapply", 0])
        self.assertEqual(g["s1_guide"]["inputs"]["conditioning"], ["refapply", 0])
        self.assertEqual(reflora.frozen_diff_no_photo(g, self.b2), [])
        empty_r = self._resolve("Goodchar", refmod_only=True)
        with self.assertRaises(ValueError) as ctx:
            build_parody_request(empty_r, seed=1, prefix="community/t/clip",
                                 image=None, cond_source=None, graph_mode="two-pass-parody")
        self.assertIn("standalone RefMod", str(ctx.exception))

    def test_drop_cond_picture_needs_the_single_injection(self):
        """drop_cond_picture refuses a plain b2 graph (no conditioning injection to feed)."""
        with self.assertRaises(ValueError) as ctx:
            reflora.drop_cond_picture(json.loads(
                Path(DEFAULT_B2_TEMPLATE).read_text(encoding="utf-8")))
        self.assertIn(reflora.PARODY_REF_APPLY, str(ctx.exception))


class OfflineClassCheck(unittest.TestCase):
    """B2-3 offline class validation: saved object_info capture + .disabled pack evidence.

    CPU only: the file's live-effect audit hook blocks socket/subprocess, and these fixtures
    read nothing outside a temp dir except the saved captures they are meant to check.
    """

    LSU3 = {"lsu3": {"class_type": "MinimaxH3LatentUpscaler3D", "inputs": {}}}
    UPSCALER_PACK = reflora.OFFLINE_PACK_UPSCALER

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="objcheck_")
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _dump(self, name: str, classes) -> Path:
        """Synthetic capture: membership is all the validator reads out of an object_info file."""
        p = self.root / name
        p.write_text(json.dumps({c: {"input": {"required": {}}} for c in classes}), encoding="utf-8")
        return p

    def _pack(self, name: str, class_name: str) -> Path:
        """A pack directory whose source registers the class (the shape grep-based evidence sees)."""
        pack = self.root / name
        (pack / "nodes").mkdir(parents=True)
        (pack / "nodes" / "n.py").write_text(
            f"NODE_CLASS_MAPPINGS = {{\"{class_name}\": TheNode}}\n", encoding="utf-8")
        return pack

    # (a) the restored pack's class passes against the fresh capture -------------------------
    def test_upscaler_class_passes_against_the_fresh_capture(self):
        if not reflora.DEFAULT_OBJINFO_DUMP.is_file():
            self.skipTest(f"no {reflora.DEFAULT_OBJINFO_DUMP} capture on this host")
        self.assertEqual(reflora.offline_class_check(self.LSU3), [])
        for tpl in (DEFAULT_B2_TEMPLATE, DEFAULT_REFMOD_TEMPLATE, DEFAULT_REFLORA_TEMPLATE,
                    DEFAULT_REFLORA_2PASS_TEMPLATE):
            with self.subTest(template=Path(tpl).name):
                g = json.loads(Path(tpl).read_text(encoding="utf-8"))
                self.assertEqual(reflora.offline_class_check(g), [],
                                 f"{Path(tpl).name} is not renderable against the fresh capture")

    # (b) a class no capture lists is rejected, naming the node ------------------------------
    def test_fake_class_is_rejected_with_the_node_id(self):
        dump = self._dump("object_info_20261105.json", ["LoadImage", "EmptySD3LatentImage"])
        out = reflora.offline_class_check(
            {"zz9": {"class_type": "NotARealNodeXYZ", "inputs": {}}}, dump,
            custom_nodes_dir=self.root / "no_packs")
        self.assertEqual(len(out), 1)
        self.assertIn("zz9", out[0])
        self.assertIn("NotARealNodeXYZ", out[0])
        self.assertIn("unknown class", out[0])

    # (c) the U5 failure: the .disabled pack is named, and said to be disabled --------------
    def test_u5_failure_line_is_exact(self):
        pack = self._pack(self.UPSCALER_PACK + reflora.DISABLED_SUFFIX,
                          "MinimaxH3LatentUpscaler3D")
        dump = self._dump("object_info_20261105.json", ["LTXVConcatAVLatent"])
        out = reflora.offline_class_check(self.LSU3, dump, custom_nodes_dir=self.root)
        self.assertEqual(
            out, ["lsu3: unknown class MinimaxH3LatentUpscaler3D "
                  f"(defined by {self.UPSCALER_PACK}{reflora.DISABLED_SUFFIX} - pack disabled)"])
        self.assertIn("pack disabled", out[0])
        self.assertEqual(pack.name, self.UPSCALER_PACK + reflora.DISABLED_SUFFIX)

    def test_old_capture_names_the_pack_and_says_disabled(self):
        """A pack parked as .disabled at capture time: the reason must name it and say disabled."""
        if not reflora.CUSTOM_NODES_DIR.is_dir():
            self.skipTest("no ComfyUI custom_nodes tree on this host")
        newest = reflora._saved_captures()
        if not newest:
            self.skipTest("no saved object_info captures on this host")
        freshest = json.loads(newest[0][1].read_text(encoding="utf-8"))
        if "MinimaxH3LatentUpscaler3D" not in freshest:
            self.skipTest("the freshest capture does not list the upscaler class")
        old = self._dump("object_info_20261101.json", ["LTXVConcatAVLatent"])
        out = reflora.offline_class_check(self.LSU3, old)
        self.assertEqual(len(out), 1, out)
        self.assertIn("lsu3: unknown class MinimaxH3LatentUpscaler3D", out[0])
        self.assertIn(self.UPSCALER_PACK, out[0])
        self.assertIn("pack disabled", out[0])

    # (d) the validator has no live effects --------------------------------------------------
    def test_validator_makes_no_socket_or_subprocess_call(self):
        import socket
        import subprocess
        for fn, args in ((socket.create_connection, (("127.0.0.1", 1), 0.05)),
                         (subprocess.Popen, (["cmd", "/c", "echo"],))):
            with self.subTest(fn=fn.__name__):
                with self.assertRaises(RuntimeError):
                    fn(*args)
        dump = self._dump("object_info_20261105.json", ["LoadImage"])
        self.assertTrue(reflora.offline_class_check(
            {"a": {"class_type": "NotARealNodeXYZ", "inputs": {}}}, dump,
            custom_nodes_dir=self.root))

    def test_missing_class_type_is_reported_and_no_capture_raises(self):
        dump = self._dump("object_info_20261105.json", ["LoadImage"])
        out = reflora.offline_class_check({"nx": {"inputs": {}}}, dump,
                                         custom_nodes_dir=self.root / "no_packs")
        self.assertEqual(out, ["nx: missing class_type"])
        with self.assertRaises(reflora.RefLoRAError):
            reflora.offline_class_check(self.LSU3, self.root / "object_info_19990101.json")


    """Header/tensor-only checks on the two smoke hybrids staged by HF (U2). CPU, read-only."""

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
