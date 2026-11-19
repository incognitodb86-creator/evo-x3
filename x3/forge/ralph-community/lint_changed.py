#!/usr/bin/env python3
"""Ralph backpressure lint: fail a pass only for NEW error-class ruff findings in the .py files it changed.

Usage (inside `uv run --no-project --with ruff`):
    python lint_changed.py <repo> [<base-commit>]

Rules: E9 (syntax/IO), F63 (bad comparisons), F7 (misplaced statements), F82 (undefined names). Findings that
already exist in the base version of a file are ignored (matched by file, code and message, not line), so legacy
issues never block an unrelated edit. Exit codes: 0 clean or nothing to lint, 3 new findings, 0 with a WARNING
when ruff itself is unavailable (the pytest gate still runs).
<repo> may be a subfolder of a repo (mono: x3/community); paths are relative to it.
"""
import collections, json, os, subprocess, sys, tempfile

RULES = "E9,F63,F7,F82"


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def ruff(paths, cwd):
    if not paths:
        return []
    r = subprocess.run([sys.executable, "-m", "ruff", "check", "--no-cache", "--select", RULES,
                        "--output-format", "json", "--exit-zero", *paths], capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[:300])
    return json.loads(r.stdout or "[]")


def keyed(findings, root):
    c = collections.Counter()
    for f in findings:
        rel = os.path.relpath(f["filename"], root).replace(os.sep, "/")
        c[(rel, f["code"], f["message"])] += 1
    return c


def main(argv):
    repo = os.path.realpath(argv[1] if len(argv) > 1 else ".")
    base = argv[2] if len(argv) > 2 and argv[2] else "HEAD"
    try:
        changed = set(git(repo, "diff", "--relative", "--name-only", "--diff-filter=AMR", base, "--", "*.py").splitlines())
        changed |= set(git(repo, "ls-files", "--others", "--exclude-standard", "--", "*.py").splitlines())
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"LINT_WARNING cannot list changed files in {repo} against {base}, lint skipped: {e}")
        return 0
    changed = sorted(p for p in changed if p and os.path.isfile(os.path.join(repo, p)))
    if not changed:
        print("LINT_OK no changed .py files")
        return 0
    try:
        head = keyed(ruff(changed, repo), repo)
        with tempfile.TemporaryDirectory() as tmp:
            old = []
            for p in changed:
                try:
                    src = git(repo, "show", f"{base}:./{p}")
                except subprocess.CalledProcessError:
                    continue  # new file: every finding is new
                dst = os.path.join(tmp, p)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "w", encoding="utf-8", newline="") as fh:
                    fh.write(src)
                old.append(p)
            before = keyed(ruff(old, tmp), tmp)
    except (RuntimeError, OSError, ValueError) as e:
        print(f"LINT_WARNING ruff unavailable or failed, lint skipped: {e}")
        return 0
    new = head - before
    if not new:
        print(f"LINT_OK files={len(changed)} rules={RULES}")
        return 0
    for (rel, code, msg), n in sorted(new.items()):
        print(f"LINT_NEW {rel}: {code} {msg}" + (f" (x{n})" if n > 1 else ""))
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
