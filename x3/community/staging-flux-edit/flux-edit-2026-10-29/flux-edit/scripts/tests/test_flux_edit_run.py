import csv
import itertools
import json
import os
import pathlib
import re
import shutil
import tempfile
import unittest

import flux_edit_guard as G
import flux_edit_pick as P
import flux_edit_run as R
from _mock_comfy import Mock
from test_flux_edit_pick import Fixture

SCRIPTS = pathlib.Path(__file__).resolve().parents[1]


def prepare():
    """Synthetic picks + head crops + allow-list seeded by the driver. Built once, copied per test."""
    fx = Fixture()
    fx.run()
    heads = fx.rows("head_refs.csv")
    os.makedirs(os.path.join(fx.out, "head_refs"))
    for h in heads:
        w, hh, sha, note = P.crop_head(os.path.join(fx.app, h["source_path"]), (0, 0, 64, 64),
                                       os.path.join(fx.out, "head_refs", f"{h['character']}_head.png"))
        h.update(crop_box="0,0,64,64", crop_w=w, crop_h=hh, crop_sha256=sha, crop_note=note)
    P.write_csv(os.path.join(fx.out, "head_refs.csv"), P.HEAD_COLS, heads)
    return fx


_BASE = None


def base():
    global _BASE
    if _BASE is None:
        _BASE = prepare()
    return _BASE


class Env:
    def __init__(self, window="1", clock=None, disk=None, **kw):
        b = base()
        self.d = tempfile.mkdtemp()
        shutil.copytree(b.d, os.path.join(self.d, "fx"))
        self.app = os.path.join(self.d, "fx", "approved")
        self.inputs = os.path.join(self.d, "fx", "inputs")
        self.allow = os.path.join(self.d, "allow.jsonl")
        self.cin, self.cout = os.path.join(self.d, "cin"), os.path.join(self.d, "cout")
        self.lock = os.path.join(self.d, "gpu-render.lock")
        self.run_dir = os.path.join(self.d, "run")
        self.mock = Mock(self.cin, self.cout)
        args = dict(run_dir=self.run_dir, inputs_dir=self.inputs, approved_dir=self.app, allow_path=self.allow,
                    window=window, lock_path=self.lock, comfy_input=self.cin, comfy_output=self.cout, poll_s=0,
                    sleep=lambda s: None, disk_free_gb=disk or (lambda: 100.0))
        if clock:
            args["clock"] = clock
        args.update(kw)
        self.args = args
        R.Driver(**dict(args, http=None)).seed_allowlist()

    def driver(self, **kw):
        return R.Driver(**dict(self.args, http=R.Http(self.mock.url), **kw))

    def log(self):
        p = os.path.join(self.run_dir, "status.log")
        return open(p).read() if os.path.isfile(p) else ""

    def done(self):
        return open(os.path.join(self.run_dir, "DONE.txt")).read()

    def close(self):
        self.mock.close()
        shutil.rmtree(self.d, ignore_errors=True)


class Base(unittest.TestCase):
    def mk(self, **kw):
        e = Env(**kw)
        self.addCleanup(e.close)
        return e


class DryRun(Base):
    def test_window1_181_and_window1b_121_zero_posts(self):
        for window, n, u in (("1", 181, 181), ("1b", 121, 181)):
            e = self.mk(window=window)
            jobs = R.Driver(**dict(e.args, http=None)).dry_run()
            files = os.listdir(os.path.join(e.run_dir, "dryrun"))
            self.assertEqual(len(files), n)
            self.assertEqual(len({j["tag"] for j in jobs}), n)
            self.assertEqual(R.units(jobs), u)
            self.assertTrue(R.budget_ok(R.units(jobs)))
            self.assertEqual(e.mock.S.log, [])
            self.assertFalse(os.path.exists(e.lock))

    def test_l_full_uses_full_still_head(self):
        e = self.mk(window="1b")
        jobs = R.plan_jobs(e.inputs, e.app, "1b")
        lf = [j for j in jobs if j["arm"] == "L-FULL"][0]
        self.assertTrue(lf["head"].startswith(e.app))
        e8 = [j for j in jobs if j["arm"] == "E8"][0]
        self.assertIn("head_refs", e8["head"])

    def test_budget_rule(self):
        self.assertTrue(R.budget_ok(181))
        self.assertFalse(R.budget_ok(182))

    def test_allow_list_missing_or_unlisted_input_stops_dry_run(self):
        e = self.mk()
        os.remove(e.allow)
        with self.assertRaises(G.GuardStop):
            R.Driver(**dict(e.args, http=None)).dry_run()


