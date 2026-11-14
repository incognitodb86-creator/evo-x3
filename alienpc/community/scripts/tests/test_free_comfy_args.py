"""B2-1 regression: run_queue.py must hand comm.free_comfy a log PATH, not the queue's log-closure function.

Measured 2026-11-05: run_queue.py's batch close called comm.free_comfy(slog) - `slog` is the queue's
log-closure FUNCTION (run_queue.py: lambda m: comm.log(m, <run_dir>/status.log)), while
comm.free_comfy(logfile: str | None = None) expects a log-file PATH string and passes it to comm.log(),
which opens it. The call raised TypeError and the next line swallowed it as a "free_comfy note", so the
end-of-batch unload/free step logged nothing observable in either log.

Source read only (ast): no import of run_queue, no GPU, no lock, no model load, no HTTP.
Blocks live effects with sys.addaudithook (same shape as scripts/parody/test_longclip_baseline.py:17-21).
"""

from __future__ import annotations

import ast
import os
import sys
import unittest

# F6b: run_queue.py moved to the shared library, so this fixture reads it there. The community path is kept
# as a fallback so the fixture still runs against an un-moved tree (the baseline check does exactly that).
CANDIDATES = [r"C:\AI\community\scripts", r"C:\AI\lib", r"C:\AI\community"]
REPO_ROOT = next(d for d in CANDIDATES if os.path.isfile(os.path.join(d, "run_queue.py")))
RUN_QUEUE = os.path.join(REPO_ROOT, "run_queue.py")
BATCH_LOG = "_render_queue.log"  # the batch log qlog() (run_queue.py:64) writes


_ACTIVE = False


def _deny_live_effects(event: str, args: tuple) -> None:
    if _ACTIVE and event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"B2-1 CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)


def _free_comfy_calls(path: str) -> list[ast.Call]:
    """Every call in `path` whose func is the attribute `comm.free_comfy`."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    hits: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if (isinstance(f, ast.Attribute) and f.attr == "free_comfy"
                and isinstance(f.value, ast.Name) and f.value.id == "comm"):
            hits.append(node)
    return hits


class TestFreeComfyArgs(unittest.TestCase):
    """The end-of-batch free step must log to a real file: a bare Name (a closure) is the regression."""

    @classmethod
    def setUpClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = True

    @classmethod
    def tearDownClass(cls) -> None:
        global _ACTIVE
        _ACTIVE = False

    def test_source_is_parseable_and_calls_free_comfy(self) -> None:
        """The test is not vacuous: run_queue.py parses and does call comm.free_comfy (renaming it away fails here)."""
        calls = _free_comfy_calls(RUN_QUEUE)
        self.assertGreaterEqual(len(calls), 1, "run_queue.py must still call comm.free_comfy at batch close")

    def test_first_argument_is_not_a_bare_name(self) -> None:
        """The B2-1 rule: a joined-path Call / Constant / attribute is fine, a bare Name (slog) is not."""
        for call in _free_comfy_calls(RUN_QUEUE):
            self.assertGreaterEqual(len(call.args), 1, "comm.free_comfy call must pass its log argument")
            arg = call.args[0]
            self.assertNotIsInstance(
                arg, ast.Name,
                "comm.free_comfy(%s) at line %d passes a bare Name: it wants a log-file PATH, "
                "not the queue's slog closure" % (ast.unparse(arg), call.lineno))

    def test_argument_names_the_batch_log_path(self) -> None:
        """The path is the batch's real log, built the way qlog() builds <run_dir>/_render_queue.log."""
        for call in _free_comfy_calls(RUN_QUEUE):
            self.assertTrue(call.args, "comm.free_comfy call must pass its log argument")
            text = ast.unparse(call.args[0])
            self.assertIn(BATCH_LOG, text,
                          "line %d passes %s: the free step must log to the batch log %s"
                          % (call.lineno, text, BATCH_LOG))
            self.assertIn("run_dir", text,
                          "line %d passes %s: the batch log path must be built from the run dir" % (call.lineno, text))


if __name__ == "__main__":
    unittest.main(verbosity=2)
