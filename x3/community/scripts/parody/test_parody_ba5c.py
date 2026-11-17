"""BA-5c CPU fixtures: default still gate, KD17 slot ledger and U8 queue route.

Synthetic temp files only. No GPU, network, process launch, live run or approved-pool read.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


def _deny_live_effects(event, args):
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"BA-5c CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

import resolve
from build_request import build_parody_request
from run_record import build_assets_record


INDEX_MD = """## Folder: `good`
| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Testa Char** | Testa Actor | Fixture Show | fixture.mp4 | 2026-11-05 |
"""
BIO = "short silver bob haircut, green eyes, navy blazer"


class TestBA5cFixes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ba5c_")
        self.root = Path(self.tmp.name)
        self.index = self.root / "index"
        self.index.mkdir()
        (self.index / "INDEX.md").write_text(INDEX_MD, encoding="utf-8")
        self.refmods = self.root / "refmods"
        self.refmods.mkdir()
        for name in (
            "minimaxh3_testachar_v1_refmod",
            "minimaxh3_testachar_alt_v1_refmod",
            "minimaxh3_testaactor_v1_refmod",
        ):
            (self.refmods / f"{name}.safetensors").write_bytes(b"fixture")
        self.pool = self.root / "approved_characters"
        (self.pool / "P1").mkdir(parents=True)
        self.pool_still = self.pool / "P1" / "fixture.png"
        self.pool_still.write_bytes(b"fixture")
        self.outside = self.root / "outside.png"
        self.outside.write_bytes(b"fixture")

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, stills=()):
        return {
            "names": ["Testa Char"],
            "character": "Testa Char",
            "actor": "Testa Actor",
            "tone": "parody",
            "length_s": 5,
            "description": BIO,
            "stills": [str(s) for s in stills],
        }

    def resolve(self, stills=(), **kwargs):
        return resolve.resolve_identities(
            self.request(stills), index_dir=self.index, refmods_dir=self.refmods, **kwargs
        )

    def test_omitted_pool_accepts_outside_still(self):
        # Pool containment dropped (Derrick t2086u/t2087u): any existing still is accepted.
        with mock.patch.object(resolve, "DEFAULT_APPROVED_STILLS_DIR", self.pool):
            res = self.resolve(stills=[self.outside])
        self.assertEqual(res["stills"], [str(Path(self.outside).resolve())])

    def test_omitted_pool_accepts_default_pool_still(self):
        with mock.patch.object(resolve, "DEFAULT_APPROVED_STILLS_DIR", self.pool):
            res = self.resolve(stills=[self.pool_still])
        self.assertEqual(res["stills"], [str(self.pool_still.resolve())])

    def test_explicit_pool_still_is_accepted(self):
        res = self.resolve(stills=[self.pool_still], approved_stills_dir=self.pool)
        self.assertEqual(res["stills"], [str(self.pool_still.resolve())])

    def test_kd17_strength_copies_ledger_matches_graph(self):
        res = self.resolve()
        slots = res["refmod_slots"]
        self.assertEqual([slots[f"mod_{i}"]["strength"] for i in range(1, 4)], [1.0, 1.0, 0.8])
        self.assertEqual([slots[f"mod_{i}"]["copies"] for i in range(1, 9)], [1] * 8)
        for i in range(4, 9):
            self.assertEqual(slots[f"mod_{i}"], {"path": "(none)", "strength": 1.0, "copies": 1})

        graph, _ = build_parody_request(res, seed=7, prefix="community/fixture/clip", frames=124)
        inputs = graph["refmods"]["inputs"]
        ledger = build_assets_record(res, graph)["refmod_ledger"]
        self.assertEqual(len(ledger), 8)
        for row in ledger:
            i = row["slot"]
            self.assertEqual(row["mod"], inputs[f"mod_{i}"])
            self.assertEqual(row["strength"], inputs[f"strength_{i}"])
            self.assertEqual(row["copies"], inputs[f"copies_{i}"])
            self.assertEqual(row["path"], slots[f"mod_{i}"]["path"])






if __name__ == "__main__":
    unittest.main()
