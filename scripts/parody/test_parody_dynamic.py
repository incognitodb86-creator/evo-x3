"""CPU tests for the dynamic H3 parody pipeline (T1 U1-U4 + prompt tweaks, 2026-11-06)."""

from __future__ import annotations

import json
from pathlib import Path
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
    return p.split("detailed_description:")[1].split("overall_soundscape:")[0]


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
        self.assertIn("an adult performer, age 28+", p)
        self.assertTrue(comm.adult_stated(p))
        self.assertLessEqual(p.lower().count("adult"), 2)
        self.assertIn("[English, using Megan Fox's exact Jennifer Check voice and signature vocal timbre]", p)
        self.assertIn("overall_soundscape:", p)

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
        self.assertIn("Camera locked off, no zoom, no pan.", p)

    def test_moving_camera_drops_locked_off(self):
        cam = "cinematic widescreen medium-wide shot from waist up including tabletop, 35mm lens, slow smooth dolly push-in"
        p = format_parody_prompt(_res(), dialogue=LINE, camera=cam, scene="sits at a neon diner counter")
        self.assertIn(f"[{cam}]", p)
        self.assertNotIn("Camera locked off", p)
        p2 = format_parody_prompt(_res(), dialogue=LINE, camera="close-up, 85mm lens")
        self.assertIn("[close-up, 85mm lens]", p2)
        self.assertIn("Camera locked off, no zoom, no pan.", p2)

    def test_pronouns_and_end_action(self):
        p = format_parody_prompt(_res(), dialogue=LINE, pronoun="he")
        self.assertIn("He holds eye contact, gives a small nod at the end, and stops talking.", p)
        self.assertIn("His mouth movements stop completely", p)
        self.assertIn("He uses Megan Fox's exact Jennifer Check voice, accent, and signature vocal timbre consistently throughout the entire clip.", p)
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
        self.assertIn("(S1) Jennifer Check - an adult performer, age 28+", both)
        self.assertIn("(S2) Needy Lesnicki - an adult performer, age 28+", both)
        self.assertIn("Non-speaking characters: none.", both)
        self.assertIn("(S2): <d>[English, using Amanda Seyfried's exact Needy Lesnicki voice and signature vocal timbre] You said that last week too.</d>", both)
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
        for bad in (str(self.outside), "sydney_misc/a.png", r"C:\Users\derek\sydney\x.png", "B01/missing.png"):
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
        self.assertIn("overall_soundscape:", p)
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
        plan = br.plan_continuation_chain([br.snap_h3_frames(6, max_frames=br.SINGLE_CLIP_MAX_FRAMES),
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

    def test_long_seconds_auto_split(self):
        res = self._submit(seconds=15, scene="sits at the counter holding a mug", dialogue=LINE)
        self.assertEqual(len(res["tags"]), 2)
        self.assertEqual(res["frames"], [175, 175])
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


if __name__ == "__main__":
    unittest.main()
