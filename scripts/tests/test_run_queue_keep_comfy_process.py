"""keep-comfy-part1 (2026-11-15): --keep-comfy-process is a chain-mode opt-in, never a default.

The rule under test: run_queue.py's end-of-batch free step (comm.free_comfy, POST /free) ALWAYS runs;
the llama-swap unload (POST /api/models/unload/comfyui_auto) is skipped ONLY when --keep-comfy-process
is set. The flag defaults off everywhere, and the submit/chain callers append it to the run_queue
argv only when their own flag was requested.

CPU fixtures, same shape as test_free_comfy_args.py: ast source reads for the structural rules, a
real argparse run for "defaults off", and mocked subprocess calls for the argv (no GPU, no lock, no
HTTP, no process launch - live effects are blocked by sys.addaudithook).
"""
from __future__ import annotations

import ast
import os
import sys
import unittest
from unittest import mock

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_QUEUE = os.path.join(SCRIPTS, "run_queue.py")
SUBMIT_PY = os.path.join(SCRIPTS, "parody", "submit_parody_run.py")
CHAIN_QUEUE = os.path.join(SCRIPTS, "queue", "chain_queue.py")
FLAG = "--keep-comfy-process"

_ACTIVE = False


def _deny_live_effects(event: str, args: tuple) -> None:
    if _ACTIVE and event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"keep-comfy CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)


def _tree(path: str) -> ast.Module:
    return ast.parse(open(path, encoding="utf-8").read())


def _calls_named(tree: ast.Module, name: str):
    """Every Call node whose func is the attribute `name` (e.g. comm.free_comfy / rgj.post)."""
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == name:
            hits.append(node)
    return hits


def _func(tree: ast.Module, name: str) -> ast.FunctionDef:
    """The def named `name` (a top-level function or a method inside a class body)."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError("function %s not found" % name)


def _main_body():
    """Statements of run_queue.main() inside its finally block (the batch-close sequence)."""
    m = _func(_tree(RUN_QUEUE), "main")
    for node in ast.walk(m):
        if isinstance(node, ast.Try):
            return node.finalbody
    raise AssertionError("run_queue.main() has no try/finally (the batch close must run on error too)")


def _find_else(body):
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.If) and any("keep_comfy_process" in ast.unparse(n) for n in node.body + [node.test]):
            return node
    raise AssertionError("no keep_comfy_process if/else found in run_queue.main finally")


def _parse_keep_comfy(run_queue_mod, argv):
    """Run run_queue.main's parser on argv by monkeypatching argparse to hand us the namespace."""
    captured = {}
    import argparse
    real_parse = argparse.ArgumentParser.parse_args

    def spy(self, args=None, namespace=None):
        ns = real_parse(self, args, namespace)
        if hasattr(ns, "keep_comfy_process"):
            captured["ns"] = ns
        raise SystemExit(0)  # stop right after parsing: no order file, lock, GPU or HTTP

    argparse.ArgumentParser.parse_args = spy
    sys.argv = ["run_queue.py"] + list(argv)
    try:
        run_queue_mod.main()
    except SystemExit:
        pass
    finally:
        argparse.ArgumentParser.parse_args = real_parse
    assert "ns" in captured, "run_queue.main() never parsed a keep_comfy_process namespace"
    return captured["ns"].keep_comfy_process


class TestRunQueueFlag(unittest.TestCase):
    """The queue itself: flag declared with default off, free_comfy unconditional, unload guarded."""

    @classmethod
    def setUpClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = True
        sys.path.insert(0, SCRIPTS)
        import run_queue  # noqa: F401  (import before the audit hook blocks any live effect)

    @classmethod
    def tearDownClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = False

    def test_flag_is_off_by_default_in_real_argparse(self):
        import run_queue
        self.assertIs(_parse_keep_comfy(run_queue, ["--run-dir", "X"]), False,
                      "a normal run_queue command must keep the default unload")
        self.assertIs(_parse_keep_comfy(run_queue, ["--run-dir", "X", FLAG]), True)

    def test_flag_parser_default_off(self):
        src = open(RUN_QUEUE, encoding="utf-8").read()
        self.assertIn('ap.add_argument("%s", action="store_true"' % FLAG, src,
                      "run_queue.py must declare --keep-comfy-process as a store_true flag (no default=True)")

    def test_finally_always_calls_free_comfy(self):
        """free_comfy sits in the finally block itself, not inside the keep/unload branch."""
        calls = _calls_named(ast.Module(body=_main_body(), type_ignores=[]), "free_comfy")
        self.assertGreaterEqual(len(calls), 1, "the batch close must call comm.free_comfy")
        for c in calls:
            for node in ast.walk(c):
                self.assertNotIsInstance(node, ast.If, "comm.free_comfy is inside an if - a branch would let a flag skip it")

    def test_llama_swap_unload_is_skipped_only_when_flag_is_on(self):
        """The only rgj.post(.../unload/comfyui_auto) in main() is guarded by `if a.keep_comfy_process` (else branch)."""
        body = _main_body()
        guarded, unguarded = [], []
        for node in ast.walk(ast.Module(body=body, type_ignores=[])):
            if isinstance(node, ast.If):
                test = ast.unparse(node.test)
                if "keep_comfy_process" in test:
                    for c in _calls_named(node, "post"):
                        guarded.append((test, ast.unparse(c)))
        for c in _calls_named(ast.Module(body=body, type_ignores=[]), "post"):
            u = ast.unparse(c)
            if "comfyui_auto" in u and "unload" in u:
                unguarded.append(u)
        self.assertEqual(len(guarded), 1, "exactly one guarded llama-swap unload of comfyui_auto expected, got %r" % guarded)
        self.assertTrue(guarded[0][0].startswith("a.keep_comfy_process"),
                        "the guard must be `if a.keep_comfy_process:` (flag on = skip), got %r" % guarded[0][0])
        self.assertIn("else", ast.unparse(_find_else(body)),
                      "the unload must sit in the else branch: flag off unloads exactly as before")

    def test_closing_line_never_claims_an_unload_the_flag_skipped(self):
        src = open(RUN_QUEUE, encoding="utf-8").read()
        needle = '"comfyui_auto kept loaded" if a.keep_comfy_process else "comfyui_auto unloaded"'
        self.assertIn(needle, src, "BATCH closed tail must say kept loaded only when the flag was on")


