"""EVO-X3 remote queue mode (consolidation P1b, 2026-11-16): checks through the real entry points, no network."""
import importlib, json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import remote_comfy as rc

G = {"img_1": {"class_type": "LoadImage", "inputs": {"image": "community/a.jpg"}},
     "aud": {"class_type": "LoadAudio", "inputs": {"audio": "v.wav"}},
     "unet": {"class_type": "UNETLoader", "inputs": {"unet_name": "x.safetensors"}}}

class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "community"))
        open(os.path.join(self.d, "community", "a.jpg"), "wb").write(b"jpg")
        open(os.path.join(self.d, "v.wav"), "wb").write(b"RIFFwav")

    def test_upload_plan_lists_image_and_audio_not_models(self):
        plan = rc.upload_plan(G, self.d)
        self.assertEqual(sorted((p["kind"], p["name"], p["subfolder"]) for p in plan),
                         [("audio", "v.wav", ""), ("image", "community/a.jpg", "community")])

    def test_missing_input_fails_closed(self):
        os.remove(os.path.join(self.d, "v.wav"))
        with self.assertRaises(FileNotFoundError):
            rc.upload_plan(G, self.d)

    def test_multipart_carries_overwrite_and_file(self):
        body, ct = rc._multipart({"subfolder": "community", "type": "input", "overwrite": "true"}, "a.wav", b"DATA")
        self.assertIn(b'name="overwrite"\r\n\r\ntrue', body)
        self.assertIn(b'name="image"; filename="a.wav"', body)
        self.assertIn(b"DATA", body)
        self.assertTrue(ct.startswith("multipart/form-data; boundary="))

    def test_lock_is_exclusive_and_released(self):
        with mock.patch.object(rc, "LOCK", os.path.join(self.d, "locks", "gpu.lock")):
            self.assertEqual(rc.lock_acquire("t")[0], 0)
            if rc.fcntl is not None:
                fh = open(rc.LOCK, "a+")
                with self.assertRaises(BlockingIOError):
                    rc.fcntl.flock(fh, rc.fcntl.LOCK_EX | rc.fcntl.LOCK_NB)
                rc.lock_release()
                rc.fcntl.flock(fh, rc.fcntl.LOCK_EX | rc.fcntl.LOCK_NB); fh.close()
            else:
                saved_fh = rc._lock_fh
                try:
                    rc._lock_fh = None
                    self.assertEqual(rc.lock_acquire("t2")[0], 1)
                finally:
                    rc._lock_fh = saved_fh
                rc.lock_release()
                self.assertEqual(rc.lock_acquire("t3")[0], 0)
                rc.lock_release()

    def test_enable_routes_submit_through_uploads_and_fetch_through_view(self):
        rq = importlib.import_module("run_queue")
        for m in (rq, rq.comm, rq.rgj):
            saved = dict(vars(m)); self.addCleanup(lambda m=m, s=saved: (vars(m).clear(), vars(m).update(s)))
        rc.enable(rq)
        self.assertEqual(rq.comm.BASE, rc.API)
        self.assertIsNone(rq.comm.comfy_loaded())
        posted = []
        outdir = os.path.join(self.d, "clip")
        with mock.patch.object(rc, "upload", side_effect=lambda it: posted.append(it["name"]) or {"name": it["name"]}), \
             mock.patch.object(rq.comm, "http", return_value={"prompt_id": "p1"}) as http:
            pid = rq.comm.submit(json.loads(json.dumps(G)), "clip", {}, outdir)
        self.assertEqual(pid, "p1")
        self.assertEqual(sorted(posted), ["community/a.jpg", "v.wav"])
        self.assertTrue(http.call_args[0][0].endswith("/prompt"))
        hist = {"p1": {"status": {"status_str": "success"}, "outputs": {"9": {"videos": [{"subfolder": "community/clip", "filename": "c_00001.mp4"}]}}}}
        def fake_dl(sub, name, dst, timeout=900):
            open(dst, "wb").write(b"mp4"); return 3
        with mock.patch.object(rq.comm, "http", return_value=hist), mock.patch.object(rc, "download", side_effect=fake_dl):
            side = rq.comm.fetch("p1", "clip", {}, outdir, 0)
        self.assertEqual(side["file"], os.path.join(outdir, "clip.mp4"))
        self.assertTrue(os.path.isfile(side["file"] + ".json"))

    def test_detach_forwards_rq_env_to_systemd_unit(self):
        rq = importlib.import_module("run_queue")
        for m in (rq, rq.comm, rq.rgj):
            saved = dict(vars(m)); self.addCleanup(lambda m=m, s=saved: (vars(m).clear(), vars(m).update(s)))
        rc.enable(rq)
        env = {"RQ_REMOTE_BUSY_WAIT_SEC": "1800", "COMFY_API": "https://h:8446", "LLM_KEY_PI": "secret"}
        with mock.patch.dict(os.environ, env), \
             mock.patch.object(rc.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="", stderr="")) as run:
            self.assertEqual(rq.detach(["--remote", "--detach", "--run-dir", self.d], self.d), 0)
        cmd = run.call_args[0][0]
        self.assertIn("--setenv=RQ_REMOTE_BUSY_WAIT_SEC=1800", cmd)
        self.assertIn("--setenv=COMFY_API=https://h:8446", cmd)
        self.assertFalse(any("LLM_KEY" in c for c in cmd))
        self.assertNotIn("--detach", cmd)
        self.assertLess(cmd.index("--setenv=COMFY_API=https://h:8446"), cmd.index(rq.PY))

    def test_remote_idle_checks_system_stats_before_queue(self):
        import io
        import urllib.error

        calls = []

        def fake_urlopen_409(url, timeout=20):
            calls.append(url)
            raise urllib.error.HTTPError(url, 409, "Conflict", {}, None)

        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen_409):
            self.assertIsNone(rc.remote_idle())
        self.assertEqual(calls, [rc.API + "/system_stats"])

        class _Resp:
            def __init__(self, body=b"{}", status=200):
                self._bio = io.BytesIO(body)
                self.status = status
            def read(self):
                return self._bio.read()
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False

        calls.clear()

        def fake_urlopen_idle(url, timeout=20):
            calls.append(url)
            if url.endswith("/system_stats"):
                return _Resp(b"{}", 200)
            return _Resp(b'{"queue_running": [], "queue_pending": []}', 200)

        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen_idle):
            self.assertIs(rc.remote_idle(), True)
        self.assertEqual(calls, [rc.API + "/system_stats", rc.API + "/queue"])

        calls.clear()

        def fake_urlopen_busy(url, timeout=20):
            calls.append(url)
            if url.endswith("/system_stats"):
                return _Resp(b"{}", 200)
            return _Resp(b'{"queue_running": [["id1"]], "queue_pending": []}', 200)

        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen_busy):
            self.assertIs(rc.remote_idle(), False)
        self.assertEqual(calls, [rc.API + "/system_stats", rc.API + "/queue"])

        calls.clear()

        def fake_urlopen_err(url, timeout=20):
            calls.append(url)
            raise urllib.error.HTTPError(url, 500, "Server Error", {}, None)

        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen_err):
            self.assertIs(rc.remote_idle(), False)
        self.assertEqual(calls, [rc.API + "/system_stats"])

    def test_upload_dedup_same_file_once_mtime_twice_error_reuploads(self):
        import io
        import urllib.error

        rq = importlib.import_module("run_queue")
        for m in (rq, rq.comm, rq.rgj):
            saved = dict(vars(m)); self.addCleanup(lambda m=m, s=saved: (vars(m).clear(), vars(m).update(s)))
        rc._UPLOAD_CACHE.clear()
        rc.enable(rq)

        upload_calls = []

        class _Resp:
            def __init__(self, payload):
                self._b = json.dumps(payload).encode("utf-8")
            def read(self):
                return self._b
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False

        def fake_urlopen(req, timeout=300):
            url = req.full_url if hasattr(req, "full_url") else str(req)
            if url.endswith("/upload/image"):
                upload_calls.append(url)
                return _Resp({"name": "a.jpg", "subfolder": "community"})
            raise AssertionError(f"unexpected urlopen {url}")

        outdir = os.path.join(self.d, "clip")
        g_img = {"img_1": {"class_type": "LoadImage", "inputs": {"image": "community/a.jpg"}}}
        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen), \
             mock.patch.object(rq.comm, "http", return_value={"prompt_id": "p1"}):
            # 1) Same file twice -> 1 upload
            self.assertEqual(rq.comm.submit(json.loads(json.dumps(g_img)), "c1", {}, outdir), "p1")
            self.assertEqual(rq.comm.submit(json.loads(json.dumps(g_img)), "c2", {}, outdir), "p1")
            self.assertEqual(len(upload_calls), 1)
            self.assertTrue(os.path.isfile(os.path.join(self.d, rc._UPLOAD_CACHE_FILE)))

            # 2) Changed mtime -> 2nd upload
            img_path = os.path.join(self.d, "community", "a.jpg")
            st = os.stat(img_path)
            os.utime(img_path, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
            self.assertEqual(rq.comm.submit(json.loads(json.dumps(g_img)), "c3", {}, outdir), "p1")
            self.assertEqual(len(upload_calls), 2)

        # 3) Queue error after cached skip -> invalidates and falls back to fresh upload + retries /prompt
        prompt_attempts = {"n": 0}
        def fail_once_then_ok(url, body=None, timeout=60):
            prompt_attempts["n"] += 1
            if prompt_attempts["n"] == 1:
                raise urllib.error.HTTPError(url, 400, "Bad Request", {}, io.BytesIO(b"missing input"))
            return {"prompt_id": "p_retry"}

        out_info = {}
        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen), \
             mock.patch.object(rq.comm, "http", side_effect=fail_once_then_ok):
            pid = rq.comm.submit(json.loads(json.dumps(g_img)), "c4", {}, outdir, out=out_info)
        self.assertEqual(pid, "p_retry")
        self.assertEqual(prompt_attempts["n"], 2)
        self.assertEqual(len(upload_calls), 3)

        # 4) Different local file targeting the same server subfolder/name -> overwrites cache, re-uploads
        alt_dir = os.path.join(self.d, "alt")
        os.makedirs(os.path.join(alt_dir, "community"), exist_ok=True)
        alt_img = os.path.join(alt_dir, "community", "a.jpg")
        open(alt_img, "wb").write(b"different-jpg-bytes")
        alt_out = os.path.join(alt_dir, "clip")
        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen), \
             mock.patch.object(rq.comm, "http", return_value={"prompt_id": "p_alt"}):
            self.assertEqual(rq.comm.submit(json.loads(json.dumps(g_img)), "c5", {}, alt_out), "p_alt")
            self.assertEqual(len(upload_calls), 4)
            # Switching back to original file under the same server name must also re-upload
            self.assertEqual(rq.comm.submit(json.loads(json.dumps(g_img)), "c6", {}, outdir), "p_alt")
            self.assertEqual(len(upload_calls), 5)

        # 5) Fetch execution_error naming a missing input invalidates the run upload cache
        hist_err = {"p_alt": {"status": {"status_str": "error",
                                         "messages": [["execution_error", {"exception_message": "File not found: community/a.jpg"}]]},
                              "outputs": {}}}
        with mock.patch.object(rq.comm, "http", return_value=hist_err):
            self.assertIsNone(rq.comm.fetch("p_alt", "c6", {}, outdir, 0))
        self.assertFalse(os.path.exists(os.path.join(self.d, rc._UPLOAD_CACHE_FILE)))
        with mock.patch.object(rc.urllib.request, "urlopen", side_effect=fake_urlopen), \
             mock.patch.object(rq.comm, "http", return_value={"prompt_id": "p_after_err"}):
            self.assertEqual(rq.comm.submit(json.loads(json.dumps(g_img)), "c7", {}, outdir), "p_after_err")
        self.assertEqual(len(upload_calls), 6)

    def test_writer_pipeline_passes_keep_comfy_process_for_continue_only(self):
        from pathlib import Path
        parody_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "parody"))
        if parody_dir not in sys.path:
            sys.path.insert(0, parody_dir)
        import render_writer_pipeline as rwp
        rd = Path(self.d) / "run_1"
        cmd_single = rwp._queue_remote_cmd(rd, is_continue=False)
        cmd_chain = rwp._queue_remote_cmd(rd, is_continue=True)
        self.assertNotIn("--keep-comfy-process", cmd_single)
        self.assertIn("--keep-comfy-process", cmd_chain)
        self.assertIn("--yes-derrick", cmd_single)
        self.assertIn("--yes-derrick", cmd_chain)


if __name__ == "__main__":
    unittest.main()