class Live(Base):
    def test_full_window_complete(self):
        e = self.mk()
        self.assertEqual(e.driver().run(), "COMPLETE")
        log = e.log()
        self.assertEqual(log.count(" JOB start "), 181)
        self.assertEqual(log.count(" JOB end "), 181)
        self.assertIn("real non-skip rows: 180 of 180", e.done())
        self.assertIn("UNLOAD LLM llm_a", log)
        self.assertFalse(os.path.exists(e.lock))
        paths = [p for _, p in e.mock.S.log]
        self.assertLess(paths.index("/running"), paths.index("/comfyui/system_stats"))
        self.assertLess(paths.index("/comfyui/system_stats"), paths.index("/comfyui/prompt"))
        self.assertIn("/api/models/unload/comfyui_auto", paths)
        G.AllowList(e.allow)  # chain still valid after driver appends
        rows = [json.loads(x) for x in open(e.allow)]
        self.assertEqual(sum(1 for x in rows if x["cls"] == "derived" and len(x["parents"]) == 2), 181)
        side = json.load(open(os.path.join(e.run_dir, "phaseA_bfs", "p01_bfs_L_s432262096973493.json")))
        self.assertEqual(side["out_wh"], [int(x) for x in side["out_wh"]])
        self.assertIn("wake path /comfyui/system_stats", open(os.path.join(e.run_dir, "preflight.txt")).read())

    def test_waits_for_llm_in_flight(self):
        e = self.mk()
        busy = {"running": [{"model": "llm_a", "state": "ready", "inflight": 1}]}
        e.mock.S.running_seq = [busy, busy, {"running": [{"model": "llm_a", "state": "busy"}]}]
        self.assertEqual(e.driver().run(), "COMPLETE")
        self.assertEqual(sum(1 for _, p in e.mock.S.log if p == "/running"), 4)

    def test_llm_never_idle_stops_zero_posts(self):
        tick = itertools.count(0, 50)
        e = self.mk(clock=lambda: next(tick))
        e.mock.S.running = [{"model": "llm_a", "state": "busy"}]
        r = e.driver(llm_wait_s=100).run()
        self.assertTrue(r.startswith("STOP"))
        self.assertEqual(e.mock.posts(), 0)

    def test_unknown_running_shape_stops(self):
        e = self.mk()
        e.mock.S.running_seq = [["weird"]]
        self.assertIn("/running shape unknown", e.driver().run())
        self.assertEqual(e.mock.posts(), 0)

    def test_foreign_lock_hold_untouched(self):
        e = self.mk()
        open(e.lock, "w").write("someone else\n")
        self.assertEqual(e.driver().run(), "HOLD")
        self.assertEqual(open(e.lock).read(), "someone else\n")
        self.assertEqual(e.mock.S.log, [])

    def test_disk_floor_start_and_mid_run(self):
        e = self.mk(disk=lambda: 11.0)
        self.assertIn("disk floor", e.driver().run())
        self.assertEqual(e.mock.posts(), 0)
        seq = iter([20.0] + [20.0] * 3 + [7.0] * 1000)
        e2 = self.mk(disk=lambda: next(seq))
        self.assertIn("disk floor", e2.driver().run())
        self.assertEqual(e2.mock.posts(), 4)  # canary + 3 jobs, then stop before the next job

    def test_version_not_038_stops_before_canary(self):
        e = self.mk()
        e.mock.S.version = "0.39.1"
        self.assertIn("comfy_ok failed", e.driver().run())
        self.assertEqual(e.mock.posts(), 0)

    def test_wake_after_ttl_unload_is_not_job_error(self):
        e = self.mk()
        e.mock.S.stats_fail_n = 3
        self.assertEqual(e.driver().run(), "COMPLETE")
        self.assertNotIn("JOB error", e.log())

    def test_canary_wrong_size_stops(self):
        e = self.mk()
        e.mock.S.wrong_wh.add("canary_bfs_L_s432262096973493")
        self.assertIn("canary", e.driver().run())
        self.assertEqual(e.mock.posts(), 1)

    def test_eviction_resubmit_once_counts_row(self):
        e = self.mk()
        e.mock.S.evict.add("p01_bfs_L_s432262096973493")
        self.assertEqual(e.driver().run(), "COMPLETE")
        log = e.log()
        self.assertIn("JOB error p01_bfs_L_s432262096973493 evicted", log)
        self.assertIn("JOB end canary_bfs_L_s432262096973493_c1 ok", log)
        self.assertIn("JOB end p01_bfs_L_s432262096973493_r1 ok", log)
        self.assertIn("real non-skip rows: 180 of 180", e.done())

    def test_second_eviction_stops(self):
        e = self.mk()
        e.mock.S.evict.update({"p01_bfs_L_s432262096973493", "p02_bfs_L_s432262096973493"})
        self.assertIn("second eviction", e.driver().run())

    def test_same_failure_twice_is_harness_suspect(self):
        e = self.mk()
        e.mock.S.error.update({"p01_bfs_L_s432262096973493", "p02_bfs_L_s432262096973493"})
        self.assertIn("harness suspect", e.driver().run())
        self.assertTrue(os.path.isfile(os.path.join(e.run_dir, "harness_suspect.json")))

    def test_resume_harvests_history_without_requeue(self):
        e = self.mk()
        e.mock.S.evict.add("p03_bfs_L_s432262096973493")
        e.mock.S.evict.add("p04_bfs_L_s432262096973493")  # 2nd eviction stops the first run mid-way
        r1 = e.driver().run()
        self.assertIn("second eviction", r1)
        # fake an in-flight job: JOB start with a pid the mock already finished
        tag = "p05_bfs_L_s432262096973493"
        pid = "deadbeef"
        drv = e.driver()
        jobs = R.plan_jobs(e.inputs, e.app, "1")
        j = [x for x in jobs if x["tag"] == tag][0]
        e.mock.S.prompts[pid] = drv.build_graph(j, G.AllowList(e.allow), "bfs_head_v1_flux-klein_9b_step3750_rank64.safetensors")
        with open(os.path.join(e.run_dir, "status.log"), "a") as f:
            f.write(f"2026-10-29 13:00:00 JOB start {tag} prompt_id={pid}\n")
        open(os.path.join(e.run_dir, tag + ".api.json"), "w").write(json.dumps(e.mock.S.prompts[pid]))
        posts_before = e.mock.posts()
        self.assertEqual(drv.run(), "COMPLETE")
        log = e.log()
        self.assertEqual(log.count(f"JOB start {tag} "), 1)  # harvested, never re-queued
        self.assertIn(f"JOB end {tag} ok", log)
        st = R.parse_log(os.path.join(e.run_dir, "status.log"))
        self.assertFalse(R.is_real(st, "p04_bfs_L_s432262096973493"))
        self.assertTrue(R.is_real(st, "p04_bfs_L_s432262096973493_r1"))  # evicted earlier, resubmitted once
        self.assertGreater(e.mock.posts(), posts_before)

    def test_split_after_block_when_projection_overruns(self):
        tick = itertools.count(0, 5)
        e = self.mk(clock=lambda: next(tick))
        self.assertEqual(e.driver().run(), "SPLIT")
        log = e.log()
        self.assertIn("SPLIT after block L", log)
        self.assertNotIn("_bfs_E_s", log)

    def test_guard_hit_in_graph_stops_before_post(self):
        e = self.mk()
        import flux_edit_workflow as W
        orig = W.PROMPT
        try:
            W.PROMPT = orig + " schoolgirl"
            W.write_template(os.path.join(e.d, "tpl"))
            drv = e.driver()
            real_build = W.build
            W.build = lambda *a, **k: real_build(*a, templates_root=os.path.join(e.d, "tpl"))
            try:
                self.assertIn("guard-stop", drv.run())
            finally:
                W.build = real_build
        finally:
            W.PROMPT = orig
        self.assertEqual(e.mock.posts(), 0)


