#!/usr/bin/env python3
r"""HF2 tests (offline, no network, 0 GPU): the web-save rule that stopped the
Ralph loop on 2026-10-23 16:59:37.

  python C:/AI/community/scripts/tests/test_web_fetch.py
  python -m unittest discover -s C:/AI/community/scripts/tests -p "test_web_fetch.py"

Every check is objective. The detector tests are self-destruct probes: the bad-file
case MUST fire, otherwise the green sweep means nothing.
"""

import json
import os
import sys
import tempfile
import unittest
from importlib import import_module

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

web_fetch = import_module("web_fetch")
check_web_saves = import_module("check_web_saves")

# The body shape that killed the loop: reddit.com/search.json answers 403 with HTML,
# and mirror/proxy pages answer 200 with a "Blocked" HTML page.
HTML_403 = b"<html><head><title>403 Forbidden</title></head><body>Blocked</body></html>"
HTML_200 = b"<!DOCTYPE html>\n<html><body>Blocked</body></html>\n"
GOOD_JSON = b'{"data": {"children": [{"title": "ok"}]}}'
PLAIN = b"plain research note, not json, not markup"


class TempDir(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="hf2_")

    def read(self, name):
        with open(os.path.join(self.tmp, name), "rb") as f:
            return f.read()


class TestClassify(TempDir):
    def test_valid_json_is_json(self):
        self.assertEqual(web_fetch.classify(200, GOOD_JSON)[:2], ("json", ""))

    def test_html_403_is_txt_stamped_with_status(self):
        ext, suffix, reason = web_fetch.classify(403, HTML_403)
        self.assertEqual((ext, suffix), ("txt", ".403"))
        self.assertIn("403", reason)

    def test_html_200_is_html_not_json(self):
        self.assertEqual(web_fetch.classify(200, HTML_200)[0], "html")

    def test_plain_text_is_txt(self):
        self.assertEqual(web_fetch.classify(200, PLAIN)[0], "txt")

    def test_empty_body_is_txt(self):
        self.assertEqual(web_fetch.classify(200, b"   ")[0], "txt")

    def test_json_name_helper_strips_extension(self):
        self.assertEqual(web_fetch.split_name("reddit_anatomy.json"), "reddit_anatomy")
        self.assertEqual(web_fetch.split_name("reddit_anatomy"), "reddit_anatomy")


class TestSave(TempDir):
    def test_html_body_never_lands_as_json(self):
        path, _ = web_fetch.save(self.tmp, "reddit_anatomy", HTML_403, status=403)
        self.assertTrue(path.endswith("reddit_anatomy.403.txt"))
        self.assertEqual(check_web_saves.sweep(self.tmp), [])

    def test_200_html_body_saves_as_html(self):
        path, _ = web_fetch.save(self.tmp, "rd_sd_pe", HTML_200)
        self.assertTrue(path.endswith("rd_sd_pe.html"))

    def test_real_json_saves_as_json_and_parses(self):
        path, _ = web_fetch.save(self.tmp, "hf_h3", GOOD_JSON)
        self.assertTrue(path.endswith("hf_h3.json"))
        self.assertEqual(json.loads(self.read("hf_h3.json"))["data"]["children"][0]["title"], "ok")

    def test_forcing_json_on_non_json_body_is_refused(self):
        with self.assertRaises(SystemExit):
            web_fetch.save(self.tmp, "trap", HTML_200, status=200, ext="json")

    def test_no_overwrite_without_force_gets_suffix(self):
        web_fetch.save(self.tmp, "dup", GOOD_JSON)
        path, _ = web_fetch.save(self.tmp, "dup", GOOD_JSON, force=False)
        self.assertTrue(path.endswith("dup-2.json"))


class TestReclassify(TempDir):
    def test_hf2_incident_replay(self):
        """The exact HF2 bomb: a non-JSON .json becomes a .html and the sweep goes clean."""
        bomb = os.path.join(self.tmp, "reddit_anatomy.json")
        with open(bomb, "wb") as f:
            f.write(HTML_403)
        self.assertEqual(len(check_web_saves.sweep(self.tmp)), 1)  # detector fires
        path, _ = web_fetch.reclassify(self.tmp, bomb)
        self.assertTrue(path.endswith("reddit_anatomy.html"))
        self.assertFalse(os.path.exists(bomb))
        self.assertEqual(check_web_saves.sweep(self.tmp), [])
        self.assertEqual(self.read("reddit_anatomy.html"), HTML_403)

    def test_status_stamped_name_round_trips(self):
        src = os.path.join(self.tmp, "rd_llama_abl.403.txt")
        with open(src, "wb") as f:
            f.write(HTML_403)
        path, _ = web_fetch.reclassify(self.tmp, src)
        self.assertTrue(path.endswith("rd_llama_abl.403.txt"))


class TestSweepAndFix(TempDir):
    def test_detector_is_non_vacuous(self):
        good = os.path.join(self.tmp, "good.json")
        bad = os.path.join(self.tmp, "bad.json")
        with open(good, "wb") as f:
            f.write(GOOD_JSON)
        with open(bad, "wb") as f:
            f.write(HTML_200)
        bads = check_web_saves.sweep(self.tmp)
        self.assertEqual([os.path.basename(p) for p in bads], ["bad.json"])
        moved = check_web_saves.fix(self.tmp)
        self.assertEqual(len(moved), 1)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "bad.html")))
        self.assertTrue(os.path.exists(good))
        self.assertEqual(check_web_saves.sweep(self.tmp), [])

    def test_fix_is_collision_safe(self):
        with open(os.path.join(self.tmp, "x.json"), "wb") as f:
            f.write(PLAIN)
        with open(os.path.join(self.tmp, "x.txt"), "wb") as f:
            f.write(b"keeper")
        check_web_saves.fix(self.tmp)
        self.assertEqual(self.read("x.txt"), b"keeper")
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "x-2.txt")))

    def test_cli_rc_reflects_state(self):
        with open(os.path.join(self.tmp, "bad.json"), "wb") as f:
            f.write(HTML_200)
        self.assertEqual(check_web_saves.main(["--dir", self.tmp]), 1)
        self.assertEqual(check_web_saves.main(["--dir", self.tmp, "--fix"]), 0)
        self.assertEqual(check_web_saves.main(["--dir", self.tmp]), 0)


class TestLiveRepo(TempDir):
    def test_notes_web_is_clean_now(self):
        """HF2 regression guard: the real notes/web has no non-JSON .json left."""
        d = web_fetch.DEFAULT_DIR
        if not os.path.isdir(d):
            self.skipTest("%s not present" % d)
        self.assertEqual(check_web_saves.sweep(d), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
