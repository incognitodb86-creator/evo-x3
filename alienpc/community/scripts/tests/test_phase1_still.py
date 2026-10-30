# Flux Phase 1 still-job tests (Derrick 2026-10-30 2:52 PM CT): run_queue job_type still, BFS template + patcher,
# banned-node check. Offline: no HTTP, GPU, lock or ComfyUI call.
import json, os, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import comm
import run_graph_job as rgj
import run_queue as rq
import make_bfs_request as mbr

TPL = json.load(open(mbr.TEMPLATE, encoding="utf-8"))


class TestTemplate(unittest.TestCase):
    def test_shipped_values(self):
        self.assertEqual(TPL["18"]["inputs"]["sampler_name"], "lcm")
        self.assertEqual(TPL["19"]["class_type"], "Flux2Scheduler")
        self.assertEqual(TPL["19"]["inputs"]["steps"], 4)
        self.assertEqual(TPL["17"]["inputs"]["cfg"], 1.0)
        self.assertEqual(TPL["2"]["inputs"]["strength_model"], 1.0)
        self.assertIn("rank64", TPL["2"]["inputs"]["lora_name"])
        self.assertEqual(TPL["25"]["inputs"]["resize_type.megapixels"], 1.0)
        self.assertTrue(TPL["5"]["inputs"]["text"].startswith("head_swap: start with Picture 1"))

    def test_no_rmbg_qwenvl_or_banned(self):
        cts = " ".join(n["class_type"].lower() for n in TPL.values())
        self.assertNotIn("rmbg", cts)
        self.assertNotIn("qwenvl", cts)
        self.assertEqual(rgj.banned_nodes(TPL), [])

    def test_guard_ok_on_template_prompts(self):
        self.assertTrue(rq.guard_graph(TPL))


