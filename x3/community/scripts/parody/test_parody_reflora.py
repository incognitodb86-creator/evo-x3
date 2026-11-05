"""RefLoRA arm U2-U4 CPU fixtures (synthetic safetensors; no GPU, network or process launch).

Covers R8 (all-three when a matching hybrid exists, absent-only fallback, broken blocks),
R9 (frozen B2 dials), R10 (Cond reaches REF2VA Picture), KTD2 (one injection route) and
KTD3 (standalone/packed provenance dedup, 8-reference budget).
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
from build_request import DEFAULT_REFMOD_TEMPLATE, DEFAULT_REFLORA_TEMPLATE, build_parody_request
from run_record import build_assets_record

INDEX_MD = """## Folder: `good`
| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Goodchar** | Goodactor | Fixture Show | g.mp4 | 2026-11-05 |
## Folder: `onthefence`
| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Fencechar** | Fenceactor | Fixture Show | f.mp4 | 2026-11-05 |
"""
INDEX_BAD_MD = """| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Badchar** | Badactor | Fixture Show | b.mp4 | 2026-11-05 |
"""
BIO = "long dark hair, hazel eyes, red leather jacket"
COND = "community/FIXTURE_COND_768x1344.png"


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
        self.tpl = json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def _mod(self, ident: str, seed: int = 1) -> Path:
        p = self.refmods / f"minimaxh3_{ident}_v1_refmod.safetensors"
        make_refmod(p, seed)
        return p

    def _hyb(self, ident: str, seed: int = 1, **kw) -> Path:
        p = self.rdir / f"minimaxh3_{ident}_v1_reflora.safetensors"
        make_hybrid(p, f"minimaxh3_{ident}_v1_refmod", seed, **kw)
        return p

    def _resolve(self, character: str):
        return resolve.resolve_identities(
            {"names": [character], "character": character, "description": BIO},
            index_dir=self.index, refmods_dir=self.refmods, reflora_dir=self.rdir)

    # R8: good/bad/fence x present/absent ----------------------------------
    def test_all_three_layers_when_hybrid_present_each_index_class(self):
        for ident, cls in (("goodchar", "good"), ("badchar", "bad"), ("fencechar", "onthefence")):
            with self.subTest(cls=cls):
                self._mod(ident)
                self._hyb(ident)
                r = self._resolve(ident.capitalize())
                self.assertEqual(r["index_status"], cls)
                self.assertEqual(r["identity_layers"], ["INDEX", "RefMod", "RefLoRA"])
                self.assertIn(BIO, r["description"])  # INDEX description never dropped
                g, prompt = build_parody_request(r, seed=1, prefix="community/t/clip", image=COND)
                self.assertIn(ident.capitalize(), prompt)
                self.assertEqual(g["s0_guide"]["inputs"]["model"], ["reflora_1", 0])
                self.assertEqual(g["s0_sched"]["inputs"]["model"], ["reflora_1", 0])
                self.assertEqual(g["s0_guide"]["inputs"]["conditioning"], ["reflora_apply_1", 0])
                self.assertEqual(g["reflora_apply_1"]["inputs"]["conditioning"], ["refapply", 0])
                self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
                self.assertEqual(g["img"]["inputs"]["image"], COND)
                self.assertEqual(reflora.frozen_diff(self.tpl, g), [])

    def test_absent_hybrid_falls_back_to_index_refmod(self):
        for ident in ("goodchar", "badchar", "fencechar"):
            with self.subTest(ident=ident):
                self._mod(ident)
                r = self._resolve(ident.capitalize())
                self.assertEqual(r["identity_layers"], ["INDEX", "RefMod"])
                self.assertFalse(r["reflora"]["enabled"])
                self.assertIn("fallback", r["reflora"]["fallback_reason"])
                g, _ = build_parody_request(r, seed=1, prefix="community/t/clip")
                self.assertFalse([k for k, v in g.items() if v["class_type"].startswith("MiniMaxH3RefLoRA")])
                self.assertEqual(reflora.frozen_diff(self.tpl, g), [])

    def test_fallback_restores_cond_when_still_given(self):
        self._mod("badchar")
        g, _ = build_parody_request(self._resolve("Badchar"), seed=1, prefix="community/t/clip", image=COND)
        self.assertEqual(g["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
        self.assertEqual(reflora.frozen_diff(self.tpl, g), [])

    def test_broken_present_hybrid_blocks(self):
        self._mod("badchar")
        self._hyb("badchar", declared=600)  # weights stripped vs declared
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
            build_parody_request(self._resolve("Badchar"), seed=1, prefix="community/t/clip")

    # KTD3 provenance --------------------------------------------------------
    def test_identical_standalone_injected_once_from_hybrid(self):
        self._mod("badchar", seed=5)
        self._hyb("badchar", seed=5)
        r = self._resolve("Badchar")
        self.assertEqual(len(r["reflora"]["standalone_deduped"]), 1)
        self.assertEqual(r["loaded_refmods"], [])
        self.assertEqual(r["refmod_slots"]["mod_1"]["path"], "(none)")
        self.assertEqual(r["reflora"]["effective_reference_count"], 1)

    def test_distinct_standalone_and_packed_both_survive(self):
        self._mod("badchar", seed=5)
        self._hyb("badchar", seed=9)
        r = self._resolve("Badchar")
        self.assertEqual(r["reflora"]["standalone_deduped"], [])
        self.assertEqual(len(r["loaded_refmods"]), 1)
        self.assertEqual(r["reflora"]["effective_reference_count"], 2)
        self.assertIn("standalone_differs", r["reflora"]["hybrids"][0])

    def test_audio_members_excluded_visual_only(self):
        self._mod("badchar")
        self._hyb("badchar", audio=True)
        r = self._resolve("Badchar")
        h = r["reflora"]["hybrids"][0]
        self.assertEqual(h["components"], "Visual")
        self.assertEqual(h["member_selection"], "1")
        self.assertEqual(h["audio_members_excluded"], ["minimaxh3_badchar_v1_refmod_voice"])

    # KTD2 / R9 graph guards --------------------------------------------------
    def _graph(self):
        self._mod("badchar")
        self._hyb("badchar")
        g, _ = build_parody_request(self._resolve("Badchar"), seed=1, prefix="community/t/clip", image=COND)
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
        g, _ = build_parody_request(r, seed=1, prefix="community/t/clip", image=COND)
        a = build_assets_record(r, g)
        self.assertEqual(a["identity_layers"], ["INDEX", "RefMod", "RefLoRA"])
        self.assertEqual(a["cond_picture"], COND)
        self.assertEqual(len(a["reflora_ledger"]), 1)
        self.assertEqual(a["reflora_ledger"][0]["components"], "Visual")
        self.assertGreater(a["reflora"]["hybrids"][0]["lora_keys"], 0)
        self.assertTrue(a["reflora"]["hybrids"][0]["sha256"])

    def test_committed_template_matches_derivation(self):
        committed = json.loads(Path(DEFAULT_REFLORA_TEMPLATE).read_text(encoding="utf-8"))
        self.assertEqual(committed, reflora.derive_reflora_template(self.tpl))
        self.assertEqual(reflora.frozen_diff(self.tpl, committed), [])


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
                sel = reflora.select_reflora([str(refmods / f"minimaxh3_{n}_v1_refmod.safetensors")],
                                             rdir, with_file_hash=False)
                self.assertTrue(sel["enabled"])
                h = sel["hybrids"][0]
                self.assertEqual(h["lora_keys"], 600)
                self.assertEqual(h["lora_name"], f"MinimaxH3\\reflora\\minimaxh3_{n}_v1_reflora.safetensors")
                self.assertEqual(len(sel["standalone_deduped"]), 1, sel)


if __name__ == "__main__":
    unittest.main()
