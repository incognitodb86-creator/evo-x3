#!/usr/bin/env python3
"""Offline unit tests for x3/still_candidate_sheet.py (ST1)."""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import still_candidate_sheet as scs


def _fake_thumb_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (80, 120, 160)).save(buf, format="PNG")
    return buf.getvalue()


def _make_hits(n: int = 30, *, start_id: int = 1, likeness: float = 0.80) -> list[dict]:
    hits = []
    for i in range(n):
        pid = start_id + i
        hits.append({
            "id": pid,
            "file_path": f"lib/img_{pid:03d}.jpg",
            "score": round(1.0 - i * 0.01, 4),
            "smart_score": round(0.95 - i * 0.005, 4),
            "likeness_score": likeness,
            "is_video": False,
        })
    return hits


class StillCandidateSheetTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.thumb = _fake_thumb_bytes()
        self.captured_urls: list[str] = []

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run_sheet(self, hits: list[dict], **kwargs) -> list[dict]:
        out = self.tmp / f"sheet_{len(self.captured_urls)}.png"

        def fake_get_json(path: str, tok: str):
            self.captured_urls.append(path)
            return list(hits)

        with (
            mock.patch.object(scs, "_token", return_value="dummy"),
            mock.patch.object(scs, "_get_json", side_effect=fake_get_json),
            mock.patch.object(scs, "_get_bytes", return_value=self.thumb),
        ):
            return scs.build_sheet("bedroom", out, **kwargs)

    def test_search_uses_limit_60_and_same_query_twice_differs(self) -> None:
        hits = _make_hits(30)
        runs_dir = self.tmp / "empty_runs"
        runs_dir.mkdir()

        s1 = self._run_sheet(hits, runs_dir=runs_dir)
        s2 = self._run_sheet(hits, runs_dir=runs_dir)

        self.assertIn("limit=60", self.captured_urls[0])
        self.assertEqual(len(s1), 6)
        self.assertEqual(len(s2), 6)
        # All chosen items come from top 18 (IDs 1..18)
        self.assertTrue(all(1 <= item["id"] <= 18 for item in s1))
        self.assertTrue(all(1 <= item["id"] <= 18 for item in s2))
        # Different sheets across calls (with overwhelming probability on 18P6)
        ids1 = [item["id"] for item in s1]
        ids2 = [item["id"] for item in s2]
        if ids1 == ids2:
            s3 = self._run_sheet(hits, runs_dir=runs_dir)
            self.assertNotEqual(ids1, [item["id"] for item in s3])

        # Logged seed rebuilds the exact same sheet
        seed1 = s1[0]["seed"]
        self.assertIsInstance(seed1, int)
        rebuilt = self._run_sheet(hits, runs_dir=runs_dir, seed=seed1)
        self.assertEqual(ids1, [item["id"] for item in rebuilt])

    def test_recent_picks_excluded_when_enough_fresh_exist(self) -> None:
        hits = _make_hits(30)
        runs_dir = self.tmp / "runs"
        runs_dir.mkdir()

        # Write 25 runs; newest 20 use IDs 1..20 (full PixlStash path & relative path)
        for i in range(25):
            rdir = runs_dir / f"run_{i:02d}"
            rdir.mkdir()
            pf = rdir / "pick.json"
            # Older runs (i=0..4) use IDs 21..25; newest 20 (i=5..24) use IDs 1..20
            if i < 5:
                still_val = f"/home/evo/AI/5slock/libraries/lib/img_{21 + i:03d}.jpg"
            else:
                pid = i - 4  # 1..20
                still_val = (
                    f"/home/evo/AI/5slock/libraries/lib/img_{pid:03d}.jpg"
                    if pid % 2 == 0
                    else f"lib/img_{pid:03d}.jpg"
                )
            pf.write_text(json.dumps({"still": still_val}), encoding="utf-8")
            os.utime(pf, (1_700_000_000 + i * 10, 1_700_000_000 + i * 10))

        summary = self._run_sheet(hits, runs_dir=runs_dir, recent_n=20, seed=42)
        chosen_ids = {item["id"] for item in summary}
        self.assertEqual(len(chosen_ids), 6)
        # None of the 20 most recent picks (IDs 1..20) may appear
        self.assertTrue(chosen_ids.isdisjoint(set(range(1, 21))), f"recent pick leaked: {chosen_ids}")

    def test_exclude_and_page_2(self) -> None:
        hits = _make_hits(30)
        runs_dir = self.tmp / "runs_empty"
        runs_dir.mkdir()

        s1 = self._run_sheet(hits, runs_dir=runs_dir, seed=7)
        shown = [item["id"] for item in s1]
        s2 = self._run_sheet(
            hits,
            runs_dir=runs_dir,
            exclude=[",".join(str(x) for x in shown)],
            page=2,
            seed=7,
        )
        shown2 = [item["id"] for item in s2]
        self.assertEqual(len(shown2), 6)
        self.assertTrue(set(shown).isdisjoint(set(shown2)))

        # Standalone --page 2 without --exclude shifts past the top-6 slice (IDs 1..6)
        s_p2 = self._run_sheet(hits, runs_dir=runs_dir, page=2, seed=9)
        self.assertTrue(all(item["id"] >= 7 for item in s_p2))

    def test_fallback_to_excluded_last_when_fewer_than_6_fresh(self) -> None:
        hits = _make_hits(8)
        runs_dir = self.tmp / "runs_fb"
        runs_dir.mkdir()
        for pid in (1, 2, 3):
            rdir = runs_dir / f"r{pid}"
            rdir.mkdir()
            (rdir / "pick.json").write_text(
                json.dumps({"still": f"/home/evo/AI/5slock/libraries/lib/img_{pid:03d}.jpg"}),
                encoding="utf-8",
            )
        # Also explicitly exclude IDs 4, 5 -> only 3 fresh remain (6, 7, 8)
        summary = self._run_sheet(hits, runs_dir=runs_dir, exclude=["4,5"], seed=11)
        ids = [item["id"] for item in summary]
        self.assertEqual(len(ids), 6)
        # Fresh 3 must come first, then excluded fallback (recent 1,2,3 before explicit 4,5)
        self.assertEqual(set(ids[:3]), {6, 7, 8})
        self.assertEqual(ids[3:], [1, 2, 3])

    def test_filters_unchanged_videos_and_likeness_fallback(self) -> None:
        runs_dir = self.tmp / "runs_filt"
        runs_dir.mkdir()
        hits = _make_hits(10, likeness=0.80)
        hits[0]["is_video"] = True
        hits[1]["likeness_score"] = 0.40

        summary = self._run_sheet(hits, character_id=1, runs_dir=runs_dir, seed=5)
        ids = {item["id"] for item in summary}
        self.assertNotIn(1, ids)  # video excluded
        self.assertNotIn(2, ids)  # likeness < 0.55 excluded

        # Line 52 fallback: when likeness filter empties, fall back to all non-video hits
        low_hits = _make_hits(8, likeness=0.30)
        low_hits[0]["is_video"] = True
        summary_fb = self._run_sheet(low_hits, character_id=1, runs_dir=runs_dir, seed=5)
        ids_fb = {item["id"] for item in summary_fb}
        self.assertEqual(len(ids_fb), 6)
        self.assertNotIn(1, ids_fb)  # video still excluded


if __name__ == "__main__":
    unittest.main()