class TestPatcher(unittest.TestCase):
    def test_patches_only_job_fields(self):
        g = mbr.build(TPL, body="community/p/b.png", head="community/p/h.png", seed=20261028, prefix="community/p/t", mp=None)
        diff = {(k, f) for k in g for f in g[k]["inputs"] if g[k]["inputs"][f] != TPL[k]["inputs"][f]}
        self.assertEqual(diff, {("7", "image"), ("8", "image"), ("20", "noise_seed"), ("24", "filename_prefix")})

    def test_refuses_other_fields(self):
        for field in ("sampler", "clip", "lora", "noise_seed", "scheduler"):
            with self.assertRaises(ValueError):
                mbr.build(TPL, **{field: 8})

    def test_arm_dials_patch_only_their_keys(self):  # Miraclein 4.3 A/B arms M4/M8/M12 (plan 2026-10-30)
        base = {"body": "community/p/b.png", "head": "community/p/h.png", "seed": 20261028, "prefix": "community/p/t"}
        job_keys = {("7", "image"), ("8", "image"), ("20", "noise_seed"), ("24", "filename_prefix")}
        allowed = {("1", "unet_name"), ("19", "steps"), ("17", "cfg")}
        for dial in ({"unet": "x.safetensors", "steps": 4}, {"unet": "x.safetensors", "steps": 8},
                     {"unet": "x.safetensors", "steps": 12, "cfg": 1.1}, {}):
            g = mbr.build(TPL, **dict(base, **dial))
            diff = {(k, f) for k in g for f in g[k]["inputs"] if g[k]["inputs"][f] != TPL[k]["inputs"][f]}
            self.assertLessEqual(diff - job_keys, allowed, str(dial))  # an arm changes nothing beyond the plan's dials
            for node, key, dial_key in (("1", "unet_name", "unet"), ("19", "steps", "steps"), ("17", "cfg", "cfg")):
                self.assertEqual(g[node]["inputs"][key], dial.get(dial_key, TPL[node]["inputs"][key]), str(dial))
        plain = mbr.build(TPL, **base)  # no dial = the Phase 1 baseline dials stay as shipped
        self.assertEqual((plain["19"]["inputs"]["steps"], plain["17"]["inputs"]["cfg"], plain["1"]["inputs"]["unet_name"]),
                         (4, 1.0, TPL["1"]["inputs"]["unet_name"]))

    def test_kv_plan_dials_patch_only_their_keys(self):  # Klein 9B-KV + BFS plan rows G/KP/KC (plan 2026-10-30)
        base = {"body": "community/p/b.png", "head": "community/p/h.png", "seed": 20261028, "prefix": "community/p/t"}
        job_keys = {("7", "image"), ("8", "image"), ("20", "noise_seed"), ("24", "filename_prefix")}
        allowed = {("1", "unet_name"), ("2", "strength_model"), ("17", "model"), ("26", "model")}
        kvfile = "flux-2-klein-9b-kv-fp8.safetensors"
        for dial in ({"unet": kvfile}, {"unet": kvfile, "kv": True}, {"unet": kvfile, "strength": 0.0},
                     {"unet": kvfile, "strength": 0.0, "kv": True}):
            g = mbr.build(TPL, **dict(base, **dial))
            diff = {(k, f) for k in g for f in g[k]["inputs"]
                    if k in TPL and g[k]["inputs"][f] != TPL[k]["inputs"][f]}
            self.assertLessEqual(diff - job_keys, allowed, str(dial))  # a KV-plan arm changes nothing beyond the plan's dials
            self.assertEqual(g["1"]["inputs"]["unet_name"], dial["unet"])
            self.assertEqual(g["2"]["inputs"]["strength_model"], dial.get("strength", 1.0))
            self.assertEqual(g["19"]["inputs"]["steps"], 4)  # fixed: 4 steps, cfg 1.0, lcm on every KV-plan row
            self.assertEqual(g["17"]["inputs"]["cfg"], 1.0)
            self.assertEqual(g["18"]["inputs"]["sampler_name"], "lcm")
            self.assertEqual(rgj.banned_nodes(g), [])
            if dial.get("kv"):
                self.assertEqual(g["26"]["class_type"], mbr.KV_CLASS)
                self.assertEqual(g["26"]["inputs"], {"model": ["2", 0]})  # LoRA (node 2) loads BEFORE the KV node
                self.assertEqual(g["17"]["inputs"]["model"], ["26", 0])
            else:
                self.assertNotIn("26", g)
                self.assertEqual(g["17"]["inputs"]["model"], ["2", 0])
        plain = mbr.build(TPL, **base)  # no dial = the baseline: base UNET, strength 1.0, no KV node
        self.assertNotIn("26", plain)
        self.assertEqual((plain["1"]["inputs"]["unet_name"], plain["2"]["inputs"]["strength_model"], plain["17"]["inputs"]["model"]),
                         (TPL["1"]["inputs"]["unet_name"], 1.0, ["2", 0]))
        self.assertTrue(rq.guard_graph(mbr.build(TPL, **dict(base, unet=kvfile, kv=True, strength=0.0))))

    def test_expected_size(self):
        self.assertEqual(mbr.expected_size(768, 1376), (752, 1360))
        self.assertEqual(mbr.expected_size(1376, 768), (1360, 752))


class TestBanned(unittest.TestCase):
    def test_banned_classes_and_models(self):
        for ct in ("ReActorFaceSwap", "PulidFluxModelLoader", "InstantIDModelLoader", "FaceDetailer",
                   "AutoCropFaces", "IPAdapterFaceID", "InsightFaceLoader", "UltralyticsDetectorProvider"):
            self.assertTrue(rgj.banned_nodes({"1": {"class_type": ct, "inputs": {}}}), ct)
        g = {"1": {"class_type": "UNETLoader", "inputs": {"unet_name": "pulid/pulid_flux2_klein_v2.safetensors"}}}
        self.assertTrue(rgj.banned_nodes(g))

    def test_pose_yolox_allowed_face_yolo_banned(self):  # audit FP-1
        ok = {"1": {"class_type": "DWPreprocessor", "inputs": {"bbox_detector": "yolox_l.onnx", "pose_estimator": "dw-ll_ucoco_384.onnx"}}}
        self.assertEqual(rgj.banned_nodes(ok), [])
        for m in ("bbox/face_yolov8m.pt", "yolov8n-face.pt", "my_face_detect_yolo11.pt"):
            g = {"1": {"class_type": "SomeLoader", "inputs": {"model_name": m}}}
            self.assertTrue(rgj.banned_nodes(g), m)

    def test_face_sim_and_mediapipe_face_allowed(self):
        for ct in ("MediaPipe-FaceMeshPreprocessor", "face_sim"):
            self.assertEqual(rgj.banned_nodes({"1": {"class_type": ct, "inputs": {}}}), [], ct)