class TestSubmitPassesFlagOnlyWhenAsked(unittest.TestCase):
    """submit_parody_run: both queue builders append the flag to run_queue argv only when asked."""

    @classmethod
    def setUpClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = True
        sys.path.insert(0, os.path.join(SCRIPTS, "parody"))
        sys.path.insert(0, SCRIPTS)
        import submit_parody_run  # noqa: F401  (imports build_request etc. before the hook blocks effects)

    @classmethod
    def tearDownClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = False

    def test_cli_flags_exist_on_both_entries(self):
        src = open(SUBMIT_PY, encoding="utf-8").read()
        self.assertIn('ap.add_argument("%s", action="store_true"' % FLAG, src, "writer-run CLI needs the flag")
        self.assertIn('parser.add_argument("%s", action="store_true"' % FLAG, src, "main CLI needs the flag")

    def test_writer_run_cli_forwards_only_when_set(self):
        fn = _func(_tree(SUBMIT_PY), "_writer_run_cli")
        blob = ast.unparse(fn)
        self.assertIn("r = submit_writer_run(", blob, "the writer-run entry builds through submit_writer_run once")
        self.assertIn("keep_comfy_process': True} if a.keep_comfy_process else {}", blob,
                      "must be conditional (only when requested), not an always-on leak")

    def test_argv_appends_are_guarded(self):
        tree = _tree(SUBMIT_PY)
        appends = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.If) and "keep_comfy_process" in ast.unparse(node.test)
                    and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "append"
                            and ast.unparse(c.args[0]) == "'%s'" % FLAG for c in ast.walk(node))):
                appends.append(ast.unparse(node.test))
        self.assertEqual(len(appends), 2,
                         "both queue builders (submit_parody_job and submit_writer_run) must append the flag under an if")

    def test_default_off_end_to_end_writer_run_argv(self):
        """A real submit_writer_run() with a mocked subprocess: no flag by default, flag when asked."""
        import submit_parody_run as spr
        graph = {"c0": {"inputs": {"prompt": "", "length": 243, "width": 768, "height": 1344}},
                 "noise": {"inputs": {"noise_seed": 0}}, "save": {"inputs": {"filename_prefix": ""}},
                 "refmods": {"inputs": {f"mod_{i}": "(none)" for i in range(1, 9)}},
                 "img_1": {"inputs": {"image": "old.png"}}}
        graph["refmods"]["inputs"]["mod_1"] = "minimaxh3_oc_poolblonde_v2_refmod_visual"
        raw = open(os.path.join(SCRIPTS, "tests", "_keep_comfy_writer_raw.txt"), encoding="utf-8").read()
        read = {"room": "a dimly lit stage with a pole", "place": "stage", "bed": False, "sheets": "",
                "surface": "the stage floor", "floor": "dark floor", "light": "dramatic spotlighting",
                "pose": "stands beside a pole with one hand gripping it, hips tilted to the side",
                "props": ["a chrome pole"],
                "garments": [{"type": "top", "name": "black mesh strappy bra top"},
                             {"type": "other", "name": "black mesh strappy bottom with garter straps"},
                             {"type": "stockings", "name": "black fishnet thigh-high stockings"}]}
        import tempfile
        calls = []

        class P:
            returncode, stdout, stderr = 0, "", ""

        def fake_run(cmd, **kw):
            calls.append(list(cmd))
            return P()

        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(spr.subprocess, "run", fake_run):
                r1 = spr.submit_writer_run(raw, dict(graph), os.path.join(td, "a"), "she has sex with him, position: missionary",
                                           "missionary", still_read=read, still_image="community/oc_poolblonde_stage.png")
                self.assertEqual(r1["status"], "READY", r1.get("reason"))
                self.assertNotIn(FLAG, calls[-1], "a normal queued writer-run must not touch the chain flag")
                self.assertEqual(calls[-1][-1], "--detach", "the flag is appended after --detach only when asked")
                r2 = spr.submit_writer_run(raw, dict(graph), os.path.join(td, "b"), "she has sex with him, position: missionary",
                                           "missionary", still_read=read, still_image="community/oc_poolblonde_stage.png",
                                           keep_comfy_process=True)
                self.assertEqual(r2["status"], "READY", r2.get("reason"))
                self.assertEqual(calls[-1][-2:], ["--detach", FLAG], "the chain call appends the flag last")

    def test_writer_run_cli_flag_parses_off_by_default(self):
        """The writer-run entry's parser: absent = False, present = True (no queue, no I/O - SystemExit 3 after parsing)."""
        import argparse
        import submit_parody_run as spr
        captured = {}
        real_parse = argparse.ArgumentParser.parse_args

        def spy(self, args=None, namespace=None):
            ns = real_parse(self, args, namespace)
            if hasattr(ns, "keep_comfy_process"):
                captured["ns"] = ns
            raise SystemExit(3)  # stop before any filesystem / queue work

        argparse.ArgumentParser.parse_args = spy
        base = ["--ask", "fixture ask", "--position", "missionary", "C:/nonexistent-dir-for-fixture"]
        try:
            spr._writer_run_cli(list(base))
            self.assertFalse(captured["ns"].keep_comfy_process, "writer-run default must be off")
            captured.clear()
            spr._writer_run_cli(base + [FLAG])
            self.assertTrue(captured["ns"].keep_comfy_process, "writer-run --keep-comfy-process must set True")
        finally:
            argparse.ArgumentParser.parse_args = real_parse


