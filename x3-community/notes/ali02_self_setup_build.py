#!/usr/bin/env python
"""
ali02_self_setup_build.py - builder for notes/self_setup_20261023.md (fix_plan 0.2).

Row contract (imported from ali02_self_setup_rows_a/b/c.py):
    (claim, evidence, verdict, what_you_will_do)
  evidence = "web/<file>" (a saved primary body in notes/web) | "local:<path>" (a committed
  probe / installed file) | "label:<command>" (a box-local probe listed in ALLOWED_LABELS),
  or a list of any of those. verdict = verified | stale | wrong - exactly Max's 0.2 format.

The URL column is NOT typed by hand: it is looked up from the fetch manifests
(ali02_sources.json / _04y / _04z), so a row can only cite a URL this audit really fetched,
and the body it cites is the body that fetch saved. Things the builder enforces:
  1. every evidence file exists on disk;
  2. every cited web/ body appears in a manifest (URL + body pair, no folklore);
  3. verdict in the 4-value vocabulary;
  4. claim text carries no saved-body path and the action is a real decision;
  5. blocked entries name a stamp file that exists (401/403/404 = unverifiable, never a fact);
  6. no row module shadows a module-level name (AST) - 0.2 shipped `BLOCKED = [...]` twice in
     a.py and b.py, so the first list was discarded and 20 blocked rows never reached the
     deliverable while --check stayed green; text grepping cannot see this, the AST can.
--selftest seeds one fault per detector; all eight MUST fire, and SHADOW must stay silent on
the live row modules (a check that cannot fail is worthless - forge rule).
Run: C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali02_self_setup_build.py [--selftest|--check]
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BOX = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import ali02_self_setup_rows_a as A  # noqa: E402
import ali02_self_setup_rows_b as B  # noqa: E402
import ali02_self_setup_rows_c as C  # noqa: E402

OUT = os.path.join(HERE, "self_setup_20261023.md")
MANIFESTS = ("ali02_sources.json", "ali02_sources_04y.json", "ali02_sources_04z.json",
             "ali02_sources_04x.json", "ali02_sources_04w.json", "ali02_sources_05a.json")
ROW_MODULES = ("ali02_self_setup_rows_a.py", "ali02_self_setup_rows_b.py",
               "ali02_self_setup_rows_c.py")
VERDICTS = {"verified", "stale", "wrong"}
STAMP = re.compile(r"\.(?:401|403|404)(?:-\d+)?\.txt$")
COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime"
# Box-local probes a row may cite as evidence without a saved body. Keep this list tiny:
# a named committed script is always better than a label.
ALLOWED_LABELS = {
    "nvidia-smi (driver version, GPU name, VRAM)",
    "ffprobe -filters / ffmpeg -version (local build)",
    "python -c 'import torch; print(torch.__version__, torch.version.cuda)' in .venv",
    "p7_budget.json ledger read",
    "Select-String over p7/jobs/r4a_1min_v2b/graph.json",
}


def load_manifest():
    """name -> url, registered stem-wise: one manifest entry covers the exact name, every
    numbered re-fetch (stem-2.json) and every refusal stamp (stem.401-2.txt) that fetch wrote
    for the same URL. That is what makes a blocked row checkable: the stamp must name the URL
    that actually wrote it."""
    mapping = {}
    webdir = os.path.join(HERE, "web")
    disk = os.listdir(webdir)
    for name in MANIFESTS:
        p = os.path.join(HERE, name)
        if not os.path.isfile(p):
            raise SystemExit("FATAL: %s missing - the URL column is derived from it" % name)
        for e in json.load(open(p, encoding="utf-8")):
            n = os.path.basename(e["name"])
            mapping[n] = e["url"]
            stem = os.path.splitext(n)[0]
            pat = re.compile(re.escape(stem) + r"(-\d+)?(\.40[134](-\d+)?)?\.(json|html|txt|md)$")
            for f in disk:
                if pat.match(f):
                    mapping.setdefault(f, e["url"])
    if len(mapping) < 150:
        raise SystemExit("FATAL: manifest too small (%d) - did the fetch list get truncated?" % len(mapping))
    return mapping


def resolve(ev: str):
    """Evidence string -> on-disk path (None for label:)."""
    if ev.startswith("web/"):
        return os.path.join(HERE, "web", ev[4:])
    if ev.startswith("local:"):
        rest = ev[6:]
        if rest.startswith(("C:/", "c:/", "/")):
            return rest
        if rest.startswith("ComfyUI/"):
            return os.path.join(COMFY, rest)
        return os.path.join(BOX, rest)
    if ev.startswith("label:"):
        return None
    return os.path.join(BOX, ev)


def evidence_items(evidence):
    return evidence if isinstance(evidence, (list, tuple)) else [evidence]


def check(rows, man, problems):
    for i, (claim, evidence, verdict, action) in enumerate(rows):
        tag = "row %d %r" % (i, claim[:46])
        if verdict not in VERDICTS:
            problems.append("VERDICT %s: %r not in verified|stale|wrong" % (tag, verdict))
        if not claim.strip() or "notes/" in claim or "web/" in claim or ".json" in claim:
            problems.append("CLAIM %s: empty, or carries a saved-body/file path (put it in evidence)" % tag)
        if len(action) < 30:
            problems.append("ACTION %s: %d chars, too short to be a decision" % (tag, len(action)))
        items = evidence_items(evidence)
        if not items:
            problems.append("EVIDENCE %s: none given" % tag)
        for ev in items:
            if ev.startswith("label:"):
                if ev[6:] not in ALLOWED_LABELS:
                    problems.append("LABEL %s: %r not in ALLOWED_LABELS - name a committed probe" % (tag, ev))
                continue
            if ev.startswith("web/") and STAMP.search(ev):
                problems.append("STAMP %s: %r is a 401/403/404 stamp, not evidence - the claim belongs in BLOCKED" % (tag, ev))
            p = resolve(ev)
            if not (p and os.path.isfile(p)):
                problems.append("CITED %s: evidence %r -> %r not on disk" % (tag, ev, p))
            if ev.startswith("web/") and os.path.basename(ev) not in man:
                problems.append("URL %s: %s has no URL in any manifest (fetch it, record name+url)" % (tag, ev))
    return rows


def url_for(evidence, man):
    parts = []
    for ev in evidence_items(evidence):
        if ev.startswith("web/"):
            parts.append(man.get(os.path.basename(ev), "UNMANIFESTED:" + ev))
        elif ev.startswith("label:"):
            parts.append("probe: %s" % ev[6:])
        else:
            parts.append("on-box: %s" % ev[6:])
    return " + ".join(parts)


def render(sections, blocked, man, self_measured=()):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = [r for _, rs in sections for r in rs]
    n_v = sum(1 for r in rows if r[2] == "verified")
    n_s = sum(1 for r in rows if r[2] == "stale")
    n_w = sum(1 for r in rows if r[2] == "wrong")
    out = [
        "# self_setup_20261023 - fix_plan 0.2: 0.1 research claims audited against primary sources",
        "",
        "Generated by `notes/ali02_self_setup_build.py` on %s. The URL column is derived from the" % now,
        "fetch manifests (ali02_sources*.json), so every URL here is a URL this audit fetched and every",
        "URL names a body that is on disk in notes/web. Verdict vocabulary is exactly Max's 0.2 format:",
        "`verified` = the primary source says it right now; `stale` = true when written, the number or",
        "version has moved; `wrong` = the primary source contradicts it. Sources that refused the fetch",
        "(401/403/404) are in the blocked table at the bottom, with the saved stamp file named -",
        "a refused fetch is never written into a fact row.",
        "",
        "**%d claims: %d verified, %d stale, %d wrong. %d claims unverifiable (blocked).**"
        % (len(rows), n_v, n_s, n_w, len(blocked)),
        "",
        "Why the blocked list is long: the 0.1 pass saved its bodies to `notes/_web/`, which no longer",
        "exists, and bodies fetched in an earlier iteration (01s_, 01r_, 02z_, some 03y_/04z_) were",
        "removed at the iteration boundary - notes/web is git-tracked, and an uncommitted body does not",
        "survive. So every number quoted below was re-fetched this pass (04y_/04z_ bodies, committed) or",
        "probed by a committed script; the rest is listed as blocked. Lesson pinned in AGENTS.md:",
        "fetch, run check_web_saves, then `git add notes/web && git commit` in the SAME iteration.",
        "",
    ]
    for title, rs in sections:
        out += ["## %s" % title, "", "| claim | source URL | verified / wrong / stale | what you will do |",
                "|---|---|---|---|"]
        for claim, evidence, verdict, action in rs:
            out.append("| %s | %s | %s | %s |" % (claim, url_for(evidence, man), verdict, action))
        out.append("")
    out += ["## unverifiable (blocked) - the source refused the fetch; stamp named, never used as a fact",
            "", "| claim | source URL | verdict | saved file |", "|---|---|---|---|"]
    for entry in blocked:
        claim, url, stamp = entry[0], entry[1], entry[2]
        kind = entry[3] if len(entry) > 3 else "refused"
        verdict = "unverifiable (blocked: source refused the fetch)" if kind == "refused" \
            else "unverifiable (the saved body does not cover the claim)"
        out.append("| %s | %s | %s | %s |" % (claim, url, verdict, stamp))
    if self_measured:
        out += ["", "## self-measured - our own numbers, never community advice",
                "",
                "These came out of this box (probes, ffprobe, timing runs). They are ours, they must be",
                "labelled ours, and they must never be written as community guidance. Before the next",
                "pass quotes one, it needs a committed script that reproduces it.", ""]
        for s in self_measured:
            out.append("- %s" % s)
    out += ["", "## re-verify", "", "```",
            "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali02_self_setup_build.py --check",
            "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali02_citation_check.py",
            "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali02_citation_check.py --selftest",
            "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali02_self_setup_build.py --selftest",
            "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/check_web_saves.py",
            "```", "",
            "The citation check also scans this file for `web/<file>` tokens, so a dead citation here",
            "fails the check. Refuted quotes (e.g. \"50-100 words\" attributed to the lightx2v card,",
            "the frame-grid attributed to the graft README) are pinned as BANNED negative controls in",
            "ali02_citation_check.py: restoring them re-fails the run.", ""]
    return "\n".join(out)


def check_blocked(blocked, man, problems):
    for entry in blocked:
        claim, url, stamp = entry[0], entry[1], entry[2]
        kind = entry[3] if len(entry) > 3 else "refused"
        tag = "BLOCKED %r" % claim[:40]
        if not url.startswith("http"):
            problems.append("%s: %r is not a URL" % (tag, url[:60]))
        p = resolve(stamp)
        if not (p and os.path.isfile(p)):
            problems.append("%s: stamp %r not on disk" % (tag, stamp))
        if kind == "refused" and not STAMP.search(stamp):
            problems.append("%s: stamp %r is not a 401/403/404 stamp file (use kind 'no-answer' for a body that fails to answer)" % (tag, stamp))
        got = man.get(os.path.basename(stamp))
        if got is None:
            problems.append("%s: stamp %r was written by no manifest URL - record the URL in ali02_sources*.json"
                            % (tag, stamp))
        elif got != url:
            problems.append("%s: URL %r is not the URL that wrote %s (manifest says %r)"
                            % (tag, url[:60], stamp, got[:60]))
    return blocked


def check_shadow(modules, problems):
    """AST detector for the defect 0.2 shipped: a module-level name assigned TWICE, so the
    first ROWS/BLOCKED list is discarded and rows silently leave the deliverable while
    --check stays green. Text grepping the file cannot see this; the AST can."""
    for path in modules:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), name)
        top = {}
        for node in tree.body:
            for t in getattr(node, "targets", []):
                if isinstance(t, ast.Name):
                    top.setdefault(t.id, []).append(node.lineno)
        for ident, lines in sorted(top.items()):
            if len(lines) > 1:
                problems.append(
                    "SHADOW %s: %s is assigned twice at module level (lines %s) - the first "
                    "assignment is discarded, so rows/block entries vanish from the deliverable "
                    "and --check cannot see it; merge them into one list" % (name, ident, lines))
    return problems


def selftest(rows, man) -> int:
    seed = [
        ("seed: dead body", "web/00zz_never_saved_body.json", "verified", "seeded citation to a body that does not exist"),
        ("seed: body with no URL", "web/02x_comfyui_issue15529.json", "verified", "seeded real body that no manifest lists (needs fetch record)"),
        ("seed: bad verdict", "web/04y_repo_comfyui.json", "verified-ish", "seeded verdict outside the vocabulary"),
        ("seed: illegal label", "label:curl.exe -sL https://api.github.com/repos/x/y", "verified", "seeded evidence label outside ALLOWED_LABELS"),
        ("web/ali02_x.md: seed claim carrying a path", "web/04y_repo_comfyui.json", "verified", "seeded claim text carrying a saved-body path"),
    ]
    seed = seed + [("seed: stamp used as evidence", "web/04x_tenstrip_repo.401-2.txt", "verified",
                    "seeded a 401 stamp as if it proved a TenStrip claim")]
    problems = []
    check(seed, man, problems)
    seed_blocked = [("seed: blocked entry whose URL did not write the stamp",
                     "https://api.github.com/repos/someone/else", "web/04x_tenstrip_repo.401-2.txt")]
    check_blocked(seed_blocked, man, problems)
    # SHADOW seed: the exact planted defect (ROWS assigned twice), kept in a string so the
    # builder's own source stays clean and the detector is the only thing that can see it.
    seed_shadow = 'ROWS = ["planted first list"]\nROWS = ["planted second list"]\n'
    seed_path = os.path.join(HERE, "_ali02_shadow_seed_a.py")
    with open(seed_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(seed_shadow)
    try:
        shadow = check_shadow([seed_path], [])
    finally:
        os.remove(seed_path)
    problems.extend(shadow)
    kinds = ("CITED", "URL", "VERDICT", "LABEL", "CLAIM", "STAMP", "BLOCKED", "SHADOW")
    fired = [k for k in kinds if any(p.startswith(k) for p in problems)]
    silent = [k for k in kinds if k not in fired]
    print("SELFTEST: %d seeded faults, detectors fired %d/%d: %s" % (len(kinds), len(fired), len(kinds), fired))
    for p in problems:
        print("   seed ->", p[:120])
    real_shadow = check_shadow([os.path.join(HERE, m) for m in ROW_MODULES], [])
    print("REAL ROW MODULES: SHADOW fires %d time(s): %s"
          % (len(real_shadow), [p.split(" ")[1] + ":" + p.split(": ")[1][:40] for p in real_shadow] or "silent"))
    if len(fired) < len(kinds):
        print("SELFTEST FAILED: the builder check is dead weight, silent detectors: %s" % silent)
        return 1
    if real_shadow:
        print("SELFTEST FAILED: a live row module shadows a name; no row is checked on it")
        return 1
    print("SELFTEST PASS: CITED / URL / VERDICT / LABEL / CLAIM / STAMP / BLOCKED / SHADOW all "
          "fire on the seeds and SHADOW is silent on the live row modules")
    return 0


def main() -> int:
    args = sys.argv[1:]
    man = load_manifest()
    sections = [
        ("A. Box facts (installed packs, models, loras, GPU, torch) - probe-verified", A.ROWS),
        ("B. settings_audit_20261023.md", B.ROWS_SETTINGS),
        ("C. hc_face / body_quality / bakeoff / video-review", B.ROWS_HC),
        ("D. hc_redo_research + plan/AGENTS + community-first claims", C.ROWS),
    ]
    blocked = list(A.BLOCKED) + list(B.BLOCKED) + list(C.BLOCKED)
    self_measured = list(getattr(A, "SELF_MEASURED", ())) + list(getattr(B, "SELF_MEASURED", ())) \
        + list(getattr(C, "SELF_MEASURED", ()))
    rows = [r for _, rs in sections for r in rs]
    if "--selftest" in args:
        return selftest(rows, man)
    problems = []
    check(rows, man, problems)
    check_blocked(blocked, man, problems)
    check_shadow([os.path.join(HERE, m) for m in ROW_MODULES], problems)
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  " + p)
        return 1
    if "--check" in args:
        print("check ok: %d rows + %d blocked + %d self-measured; every evidence file on disk; "
              "every URL from a fetch manifest; no stamp used as evidence"
              % (len(rows), len(blocked), len(self_measured)))
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(sections, blocked, man, self_measured))
    print("wrote %s: %d rows + %d blocked + %d self-measured" % (OUT, len(rows), len(blocked), len(self_measured)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
