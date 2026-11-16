"""CPU tests for the dynamic H3 parody pipeline (T1 U1-U4 + prompt tweaks, 2026-11-06)."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import build_request as br
from build_request import (
    build_parody_request,
    format_parody_prompt,
    merge_refmod_slots,
    resolve_canvas,
    snap_h3_frames,
    verify_keep_dials,
)
import comm
from resolve import validate_reference_images
import submit_parody_run as spr

TEMPLATE = br.DEFAULT_REFMOD_TEMPLATE
INDEX_BAD = """| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Nora Fixture** | Nora Fixture | Fixture Show | fixture.mp4 | 2026-08-21 |
| **Ivy Fixture** | Ivy Fixture | Fixture Show | fixture.mp4 | 2026-08-21 |
"""
BIO = "long dark glossy layered hair, hazel eyes, high cheekbones, tailored black leather jacket over a crimson silk top"
LINE = "Relax, the coffee here is the only thing scarier than me after midnight."


def _slots(*names):
    out = {}
    for i in range(1, 9):
        out[f"mod_{i}"] = ({"path": f"C:/refmods/{names[i - 1]}.safetensors", "strength": 1.0, "copies": 1}
                           if i - 1 < len(names) else {"path": "(none)", "strength": 1.0, "copies": 1})
    return out


def _res(name="Jennifer Check", actor="Megan Fox", mods=("minimaxh3_meganfox_v1_refmod",), bio=BIO):
    return {"names": [actor], "character": name, "actor": actor,
            "description": f"featuring {actor} (character {name}), {bio}, styled in satirical adult parody tone.",
            "refmod_slots": _slots(*mods)}


def _detail(p):
    return p.split("detailed_description:", 1)[1]


def _summary(p):
    return p.split("summary:")[1].split("detailed_description:")[0]


class TestU1Frames(unittest.TestCase):
    def test_snap_grid_values(self):
        self.assertEqual(snap_h3_frames(5), 124)
        self.assertEqual(snap_h3_frames(8), 192)
        self.assertEqual(snap_h3_frames(10), 243)
        self.assertEqual(snap_h3_frames(15), 243)  # default cap = SINGLE_CLIP_MAX_FRAMES (243 on 16 GB)
        self.assertEqual(snap_h3_frames(15, max_frames=362), 362)
        self.assertEqual(snap_h3_frames(30, max_frames=999), 362)
        self.assertEqual(snap_h3_frames(0.5), 56)
        for s in (2.3, 4.4, 6.1, 9.9, 12.2, 14.7):
            self.assertEqual((snap_h3_frames(s) - 5) % 17, 0)

    def test_single_clip_hard_ceiling(self):
        for bad in (260, 362, 379):
            with self.assertRaises(ValueError, msg=bad):
                build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=bad)
        g, _ = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=243)
        self.assertEqual(g["c0"]["inputs"]["length"], 243)

    def test_ceiling_constant_sane(self):
        self.assertEqual(br.SINGLE_CLIP_MAX_FRAMES, 243)  # t271u: 362f ruled FAIL on 16 GB
        self.assertEqual((br.SINGLE_CLIP_MAX_FRAMES - 5) % 17, 0)


class TestU3Canvas(unittest.TestCase):
    def test_presets_and_size(self):
        self.assertEqual(resolve_canvas(), (768, 1344))
        self.assertEqual(resolve_canvas("16:9"), (1344, 768))
        self.assertEqual(resolve_canvas("widescreen"), (1344, 768))
        self.assertEqual(resolve_canvas("square"), (1024, 1024))
        self.assertEqual(resolve_canvas("4:3"), (1152, 864))
        self.assertEqual(resolve_canvas("3:4"), (864, 1152))
        self.assertEqual(resolve_canvas(size="1280x704"), (1280, 704))
        for bad in ("1000x768", "128x128", "4096x768", "wide"):
            with self.assertRaises(ValueError):
                resolve_canvas(size=bad)
        with self.assertRaises(ValueError):
            resolve_canvas("21:9")

    def test_graph_canvas_and_keep_dials(self):
        g, _ = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=243,
                                    width=1344, height=768)
        self.assertEqual((g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]), (1344, 768))
        self.assertEqual(len(g), 20)
        verify_keep_dials(g)
        tpl = json.loads(Path(TEMPLATE).read_text(encoding="utf-8"))
        for node in ("unet", "s0_sched", "m_shift", "refapply", "ksel"):
            self.assertEqual(g[node]["inputs"], tpl[node]["inputs"], node)
        self.assertEqual(tpl["c0"]["inputs"]["width"], 768)  # template untouched


class TestPromptTweaks(unittest.TestCase):
    def test_no_adult_filler_but_adult_stated(self):
        p = format_parody_prompt(_res(), dialogue=LINE, scene="sits in a neon diner booth, holding a coffee mug")
        self.assertNotIn("Adult cast", p)
        self.assertNotIn("adults-only", p)
        self.assertNotIn("an adult performer, age 28+", p)
        self.assertLessEqual(p.lower().count("adult"), 2)
        self.assertIn("(S1) says in Megan Fox's exact Jennifer Check voice with signature vocal timbre: <d>[English] ", p)
        self.assertIn("<d>[English] Relax, the coffee here is the only thing scarier than me after midnight.</d>", p)
        self.assertNotIn("overall_soundscape:", p)

    def test_600_word_scene_preserved_untruncated(self):
        sent = ("She leans across the chrome-trimmed counter under pink and cyan neon, rain streaking the dark glass "
                "behind her while both five-finger hands wrap a white ceramic diner mug and lift it slowly. ")
        scene = (sent * 25).strip()
        self.assertGreaterEqual(len(scene.split()), 600)
        g, p = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=243,
                                    scene=scene, dialogue=LINE)
        self.assertIn(scene.rstrip("."), _detail(p))
        self.assertEqual(_summary(p).count("She leans across the chrome-trimmed counter"), 1)
        self.assertIn(scene.rstrip("."), g["c0"]["inputs"]["prompt"])
        ok, why = comm.guard_reason(g)
        self.assertTrue(ok, why)

    def test_explicit_summary(self):
        p = format_parody_prompt(_res(), dialogue=LINE, scene="a long scene. With two sentences.",
                                 summary_text="Jennifer holds court at a diner counter.")
        self.assertIn("(S1) Jennifer holds court at a diner counter. Non-speaking characters: none.", p)


class TestU4CameraPronoun(unittest.TestCase):
    def test_default_static_camera(self):
        p = format_parody_prompt(_res(), dialogue=LINE)
        self.assertIn("[static medium shot, eye level, 50mm lens, shallow depth of field]", p)
        self.assertNotIn("Camera locked off", p)

    def test_moving_camera_drops_locked_off(self):
        cam = "cinematic widescreen medium-wide shot from waist up including tabletop, 35mm lens, slow smooth dolly push-in"
        p = format_parody_prompt(_res(), dialogue=LINE, camera=cam, scene="sits at a neon diner counter")
        self.assertIn(f"[{cam}]", p)
        self.assertNotIn("Camera locked off", p)
        p2 = format_parody_prompt(_res(), dialogue=LINE, camera="close-up, 85mm lens")
        self.assertIn("[close-up, 85mm lens]", p2)
        self.assertNotIn("Camera locked off", p2)

    def test_pronouns_and_end_action(self):
        p = format_parody_prompt(_res(), dialogue=LINE, pronoun="he")
        self.assertIn("He holds eye contact, gives a small nod at the end, and stops talking.", p)
        self.assertIn("His mouth movements stop completely", p)
        self.assertNotIn("consistently throughout the entire clip", p)
        t = format_parody_prompt(_res(), dialogue=None, pronoun="they")
        self.assertIn("They do not speak; their lips stay closed", t)
        e = format_parody_prompt(_res(), dialogue=LINE,
                                 end_action="takes a calm sip from the mug and holds a dry deadpan smirk")
        self.assertIn("She takes a calm sip from the mug and holds a dry deadpan smirk. Her mouth movements stop", e)
        self.assertNotIn("small nod", e)
        with self.assertRaises(ValueError):
            format_parody_prompt(_res(), dialogue=LINE, pronoun="it")
        # MA-6 end-action grammar
        smile = format_parody_prompt(_res(), dialogue=LINE, end_action="A knowing smile and a slow wink")
        self.assertIn("She gives a knowing smile and a slow wink.", smile)
        self.assertNotIn("She A knowing", smile)
        holds = format_parody_prompt(_res(), dialogue=LINE, end_action="Holds eye contact with a wry tired smile")
        self.assertIn("She holds eye contact with a wry tired smile.", holds)
        she_dup = format_parody_prompt(_res(), dialogue=LINE, end_action="She holds a wry smile")
        self.assertIn("She holds a wry smile.", she_dup)
        self.assertNotIn("She She ", she_dup)

    def test_two_subjects(self):
        r2 = _res(name="Needy Lesnicki", actor="Amanda Seyfried", mods=("minimaxh3_amandaseyfried_v1_refmod",),
                  bio="wavy honey-blonde hair, wide blue eyes, oversized cardigan")
        both = format_parody_prompt(_res(), dialogue=LINE, resolved2=r2, dialogue2="You said that last week too.")
        self.assertIn("(S1) Jennifer Check - ", both)
        self.assertIn("(S2) Needy Lesnicki - ", both)
        self.assertNotIn("an adult performer, age 28+", both)
        self.assertIn("Non-speaking characters: none.", both)
        self.assertIn("(S2) says in Amanda Seyfried's exact Needy Lesnicki voice with signature vocal timbre: <d>[English] You said that last week too.</d>", both)
        one = format_parody_prompt(_res(), dialogue=LINE, resolved2=r2)
        self.assertIn("Non-speaking characters: (S2).", one)
        self.assertIn("(S2) She does not speak", one)
        g, _ = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", resolved2=r2, dialogue=LINE)
        self.assertEqual(g["refmods"]["inputs"]["mod_1"], "minimaxh3_meganfox_v1_refmod")
        self.assertEqual(g["refmods"]["inputs"]["mod_2"], "minimaxh3_amandaseyfried_v1_refmod")
        self.assertEqual(g["refmods"]["inputs"]["mod_3"], "(none)")

    def test_merge_4_plus_4(self):
        a = _slots(*[f"a{i}" for i in range(6)])
        b = _slots(*[f"b{i}" for i in range(6)])
        m = merge_refmod_slots(a, b)
        stems = [Path(m[f"mod_{i}"]["path"]).stem for i in range(1, 9)]
        self.assertEqual(stems, ["a0", "a1", "a2", "a3", "b0", "b1", "b2", "b3"])
        m2 = merge_refmod_slots(_slots("a0"), b)
        self.assertEqual([Path(m2[f"mod_{i}"]["path"]).stem for i in range(1, 9)][:2], ["a0", "b0"])
        self.assertEqual(Path(m2["mod_7"]["path"]).stem, "b5")


class TestU2Images(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="u2_")
        root = Path(self.tmp.name)
        self.pool = root / "approved_characters"
        (self.pool / "B01").mkdir(parents=True)
        self.img = self.pool / "B01" / "diner_ref.png"
        self.img.write_bytes(b"\x89PNG fixture")
        self.outside = root / "elsewhere.png"
        self.outside.write_bytes(b"x")
        (self.pool / "sydney_misc").mkdir()
        (self.pool / "sydney_misc" / "a.png").write_bytes(b"x")
        self.input = root / "comfy_input"

    def tearDown(self):
        self.tmp.cleanup()

    def test_gate(self):
        pools = (self.pool,)
        self.assertEqual(validate_reference_images([str(self.img)], pools=pools), [str(self.img.resolve())])
        self.assertEqual(validate_reference_images(["B01/diner_ref.png"], pools=pools), [str(self.img.resolve())])
        # Sydney path block dropped (Derrick t2084u): an in-pool sydney path is accepted like any other.
        self.assertEqual(validate_reference_images(["sydney_misc/a.png"], pools=pools),
                         [str((self.pool / "sydney_misc" / "a.png").resolve())])
        # Pool containment dropped (Derrick t2086u/t2087u): an existing outside path is accepted.
        self.assertEqual(validate_reference_images([str(self.outside)], pools=pools), [str(self.outside.resolve())])
        for bad in ("/nonexistent/x.png", "B01/missing.png"):
            with self.assertRaises(ValueError, msg=bad):
                validate_reference_images([bad], pools=pools)
        with self.assertRaises(ValueError):
            validate_reference_images([str(self.img)] * 5, pools=pools)

    def test_wired_graph_and_prompt(self):
        paths = validate_reference_images([str(self.img)], pools=(self.pool,))
        staged = br.stage_reference_images(paths, self.input)
        self.assertTrue(staged[0].startswith("community/parody_ref_"))
        self.assertTrue((self.input / staged[0].split("/", 1)[1]).is_file())
        g, p = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", images=staged, dialogue=LINE)
        self.assertEqual(g["img_1"]["class_type"], "LoadImage")
        self.assertEqual(g["img_1"]["inputs"]["image"], staged[0])
        self.assertEqual(g["add_guide"]["class_type"], "MiniMaxH3AddGuide")
        self.assertEqual(g["add_guide"]["inputs"], {"positive": ["c0", 0], "latent": ["c0", 1], "vae": ["vvae", 0],
                                                    "image": ["img_1", 0], "frame_idx": 0})
        self.assertEqual(g["refapply"]["inputs"]["conditioning"], ["add_guide", 0])
        self.assertEqual(g["s0_guide"]["inputs"]["conditioning"], ["refapply", 0])
        self.assertEqual(g["s0_samp"]["inputs"]["latent_image"], ["c0", 1])
        self.assertFalse([k for k in g["c0"]["inputs"] if k.startswith("ref_images")])
        self.assertEqual(len(g), 22)
        self.assertNotIn("<Picture", p)
        self.assertNotIn("[reference generation]", p)
        self.assertNotIn("retention_analysis", p)
        self.assertNotIn("overall_soundscape:", p)
        g0, p0 = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", dialogue=LINE)
        self.assertEqual(p, p0)  # --image never changes the text Qwen sees
        with self.assertRaises(ValueError):
            build_parody_request(_res(), seed=51083601, prefix="community/t/clip", images=staged * 2, dialogue=LINE)
        ok, why = comm.guard_reason(g)
        self.assertTrue(ok, why)

    def test_no_images_zero_picture_tags(self):
        g, p = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", dialogue=LINE)
        self.assertFalse([n for n in g.values() if n.get("class_type") == "LoadImage"])
        self.assertNotIn("<Picture", p)
        self.assertNotIn("retention_analysis", p)
        self.assertNotIn("ref_images.ref_image_1", g["c0"]["inputs"])
        self.assertFalse([n for n in g.values() if n.get("class_type") == "MiniMaxH3AddGuide"])
        self.assertEqual(len(g), 20)
        self.assertEqual(g["refapply"]["inputs"]["conditioning"], ["c0", 0])


class TestSubmitDynamic(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dyn_")
        self.root = Path(self.tmp.name)
        self.index = self.root / "index"
        self.index.mkdir()
        (self.index / "INDEX_BAD.md").write_text(INDEX_BAD, encoding="utf-8")
        self.refmods = self.root / "refmods"
        self.refmods.mkdir()
        (self.refmods / "minimaxh3_norafixture_v1_refmod.safetensors").write_bytes(b"f")
        (self.refmods / "minimaxh3_ivyfixture_v1_refmod.safetensors").write_bytes(b"f")
        self.run_dir = self.root / "run"

    def tearDown(self):
        self.tmp.cleanup()

    def _patches(self):
        return (
            mock.patch.object(spr, "INDEX_DIR", self.index),
            mock.patch.object(spr, "REFMODS_DIR", self.refmods),
            mock.patch.object(spr, "ALIASES_PATH", self.root / "no-aliases.json"),
            mock.patch.object(spr.subprocess, "run"),
        )

    def _submit(self, **kw):
        p1, p2, p3, p4 = self._patches()
        with p1, p2, p3, p4 as run:
            res = spr.submit_parody_job(name="Nora Fixture", actor="Nora Fixture", description=BIO,
                                        run_dir_override=self.run_dir, dry_run=True, **kw)
            run.assert_not_called()
        return res

    def test_single_10s_widescreen(self):
        res = self._submit(seconds=10, aspect="16:9", dialogue=LINE,
                           camera="35mm lens, slow smooth dolly push-in across the counter",
                           scene="sits at a 2 AM neon diner counter, both hands lifting a ceramic mug")
        self.assertEqual(res["frames"], [243])
        self.assertEqual(res["size"], "1344x768")
        g = json.loads((self.run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
        self.assertEqual(g["c0"]["inputs"]["length"], 243)
        self.assertEqual((g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]), (1344, 768))
        order = json.loads((self.run_dir / "_render_order.json").read_text(encoding="utf-8"))
        self.assertNotIn("cell_contract", order)
        self.assertEqual([j["tag"] for j in order["order"]], ["clip"])

    def test_multi_beat_shared_anchor_cells(self):
        """2+ --beat args build ONE native latent-tail continuation clip, not shared-anchor cells.

        The stitched shared-anchor cell path stays covered by test_long_seconds_auto_split.
        """
        res = self._submit(aspect="16:9", beats=["sits at the counter, both hands on a mug",
                                                 "leans back in the booth holding the mug"],
                           beat_dialogues=["First line here for the opener.", "Second line closes it out."],
                           beat_seconds=[6, 8])
        # the deliverable's frame count is the continuation chain's cumulative total, derived from the plan
        plan = br._layout_chain([br.snap_h3_frames(6, max_frames=br.SINGLE_CLIP_MAX_FRAMES),
                                 br.snap_h3_frames(8, max_frames=br.SINGLE_CLIP_MAX_FRAMES)])
        lay = plan[-1]["layout"]
        self.assertTrue(plan[1]["is_continuation"])
        self.assertLessEqual(lay["window_frames"], br.CONTINUATION_WINDOW_MAX_FRAMES)
        self.assertEqual(res["tags"], ["clip"])
        self.assertEqual(res["frames"], [lay["total_frames"]])
        self.assertEqual(res["total_frames"], lay["total_frames"])
        self.assertGreater(lay["total_frames"], lay["base_frames"])  # beat 2 extends, never restarts
        order = json.loads((self.run_dir / "_render_order.json").read_text(encoding="utf-8"))
        self.assertNotIn("cell_contract", order)
        self.assertEqual([j["tag"] for j in order["order"]], ["clip"])
        g = json.loads((self.run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
        self.assertEqual(json.loads((self.run_dir / "request.api.json").read_text(encoding="utf-8")), g)
        self.assertEqual(g["c0"]["inputs"]["length"], lay["base_frames"])  # beat 1 keeps its own length
        self.assertEqual({g[k]["class_type"] for k in ("c2_gen", "c2_tail", "c2_append")},
                         {"MiniMaxH3GuidedContinuationWindow", "MiniMaxH3LatentTailGuide", "MiniMaxH3AppendContinuation"})
        self.assertEqual(g["c2_gen"]["inputs"], {"previous_av_latent": ["s0_samp", 0],
                                                 "overlap_frames": lay["overlap_frames"],
                                                 "extension_frames": lay["extension_frames"]})
        self.assertEqual(g["s0_sep"]["inputs"]["av_latent"], ["c2_append", 0])  # one joined latent is decoded
        for key in ("c0", "c2"):
            self.assertEqual((g[key]["inputs"]["width"], g[key]["inputs"]["height"]), (1344, 768))
        self.assertEqual(g["noise"]["inputs"]["noise_seed"], 51083601)
        self.assertEqual(g["save"]["inputs"]["filename_prefix"], f"community/{self.run_dir.name}/clip")
        ok, why = comm.guard_reason(g)
        self.assertTrue(ok, why)
        self.assertIn("First line here for the opener.", g["c0"]["inputs"]["prompt"])
        self.assertIn("Second line closes it out.", g["c2"]["inputs"]["prompt"])
        self.assertIn("The shot continues from the last seen moment", g["c2"]["inputs"]["prompt"])

    def test_long_seconds_without_beats_is_refused(self):
        # Step 2/3 (2026-11-09): a long ask must not clone one scene into N beats.
        with self.assertRaises(ValueError):
            self._submit(seconds=15, scene="sits at the counter holding a mug", dialogue=LINE)
        self.assertFalse(self.run_dir.exists())
        res = self._submit(seconds=10, scene="sits at the counter holding a mug", dialogue=LINE)
        self.assertEqual(res["frames"], [243])
        self.assertTrue(all((f - 5) % 17 == 0 and f <= 243 for f in res["frames"]))

    def test_frames_over_ceiling_fails_before_run_dir(self):
        with self.assertRaises(ValueError):
            self._submit(frames=260)
        self.assertFalse(self.run_dir.exists())

    def test_second_subject_requires_description(self):
        with self.assertRaises(ValueError):
            self._submit(name2="Ivy Fixture")
        res = self._submit(name2="Ivy Fixture", actor2="Ivy Fixture", description2="short red bob, green eyes, denim jacket",
                           dialogue=LINE, dialogue2="Same table, same bad coffee, same us.")
        g = json.loads((self.run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
        self.assertEqual(g["refmods"]["inputs"]["mod_2"], "minimaxh3_ivyfixture_v1_refmod")
        self.assertIn("(S2) Ivy Fixture", g["c0"]["inputs"]["prompt"])


class TestWaitFinalize(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="wait_")
        self.run = Path(self.tmp.name) / "parody_x_1"
        self.run.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_wait_for_new_batch_line(self):
        log = self.run / "_render_queue.log"
        log.write_text("2026 BATCH closed rc=7 reason=old\n", encoding="utf-8")
        since = spr._batch_count(self.run)
        log.write_text(log.read_text() + "2026 BATCH closed rc=0 reason=all done\n", encoding="utf-8")
        self.assertEqual(spr.wait_for_batch(self.run, since, timeout=2, poll=0.01), 0)
        with self.assertRaises(TimeoutError):
            spr.wait_for_batch(self.run, since + 1, timeout=0.05, poll=0.01)

    def test_finalize_single_and_qnap(self):
        (self.run / "clip").mkdir()
        (self.run / "clip" / "clip.mp4").write_bytes(b"mp4")
        out = spr.finalize_clip(self.run, ["clip"], "python")
        self.assertEqual(Path(out["final_mp4"]).read_bytes(), b"mp4")
        with mock.patch.object(spr.subprocess, "run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="Copied", stderr="")
            q = spr.qnap_put(Path(out["final_mp4"]), self.run.name, "python")
        self.assertEqual(q["qnap_path"], "pi-drop/parody_x_1.mp4")
        self.assertIn("put", run.call_args[0][0])

    def test_finalize_cells_stitch(self):
        for t in ("c01_s51083601", "c02_s51083602"):
            (self.run / t).mkdir()
            (self.run / t / f"{t}.mp4").write_bytes(b"cell")

        def fake_run(cmd, **kw):
            (self.run / "_stitch").mkdir(exist_ok=True)
            (self.run / "_stitch" / "stitched.mp4").write_bytes(b"film")
            return mock.Mock(returncode=0, stdout="PROOF film ok\nSTITCH OK cells=2", stderr="")

        with mock.patch.object(spr.subprocess, "run", side_effect=fake_run) as run:
            out = spr.finalize_clip(self.run, ["c01_s51083601", "c02_s51083602"], "python")
        self.assertTrue(out["stitched"])
        self.assertEqual((self.run / "clip.mp4").read_bytes(), b"film")
        self.assertIn("--name", run.call_args[0][0])
        self.assertIn("stitched", run.call_args[0][0])

    def test_finalize_prefers_upscaled_cell_mp4_not_raw(self):
        """MA-13: after RTX 2x, finalize stitches <cell>/<cell>.mp4 (1536x..) not <cell>_raw.mp4."""
        t1, t2 = "c01_s51083610", "c02_s51083611"
        for t in (t1, t2):
            d = self.run / t
            d.mkdir(parents=True)
            (d / f"{t}_raw.mp4").write_bytes(b"RAW768")
            (d / f"{t}.mp4").write_bytes(b"UPSCALED1536")
        def fake_run(cmd, **kw):
            # stitcher must receive cell dirs that already hold the upscaled mp4 names
            self.assertTrue((self.run / t1 / f"{t1}.mp4").is_file())
            self.assertEqual((self.run / t1 / f"{t1}.mp4").read_bytes(), b"UPSCALED1536")
            self.assertEqual((self.run / t1 / f"{t1}_raw.mp4").read_bytes(), b"RAW768")
            (self.run / "_stitch").mkdir(exist_ok=True)
            (self.run / "_stitch" / "stitched.mp4").write_bytes(b"FILM1536")
            return mock.Mock(returncode=0, stdout="PROOF film ok video=1536x2688@24/1\nSTITCH OK cells=2", stderr="")
        with mock.patch("subprocess.run", side_effect=fake_run) as run:
            out = spr.finalize_clip(self.run, [t1, t2], "python")
        self.assertTrue(out["stitched"])
        self.assertEqual(Path(out["final_mp4"]).read_bytes(), b"FILM1536")
        self.assertIn("take_chain_stitch.py", " ".join(run.call_args[0][0]))
        # raw preserved beside upscaled
        self.assertTrue((self.run / t1 / f"{t1}_raw.mp4").is_file())
        self.assertTrue((self.run / t2 / f"{t2}_raw.mp4").is_file())

    def test_finalize_missing_cell_refuses(self):
        (self.run / "c01_s51083601").mkdir()
        (self.run / "c01_s51083601" / "c01_s51083601.mp4").write_bytes(b"cell")
        with mock.patch.object(spr, "COMFY_OUT_COMMUNITY", Path(self.tmp.name) / "none"):
            with self.assertRaises(FileNotFoundError):
                spr.finalize_clip(self.run, ["c01_s51083601", "c02_s51083602"], "python")


class TestContinuationFiveItems(unittest.TestCase):
    """Focused tests for the 5 native continuation items in 2026-11-09 brief."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cont_five_")
        self.run_dir = Path(self.tmp.name) / "run_test"

    def tearDown(self):
        self.tmp.cleanup()

    def test_item1_ambience_option(self):
        # 1. Default ambience when omitted or None
        p_def = format_parody_prompt(_res(), dialogue=LINE)
        self.assertIn("Quiet room ambience, soft natural room tone, with the single close-micd human voice in the foreground.", p_def)

        # 2. Custom ambience in single voice
        custom_amb = "quiet night room tone, distant gentle rain"
        p_custom = format_parody_prompt(_res(), dialogue=LINE, ambience=custom_amb)
        self.assertIn("Quiet night room tone, distant gentle rain, with the single close-micd human voice in the foreground.", p_custom)

        # 3. Custom ambience with 2 voices
        p_two = format_parody_prompt(_res(), dialogue=LINE, resolved2=_res("Ivy Fixture", "Ivy Fixture"),
                                     dialogue2="Coffee is ready.", ambience="soft cafe ambience, subtle espresso steam")
        self.assertIn("Soft cafe ambience, subtle espresso steam, with two close-micd human voices in the foreground, one speaker at a time.", p_two)

        # 4. Custom ambience with silent clip
        p_silent = format_parody_prompt(_res(), dialogue=None, ambience="deep space hum, airlock circulation")
        self.assertIn("Deep space hum, airlock circulation, with no spoken voice.", p_silent)

        # 5. build_parody_request carries ambience through
        _, prompt = build_parody_request(_res(), seed=51083601, prefix="community/amb_test/clip", frames=124,
                                        dialogue=LINE, ambience="crackling fireplace, quiet parlor")
        self.assertIn("Crackling fireplace, quiet parlor", prompt)

    def test_item2_refuse_long_seconds_without_two_plus_beats(self):
        # Refuses > 243 frames (~10.125s) with 0 beats
        with self.assertRaises(ValueError) as ctx:
            spr.submit_parody_job(name="Megan Fox", description=BIO, seconds=15.0, scene="sitting calmly",
                                  run_dir_override=self.run_dir, dry_run=True)
        self.assertIn("pass 2 or more --beat scenes", str(ctx.exception))
        self.assertFalse(self.run_dir.exists())

        # Refuses > 243 frames with only 1 beat
        with self.assertRaises(ValueError) as ctx2:
            spr.submit_parody_job(name="Megan Fox", description=BIO, seconds=12.0, beats=["lone beat"],
                                  run_dir_override=self.run_dir, dry_run=True)
        self.assertIn("pass 2 or more --beat scenes", str(ctx2.exception))
        self.assertFalse(self.run_dir.exists())

        # Allows <= 243 frames (~10.125s) without beats as a single shot
        res_ok = spr.submit_parody_job(name="Megan Fox", description=BIO, seconds=10.0, scene="sitting calmly",
                                       run_dir_override=self.run_dir, dry_run=True)
        self.assertEqual(res_ok["frames"], [243])
        self.assertEqual(res_ok["tags"], ["clip"])

        # Allows > 243 frames with 2+ beats as native continuation
        run_2b = Path(self.tmp.name) / "run_2b"
        res_2b = spr.submit_parody_job(name="Megan Fox", description=BIO, seconds=15.0,
                                       beats=["sitting calmly holding cup", "stands up smoothly"],
                                       run_dir_override=run_2b, dry_run=True)
        self.assertEqual(res_2b["tags"], ["clip"])
        self.assertGreater(res_2b["total_frames"], 243)

    def test_item3_native_continuation_node_wiring_and_chain(self):
        beats = [
            {"scene": "sits at the mahogany counter, both hands on a cup", "frames": 192},
            {"scene": "stands up slowly, resting right hand on the edge", "frames": 192},
            {"scene": "walks toward the tall window, turning slightly", "frames": 192},
        ]
        g, p_all, plan = br.build_continuation_request(_res(), seed=51083601, prefix="community/cont3/clip",
                                                       beats=beats)
        self.assertEqual(plan["clip_count"], 3)
        self.assertEqual(len(plan["beats"]), 3)
        self.assertEqual(br.CONTINUATION_OVERLAP_FRAMES, 22)
        self.assertEqual(br.CONTINUATION_WINDOW_MAX_FRAMES, 243)

        # Check Beat 2 wiring
        # previous_av_latent = ["s0_samp", 0]
        self.assertEqual(g["c2_gen"]["class_type"], "MiniMaxH3GuidedContinuationWindow")
        self.assertEqual(g["c2_gen"]["inputs"]["previous_av_latent"], ["s0_samp", 0])
        self.assertEqual(g["c2_gen"]["inputs"]["overlap_frames"], 39)  # 22 off a 192f tail is audio-misaligned (c2_samp)
        ext2 = g["c2_gen"]["inputs"]["extension_frames"]
        self.assertEqual(ext2 % 17, 0)
        self.assertLessEqual(39 + ext2, 243)

        self.assertEqual(g["c2_tail"]["class_type"], "MiniMaxH3LatentTailGuide")
        self.assertEqual(g["c2_tail"]["inputs"]["previous_av_latent"], ["s0_samp", 0])
        self.assertEqual(g["c2_tail"]["inputs"]["target_av_latent"], ["c2_gen", 0])
        self.assertEqual(g["c2_tail"]["inputs"]["positive"], ["c2_refapply", 0])

        self.assertEqual(g["c2_refapply"]["class_type"], "MiniMaxH3RefModApply")
        self.assertEqual(g["c2_refapply"]["inputs"]["conditioning"], ["c2", 0])
        self.assertEqual(g["c2_refapply"]["inputs"]["mods"], ["refmods", 0])

        self.assertEqual(g["c2_samp"]["class_type"], "SamplerCustomAdvanced")
        self.assertEqual(g["c2_samp"]["inputs"]["latent_image"], ["c2_gen", 0])
        self.assertEqual(g["c2_samp"]["inputs"]["sigmas"], ["c2_sched", 0])

        self.assertEqual(g["c2_append"]["class_type"], "MiniMaxH3AppendContinuation")
        self.assertEqual(g["c2_append"]["inputs"]["previous_av_latent"], ["s0_samp", 0])
        self.assertEqual(g["c2_append"]["inputs"]["sampled_window"], ["c2_samp", 0])

        # Check Beat 3 wiring
        # previous_av_latent = ["c2_append", 0]
        self.assertEqual(g["c3_gen"]["class_type"], "MiniMaxH3GuidedContinuationWindow")
        self.assertEqual(g["c3_gen"]["inputs"]["previous_av_latent"], ["c2_append", 0])
        self.assertEqual(g["c3_gen"]["inputs"]["overlap_frames"], 22)

        self.assertEqual(g["c3_tail"]["class_type"], "MiniMaxH3LatentTailGuide")
        self.assertEqual(g["c3_tail"]["inputs"]["previous_av_latent"], ["c2_append", 0])
        self.assertEqual(g["c3_tail"]["inputs"]["positive"], ["c3_refapply", 0])

        self.assertEqual(g["c3_refapply"]["class_type"], "MiniMaxH3RefModApply")
        self.assertEqual(g["c3_refapply"]["inputs"]["conditioning"], ["c3", 0])
        self.assertEqual(g["c3_refapply"]["inputs"]["mods"], ["refmods", 0])

        self.assertEqual(g["c3_append"]["class_type"], "MiniMaxH3AppendContinuation")
        self.assertEqual(g["c3_append"]["inputs"]["previous_av_latent"], ["c2_append", 0])
        self.assertEqual(g["c3_append"]["inputs"]["sampled_window"], ["c3_samp", 0])

        # Rewired s0_sep points to the last append node
        self.assertEqual(g["s0_sep"]["inputs"]["av_latent"], ["c3_append", 0])

        # One window per requested beat: exactly c0, c2, c3
        c_nodes = {k for k in g if k.startswith("c") and k[1:].isdigit()}
        self.assertEqual(c_nodes, {"c0", "c2", "c3"})

        # RefMod on every beat
        refapplies = {k for k in g if "refapply" in k}
        self.assertEqual(refapplies, {"refapply", "c2_refapply", "c3_refapply"})

        # No AddGuide or LoadImage on continuation beats
        self.assertFalse(any(n.get("class_type") in ("MiniMaxH3AddGuide", "LoadImage") for n in g.values()))

    def test_item3_addguide_start_photo_beat1_only(self):
        beats = [
            {"scene": "sits at the counter", "frames": 192, "images": ["community/megan_ref.jpg"]},
            {"scene": "stands up slowly", "frames": 192},
        ]
        g, _, _ = br.build_continuation_request(_res(), seed=51083601, prefix="community/addguide/clip",
                                                beats=beats)
        # beat 1 has AddGuide
        self.assertIn("add_guide", g)
        self.assertEqual(g["add_guide"]["class_type"], "MiniMaxH3AddGuide")
        self.assertIn("img_1", g)

        # Continuation beat must reject start images
        with self.assertRaises(ValueError):
            br.build_parody_request(_res(), seed=51083601, prefix="community/test", continuation=True,
                                    images=["community/invalid.jpg"])

    def test_item4_airlock_wording(self):
        beats = [
            {"scene": "sits at the counter, both hands on a mug", "frames": 192},
            {"scene": "leans back in the booth holding the mug", "frames": 192},
        ]
        g, p_all, _ = br.build_continuation_request(_res(), seed=51083601, prefix="community/airlock/clip",
                                                    beats=beats, pronoun="she")
        p_b1 = g["c0"]["inputs"]["prompt"]
        p_b2 = g["c2"]["inputs"]["prompt"]

        self.assertNotIn("The shot continues from the last seen moment", p_b1)
        self.assertIn("The shot continues from the last seen moment", p_b2)
        # dynsafe brief item 1: beat 2 inherits beat 1's actual closing pose, never a hardcoded standing pose
        self.assertIn("the same framing, the same pose the previous beat ended on (she sits at the counter, both hands on a mug)", p_b2)
        self.assertNotIn("standing pose", p_b2)
        self.assertIn("natural micro-motion", p_b2)
        self.assertIn("The camera does not change angle and the shot never resets to a starting photo.", p_b2)
        self.assertIn("and she is still in the same place", p_b2)
        self.assertIn("She keeps her exact voice", p_b2)

    def test_item5_submit_parody_run_native_continuation_graph(self):
        res = spr.submit_parody_job(
            name="Megan Fox", description=BIO,
            beats=["sits at the counter, both hands on a mug", "stands up slowly beside the stool"],
            beat_dialogues=["First line.", "Second line."],
            beat_seconds=[6, 8],
            run_dir_override=self.run_dir,
            dry_run=True,
        )
        self.assertEqual(res["tags"], ["clip"])
        self.assertNotIn("c01_s51083601", res["tags"])
        order = json.loads((self.run_dir / "_render_order.json").read_text(encoding="utf-8"))
        self.assertNotIn("cell_contract", order)
        self.assertEqual([j["tag"] for j in order["order"]], ["clip"])

        g = json.loads((self.run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
        self.assertEqual(g["c2_gen"]["inputs"]["previous_av_latent"], ["s0_samp", 0])
        self.assertEqual(g["s0_sep"]["inputs"]["av_latent"], ["c2_append", 0])

    def test_plan_continuation_chain_removed(self):
        self.assertFalse(hasattr(br, "plan_continuation_chain"))

    def test_continuation_layout_defaults_match_verified_379_layout(self):
        lay = br.continuation_layout()
        self.assertEqual(lay["base_frames"], 192)
        self.assertEqual(lay["extension_frames"], 187)
        # c2-samp fix: the asked 22-frame overlap stays, but only when its window audio equals temporal_shape(window).
        # Off a 192-frame tail 22/187 allocates 349 tokens for a 209f window whose official length is 348, so the
        # layout steps to the nearest legal 17k + 5 overlap that matches (39, window 226). The 379 visible frames, the
        # window ceiling and the extension are untouched.
        self.assertEqual(lay["requested_overlap_frames"], 22)
        self.assertEqual(lay["overlap_frames"], 39)
        self.assertEqual(lay["window_frames"], 226)
        self.assertEqual(lay["total_frames"], 379)
        self.assertLessEqual(lay["window_frames"], br.CONTINUATION_WINDOW_MAX_FRAMES)
        self.assertEqual(lay["window_audio_t"], lay["window_audio_official_t"])
        self.assertFalse(br.continuation_window_audio_is_aligned(192, 22, 187))
        self.assertTrue(br.continuation_window_audio_is_aligned(192, 39, 187))
        self.assertTrue(br.continuation_window_audio_is_aligned(124, 22, 187))  # the 311f pack keeps its 22

    def test_two_beats_omitted_seconds_uses_continuation_defaults(self):
        with mock.patch("submit_parody_run.plan_c2v_chain") as mock_c2v:
            res = spr.submit_parody_job(
                name="Megan Fox", description=BIO,
                beats=["sits at the counter, both hands on a mug", "stands up slowly beside the stool"],
                run_dir_override=self.run_dir,
                dry_run=True,
            )
            mock_c2v.assert_not_called()
        self.assertEqual(res["tags"], ["clip"])
        self.assertEqual(res["frames"], [379])
        self.assertEqual(res["total_frames"], 379)
        g = json.loads((self.run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
        self.assertEqual(g["c0"]["inputs"]["length"], 192)
        self.assertEqual(g["c2_gen"]["inputs"]["extension_frames"], 187)
        self.assertEqual(g["c2_gen"]["inputs"]["overlap_frames"], 39)  # audio-aligned for a 192f tail, visible 379 kept
        self.assertLessEqual(39 + 187, br.CONTINUATION_WINDOW_MAX_FRAMES)

    def test_single_shot_byte_identical_and_locked_dials(self):
        g, p = build_parody_request(_res(), seed=51083601, prefix="community/test/clip", frames=124)
        verify_keep_dials(g)

        import hashlib
        s = json.dumps(g, indent=2, sort_keys=True)
        g_hash = hashlib.sha256(s.encode("utf-8")).hexdigest()
        p_hash = hashlib.sha256(p.encode("utf-8")).hexdigest()
        self.assertEqual(g_hash, "1778d290d18c38c9767080d7de4181bb8775d3917cbadffe4f2f8b346ccc4ce3")
        self.assertEqual(p_hash, "9d36f0c68585c717bf1ec95797402a17b144c5ef6975d93746f5726f81703971")

        # Verify locked dials
        c0 = g["c0"]["inputs"]
        self.assertEqual((c0["width"], c0["height"]), (768, 1344))
        self.assertIn("10Eros_Max_h3_8stepTURBO_beta7_int8HQ", json.dumps(g["unet"]["inputs"]))
        self.assertEqual(g["s0_sched"]["inputs"]["steps"], 8)
        self.assertEqual(g["s0_sched"]["inputs"]["scheduler"], "simple")
        self.assertEqual(g["c0"]["class_type"], "MiniMaxH3ReferenceToVideo")
        self.assertEqual(g["refapply"]["class_type"], "MiniMaxH3RefModApply")


class TestPlainDiegeticSoundTail(unittest.TestCase):
    def test_no_overall_soundscape_header_and_trailing_plain_sound(self):
        p = format_parody_prompt(_res(), dialogue=LINE, scene="sits in a neon diner booth, holding a coffee mug")
        self.assertNotIn("overall_soundscape", p.lower())
        self.assertNotIn("no_dubs:", p)
        # spoken clip: voice mentioned in the plain tail, after speech / detailed_description
        tail = p.strip().splitlines()[-1].strip()
        self.assertFalse(tail.endswith("No music, no songs, no score, no soundtrack."))
        self.assertNotIn("No music, no songs, no score, no soundtrack.", tail)
        self.assertIn("Quiet room ambience, soft natural room tone, with the single close-micd human voice in the foreground.", tail)
        self.assertNotIn("No singing, no rapping, no songs, no music, no narration, no voice-over.", p)
        self.assertGreaterEqual(tail.count("."), 2)
        self.assertLessEqual(tail.count("."), 4)
        silent = format_parody_prompt(_res(), dialogue=None, scene="sits in a neon diner booth, holding a coffee mug")
        self.assertNotIn("overall_soundscape", silent.lower())
        stail = silent.strip().splitlines()[-1].strip()
        self.assertIn("Quiet room ambience, soft natural room tone, with no spoken voice.", stail)
        self.assertNotIn("No music, no songs, no score, no soundtrack.", stail)
        custom = format_parody_prompt(_res(), dialogue=LINE, ambience="soft leather and low neon hum")
        self.assertIn("Soft leather and low neon hum, with the single close-micd human voice in the foreground.", custom)



class TestDialogueTimbreOutsideD(unittest.TestCase):
    def test_voice_and_timbre_outside_d_tags(self):
        p = format_parody_prompt(_res(), dialogue=LINE, scene="sits in a neon diner booth, holding a coffee mug")
        import re
        insides = re.findall(r"<d>(.*?)</d>", p, flags=re.DOTALL)
        self.assertTrue(insides)
        for inner in insides:
            self.assertTrue(inner.startswith("[English] "), inner)
            low = inner.lower()
            for banned in ("timbre", "voice", "using ", "says in"):
                self.assertNotIn(banned, low, inner)
        pre = p.split("<d>", 1)[0]
        self.assertIn("says in Megan Fox's exact Jennifer Check voice with signature vocal timbre:", pre)
        self.assertIn("<d>[English] Relax, the coffee here is the only thing scarier than me after midnight.</d>", p)
        r2 = _res(name="Needy Lesnicki", actor="Amanda Seyfried", mods=("minimaxh3_amandaseyfried_v1_refmod",),
                  bio="wavy honey-blonde hair, wide blue eyes, oversized cardigan")
        both = format_parody_prompt(_res(), dialogue=LINE, resolved2=r2, dialogue2="You said that last week too.")
        insides2 = re.findall(r"<d>(.*?)</d>", both, flags=re.DOTALL)
        self.assertEqual(len(insides2), 2)
        for inner in insides2:
            self.assertTrue(inner.startswith("[English] "), inner)
            self.assertNotIn("timbre", inner.lower())
            self.assertNotIn("voice", inner.lower())



class TestVoiceQualityCue(unittest.TestCase):
    def test_cassie_voice_description_outside_d_and_no_repeated_uses_line(self):
        cassie = _res(name="Cassie Howard", actor="Sydney Sweeney",
                      mods=("minimaxh3_sydneysweeney_v1_refmod",),
                      bio="long centre-parted blonde hair, blue eyes, tanned skin")
        p = format_parody_prompt(cassie, dialogue=LINE, scene="sits in a neon diner booth, holding a coffee mug")
        pre = p.split("<d>", 1)[0]
        self.assertIn(
            "(S1) says in Sydney Sweeney's exact Cassie Howard voice with signature vocal timbre, "
            "a low, soft, breathy voice with light vocal fry, unhurried:",
            pre,
        )
        import re
        insides = re.findall(r"<d>(.*?)</d>", p, flags=re.DOTALL)
        self.assertTrue(insides)
        for inner in insides:
            self.assertTrue(inner.startswith("[English] "), inner)
            self.assertEqual(inner, f"[English] {LINE}")
            low = inner.lower()
            for banned in ("timbre", "voice", "fry", "breathy"):
                self.assertNotIn(banned, low, inner)
        self.assertNotIn("consistently throughout the entire clip", p)
        unknown = format_parody_prompt(_res(), dialogue=LINE)
        self.assertIn(
            "(S1) says in Megan Fox's exact Jennifer Check voice with signature vocal timbre: <d>[English] ",
            unknown,
        )
        self.assertNotIn("a low, soft, breathy voice", unknown)
        self.assertNotIn("contralto", unknown)
        self.assertNotIn("consistently throughout the entire clip", unknown)





class TestApprovedCamVoiceMusic(unittest.TestCase):
    """Camera header derive, OC voice cue, and music-negative placement (2026-11-10)."""

    def test_holds_sentence_derives_header_instead_of_eye_level_default(self):
        scene = (
            "The camera holds a static medium-wide shot from a tripod at hip height on a 50mm lens, "
            "holding her face and the seated man's face in the same frame. She stands at the right edge of the seat."
        )
        p = format_parody_prompt(_res(), dialogue=LINE, scene=scene)
        self.assertIn("[static medium-wide shot, hip height, 50mm lens, shallow depth of field]", p)
        self.assertNotIn("[static medium shot, eye level, 50mm lens, shallow depth of field]", p)
        self.assertNotIn("Camera locked off", p)

    def test_explicit_camera_arg_not_overwritten_by_holds_sentence(self):
        scene = (
            "The camera holds a static medium-wide shot from a tripod at hip height on a 50mm lens, "
            "holding her face and the seated man's face in the same frame."
        )
        cam = "close-up, 85mm lens"
        p = format_parody_prompt(_res(), dialogue=LINE, scene=scene, camera=cam)
        self.assertIn("[close-up, 85mm lens]", p)
        self.assertNotIn("[static medium-wide shot, hip height, 50mm lens, shallow depth of field]", p)

    def test_oc_description_voice_cue_on_says_line(self):
        oc = {
            "names": ["Pool Blonde"],
            "character": "Pool Blonde",
            "actor": "",
            "description": (
                "featuring oc poolblonde (character Pool Blonde), an adult woman aged 28, "
                "an original character with an invented face, voice and body, her own signature vocal timbre, "
                "a low, dry, unhurried alto with a slight rasp, wearing a jewelled choker, styled in club tone."
            ),
            "refmod_slots": _slots("minimaxh3_oc_poolblonde_v1_refmod"),
        }
        p = format_parody_prompt(oc, dialogue=LINE, scene="stands at the seat edge")
        pre = p.split("<d>", 1)[0]
        self.assertIn(
            "says in Pool Blonde's exact voice with signature vocal timbre, "
            "a low, dry, unhurried alto with a slight rasp:",
            pre,
        )

    def test_voice_quality_field_wins_over_description(self):
        r = _res()
        r["voice_quality"] = "a dry mid alto"
        p = format_parody_prompt(r, dialogue=LINE)
        pre = p.split("<d>", 1)[0]
        self.assertIn("signature vocal timbre, a dry mid alto:", pre)
        self.assertNotIn("a low, soft, breathy voice", pre)


class TestArgonLowMultiStillAndLeadIn(unittest.TestCase):
    """argon-low Section C (2026-11-11): D dynamic lead-in, A Beat-1 AddGuide chain, B continuation AddGuide, C new-shot."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="argon_c_")
        self.root = Path(self.tmp.name)
        self.pool = self.root / "approved_characters"
        (self.pool / "B01").mkdir(parents=True)
        self.img1 = self.pool / "B01" / "start.png"
        self.img2 = self.pool / "B01" / "mid.png"
        self.img3 = self.pool / "B01" / "cut.png"
        for i, p in enumerate((self.img1, self.img2, self.img3), start=1):
            p.write_bytes(f"\x89PNG fixture {i}".encode())
        self.input_dir = self.root / "comfy_input"
        self.index = self.root / "index"
        self.index.mkdir()
        (self.index / "INDEX_BAD.md").write_text(INDEX_BAD, encoding="utf-8")
        self.refmods = self.root / "refmods"
        self.refmods.mkdir()
        (self.refmods / "minimaxh3_norafixture_v1_refmod.safetensors").write_bytes(b"f")
        self.run_dir = self.root / "run"

    def tearDown(self):
        self.tmp.cleanup()

    def test_c1_dynamic_lead_in_when_beat_moves_cuts_or_walks(self):
        closer = br.beat_closer(
            {"scene": "She pulls the silk robe down over her hips and drops it on the bedroom rug. She kneels on the rug."},
            "she",
        )
        self.assertEqual(closer["place"], "bedroom")
        # Static continuation keeps same-framing / same-room lead-in
        s_static = br.continuation_scene("She leans forward and rests her palms on the rug.", "she", closer=closer)
        self.assertIn("the same framing", s_static)
        self.assertIn("the same room lighting", s_static)
        self.assertIn("The camera does not change angle", s_static)
        self.assertIn("never resets to a starting photo", s_static)
        # Camera move / timed cut / walk drops "same framing / camera does not change angle / same room"
        for kw in (
            {"scene": "The camera pushes in with small amplitude at slow speed as she rises."},
            {"scene": "She walks across the floor to the window."},
            {"scene": "[Shot 2] Cut to a closer angle at the edge of the bed.", "new_shot": True},
        ):
            s_dyn = br.continuation_scene(kw["scene"], "she", closer=closer, new_shot=kw.get("new_shot", False))
            self.assertNotIn("the same framing", s_dyn)
            self.assertNotIn("the same room lighting", s_dyn)
            self.assertNotIn("camera does not change angle", s_dyn.lower())
            self.assertIn("never resets to a starting photo", s_dyn)
            self.assertIn("she kneels on the rug", s_dyn)

    def test_c2_beat1_chained_add_guides_and_fail_closed(self):
        staged = br.stage_reference_images(
            validate_reference_images([str(self.img1), str(self.img2)], pools=(self.pool,)),
            self.input_dir,
        )
        g, p = build_parody_request(
            _res(), seed=51083601, prefix="community/t/clip", frames=124,
            images=staged, image_times=[3.0], dialogue=LINE,
        )
        self.assertEqual(g["img_1"]["inputs"]["image"], staged[0])
        self.assertEqual(g["img_2"]["inputs"]["image"], staged[1])
        self.assertEqual(g["add_guide"]["inputs"], {
            "positive": ["c0", 0], "latent": ["c0", 1], "vae": ["vvae", 0], "image": ["img_1", 0], "frame_idx": 0,
        })
        self.assertEqual(g["add_guide_2"]["inputs"], {
            "positive": ["add_guide", 0], "latent": ["c0", 1], "vae": ["vvae", 0], "image": ["img_2", 0], "frame_idx": 72,
        })
        self.assertEqual(g["refapply"]["inputs"]["conditioning"], ["add_guide_2", 0])
        self.assertFalse([k for k in g["c0"]["inputs"] if k.startswith("ref_images")])
        self.assertEqual(br.snap_still_token_frame(3.0), 68)
        # Fail closed: later image with no time, time outside beat 1, or pins < 0.5s apart
        with self.assertRaises(ValueError):
            build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=124, images=staged)
        with self.assertRaises(ValueError):
            build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=124,
                                 images=staged, image_times=[6.0])
        with self.assertRaises(ValueError):
            build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=124,
                                 images=staged, image_times=[0.3])

    def test_c3_and_c4_continuation_beat_guides_and_new_shot_mode(self):
        staged = br.stage_reference_images(
            validate_reference_images([str(self.img1), str(self.img2), str(self.img3)], pools=(self.pool,)),
            self.input_dir,
        )
        # B mode: continuing beat pin at >= 0.5s into Beat 2 (clip time 6.5s on a 124f / 5.1667s base beat -> ~1.333s into beat 2)
        p1 = mock.patch.object(spr, "INDEX_DIR", self.index)
        p2 = mock.patch.object(spr, "REFMODS_DIR", self.refmods)
        p3 = mock.patch.object(spr, "ALIASES_PATH", self.root / "no-aliases.json")
        p4 = mock.patch.object(spr.subprocess, "run")
        with p1, p2, p3, p4:
            res = spr.submit_parody_job(
                name="Nora Fixture", actor="Nora Fixture", description=BIO,
                run_dir_override=self.run_dir, dry_run=True,
                beats=["stands in the bedroom holding a mug", "steps toward the counter and sets the mug down"],
                beat_seconds=[5.0, 6.0],
                images=[str(self.img1), str(self.img2)],
                image_times=[6.5],
                image_pools=(self.pool,),
                image_input_dir=self.input_dir,
            )
        g = json.loads((self.run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
        self.assertEqual(g["img_1"]["inputs"]["image"], staged[0])
        self.assertEqual(g["c2_img"]["inputs"]["image"], staged[1])
        self.assertEqual(g["c2_guide"]["inputs"]["positive"], ["c2_refapply", 0])
        self.assertEqual(g["c2_guide"]["inputs"]["latent"], ["c2_gen", 0])
        self.assertGreaterEqual(g["c2_guide"]["inputs"]["frame_idx"], 22 + 12)
        self.assertEqual(g["c2_tail"]["inputs"]["positive"], ["c2_guide", 0])

        # Reject pin inside hidden overlap (< 22) and continuing-beat pin < 0.5s into new part
        g_base, _ = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=124)
        g_beat, _ = build_parody_request(_res(), seed=51083601, prefix="community/t/clip", frames=158, continuation=True)
        lay = br.continuation_layout(124, 136, 22)
        with self.assertRaises(ValueError):
            br.add_continuation_beat(g_base, g_beat, lay, 2, beat_guides=[{"image": staged[1], "frame_idx": 10}])
        with self.assertRaises(ValueError):
            br.add_continuation_beat(g_base, g_beat, lay, 2, beat_guides=[{"image": staged[1], "sec": 0.2}], new_shot=False)

        # C mode ("new shot"): allows pin in first 0.5s of beat 2, uses dynamic cut lead-in, and rejects walk between two rooms
        g_cut = br.add_continuation_beat(g_base, g_beat, lay, 2, beat_guides=[{"image": staged[2], "sec": 0.25}], new_shot=True)
        self.assertEqual(g_cut["c2_guide"]["inputs"]["frame_idx"], 22 + 6)
        with self.assertRaises(ValueError):
            br.add_continuation_beat(g_base, g_beat, lay, 2, beat_guides=[{"image": staged[2], "sec": 1.2}], new_shot=True)
        with self.assertRaises(ValueError):
            build_parody_request(
                _res(), seed=51083601, prefix="community/t/clip", frames=158, continuation=True,
                prior_closer={"pose": "she stands", "wardrobe": "", "place": "bedroom"},
                scene="She walks into the kitchen and leans on the counter.", new_shot=False,
            )

    def test_prequel_last_frame_pin_resolves_to_frames_minus_one_single_clip(self):
        staged = br.stage_reference_images(
            validate_reference_images([str(self.img1), str(self.img2)], pools=(self.pool,)),
            self.input_dir,
        )
        # 1. Single prequel clip with 1 image and image_times=["end"] -> resolves to frames - 1 (123)
        g1, _ = build_parody_request(
            _res(), seed=51083601, prefix="community/t/clip", frames=124,
            images=[staged[0]], image_times=["end"], dialogue=LINE,
        )
        self.assertEqual(g1["add_guide"]["inputs"]["frame_idx"], 123)
        self.assertNotIn("add_guide_2", g1)

        # 2. Single prequel clip with 1 image and image_times=[-1] -> resolves to frames - 1 (123)
        g2, _ = build_parody_request(
            _res(), seed=51083601, prefix="community/t/clip", frames=124,
            images=[staged[0]], image_times=[-1], dialogue=LINE,
        )
        self.assertEqual(g2["add_guide"]["inputs"]["frame_idx"], 123)

        # 3. Single prequel clip with frame_indices=[-1]
        g3, _ = build_parody_request(
            _res(), seed=51083601, prefix="community/t/clip", frames=124,
            images=[staged[0]], frame_indices=[-1], dialogue=LINE,
        )
        self.assertEqual(g3["add_guide"]["inputs"]["frame_idx"], 123)

        # 4. Start still (frame 0) + last-frame pin (123) with image_times=["end"]
        g4, _ = build_parody_request(
            _res(), seed=51083601, prefix="community/t/clip", frames=124,
            images=staged, image_times=["end"], dialogue=LINE,
        )
        self.assertEqual(g4["add_guide"]["inputs"]["frame_idx"], 0)
        self.assertEqual(g4["add_guide_2"]["inputs"]["frame_idx"], 123)

        # 5. Start still (frame 0) + last-frame pin (123) with frame_indices=[0, -1]
        g5, _ = build_parody_request(
            _res(), seed=51083601, prefix="community/t/clip", frames=124,
            images=staged, frame_indices=[0, -1], dialogue=LINE,
        )
        self.assertEqual(g5["add_guide"]["inputs"]["frame_idx"], 0)
        self.assertEqual(g5["add_guide_2"]["inputs"]["frame_idx"], 123)

        # Ensure no negative frame_idx is written anywhere in the graph
        for nid, node in g4.items():
            if node.get("class_type") == "MiniMaxH3AddGuide":
                self.assertGreaterEqual(node["inputs"]["frame_idx"], 0)

    def test_prequel_rejects_mid_act_frame_as_last_frame_pin(self):
        # 1. validate_target_opening_pose checks
        br.validate_target_opening_pose("character_opening_pose.png")
        br.validate_target_opening_pose("character_frame_0.png", frame_idx=0)
        with self.assertRaises(ValueError) as cm:
            br.validate_target_opening_pose("character_mid_act.png")
        self.assertIn("mid-act frame is not accepted as the last-frame pin image", str(cm.exception))

        with self.assertRaises(ValueError) as cm2:
            br.validate_target_opening_pose("character_scene_mid_frame.png")
        self.assertIn("mid-act frame is not accepted as the last-frame pin image", str(cm2.exception))

        with self.assertRaises(ValueError) as cm3:
            br.validate_target_opening_pose("character_scene.png", frame_idx=48)
        self.assertIn("mid-act frame", str(cm3.exception))

        with self.assertRaises(ValueError) as cm4:
            br.validate_target_opening_pose("character_scene.png", is_opening_pose=False)
        self.assertIn("mid-act frame", str(cm4.exception))

        # 2. build_parody_request rejects mid-act image path on last-frame pin
        mid_img = self.pool / "fixture_mid_act.png"
        mid_img.write_bytes(self.img1.read_bytes())
        staged_mid = br.stage_reference_images(
            validate_reference_images([str(mid_img)], pools=(self.pool,)),
            self.input_dir,
        )
        with self.assertRaises(ValueError) as cm5:
            build_parody_request(
                _res(), seed=51083601, prefix="community/t/clip", frames=124,
                images=staged_mid, image_times=["end"], dialogue=LINE,
            )
        self.assertIn("mid-act frame is not accepted", str(cm5.exception))

    def test_prequel_stitch_join_path_not_latent_tail(self):
        # Create a fixture target mp4
        target_mp4 = self.root / "existing_scene.mp4"
        target_mp4.write_bytes(b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41")

        # 1. submit_parody_job with prequel_to and dry_run=True
        p1 = mock.patch.object(spr, "INDEX_DIR", self.index)
        p2 = mock.patch.object(spr, "REFMODS_DIR", self.refmods)
        p3 = mock.patch.object(spr, "ALIASES_PATH", self.root / "no-aliases.json")
        p4 = mock.patch.object(spr.subprocess, "run")
        with p1, p2, p3, p4:
            res = spr.submit_parody_job(
                name="Nora Fixture", actor="Nora Fixture", description=BIO,
                run_dir_override=self.run_dir, dry_run=True,
                scene="She enters the room before the meeting.",
                prequel_to=target_mp4,
            )
        self.assertTrue(res["dry_run"])
        self.assertEqual(res["prequel_to"], str(target_mp4.resolve()))
        self.assertTrue(res["prequel_stitch"])
        # Check that the request graph is a single clip and has NO LatentTailGuide
        g = json.loads((self.run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
        for nid, node in g.items():
            self.assertNotEqual(node.get("class_type"), "MiniMaxH3LatentTailGuide")

        # 2. finalize_clip stitches [prequel, existing]
        prequel_clip = self.run_dir / "prequel_01.mp4"
        shutil.copyfile(target_mp4, prequel_clip)

        def _fake_run(cmd, *args, **kwargs):
            stitch_dir = self.run_dir / "_stitch"
            stitch_dir.mkdir(parents=True, exist_ok=True)
            (stitch_dir / "stitched.mp4").write_bytes(b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41fake")
            return mock.MagicMock(returncode=0, stdout="PROOF film stitched\nSTITCH done\n", stderr="")

        with mock.patch("subprocess.run", side_effect=_fake_run):
            fres = spr.finalize_clip(self.run_dir, ["prequel_01"], sys.executable, prequel_to=target_mp4)
        self.assertTrue(fres["stitched"])
        self.assertEqual(fres["prequel_to"], str(target_mp4.resolve()))
        self.assertTrue(Path(fres["final_mp4"]).is_file())
        self.assertGreater(Path(fres["final_mp4"]).stat().st_size, 0)
        self.assertEqual(fres["clips"], [str(prequel_clip.resolve()), str(target_mp4.resolve())])


if __name__ == "__main__":
    unittest.main()

