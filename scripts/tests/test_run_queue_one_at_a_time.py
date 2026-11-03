# Unit test for run_queue.py one-at-a-time submit (MAX_IN_FLIGHT = 1),
# queue timeout stopping detection, and eviction retry wave. Offline.
import json, os, sys, tempfile, time, unittest
import urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import comm
import run_queue as rq


class TestRunQueueOneAtATime(unittest.TestCase):
    """Test suite covering FIX 3 runner enhancements."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = os.path.join(self.tmp.name, "run_test")
        os.makedirs(self.run_dir, exist_ok=True)
        self.actions_log = os.path.join(self.tmp.name, "actions.log")
        self.out_root = os.path.join(self.tmp.name, "out")
        os.makedirs(self.out_root, exist_ok=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _make_job(self, tag: str, pos: int, prompt: str = "an adult woman in cinematic lighting") -> dict:
        """Create job directory and valid request.api.json graph."""
        d = os.path.join(self.run_dir, tag)
        os.makedirs(d, exist_ok=True)
        graph = {
            "save_node": {
                "class_type": "SaveVideo",
                "inputs": {
                    "filename_prefix": f"community/run_test/{tag}",
                    "prompt": prompt,
                },
            }
        }
        with open(os.path.join(d, "request.api.json"), "w", encoding="utf-8") as f:
            json.dump(graph, f)
        return {"pos": pos, "tag": tag, "arm": "A1", "scene": "S1", "seed": 42}

    def test_only_one_prompt_in_flight(self) -> None:
        """Cover 3a: at most MAX_IN_FLIGHT (1) prompt is in ComfyUI at any time."""
        j1 = self._make_job("clip1", 1)
        j2 = self._make_job("clip2", 2)
        in_flight = 0
        max_in_flight = 0
        submitted = []

        def fake_submit(g, tag, meta, outdir, logfile=None, out=None):
            nonlocal in_flight, max_in_flight
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
            submitted.append(tag)
            return f"pid_{tag}"

        def fake_http(url, data=None, timeout=60, method=None):
            if "/queue" in url:
                # ComfyUI reports queue is empty -> trigger fetch
                return {"queue_running": [], "queue_pending": []}
            return {}

        def fake_fetch(pid, tag, meta, outdir, t0, logfile=None, out=None):
            nonlocal in_flight
            in_flight -= 1
            dst = os.path.join(outdir, f"{tag}.mp4")
            with open(dst, "wb") as f:
                f.write(b"mp4_content")
            return {"file": dst}

        with mock.patch.object(rq, "ACTIONS", self.actions_log), \
             mock.patch.object(rq, "OUT_ROOT", self.out_root), \
             mock.patch.object(comm, "submit", side_effect=fake_submit), \
             mock.patch.object(comm, "http", side_effect=fake_http), \
             mock.patch.object(comm, "fetch", side_effect=fake_fetch), \
             mock.patch.object(comm, "comfy_loaded", return_value=True), \
             mock.patch.object(rq.rgj, "wake", return_value=True), \
             mock.patch.object(rq.rgj, "static_check", return_value=[]), \
             mock.patch.object(rq.rgj, "probe", return_value={"bytes": 100, "w": 768, "h": 1344, "frames": 124, "audio": True, "duration": 5.0}), \
             mock.patch.object(rq.rgj, "blackfreeze", return_value=[]), \
             mock.patch.object(rq.rgj, "contact_sheet", return_value=None), \
             mock.patch.object(rq.time, "sleep", return_value=None):
            failed, stopped = rq.run_wave(self.run_dir, [j1, j2], 124, (768, 1344), False, lambda *a: None)

        self.assertEqual(rq.MAX_IN_FLIGHT, 1)
        self.assertEqual(max_in_flight, 1)
        self.assertEqual(submitted, ["clip1", "clip2"])
        self.assertEqual(failed, [])
        self.assertFalse(stopped)

    def test_two_queue_timeouts_stopping_state_and_short_timeout(self) -> None:
        """Cover 3b: 2 consecutive /queue timeouts switch to stopping state and short timeout (10s)."""
        j1 = self._make_job("clip1", 1)
        timeouts_used = []
        logged_msgs = []

        def fake_submit(g, tag, meta, outdir, logfile=None, out=None):
            return "pid_clip1"

        def fake_http(url, data=None, timeout=60, method=None):
            if "/queue" in url:
                timeouts_used.append(timeout)
                if len(timeouts_used) <= 2:
                    raise urllib.error.URLError("timed out")
                # On 3rd call, return normal queue response so job can settle
                return {"queue_running": [], "queue_pending": []}
            return {}

        def fake_fetch(pid, tag, meta, outdir, t0, logfile=None, out=None):
            dst = os.path.join(outdir, f"{tag}.mp4")
            with open(dst, "wb") as f:
                f.write(b"mp4_content")
            return {"file": dst}

        with mock.patch.object(rq, "ACTIONS", self.actions_log), \
             mock.patch.object(rq, "OUT_ROOT", self.out_root), \
             mock.patch.object(comm, "submit", side_effect=fake_submit), \
             mock.patch.object(comm, "http", side_effect=fake_http), \
             mock.patch.object(comm, "fetch", side_effect=fake_fetch), \
             mock.patch.object(comm, "comfy_loaded", return_value=True), \
             mock.patch.object(rq.rgj, "wake", return_value=True), \
             mock.patch.object(rq.rgj, "static_check", return_value=[]), \
             mock.patch.object(rq.rgj, "probe", return_value={"bytes": 100, "w": 768, "h": 1344, "frames": 124, "audio": True, "duration": 5.0}), \
             mock.patch.object(rq.rgj, "blackfreeze", return_value=[]), \
             mock.patch.object(rq.rgj, "contact_sheet", return_value=None), \
             mock.patch.object(rq.time, "sleep", return_value=None):
            failed, stopped = rq.run_wave(self.run_dir, [j1], 124, (768, 1344), False, logged_msgs.append)

        # First two polls should use POLL_TIMEOUT (120 s)
        self.assertEqual(timeouts_used[0], comm.POLL_TIMEOUT)
        self.assertEqual(timeouts_used[1], comm.POLL_TIMEOUT)
        # Third poll after 2 timeouts should use QUEUE_TIMEOUT_STOPPING (10 s)
        self.assertEqual(timeouts_used[2], rq.QUEUE_TIMEOUT_STOPPING)
        # Verify log indicated stopping state
        self.assertTrue(any("looks like it is being stopped (2 /queue timeouts)" in m for m in logged_msgs))
        self.assertEqual(failed, [])

    def test_eviction_fails_into_retry_wave(self) -> None:
        """Cover 3c: comfyui_auto stopping/down evicts running job into retry wave, which promptly re-submits."""
        j1 = self._make_job("clip1", 1)

        def fake_submit(g, tag, meta, outdir, logfile=None, out=None):
            return "pid_clip1"

        def fake_http_wave1(url, data=None, timeout=60, method=None):
            if "/queue" in url:
                raise urllib.error.URLError("connection refused")
            return {}

        # Wave 1: comfy_loaded returns False -> eviction
        with mock.patch.object(rq, "ACTIONS", self.actions_log), \
             mock.patch.object(rq, "OUT_ROOT", self.out_root), \
             mock.patch.object(comm, "submit", side_effect=fake_submit), \
             mock.patch.object(comm, "http", side_effect=fake_http_wave1), \
             mock.patch.object(comm, "comfy_loaded", return_value=False), \
             mock.patch.object(rq.rgj, "wake", return_value=True), \
             mock.patch.object(rq.rgj, "static_check", return_value=[]), \
             mock.patch.object(rq, "disk_output", return_value=None), \
             mock.patch.object(rq, "prefix_output", return_value=None), \
             mock.patch.object(rq.rgj, "collect_from_disk", return_value=None), \
             mock.patch.object(rq.time, "sleep", return_value=None):
            failed, stopped = rq.run_wave(self.run_dir, [j1], 124, (768, 1344), False, lambda *a: None)

        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["tag"], "clip1")
        self.assertFalse(stopped)

        # Wave 2 (retry wave): comfyui_auto is loaded again -> completes ok
        def fake_http_wave2(url, data=None, timeout=60, method=None):
            if "/queue" in url:
                return {"queue_running": [], "queue_pending": []}
            return {}

        def fake_fetch_wave2(pid, tag, meta, outdir, t0, logfile=None, out=None):
            dst = os.path.join(outdir, f"{tag}.mp4")
            with open(dst, "wb") as f:
                f.write(b"mp4_content")
            return {"file": dst}

        with mock.patch.object(rq, "ACTIONS", self.actions_log), \
             mock.patch.object(rq, "OUT_ROOT", self.out_root), \
             mock.patch.object(comm, "submit", side_effect=fake_submit), \
             mock.patch.object(comm, "http", side_effect=fake_http_wave2), \
             mock.patch.object(comm, "fetch", side_effect=fake_fetch_wave2), \
             mock.patch.object(comm, "comfy_loaded", return_value=True), \
             mock.patch.object(rq.rgj, "wake", return_value=True), \
             mock.patch.object(rq.rgj, "static_check", return_value=[]), \
             mock.patch.object(rq.rgj, "probe", return_value={"bytes": 100, "w": 768, "h": 1344, "frames": 124, "audio": True, "duration": 5.0}), \
             mock.patch.object(rq.rgj, "blackfreeze", return_value=[]), \
             mock.patch.object(rq.rgj, "contact_sheet", return_value=None), \
             mock.patch.object(rq.time, "sleep", return_value=None):
            retry_failed, retry_stopped = rq.run_wave(self.run_dir, failed, 124, (768, 1344), True, lambda *a: None)

        self.assertEqual(retry_failed, [])
        self.assertFalse(retry_stopped)

    def test_job_timeout_cancels_via_interrupt_and_queue_delete(self) -> None:
        """Cover FIX 3: jobs exceeding timeout cancel via POST /interrupt and /queue delete."""
        j1 = self._make_job("clip1", 1)
        calls = []

        def fake_submit(g, tag, meta, outdir, logfile=None, out=None):
            return "pid_clip1"

        def fake_http(url, data=None, timeout=60, method=None):
            calls.append((url, data, method))
            if "/queue" in url and method != "POST":
                # Keep prompt in queue_running
                return {"queue_running": [["0", "pid_clip1"]], "queue_pending": []}
            return {}

        clock = 1000.0
        def fake_time():
            nonlocal clock
            clock += 4000.0  # Exceed JOB_TIMEOUT (3600s) on second check
            return clock

        with mock.patch.object(rq, "ACTIONS", self.actions_log), \
             mock.patch.object(rq, "OUT_ROOT", self.out_root), \
             mock.patch.object(comm, "submit", side_effect=fake_submit), \
             mock.patch.object(comm, "http", side_effect=fake_http), \
             mock.patch.object(comm, "comfy_loaded", return_value=True), \
             mock.patch.object(rq.rgj, "wake", return_value=True), \
             mock.patch.object(rq.rgj, "static_check", return_value=[]), \
             mock.patch.object(rq, "disk_output", return_value=None), \
             mock.patch.object(rq, "prefix_output", return_value=None), \
             mock.patch.object(rq.rgj, "collect_from_disk", return_value=None), \
             mock.patch.object(rq.time, "time", side_effect=fake_time), \
             mock.patch.object(rq.time, "sleep", return_value=None):
            failed, stopped = rq.run_wave(self.run_dir, [j1], 124, (768, 1344), False, lambda *a: None)

        self.assertEqual(len(failed), 1)
        self.assertFalse(stopped)
        # Verify /interrupt POST was dispatched
        interrupt_calls = [c for c in calls if "/interrupt" in c[0] and c[2] == "POST"]
        self.assertEqual(len(interrupt_calls), 1)
        # Verify /queue delete POST was dispatched with the PID
        queue_delete_calls = [c for c in calls if "/queue" in c[0] and c[2] == "POST" and c[1] == {"delete": ["pid_clip1"]}]
        self.assertEqual(len(queue_delete_calls), 1)


if __name__ == "__main__":
    unittest.main()
