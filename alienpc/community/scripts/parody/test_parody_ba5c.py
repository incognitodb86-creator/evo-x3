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
import submit_parody_run as spr
from build_request import build_parody_request
from run_record import build_assets_record


INDEX_MD = """## Folder: `good`
| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Testa Char** | Testa Actor | Fixture Show | fixture.mp4 | 2026-11-05 |
"""
# B2-6: a fixture bio must state an adult age (the builder refuses one that does not).
BIO = "a woman of 30 years, short silver bob haircut, green eyes, navy blazer"


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
            "minimaxh3_testaextra_v1_refmod",
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
            "names": ["Testa Char", "Testa Extra"],
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

    def test_omitted_pool_rejects_outside_still(self):
        with mock.patch.object(resolve, "DEFAULT_APPROVED_STILLS_DIR", self.pool):
            with self.assertRaisesRegex(ValueError, "approved_characters pool"):
                self.resolve(stills=[self.outside])

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

        graph, _, _ = build_parody_request(res, seed=7, prefix="community/fixture/clip", frames=124, require_cond=False)
        inputs = graph["refmods"]["inputs"]
        ledger = build_assets_record(res, graph)["refmod_ledger"]
        self.assertEqual(len(ledger), 8)
        for row in ledger:
            i = row["slot"]
            self.assertEqual(row["mod"], inputs[f"mod_{i}"])
            self.assertEqual(row["strength"], inputs[f"strength_{i}"])
            self.assertEqual(row["copies"], inputs[f"copies_{i}"])
            self.assertEqual(row["path"], slots[f"mod_{i}"]["path"])

    def submit(self, returncode):
        run_dir = self.root / "run"
        done = subprocess.CompletedProcess(["fixture"], returncode, stdout="fixture stdout", stderr="")
        with mock.patch.object(spr, "INDEX_DIR", self.index), mock.patch.object(
            spr, "REFMODS_DIR", self.refmods
        ), mock.patch.object(spr, "ALIASES_PATH", self.root / "no-aliases.json"), mock.patch.object(
            spr, "REFLORA_DIR", None), mock.patch.object(
            spr.subprocess, "run", return_value=done
        ) as run:
            result = spr.submit_parody_job(
                name="Testa Char",
                character="Testa Char",
                actor="Testa Actor",
                description=BIO,
                seed=11,
                frames=124,
                run_dir_override=run_dir,
                require_cond=False,
                refmod_only=True,
            )
        return run_dir, result, run.call_args.args[0]

    def test_u8_uses_detached_run_queue_and_queue_manifest(self):
        run_dir, result, cmd = self.submit(0)
        self.assertIn("run_queue.py", " ".join(cmd))
        self.assertNotIn("run_graph_job.py", " ".join(cmd))
        # submit_parody_run passes --frames then --size (objective canvas) and ends with --detach.
        self.assertEqual(cmd[cmd.index("--frames") + 1], "124")
        self.assertEqual(cmd[cmd.index("--size") + 1], "768x1344")
        self.assertEqual(cmd[-1], "--detach")
        self.assertIn(str(run_dir), cmd)
        self.assertTrue(result["submitted"])
        self.assertTrue(result["detached"])
        self.assertFalse(result.get("gpu_busy", False))
        order = json.loads((run_dir / "_render_order.json").read_text(encoding="utf-8"))
        self.assertEqual(order["order"], [{"pos": 1, "tag": "clip", "arm": "parody", "scene": "Testa Char", "seed": 11, "graph_mode": "single-pass", "refmod_only": True, "unet": "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors", "pass1_lora_strength": None, "pass2_lora_strength": None}])
        self.assertEqual(
            json.loads((run_dir / "clip" / "request.api.json").read_text(encoding="utf-8")),
            json.loads((run_dir / "request.api.json").read_text(encoding="utf-8")),
        )

    def test_u8_rc7_is_gpu_busy_not_generic_failure(self):
        _, result, _ = self.submit(7)
        self.assertTrue(result["gpu_busy"])
        self.assertFalse(result["submitted"])
        self.assertEqual(result["returncode"], 7)
        with mock.patch.object(spr, "submit_parody_job", return_value=result):
            self.assertEqual(spr.main(["--name", "Testa Char", "--description", BIO]), 7)

    def test_detached_queue_log_rc7_is_gpu_busy(self):
        run_dir = self.root / "detached"
        run_dir.mkdir()
        (run_dir / "_render_queue.log").write_text(
            "2026-11-05T16:00:00-05:00 BATCH closed rc=7 reason=GPU busy done=0/1\n", encoding="utf-8"
        )
        self.assertEqual(spr.queue_outcome(run_dir), {"rc": 7, "gpu_busy": True})


if __name__ == "__main__":
    unittest.main()
