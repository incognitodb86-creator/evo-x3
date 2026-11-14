# Text-only stub tests for the simplified adults guard (2026-11-02). No images are created, read or stored.
import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPTS = os.path.dirname(HERE)
if SCRIPTS not in sys.path: sys.path.insert(0, SCRIPTS)
import comm, run_queue as rq

def g(*texts):
    return {str(i): {"class_type": "CLIPTextEncode", "inputs": {"text": t}} for i, t in enumerate(texts)}

class TestAdultsGuard(unittest.TestCase):
    def test_blocks_minor_coded_words(self):
        for w in ("underage", "minor", "minors", "child", "children"):
            self.assertFalse(comm.guard_ok("a woman, " + w + ", outdoors"), w)
    def test_allows_adult_words_that_contain_bad_substrings(self):
        for w in ("cowgirl", "girlfriend", "eighteen", "kidnap", "childhood",
                  "girl", "Good girl", "teen", "school", "kid", "loli", "barely legal"):
            self.assertTrue(comm.guard_ok("an adult woman, " + w), w)
    def test_non_string_fails_closed(self):
        self.assertFalse(comm.guard_ok(None)); self.assertFalse(comm.guard_ok(123))
    def test_adult_stated(self):
        self.assertTrue(comm.adult_stated("a fictional adult age twenty-eight"))
        self.assertFalse(comm.adult_stated("a woman on a terrace"))
        self.assertFalse(comm.adult_stated("adulthood"))
    def test_graph_bad_word_anywhere_fails(self):
        self.assertFalse(rq.guard_graph(g("a fictional adult woman", "Negative: child")))
    def test_graph_require_adult(self):
        self.assertTrue(rq.guard_graph(g("a fictional adult woman")))
        self.assertTrue(rq.guard_graph(g("a woman")))  # denylist only; adult/age stamp not required
        self.assertTrue(rq.guard_graph(g("a woman"), require_adult=True))  # flag ignored
        self.assertTrue(rq.guard_graph(g("a fictional adult woman"), require_adult=True))
        self.assertFalse(rq.guard_graph({}, require_adult=True))  # nothing to check -> fail closed
    def test_graph_malformed_fails_closed(self):
        self.assertFalse(rq.guard_graph(None)); self.assertFalse(rq.guard_graph({"1": "x"}))
    def test_script_key_is_scanned(self):
        self.assertFalse(rq.guard_graph({"30": {"class_type": "H3MultishotMemorySampler", "inputs": {"script": "a child"}}}))

if __name__ == "__main__":
    unittest.main()
