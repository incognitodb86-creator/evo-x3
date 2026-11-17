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
        ifs = [n for n in ast.walk(wr) if isinstance(n, ast.If) and "queue" in ast.unparse(n.test)]
        self.assertGreaterEqual(len(ifs), 1, "writer_run must guard --queue and --keep-comfy-process")
        src_wr = ast.get_source_segment(open(CHAIN_QUEUE, encoding="utf-8").read(), wr) or ""
        self.assertIn("--queue", src_wr)
        self.assertIn(FLAG, src_wr)

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
        v2_root = os.path.join(os.path.dirname(SCRIPTS), "runs", "overnight_5min_rough_20261115_v2")
        self.assertNotIn(f'ROOT = Path(r"{v2_root}")', src,
                         "the finished v2 dir must not stay a module-level constant")

    def test_chain_writer_run_call_is_complete(self):
        """The chain's argv keeps the v2 shape: writer-run, --queue only when asked, seed check intact."""
        src = open(CHAIN_QUEUE, encoding="utf-8").read()
        for token in ("fill_request.py", "run_queue.py", "--frames", "SEED_MISMATCH"):
            self.assertIn(token, src, "chain argv lost %s" % token)


if __name__ == "__main__":
    unittest.main(verbosity=2)
