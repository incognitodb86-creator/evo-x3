#!/usr/bin/env python3
"""Offline unit tests for x3/still_candidate_sheet.py (ST1 + 2026-11-20 PixlStash 2.0 picker upgrade)."""
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


def _make_hits(
    n: int = 30,
    *,
    start_id: int = 1,
    likeness: float = 0.80,
    smart_score: float | None = 3.5,
    width: int = 1024,
    height: int = 1536,
    stack_ids: dict[int, int] | None = None,
) -> list[dict]:
    hits = []
    for i in range(n):
        pid = start_id + i
        ss = None if smart_score is None else round(smart_score - i * 0.01, 2)
        hits.append({
            "id": pid,
            "file_path": f"lib/img_{pid:03d}.jpg",
            "format": "JPEG",
            "width": width,
            "height": height,
            "score": round(1.0 - i * 0.01, 4),
            "smart_score": ss,
            "likeness_score": likeness,
            "stack_id": (stack_ids or {}).get(pid),
            "imported_at": f"2026-11-{(i % 19) + 1:02d}T12:00:00Z",
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

    def _run_sheet(self, hits_or_fn, **kwargs) -> list[dict]:
        out = kwargs.pop("out_path", self.tmp / f"sheet_{len(self.captured_urls)}.png")

        def fake_get_json(path: str, tok: str):
            self.captured_urls.append(path)
            if callable(hits_or_fn):
                return hits_or_fn(path)
            return list(hits_or_fn)

        with (
            mock.patch.object(scs, "_token", return_value="dummy"),
            mock.patch.object(scs, "_get_json", side_effect=fake_get_json),
            mock.patch.object(scs, "_get_bytes", return_value=self.thumb),
        ):
            return scs.build_sheet(out_path=out, **kwargs)

    def test_free_text_search_uses_wide_pool_and_varies_across_calls(self) -> None:
        hits = _make_hits(30)
        runs_dir = self.tmp / "empty_runs"
        runs_dir.mkdir()

        s1 = self._run_sheet(hits, query="bedroom", runs_dir=runs_dir)
        s2 = self._run_sheet(hits, query="bedroom", runs_dir=runs_dir)

        self.assertIn("/api/v1/pictures/search?", self.captured_urls[0])
        self.assertIn(f"limit={scs.FETCH_LIMIT}", self.captured_urls[0])
        self.assertEqual(len(s1), 6)
        self.assertEqual(len(s2), 6)
        ids1 = [item["id"] for item in s1]
        ids2 = [item["id"] for item in s2]
        if ids1 == ids2:
            s3 = self._run_sheet(hits, query="bedroom", runs_dir=runs_dir)
            self.assertNotEqual(ids1, [item["id"] for item in s3])

        seed1 = s1[0]["seed"]
        rebuilt = self._run_sheet(hits, query="bedroom", runs_dir=runs_dir, seed=seed1)
        self.assertEqual(ids1, [item["id"] for item in rebuilt])

    def test_smart_score_is_floor_only_and_none_passes(self) -> None:
        runs_dir = self.tmp / "runs_ss"
        runs_dir.mkdir()
        hits = [
            {"id": 1, "file_path": "lib/low.jpg", "width": 1024, "height": 1536, "score": 0.99, "smart_score": 1.8, "likeness_score": 0.90},
            {"id": 2, "file_path": "lib/edge.jpg", "width": 1024, "height": 1536, "score": 0.95, "smart_score": 2.2, "likeness_score": 0.85},
            {"id": 3, "file_path": "lib/unscored.jpg", "width": 1024, "height": 1536, "score": 0.94, "smart_score": None, "likeness_score": 0.84},
            {"id": 4, "file_path": "lib/below.jpg", "width": 1024, "height": 1536, "score": 0.93, "smart_score": 2.19, "likeness_score": 0.83},
            {"id": 5, "file_path": "lib/ok1.jpg", "width": 1024, "height": 1536, "score": 0.80, "smart_score": 2.5, "likeness_score": 0.80},
            {"id": 6, "file_path": "lib/ok2.jpg", "width": 1024, "height": 1536, "score": 0.79, "smart_score": 4.9, "likeness_score": 0.79},
            {"id": 7, "file_path": "lib/ok3.jpg", "width": 1024, "height": 1536, "score": 0.78, "smart_score": 2.4, "likeness_score": 0.78},
            {"id": 8, "file_path": "lib/ok4.jpg", "width": 1024, "height": 1536, "score": 0.77, "smart_score": 2.3, "likeness_score": 0.77},
        ]
        summary = self._run_sheet(hits, query="portrait", runs_dir=runs_dir, min_smart_score=2.2, seed=42)
        ids = {item["id"] for item in summary}
        self.assertEqual(ids, {2, 3, 5, 6, 7, 8})
        self.assertNotIn(1, ids)  # 1.8 < 2.2 dropped
        self.assertNotIn(4, ids)  # 2.19 < 2.2 dropped
        self.assertIn(3, ids)     # None passes (newly imported unscored still)
        self.assertFalse(summary[0]["smart_floor_fallback"])

    def test_character_query_uses_pictures_endpoint_never_search_with_character_id(self) -> None:
        runs_dir = self.tmp / "runs_char"
        runs_dir.mkdir()
        primary = _make_hits(15, start_id=1, likeness=0.82)
        recent = _make_hits(5, start_id=100, likeness=0.75)

        def fake_api(path: str):
            if "sort=IMPORTED_AT" in path:
                return recent
            return primary

        summary = self._run_sheet(
            fake_api,
            character_id=1,
            tags=["office"],
            rejected_tags=["blurry"],
            runs_dir=runs_dir,
            seed=12,
        )
        self.assertTrue(any("/api/v1/pictures?" in u and "character_id=1" in u and "sort=CHARACTER_LIKENESS" in u for u in self.captured_urls))
        self.assertTrue(any("/api/v1/pictures?" in u and "sort=IMPORTED_AT" in u for u in self.captured_urls))
        self.assertTrue(all("descending=true" in u for u in self.captured_urls if "/api/v1/pictures?" in u))
        self.assertFalse(any("/api/v1/pictures/search" in u for u in self.captured_urls))
        self.assertFalse(any("SMART_SCORE" in u for u in self.captured_urls))
        # Stratified sample must include at least one recent import (IDs 100..104)
        ids = {item["id"] for item in summary}
        self.assertTrue(ids & {100, 101, 102, 103, 104}, f"no recent imports stratified: {ids}")

    def test_smart_set_id_passed_to_pictures_endpoint(self) -> None:
        runs_dir = self.tmp / "runs_set"
        runs_dir.mkdir()
        hits = _make_hits(10)
        summary = self._run_sheet(hits, set_id=7, runs_dir=runs_dir, seed=3)
        self.assertEqual(len(summary), 6)
        self.assertIn("/api/v1/pictures?", self.captured_urls[0])
        self.assertIn("set_id=7", self.captured_urls[0])
        self.assertIn("format=JPEG", self.captured_urls[0])
        self.assertIn("format=PNG", self.captured_urls[0])

    def test_aspect_filter_and_needs_reframe_fallback(self) -> None:
        runs_dir = self.tmp / "runs_asp"
        runs_dir.mkdir()
        portrait = _make_hits(6, start_id=1, width=832, height=1248)
        landscape = _make_hits(6, start_id=20, width=1536, height=864)
        small = _make_hits(4, start_id=40, width=512, height=320)

        # Request 16:9 -> picks only landscape (>=768 short edge), needs_reframe=False
        s_land = self._run_sheet(portrait + landscape + small, query="cafe", aspect="16:9", runs_dir=runs_dir, seed=5)
        self.assertTrue(all(20 <= item["id"] <= 25 for item in s_land))
        self.assertFalse(s_land[0]["needs_reframe"])

        # Request 16:9 when ONLY portrait exists -> falls back with needs_reframe=True
        s_fb = self._run_sheet(portrait, query="cafe", aspect="16:9", runs_dir=runs_dir, seed=5)
        self.assertEqual(len(s_fb), 6)
        self.assertTrue(all(item["needs_reframe"] for item in s_fb))

    def test_stack_dedup_picks_at_most_one_per_stack(self) -> None:
        runs_dir = self.tmp / "runs_stack"
        runs_dir.mkdir()
        # IDs 1..5 share stack 99; IDs 6..10 are unstacked
        stack_map = {1: 99, 2: 99, 3: 99, 4: 99, 5: 99}
        hits = _make_hits(10, stack_ids=stack_map)
        summary = self._run_sheet(hits, query="studio", runs_dir=runs_dir, seed=8)
        stack_99_picks = [item for item in summary if item["stack_id"] == 99]
        self.assertEqual(len(stack_99_picks), 1)
        self.assertEqual(len(summary), 6)

    def test_recent_picks_excluded_and_exclude_and_page_2(self) -> None:
        hits = _make_hits(30)
        runs_dir = self.tmp / "runs"
        runs_dir.mkdir()
        for i in range(25):
            rdir = runs_dir / f"run_{i:02d}"
            rdir.mkdir()
            pf = rdir / "pick.json"
            still_val = (
                f"/home/evo/AI/5slock/libraries/lib/img_{21 + i:03d}.jpg"
                if i < 5
                else f"lib/img_{i - 4:03d}.jpg"
            )
            pf.write_text(json.dumps({"still": still_val}), encoding="utf-8")
            os.utime(pf, (1_700_000_000 + i * 10, 1_700_000_000 + i * 10))

        summary = self._run_sheet(hits, query="bedroom", runs_dir=runs_dir, recent_n=20, seed=42)
        chosen_ids = {item["id"] for item in summary}
        self.assertTrue(chosen_ids.isdisjoint(set(range(1, 21))))

        # Explicit exclude works
        s2 = self._run_sheet(hits, query="bedroom", runs_dir=self.tmp / "no_runs", exclude=["1,2,3,4,5,6"], seed=7)
        self.assertTrue({item["id"] for item in s2}.isdisjoint({1, 2, 3, 4, 5, 6}))

    def test_media_dir_creates_space_free_symlinks_without_out_sheet(self) -> None:
        runs_dir = self.tmp / "runs_med"
        runs_dir.mkdir()
        media_dir = self.tmp / "image_cache"
        hits = _make_hits(6)
        hits[0]["file_path"] = "My Folder/photo with spaces.jpg"
        created: list[tuple[str, str]] = []
        if os.name == "nt":
            cm = mock.patch.object(scs.os, "symlink", side_effect=lambda src, dst: created.append((src, dst)))
        else:
            cm = mock.nullcontext()
        with cm:
            summary = self._run_sheet(
                hits,
                query="office",
                out_path=None,
                media_dir=media_dir,
                limit=3,
                runs_dir=runs_dir,
                seed=2,
            )
        self.assertEqual(len(summary), 3)
        for item in summary:
            mp = item.get("media_path") or ""
            self.assertTrue(mp and " " not in mp)
            if os.name == "nt":
                self.assertTrue(any(dst == mp for _, dst in created))
            else:
                self.assertTrue(Path(mp).is_symlink())


if __name__ == "__main__":
    unittest.main()