class TestChainQueuePassesFlag(unittest.TestCase):
    """The canonical chain harness: flag on every queued writer-run, ping during the gaps."""

    @classmethod
    def setUpClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = True

    @classmethod
    def tearDownClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = False

    def test_chain_appends_flag_only_on_the_queued_call(self):
        tree = _tree(CHAIN_QUEUE)
        wr = _func(tree, "writer_run")
        ifs = [n for n in ast.walk(wr) if isinstance(n, ast.If) and ast.unparse(n.test) == "queue"]
        self.assertEqual(len(ifs), 1, "writer_run must have an `if queue:` block (the --queue call)")
        appends = [ast.unparse(c.args[0]) for c in _calls_named(ifs[0], "append")]
        self.assertIn("'--queue'", appends, "the chain queues")
        self.assertIn("'%s'" % FLAG, appends, "the chain passes the flag it documented (keep-comfy-part1)")
        all_appends = [c for c in _calls_named(wr, "append") if ast.unparse(c.args[0]) == "'%s'" % FLAG]
        self.assertEqual(len(all_appends), 1, "exactly one guarded append of the flag in writer_run")

    def test_chain_pings_the_comfy_route_under_the_ttl(self):
        src = open(CHAIN_QUEUE, encoding="utf-8").read()
        self.assertIn('COMFY + "/system_stats"', src,
                      "keep-alive must ping llama-swap /comfyui/system_stats (ignored path: resets ttl, never wakes)")
        self.assertLessEqual(60, 300, "sanity")
        import re as _re
        m = _re.search(r"^PING_SEC\s*=\s*(\d+)", src, _re.M)
        self.assertIsNotNone(m, "the ping interval is a named constant")
        self.assertLess(int(m.group(1)), 300, "ping interval must stay well under comfyui_auto's ttl (300 s)")

    def test_chain_is_parameterized(self):
        src = open(CHAIN_QUEUE, encoding="utf-8").read()
        self.assertIn('"--run-dir"', src, "chain_queue.py must accept --run-dir (not hard-wired to one run)")
        self.assertNotIn('ROOT = Path(r"/home/derekboone/AI/community/runs/overnight_5min_rough_20261115_v2")', src,
                         "the finished v2 dir must not stay a module-level constant")

    def test_chain_writer_run_call_is_complete(self):
        """The chain's argv keeps the v2 shape: writer-run, --queue only when asked, seed check intact."""
        src = open(CHAIN_QUEUE, encoding="utf-8").read()
        for token in ('"writer-run"', "--continued", "--scene-read", "--inherited-garments", "SEED_MISMATCH"):
            self.assertIn(token, src, "chain argv lost %s" % token)


if __name__ == "__main__":
    unittest.main(verbosity=2)
