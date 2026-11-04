# Unit tests for expanded guard_ok key scope (S1a, ALI-173 / Argon Audit 2026-10-26)
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import comm

class TestGuardScope(unittest.TestCase):
    def test_prompt_keys_tuple(self):
        expected = ("prompt", "text", "prompt_1", "prompt_2", "prompt_3", "prompt_4", "prompt_5", "prompt_6", "clips_json", "sequence_prompt", "value", "script")
        for k in expected:
            self.assertIn(k, comm.PROMPT_KEYS)

    def test_prompt_strings_extraction(self):
        inputs = {
            "prompt": "adult woman",
            "text": "golden hour beach",
            "prompt_1": "close up shot",
            "prompt_2": "wide surf view",
            "clips_json": '{"clip": 1}',
            "sequence_prompt": "slow pan",
            "value": "cinematic tone",
            "seed": 51150011,
            "length": 243,
            "other_non_str": None,
        }
        extracted = list(comm.prompt_strings(inputs))
        self.assertEqual(len(extracted), 7)
        self.assertIn("adult woman", extracted)
        self.assertIn("golden hour beach", extracted)
        self.assertIn("close up shot", extracted)
        self.assertIn("wide surf view", extracted)
        self.assertIn('{"clip": 1}', extracted)
        self.assertIn("slow pan", extracted)
        self.assertIn("cinematic tone", extracted)

    def test_guard_blocks_every_key(self):
        banned_word = "underage"
        for key in comm.PROMPT_KEYS:
            inputs = {key: f"scene with {banned_word} figure"}
            has_blocked = any(not comm.guard_ok(s) for s in comm.prompt_strings(inputs))
            self.assertTrue(has_blocked, f"Key {key} failed to trigger adults-only guard")

    def test_guard_allows_valid_adult_prompts(self):
        valid_prompt = "Two adult women 22 years old in surf at golden hour, shallow water, warm rim light."
        for key in comm.PROMPT_KEYS:
            inputs = {key: valid_prompt}
            all_ok = all(comm.guard_ok(s) for s in comm.prompt_strings(inputs))
            self.assertTrue(all_ok, f"Key {key} falsely blocked valid adult prompt")

    # --- 2026-11-04: node MiniMaxH3PromptBuilder put its prompt in prompt_text/builder_state, the
    # key list missed it, the guard collected 0 strings and a clean prompt was reported as
    # "adults guard" (runs/pw_strip_20261104b). These tests keep that path visible and named. ---

    PB_GRAPH = {"pw": {"class_type": "MiniMaxH3PromptBuilder",
                       "inputs": {"prompt_text": "the adult woman in <Picture 1> takes her micro brief off",
                                  "builder_state": "{\"mode\": \"ref2va\"}"}}}

    def test_prompt_builder_keys_are_scanned(self):
        for key in ("prompt_text", "builder_state"):
            self.assertIn(key, comm.PROMPT_KEYS)
            inputs = {key: "the schoolgirl takes her micro brief off"}
            self.assertTrue(any(not comm.guard_ok(s) for s in comm.prompt_strings(inputs)),
                            "key %s is not scanned by the guard" % key)

    def test_prompt_builder_graph_passes(self):
        ok, why = comm.guard_reason(self.PB_GRAPH)
        self.assertTrue(ok, why)
        import run_queue as rq
        self.assertTrue(rq.guard_graph(self.PB_GRAPH))

    def test_prompt_builder_minor_word_names_the_node(self):
        g = {"pw": {"class_type": "MiniMaxH3PromptBuilder",
                    "inputs": {"builder_state": "{\"cast\": \"a schoolgirl\"}"}}}
        ok, why = comm.guard_reason(g)
        self.assertFalse(ok)
        self.assertIn("builder_state", why)
        self.assertIn("MiniMaxH3PromptBuilder", why)

    def test_invisible_prompt_fails_with_a_named_reason(self):
        # a node whose only string key is outside PROMPT_KEYS must NOT look like a wording problem
        g = {"pw": {"class_type": "MiniMaxH3PromptBuilder", "inputs": {"some_new_key": "an adult woman"}}}
        ok, why = comm.guard_reason(g)
        self.assertFalse(ok)
        self.assertIn("no prompt text visible", why)

    def test_no_adult_stated_names_the_count(self):
        g = {"pw": {"class_type": "MiniMaxH3PromptBuilder",
                    "inputs": {"prompt_text": "she takes her micro brief off"}}}
        ok, why = comm.guard_reason(g)
        self.assertFalse(ok)
        self.assertIn("no adult stated", why)

    def test_age_statements_count_as_adult(self):
        for t in ("a 28-year-old woman in a bikini", "she is 28 years old", "a man, 41 yo",
                  "a 21+ year old", "a woman age 33", "a fictional adult"):
            self.assertTrue(comm.adult_stated(t), t)

    def test_unclear_age_stays_blocked(self):
        for t in ("a 17 years old woman", "a woman in her twenties", "a 12-year-old",
                  "a woman on a terrace", "adulthood"):
            self.assertFalse(comm.adult_stated(t), t)

    def test_graph_level_blocking(self):
        graph = {
            "10": {
                "class_type": "PrimitiveStringMultiline",
                "inputs": {"value": "avoidance: schoolgirl"}
            },
            "11": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "two adult women enjoying the ocean"}
            }
        }
        # Check node 10 value triggers guard
        node_10_strings = list(comm.prompt_strings(graph["10"]["inputs"]))
        self.assertTrue(any(not comm.guard_ok(s) for s in node_10_strings))

        # Check node 11 text passes guard
        node_11_strings = list(comm.prompt_strings(graph["11"]["inputs"]))
        self.assertTrue(all(comm.guard_ok(s) for s in node_11_strings))

if __name__ == "__main__":
    unittest.main()