class TestStillBranch(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.tag = "p1_x_s1"
        os.makedirs(os.path.join(self.d, self.tag))
        g = mbr.build(TPL, body="b.png", head="h.png", seed=1, prefix="community/p/" + self.tag)
        json.dump(g, open(os.path.join(self.d, self.tag, "request.api.json"), "w"))
        self.png = os.path.join(self.d, self.tag, self.tag + ".png")
        open(self.png, "wb").write(b"x" * 10)
        self.job = {"pos": 1, "tag": self.tag, "seed": 1, "job_type": "still", "size": "752x1360"}
        self.acts = os.path.join(self.d, "actions.log")

    def _run(self, probe, job=None):
        with mock.patch.object(rq, "ACTIONS", self.acts), mock.patch.object(rgj, "wake", return_value=True), \
             mock.patch.object(rgj, "static_check", return_value=[]), mock.patch.object(rgj, "probe", return_value=probe), \
             mock.patch.object(rgj, "blackfreeze") as bf, mock.patch.object(rgj, "contact_sheet") as cs, \
             mock.patch.object(comm, "run", return_value={"file": self.png}):
            ok = rq.render_clip(self.d, job or self.job, 124, (768, 1344), False, lambda m: None)
            self.assertFalse(bf.called); self.assertFalse(cs.called)
        return ok, open(os.path.join(self.d, "_render_queue.log"), encoding="utf-8").read()

    def test_still_ok_no_frames_or_audio(self):
        ok, log = self._run({"bytes": 10, "w": 752, "h": 1360, "frames": 1, "audio": False, "duration": 0})
        self.assertTrue(ok)
        self.assertIn(rq.done_tags(self.d).pop(), self.tag)
        r = json.load(open(os.path.join(self.d, self.tag, "render_ok.json")))
        self.assertEqual(r["job_type"], "still")

    def test_still_wrong_size_fails(self):
        ok, log = self._run({"bytes": 10, "w": 768, "h": 1344, "frames": 1, "audio": False, "duration": 0})
        self.assertFalse(ok)
        self.assertIn("objective size 768x1344 != 752x1360", log)

    def test_still_adults_guard_reused(self):
        with mock.patch.object(comm, "guard_ok", return_value=False), mock.patch.object(rq, "ACTIONS", self.acts):
            self.assertFalse(rq.render_clip(self.d, self.job, 124, (768, 1344), False, lambda m: None))
        self.assertIn("GATE-FAIL", open(os.path.join(self.d, "_render_queue.log"), encoding="utf-8").read())

    def test_video_job_still_uses_video_checks(self):
        job = dict(self.job); job.pop("job_type"); job.pop("size")
        with mock.patch.object(rq, "ACTIONS", self.acts), mock.patch.object(rgj, "wake", return_value=True), \
             mock.patch.object(rgj, "static_check", return_value=[]), \
             mock.patch.object(rgj, "probe", return_value={"bytes": 10, "w": 768, "h": 1344, "frames": 1, "audio": False, "duration": 0}), \
             mock.patch.object(rgj, "blackfreeze", return_value=[]), mock.patch.object(comm, "run", return_value={"file": self.png}):
            self.assertFalse(rq.render_clip(self.d, job, 124, (768, 1344), False, lambda m: None))
        log = open(os.path.join(self.d, "_render_queue.log"), encoding="utf-8").read()
        self.assertIn("frames 1 != 124", log); self.assertIn("no audio stream", log)


if __name__ == "__main__":
    unittest.main()
