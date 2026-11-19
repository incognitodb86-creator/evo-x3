# run_queue.prompt_sha must hash the prompt TEXT behind an input, following a writer link.
# Measured 2026-11-04 (runs/pw_strip_20261104c): a writer-routed graph wires c0.prompt as ["pw", 0],
# the journal step did hashlib.sha256(prompt.encode(...)) on that list, raised AttributeError after a
# good render, and the queue marked the clip failed (BATCH closed rc=5, done=0/1).
# These tests keep the link resolved, the sha equal to the builder tool's sha, and the failure a note.
import hashlib, os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPTS = os.path.dirname(HERE)
if SCRIPTS not in sys.path: sys.path.insert(0, SCRIPTS)
import run_queue as rq

TEXT = "the adult woman in <Picture 1> takes her micro brief off"
SHA = hashlib.sha256(TEXT.encode("utf-8")).hexdigest()

G = {
    "pw": {"class_type": "MiniMaxH3PromptBuilder", "inputs": {"prompt_text": TEXT, "builder_state": "{}"}},
    "c0": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {"prompt": ["pw", 0], "length": 124}},
    "c1": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {"prompt": TEXT}},
    "c2": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {"prompt": ["ghost", 0]}},
    "c3": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {"prompt": ""}},
    "c4": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {"prompt": 124}},
    "c5": {"class_type": "CLIPTextEncode", "inputs": {"text": ["pw", 0]}},
    "c6": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {"prompt": ["plain", 0]}},
    "plain": {"class_type": "SomeNode", "inputs": {"seed": 5}},
}


class TestPromptSha(unittest.TestCase):
    def sha(self, node):
        return rq.prompt_sha(G, G[node]["inputs"].get("prompt"))

    def test_plain_text_hashes_as_before(self):
        self.assertEqual(self.sha("c1"), (SHA, ""))

    def test_writer_link_is_resolved_to_its_text(self):
        self.assertEqual(self.sha("c0"), (SHA, ""))
        self.assertEqual(rq.prompt_behind(G, ["pw", 0]), (TEXT, ""))

    def test_still_path_link_resolves_to_its_text(self):
        # a Klein graph may wire the positive CLIPTextEncode from another node; same rule, same result
        self.assertEqual(rq.prompt_sha(G, rq.still_prompt(G)), (SHA, ""))

    def test_unresolvable_values_are_named_not_fatal(self):
        for node, needle in (("c2", "ghost"), ("c3", "empty"), ("c4", "neither text nor"),
                             ("c6", "no prompt-bearing key")):
            sha, note = self.sha(node)
            self.assertEqual(sha, "unresolved", node)
            self.assertIn(needle, note, node)

    def test_no_input_shape_raises(self):
        for node in ("c0", "c1", "c2", "c3", "c4", "c6"):
            rq.prompt_sha(G, G[node]["inputs"].get("prompt"))
        rq.prompt_sha(G, None)
        rq.prompt_sha({}, ["pw", 0])

    def test_journal_writer_shape_survives(self):
        # the value the video path passes in: the c0 prompt of a writer-routed graph
        val = next(n["inputs"].get("prompt") for n in G.values()
                   if n.get("class_type") == "MiniMaxH3ReferenceToVideo")
        self.assertEqual(rq.prompt_sha(G, val), (SHA, ""))


if __name__ == "__main__":
    unittest.main()
