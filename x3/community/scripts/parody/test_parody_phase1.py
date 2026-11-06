"""Unit tests for Phase 1 Parody units (U1, U2, U3, U4).

Tests requirements R1-R6 and R9, KD2, KD9, KD10, KD13, KD14, KD15.
"""

from pathlib import Path
import shutil
import tempfile
import unittest

from request import parse_request
from resolve import resolve_identities, validate_stills
from sync_refmods import check_sync_status, sync_refmods


class TestParodyPhase1(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="parody_test_"))
        self.index_dir = Path(r"C:\AI\community\index\h3-known-characters")
        self.refmods_dir = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
        self.approved_dir = Path(r"C:\Users\derek\5slock\approved_characters")
        self.aliases_path = Path(r"C:\AI\community\scripts\parody\aliases.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_u1_r9a_chat_and_fields_identical(self):
        """R9-a: Chat 'Daenerys parody, 10s' and fields produce identical JSON."""
        chat_req = parse_request("Daenerys parody, 10s")
        fields_req = parse_request({
            "character": "Daenerys",
            "tone": "parody",
            "length_s": 10
        })
        self.assertEqual(chat_req["names"], ["Daenerys"])
        self.assertEqual(chat_req["character"], "Daenerys")
        self.assertEqual(chat_req["tone"], "parody")
        self.assertEqual(chat_req["length_s"], 10)
        self.assertEqual(chat_req["stills"], [])

        self.assertEqual(fields_req["names"], ["Daenerys"])
        self.assertEqual(fields_req["character"], "Daenerys")
        self.assertEqual(fields_req["tone"], "parody")
        self.assertEqual(fields_req["length_s"], 10)
        self.assertEqual(fields_req["stills"], [])
        self.assertEqual(chat_req, fields_req)

    def test_u1_r9b_missing_name_raises(self):
        """R9-b: Missing name in request raises ValueError."""
        with self.assertRaises(ValueError):
            parse_request("")
        with self.assertRaises(ValueError):
            parse_request({})
        with self.assertRaises(ValueError):
            parse_request({"names": [], "character": None, "actor": None})

    def test_u2_r2_good_row_native_face_voice(self):
        """R2: Good row (Daenerys / Emilia Clarke) gives mode native_face_voice with RefMod slots."""
        req = parse_request("Daenerys parody, 10s, bio: platinum-blonde braided hair, fantasy scale top")
        res = resolve_identities(
            req,
            index_dir=self.index_dir,
            refmods_dir=self.refmods_dir,
            approved_stills_dir=self.approved_dir,
            aliases_path=self.aliases_path,
        )
        self.assertEqual(res["mode"], "native_face_voice")
        self.assertEqual(res["index_status"], "good")
        self.assertGreater(len(res["index_rows"]), 0)
        # RefMod slots must be present and filled
        self.assertIn("mod_1", res["refmod_slots"])
        self.assertTrue(any("emiliaclarke" in s["path"] for s in res["refmod_slots"].values()))
        self.assertIn("Daenerys", res["description"])
        self.assertIn("platinum-blonde", res["description"])

    def test_u2_r3_bad_and_fence_rows(self):
        """R3: Bad and onthefence rows produce mode native_voice_refmod_look."""
        # Lara Croft is onthefence in INDEX.md
        req_fence = parse_request({
            "character": "Lara Croft",
            "tone": "parody",
            "length_s": 10,
            "description": "brunette braid, athletic explorer gear",
        })
        res_fence = resolve_identities(
            req_fence,
            index_dir=self.index_dir,
            refmods_dir=self.refmods_dir,
            approved_stills_dir=self.approved_dir,
            aliases_path=self.aliases_path,
        )
        self.assertEqual(res_fence["mode"], "native_voice_refmod_look")
        self.assertIn(res_fence["index_status"], ("onthefence", "good"))  # Angelina Jolie is good, Lara is onthefence

        # Agent Dale Cooper is bad in INDEX_BAD.md
        req_bad = parse_request({
            "character": "Agent Dale Cooper",
            "tone": "parody",
            "length_s": 10,
            "description": "neat dark suit, trenchcoat, coffee cup",
        })
        res_bad = resolve_identities(
            req_bad,
            index_dir=self.index_dir,
            refmods_dir=self.refmods_dir,
            approved_stills_dir=self.approved_dir,
            aliases_path=self.aliases_path,
        )
        self.assertEqual(res_bad["mode"], "native_voice_refmod_look")
        self.assertEqual(res_bad["index_status"], "bad")

    def test_u2_kd15_not_in_index(self):
        """KD15: Identity not in INDEX treated as bad (refmod look) and flagged index:none."""
        req = parse_request({
            "character": "UnknownFictionalPersona999",
            "tone": "parody",
            "length_s": 10,
            "description": "masked figure in silver cape",
        })
        res = resolve_identities(
            req,
            index_dir=self.index_dir,
            refmods_dir=self.refmods_dir,
            approved_stills_dir=self.approved_dir,
            aliases_path=self.aliases_path,
        )
        self.assertEqual(res["mode"], "native_voice_refmod_look")
        self.assertEqual(res["index_status"], "none")
        self.assertEqual(res["index_flag"], "index:none")

    def test_u2_r4_dual_match_stacking(self):
        """R4: Dual match stacks both character and actor assets."""
        req = parse_request({
            "character": "Rachel Green",
            "actor": "Jennifer Aniston",
            "tone": "adult",
            "length_s": 10,
            "description": "layered 90s blonde hair, cafe denim vest",
        })
        res = resolve_identities(
            req,
            index_dir=self.index_dir,
            refmods_dir=self.refmods_dir,
            approved_stills_dir=self.approved_dir,
            aliases_path=self.aliases_path,
        )
        self.assertEqual(res["mode"], "native_face_voice")
        # Check both are mentioned in description and loaded
        self.assertIn("Rachel Green", res["description"])
        self.assertIn("Jennifer Aniston", res["description"])
        self.assertIn("layered 90s blonde hair", res["description"])
        self.assertTrue(any("jenniferaniston" in s["path"] for s in res["refmod_slots"].values()))

    def test_u2_kd14_over_8_slots_truncation(self):
        """KD14: Over 8 RefMods keeps character matches first, highest index status, exactly 8 slots."""
        mock_refmods_dir = self.test_dir / "mock_refmods"
        mock_refmods_dir.mkdir()
        # Create 10 fake refmod files
        fake_files = []
        for i in range(1, 11):
            p = mock_refmods_dir / f"minimaxh3_char{i}_v1_refmod.safetensors"
            p.write_bytes(b"dummy" * 1000)
            fake_files.append(p)

        # Request matching all 10
        names = [f"char{i}" for i in range(1, 11)]
        req = {
            "names": names,
            "character": "char1",
            "actor": None,
            "tone": "parody",
            "length_s": 10,
            "stills": [],
            "description": "short brown hair, athletic green flight suit",
        }
        res = resolve_identities(
            req,
            index_dir=self.index_dir,
            refmods_dir=mock_refmods_dir,
            approved_stills_dir=self.approved_dir,
            aliases_path=None,
        )
        # Must keep exactly 8 slots
        self.assertEqual(len(res["refmod_slots"]), 8)
        self.assertEqual(len(res["loaded_refmods"]), 8)
        self.assertEqual(len(res["dropped_refmods"]), 2)
        # char1 (character) must be kept
        self.assertTrue(any("char1" in str(p) for p in res["loaded_refmods"]))

    def test_u3_r5_stills_gate(self):
        """R5 / U3: Stills gate permits only approved pool, rejects non-pool and Sydney."""
        # 1. Pool still (valid)
        pool_img = self.approved_dir / "BEDROOM01" / "preview.png"
        if not pool_img.exists():
            # Find any valid file in approved_dir
            for f in self.approved_dir.rglob("*.png"):
                if "sydney" not in str(f).lower():
                    pool_img = f
                    break

        if pool_img.is_file():
            validated = validate_stills([str(pool_img)], self.approved_dir)
            self.assertEqual(len(validated), 1)

        # 2. Non-pool still -> rejected
        fake_still = self.test_dir / "random.png"
        fake_still.write_bytes(b"data")
        with self.assertRaises(ValueError) as ctx:
            validate_stills([str(fake_still)], self.approved_dir)
        self.assertIn("not within the approved_characters pool", str(ctx.exception))

        # 3. Sydney path -> rejected
        sydney_fake = self.approved_dir / "SYDNEY" / "face.png"
        with self.assertRaises(ValueError) as ctx:
            validate_stills([str(sydney_fake)], self.approved_dir)
        self.assertIn("Sydney paths are strictly prohibited", str(ctx.exception))

    def test_u4_r6_sync_dry_run_and_fixtures(self):
        """R6 / U4: Sync dry-run reports missing/short without downloading."""
        mock_target = self.test_dir / "sync_target"
        mock_target.mkdir()

        # 1. Existing valid file
        valid_fn = "minimaxh3_emiliaclarke_v1_refmod.safetensors"
        (mock_target / valid_fn).write_bytes(b"x" * 600_000)

        # 2. Incomplete file (< 500 KB)
        short_fn = "minimaxh3_short_v1_refmod.safetensors"
        (mock_target / short_fn).write_bytes(b"x" * 100_000)

        # 3. Missing file
        missing_fn = "minimaxh3_missing_v1_refmod.safetensors"

        status = check_sync_status(
            names=[],
            target_dir=mock_target,
            expected_filenames=[valid_fn, short_fn, missing_fn],
        )
        self.assertIn(valid_fn, status["up_to_date"])
        self.assertIn(short_fn, status["incomplete"])
        self.assertIn(missing_fn, status["missing"])
        self.assertEqual(set(status["to_download"]), {short_fn, missing_fn})

        # Dry run result
        res = sync_refmods(
            names=[],
            target_dir=mock_target,
            dry_run=True,
            expected_filenames=[valid_fn, short_fn, missing_fn],
        )
        self.assertTrue(res["dry_run"])
        self.assertEqual(len(res["downloaded"]), 0)
        self.assertEqual(set(res["to_download"]), {short_fn, missing_fn})


if __name__ == "__main__":
    unittest.main()
