import json
import os
import shutil
import subprocess
import tempfile
import unittest

import pins_record as PR


def git(*a, cwd):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                            GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid"))


class Pins(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, True)

    def test_git_heads_and_non_git(self):
        cn = os.path.join(self.d, "custom_nodes")
        a = os.path.join(cn, "node_a")
        os.makedirs(a)
        os.makedirs(os.path.join(cn, "plain_folder"))
        os.makedirs(os.path.join(cn, "__pycache__"))
        git("init", "-q", cwd=a)
        open(os.path.join(a, "x.py"), "w").close()
        git("add", ".", cwd=a)
        git("commit", "-qm", "x", cwd=a)
        head = subprocess.run(["git", "-C", a, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        rec = PR.record(cn)
        self.assertEqual(rec["nodes"]["node_a"], {"status": "git", "head": head})
        self.assertEqual(rec["nodes"]["plain_folder"]["status"], "not_git")
        self.assertNotIn("__pycache__", rec["nodes"])

    def test_snapshot_verbatim_with_sha(self):
        p = os.path.join(self.d, "snap.json")
        with open(p, "w") as f:
            json.dump({"comfyui": "abc", "git_custom_nodes": {}}, f)
        rec = PR.record(snapshot=p)
        self.assertEqual(rec["snapshot"]["comfyui"], "abc")
        self.assertEqual(len(rec["snapshot_sha256"]), 64)

    def test_missing_dir_stops(self):
        with self.assertRaises(SystemExit):
            PR.record(os.path.join(self.d, "nope"))


if __name__ == "__main__":
    unittest.main()