class R6AndStatic(unittest.TestCase):
    def test_parse_log_r6(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "status.log")
        open(p, "w").write("\n".join([
            "t t JOB start a prompt_id=1", "t t JOB end a ok secs=3.0",
            "t t JOB start b prompt_id=2", "t t JOB end b ok secs=3.0", "t t CLIP_SKIP b",
            "t t JOB start c prompt_id=3", "t t JOB timeout c",
            "t t JOB start d prompt_id=4",
            "t t JOB end e ok secs=1", "t t SKIP f adults-only guard hit"]) + "\n")
        st = R.parse_log(p)
        self.assertEqual([t for t in "abcdef" if R.is_real(st, t)], ["a"])
        self.assertEqual(R.real_rows(st, list("abcdef")), 1)

    def test_should_split(self):
        self.assertFalse(R.should_split([5] * 4, 100, 0, 1000))
        self.assertFalse(R.should_split([5] * 5, 100, 0, 1000))
        self.assertTrue(R.should_split([9] * 5, 100, 0, 1000))

    def test_http_needs_url(self):
        with self.assertRaises(R.Stop):
            R.Http("")

    def test_driver_has_no_llm_route(self):
        src = (SCRIPTS / "flux_edit_run.py").read_text()
        for bad in ("comm.llm", "llm(", "/v1/chat", "/v1/completions", "prompt_writer", "import comm"):
            self.assertNotIn(bad, src)

    def test_all_image_scripts_import_guard_and_no_llm(self):
        for name in ("flux_edit_pick.py", "flux_edit_run.py", "flux_edit_score.py", "flux_edit_workflow.py",
                     "tpl_fill.py", "tpl_check.py"):
            p = SCRIPTS / name
            if not p.exists():
                continue
            src = p.read_text()
            self.assertRegex(src, r"(?m)^import flux_edit_guard", name)
            self.assertNotRegex(src, r"/v1/chat|prompt_writer|comm\.llm", name)

    def test_no_hardcoded_hosts_in_run_path(self):
        for p in SCRIPTS.glob("*.py"):
            self.assertNotRegex(p.read_text(), r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b|localhost", p.name)


if __name__ == "__main__":
    unittest.main()
