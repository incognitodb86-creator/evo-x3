#!/usr/bin/env python
# -*- coding: ascii -*-
# HISTORICAL one-shot record (U2), not a reusable check: hard-coded paths/sizes/dates from that day; do not re-run as a live gate. Max2 audit-fix #19, 2026-10-29.
"""U2 close-out check (2026-10-29, MAX block item 1): the "single home for prompt rules" test.

Version 2 (2026-10-29 10:3x CT) - tightened after Max's independent verify
(C:/Users/derek/5slock/ralph-community/notes/2026-10-29-max-U2-verify-FAIL.md). Its checks 1, 3, 6 passed and its
FAILs were real, so this version adds what v1 could not see:

  A. a PHRASE check (not a prefix check): 5-word shingles of every home rule, compared against the pointer skills
     and their references - this is what catches a paraphrase of a rule, not only a copy-paste of it;
  B. the four key phrases Max named (does not pin frame 0 / zoom out / only if loaded / unique seed per cell)
     must not appear in any pointer skill;
  C. internal duplication inside the home (R26 vs R7) is now a FAIL;
  D. every skill supporting file that names the two audio blocks must mark them superseded/deleted by R7
     (this is what caught director references/max-i2v-prompt-improve-v1.md);
  E. the audio "deleted context" list drops the weak words "block", "history", "nothing" (Max: any line
     containing "block" used to pass), and the audio test works on SENTENCES (v1 tested single lines, which fails
     on hard-wrapped prose);
  F. the restored "no scripts/runs/p7/p3/specs touched" clause (dropped in v1), plus the u2fix backups by sha
     prefix, plus the mid-snapshot must live in notes/, not in the skill folder;
  G. the one-place rule: the Max-TE lane rule appears in exactly one skill (the director); no pointer file may
     grow more than 400 B in the fix pass (cites and history markers add words - a rule restatement is caught by
     the phrase check, not by size) and none may return to its pre-U2 size.

v1 clauses kept: rule-signature uniqueness, pointer checks, home content requirements (output-only-prompt,
adults 18+, 3-6 examples, TenStrip HF #77 audio, checklist), p15 verbatim examples, PROMPT.md L16 liveness,
the five u2 backups, youth guard tests, gpu_guard IDLE.

Run: C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/u2_check.py
Exit 0 = every clause passes. Nothing is written except pytest caches.
"""
import hashlib
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

HOME = r"C:\AI\community\skills\h3-prompting\SKILL.md"
P_REF2VA = r"C:\Users\derek\.pi\agent\skills\ref2va-prompt\SKILL.md"
P_CHAIN = r"C:\Users\derek\.pi\agent\skills\h3-ref2va-prompt-chain\SKILL.md"
P_DIR = r"C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\SKILL.md"
POINTERS = [P_REF2VA, P_CHAIN, P_DIR]
PROMPT = r"C:\Users\derek\5slock\ralph-community\PROMPT.md"
PROMPT_BAK = r"C:\Users\derek\5slock\ralph-community\PROMPT.md.bak-20261029-u2-l16"
P15 = r"C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md"
SKILL_TREES = [r"C:\AI\community\skills", r"C:\Users\derek\.pi\agent\skills"]
COMMUNITY = r"C:\AI\community"
GUARD_TESTS = [r"C:\AI\community\scripts\tests\test_p6_review.py",
               r"C:\AI\community\scripts\tests\test_guard_scope.py"]
PY = r"C:\AI\director\.venv\Scripts\python.exe"
SIG_LEN = 90
SHINGLE = 5
NOTE = os.path.join(COMMUNITY, "notes", "2026-10-29-U2-prompt-skill-merge-DONE.md")
MAX_VERIFY = r"C:\Users\derek\5slock\ralph-community\notes\2026-10-29-max-U2-verify-FAIL.md"
MID_NOTES = os.path.join(COMMUNITY, "notes", "SKILL.md.mid-20261029-u2-examples")
KEY_PHRASES = ["does not pin frame 0", "zoom out", "only if loaded", "unique seed per cell"]

# measured pre-edit bytes, printed before any edit (u2_closeout_record / u2fix_start_record output)
BACKUPS_U2 = {
    r"C:\AI\community\skills\h3-prompting\SKILL.md.bak-20261029-u2": "02d7a031",
    r"C:\Users\derek\.pi\agent\skills\ref2va-prompt\SKILL.md.bak-20261029-u2": "d61b2d36",
    r"C:\Users\derek\.pi\agent\skills\h3-ref2va-prompt-chain\SKILL.md.bak-20261029-u2": "eb9a0ba6",
    r"C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\SKILL.md.bak-20261029-u2": "21a3095e",
    PROMPT_BAK: "38cef8b1",
}
BACKUPS_FIX = {  # the FIX pass backups, printed 10:3x CT by u2fix_start_record.py
    HOME + ".bak-20261029-u2fix": "5a293990",
    P_DIR + ".bak-20261029-u2fix": "47e69734",
    r"C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\references\max-i2v-prompt-improve-v1.md"
    ".bak-20261029-u2fix": "612ec3b3",
    P_REF2VA + ".bak-20261029-u2fix": "3e534e78",
    P_CHAIN + ".bak-20261029-u2fix": "54f8c402",
}
EDITED_IN_FIX = [HOME, P_DIR, P_REF2VA, P_CHAIN,
                 r"C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\references"
                 r"\max-i2v-prompt-improve-v1.md"]


def u(t):
    """Line-ending normalisation (the ralph-community tree is CRLF, skill supporting files are LF).
    For content comparison only; byte and sha checks stay binary."""
    return t.replace("\r\n", "\n")


def norm_text(t):
    t = t.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", t).strip()


def skill_names():
    """Skill names are pointers, not rule text (every skill cites the home by name and path)."""
    names = set()
    for root in SKILL_TREES:
        for d in os.listdir(root):
            if os.path.isdir(os.path.join(root, d)):
                names.add(d)
    return sorted(names, key=len, reverse=True)


SKILL_NAMES = skill_names()
STOP = set("""a an the of to in for and or on with that this these those it is are was be been as at by from per
not no nor so than then there they them his her its their you your we our i me my us s t d ll ve re
will would can could should may might must do does did have has had just very more most other others such same
into onto off up down over under out about against between while when where who whom whose how why all any each
both few many much several own""".split())


def prose(t):
    """Normalise for PHRASE comparison: lowercase, no markdown, no paths/filenames (every skill repeats the
    home's path), no skill names, no R-citations (a cite is a pointer, not a restatement), no punctuation."""
    t = u(t).lower()
    t = re.sub(r"[a-z]:[\\/][^\s`,)\"]*", " PATH ", t)
    t = re.sub(r"[a-z0-9_.-]+[\\/][a-z0-9_./-]*", " PATH ", t)
    t = re.sub(r"\b[a-z0-9_.-]+\.(md|py|ps1|json|txt|csv|log)\b", " PATH ", t)
    for n in SKILL_NAMES:
        t = t.replace(n.lower(), " SKILL ")
    t = t.replace("**", "").replace("`", "")
    t = re.sub(r"\br\d+[a-z]?\b", " RN ", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def shingles(t, n=SHINGLE):
    """n-word phrases, keeping only those with >=2 content words (a run of pure function words like
    'that is not in the' is English, not a rule)."""
    w = t.split()
    out = set()
    for i in range(len(w) - n + 1):
        g = w[i:i + n]
        if sum(1 for x in g if x not in STOP) >= 2:
            out.add(tuple(g))
    return out


def parse_rules(text):
    # CRLF-tolerant: files are read in binary (byte-exact sha checks), so boundaries match \r\n as well as \n.
    blocks = re.findall(r"(?ms)^\*\*(R\d+) - (.*?)(?=\r?\n\r?\n\*\*R\d+ - |\r?\n\r?\n## |\Z)", text)
    return [(rid, norm_text(body)) for rid, body in blocks]


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def sha8(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:8]


def sh(cmd):
    q = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (q.stdout or "") + (q.stderr or "")


def skill_files():
    out = []
    for root in SKILL_TREES:
        for base, _dirs, files in os.walk(root):
            for fn in files:
                if fn == "SKILL.md":
                    out.append(os.path.join(base, fn))
    return sorted(out)


def skill_pkg(skill_md):
    """A pi skill is its SKILL.md plus supporting files (pi docs configuration.md)."""
    d = os.path.dirname(skill_md)
    out = []
    for base, _dirs, files in os.walk(d):
        for fn in files:
            p = os.path.join(base, fn)
            if fn.endswith((".md", ".txt")) and ".bak-" not in fn and ".mid-" not in fn:
                out.append(p)
    return sorted(out)


def rel(p):
    for root in SKILL_TREES:
        if p.startswith(root):
            return os.path.relpath(p, root).replace("\\", "/")
    return p


REF = os.path.join(os.path.dirname(HOME), "references", "examples_archived.md")
results = []


def rec(name, ok, detail=""):
    results.append((name, bool(ok), detail))


home = read(HOME)
skills = skill_files()
pkg_docs = {}
for sm in skills:
    for f in skill_pkg(sm):
        pkg_docs[f] = read(f)
norm_docs = {f: norm_text(t) for f, t in pkg_docs.items()}
prose_docs = {f: prose(t) for f, t in pkg_docs.items()}
norm_home = norm_docs[HOME]

# ---- 1. the plan's check: each rule string appears in exactly one skill (verbatim prefix) -------------
parsed = parse_rules(home)
want = ["R%d" % i for i in range(1, 32)]
rec("rules_R1_to_R31_parsed_from_home", [r[0] for r in parsed] == want,
    "parsed %d rule blocks, ids %s" % (len(parsed), "R1..R31 in order" if [r[0] for r in parsed] == want
                                        else [r[0] for r in parsed]))
dups, thin = [], []
for rid, body in parsed:
    sig = body[:SIG_LEN]
    if len(sig) < 40:
        thin.append((rid, sig))
        continue
    hits = [f for f, txt in norm_docs.items() if sig in txt]
    if len(hits) != 1 or hits[0] != HOME:
        dups.append((rid, len(hits), [rel(h) for h in hits]))
rec("each_rule_string_in_exactly_one_skill", not dups and not thin and len(parsed) == 31,
    "%d/%d rule signatures unique to the home SKILL.md across %d skill-package files; duplicates=%s "
    "short-signature=%s" % (len(parsed) - len(dups) - len(thin), len(parsed), len(pkg_docs), dups or "none",
                            thin or "none"))
rec("scan_scope_all_skills_both_trees", len(skills) >= 10,
    "%d SKILL.md + %d supporting files scanned: %s" % (len(skills), len(pkg_docs),
     ", ".join(os.path.basename(os.path.dirname(p)) for p in skills)))
home_size = len(home.encode("utf-8"))
rec("home_skill_size_within_context_budget", home_size <= 30000,
    "SKILL.md = %d B (was 36,109 B with the verbatim examples inline; they live in "
    "references/examples_archived.md, read on demand). Largest skill on the box - report the load cost to Max."
    % home_size)

# ---- 2. the phrase check (Max item 5): a paraphrase of a rule is a duplicate -------------------------
rule_shingle = {}
for rid, body in parsed:
    for g in shingles(prose(body)):
        rule_shingle.setdefault(g, rid)
pointer_pkgs = []
for p in POINTERS:
    pointer_pkgs += [f for f in skill_pkg(p)]
for p in POINTERS:
    name = os.path.basename(os.path.dirname(p))
    hits = sorted(set((rule_shingle[g], " ".join(g)) for g in shingles(prose(read(p))) if g in rule_shingle))
    rec("no_rule_phrases_paraphrased_in_%s" % name, not hits,
        "%d-word shingles of home rules found in this SKILL.md: %s"
        % (SHINGLE, hits[:6] if hits else "none (0 of %d rule shingles)" % len(rule_shingle)))
ref_hits = []
for f in pointer_pkgs:
    if f in POINTERS:
        continue
    txt = prose(read(f))
    hits = sorted(set(" ".join(g) for g in shingles(txt) if g in rule_shingle))
    if hits:
        marked_hist = "history" in txt and "rn" in txt
        ref_hits.append((rel(f), len(hits), marked_hist, hits[:3]))
# A supporting file may keep archived rule wording ONLY if it declares itself history/superseded (Max's fix
# for the director pack: mark it history, stop sending writers there as a live guide).
unmarked = [h for h in ref_hits if not h[2]]
rec("no_rule_phrases_in_pointer_supporting_files", not unmarked,
    "supporting files carrying rule wording and NOT marked history: %s | all such files (path, hits, marked): %s"
    % (unmarked or "none", [(h[0], h[1], h[2]) for h in ref_hits] or "none"))
pn = {p: prose(read(p)) for p in POINTERS}
pinfo = []
for ph in KEY_PHRASES:
    q = prose(ph)
    in_pointers = [os.path.basename(os.path.dirname(p)) for p in POINTERS if q in pn[p]]
    in_home_rules = any(q in prose(b) for _, b in parsed)
    pinfo.append("%r pointers=%s home_rule=%s" % (ph, in_pointers or "none", "yes" if in_home_rules else "no"))
rec("max_named_key_phrases_absent_from_pointers",
    not any(ph in pn[p] for ph in KEY_PHRASES for p in POINTERS),
    "Max's four phrases: %s" % "; ".join(pinfo))

# ---- 3. internal duplication inside the home (Max: R26 overlapped R7) --------------------------------
pairs = []
for i in range(len(parsed)):
    ri, bi = parsed[i]
    si = shingles(prose(bi))
    for j in range(i + 1, len(parsed)):
        rj, bj = parsed[j]
        shared = si & shingles(prose(bj))
        if shared:
            pairs.append((ri, rj, sorted(" ".join(g) for g in shared)[:2]))
rec("home_rules_do_not_share_phrases", not pairs,
    "pairs of home rules sharing a %d-word phrase: %s" % (SHINGLE, pairs if pairs else "none"))

# ---- 4. audio: R7 is the only home of the rule; every file naming the blocks marks them deleted ------
fenced = re.findall(r"(?s)```.*?```", home)
strip_examples = home
for b in fenced:
    strip_examples = strip_examples.replace(b, "")
flat = " ".join(p.strip() for p in strip_examples.split("\n"))
sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat) if s.strip()]
audio_sents = [s for s in sents if "overall_soundscape" in s.lower() or "non_diegetic_music" in s.lower()]
neg = ("deleted", "delete", "never", "no ", "stop", "superseded", "not a prompt section", "hf #77",
       "discussion", "r7")  # v2: "block", "history", "nothing" removed (Max: they let any line pass)
r7 = dict(parsed)["R7"]
bad_sents = [s[:110] for s in audio_sents if not any(k in s.lower() for k in neg)]
rec("home_audio_rule_no_soundscape_block",
    len(audio_sents) >= 3 and not bad_sents and "never a section" in r7 and "overall_soundscape" in r7
    and "non_diegetic_music" in r7 and "end of" in r7,
    "%d sentences name the two blocks, %d without a deleted/forbidden marker: %s; R7 bans both and puts plain "
    "cues at the end: %s" % (len(audio_sents), len(bad_sents), bad_sents or "none",
                             "yes" if "never a section" in r7 and "end of" in r7 else "no"))
marked = []
for f, t in prose_docs.items():
    if "overall_soundscape" in t or "non_diegetic_music" in t:
        ok_mark = ("superseded" in t and "rn " in t) or ("delet" in t and "rn " in t)
        if not ok_mark:
            marked.append(rel(f))
rec("every_skill_file_naming_audio_blocks_marks_it_superseded", not marked,
    "files under any skill dir naming the two audio blocks without an R7 supersession/deletion marker: %s "
    "(this is the clause that caught director references/max-i2v-prompt-improve-v1.md)"
    % (marked or "none - all named files carry the R7 marker"))
rec("home_cites_tenstrip_hf77", "discussion #77" in home and "cartoon sounds" in home
    and os.path.join(COMMUNITY, "notes", "web", "tenstrip_hf77_audio_20261029.md") and os.path.exists(
        os.path.join(COMMUNITY, "notes", "web", "tenstrip_hf77_audio_20261029.md")),
    "owner ruling quoted verbatim + saved to notes/web")

# ---- 5. the lane rule lives in exactly one skill ------------------------------------------------------
te = prose("a POS built for another lane never enters Max TE")
te_files = [rel(p) for p in skills if te in prose_docs.get(p, "")]
rec("max_te_lane_rule_in_one_place", te_files == [rel(P_DIR)],
    "the Max-TE lane rule is stated in %s (the director owns the lane rule; ref2va points to it)"
    % (te_files if len(te_files) == 1 else te_files or "no skill"))

# ---- 6. the home satisfies the plan's U2 content requirements ----------------------------------------
rec("home_has_output_contract", "Output only the prompt" in norm_home and "Count words; nothing else" in norm_home,
    "R1 + the loop's 1c wording cited")
rec("home_adults_only_18plus", "Adults only, 18+" in norm_home
    and "minors are a hard stop: pause any item whose image shows a minor" in norm_home.lower()
    and "aged 28 by canon declaration" in norm_home and "21+" in norm_home,
    "adults-only 18+ floor + the 21+ canon-age declaration convention kept")
rec("home_examples_3_to_6", 3 <= len(re.findall(r"^### Example (\d+)", home, flags=re.M))
    + len(re.findall(r"(?m)^## Archived Example ", read(REF))) <= 6,
    "%d inline examples + %d archived in the skill package = %d (plan range 3-6)"
    % (len(re.findall(r"^### Example (\d+)", home, flags=re.M)),
       len(re.findall(r"(?m)^## Archived Example ", read(REF))),
       len(re.findall(r"^### Example (\d+)", home, flags=re.M))
       + len(re.findall(r"(?m)^## Archived Example ", read(REF)))))
rec("home_examples_sourced_as_planned",
    "p15_writer_skill.md" in home and "references/examples_archived.md" in home and "9,749 B" in home,
    "SKILL.md points at the p15 few-shots in the supporting file and states the measured size (was '~10 KB each', "
    "the file is 9,749 B for both)")
p15 = read(P15)
blocks = re.findall(r"```text\n(.*?)```", u(p15), flags=re.S)
ref_txt = u(read(REF))
verbatim = [i + 1 for i, b in enumerate(blocks) if b.strip() in ref_txt]
rec("home_has_all_p15_fewshots", len(blocks) >= 1 and len(verbatim) == len(blocks) and read(REF).count("\r\n") == 0,
    "p15 carries %d few-shots; reproduced character-for-character (LF-normalized, source is CRLF) in %s -> %s"
    % (len(blocks), rel(REF), verbatim))
ex2 = norm_text(home.split("### Example 2")[1].split("## 7.")[0]) if "### Example 2" in home else ""
rec("example2_carries_the_full_r11_clause",
    "of the reference pictures and in the first 5 seconds of this clip, preserving her face, hairstyle, body, skin "
    "and figure with complete fidelity" in ex2,
    "Example 2 uses the R11 clause in full (Max: it was shortened to '...'); scanned with whitespace normalised so "
    "hard wrapping cannot hide a shortening")
rec("no_negatives_in_r22_or_examples", not re.search(r"no mark, no swelling|no bruise, no tear", home),
    "R22 and Example 1 state the slap aftermath as positives (R24); the negative stack is gone")
rec("p15_writer_skill_untouched",
    "Grounding & Core Standards" in p15 and "Rubric & Review Guide" in p15 and "Few-Shot 1" in p15,
    "T-6 gate evidence (plain-wording standards + a detail checklist exist in p15); the file is not edited")
pe = sh('powershell -NoProfile -Command "Get-ChildItem C:\\ -Recurse -Depth 6 -Filter prompt_extend.py '
        '-EA SilentlyContinue | Select -First 3 -ExpandProperty FullName"').strip()
rec("wan_prompt_extend_absent_recorded", pe == "", "prompt_extend.py not on this box (C:\\ depth 6 + both "
    "ComfyUI-WanVideoWrapper trees searched) -> the T-6 gate is met by p15 alone; %r" % pe)
rec("home_has_detail_checklist", "Detail checklist" in home and "self-refine" in home,
    "section 5, adapted from p15's rubric, audio line updated for R7")
rec("home_points_out_who_defers", all(n in home for n in ("ref2va-prompt", "h3-ref2va-prompt-chain",
                                                           "alienpc-hardcore-i2v-director")),
    "section 7 names the pointer skills and the lanes that keep their own material")
rec("home_states_p15_single_copy_location",
    "C:\\Users\\derek\\5slock\\ralph-community\\notes\\p15_writer_skill.md" in home
    and not os.path.exists(os.path.join(COMMUNITY, "notes", "p15_writer_skill.md")),
    "the home names the one real copy of p15 (the old claim 'both notes roots point at the same file' was false)")

# ---- 7. PROMPT.md L16 -------------------------------------------------------------------------------
old = read(PROMPT_BAK).split("\n")
new = read(PROMPT).split("\n")
diff = [(i, a, b) for i, (a, b) in enumerate(zip(old, new)) if a != b]
l16 = new[15]
dead = [n for n in ("p15_writer_batch.py", "p15_driver.ps1") if n in l16]
named = re.findall(r"(?:notes\\[A-Za-z0-9_.-]+)|(?:[A-Za-z]:\\[A-Za-z0-9_.\\-]+)", l16)
missing_paths = []
for c in named:
    path = c if re.match(r"^[A-Za-z]:", c) else os.path.join(r"C:\Users\derek\5slock\ralph-community", c)
    if not os.path.exists(path):
        missing_paths.append(path)
rec("promptmd_one_line_only_changed", len(diff) == 1 and diff[0][0] == 15 and len(old) == len(new),
    "line %d changed, %d lines in both files" % (diff[0][0] + 1 if diff else -1, len(new)))
rec("promptmd_L16_dead_names_gone", not dead and len(named) >= 6, "dead names left: %s; %d paths now named"
    % (dead or "none", len(named)))
rec("promptmd_L16_every_path_exists", not missing_paths, "checked %d paths, missing: %s"
    % (len(named), missing_paths or "none"))

# ---- 8. backups, the mid snapshot, and the fix pass only shrinks -------------------------------------
bad = []
for bak, want8 in list(BACKUPS_U2.items()) + list(BACKUPS_FIX.items()):
    if not os.path.exists(bak):
        bad.append("%s MISSING" % bak)
    elif sha8(bak) != want8:
        bad.append("%s sha8=%s expected=%s" % (bak, sha8(bak), want8))
rec("backups_exist_with_pre_edit_bytes", not bad,
    "%d backups (5 u2 + 5 u2fix) verified by sha256 prefix: %s" % (len(BACKUPS_U2) + len(BACKUPS_FIX),
                                                                   bad or "all match"))
deltas = []
grew = []
for p in EDITED_IN_FIX:
    b, a = len(read(p + ".bak-20261029-u2fix")), len(read(p))
    deltas.append("%s %d->%d (%+d)" % (rel(p), b, a, a - b))
    if p in POINTERS and a > b + 400:  # cites/history markers add words; a rule restatement is caught by phrases
        grew.append(rel(p))
over_base = [rel(p) for p in POINTERS if len(read(p)) >= len(read(p + ".bak-20261029-u2"))]
rec("pointer_files_stay_below_pre_u2_size", not grew and not over_base,
    "no pointer grew by more than 400 B in the fix pass and none is at/above its pre-U2 size: grew=%s "
    "over_pre_u2=%s | deltas vs u2fix: %s" % (grew or "none", over_base or "none", "; ".join(deltas)))
mid_in_skill = [fn for fn in os.listdir(os.path.dirname(HOME)) if ".mid-" in fn]
rec("mid_snapshot_moved_out_of_skill_folder", not mid_in_skill and os.path.exists(MID_NOTES),
    "skill folder entries with '.mid-': %s; notes copy: %s (%d B)"
    % (mid_in_skill or "none", MID_NOTES, len(read(MID_NOTES)) if os.path.exists(MID_NOTES) else 0))
for p in POINTERS:
    bak = p + ".bak-20261029-u2"
    name = os.path.basename(os.path.dirname(p))
    t = read(p)
    points = ("h3-prompting" in t) and (HOME in t)
    leaked = [rid for rid, body in parsed if body[:SIG_LEN] in norm_text(t)]
    rec("pointer_%s_points_home" % name, points, "names the home skill and its path: %s" % points)
    rec("pointer_%s_carries_no_rule_text" % name, not leaked, "rule signatures present: %s" % (leaked or "none"))
    rec("pointer_%s_shrank_vs_u2_backup" % name, len(t) < len(read(bak)),
        "%d B -> %d B (-%d, pre-U2 baseline)" % (len(read(bak)), len(t), len(read(bak)) - len(t)))

# ---- 9. scope: no GPU, guard intact, no scripts/runs/p7/p3/specs touched -----------------------------
g = sh('powershell -NoProfile -ExecutionPolicy Bypass -File "C:\\AI\\director\\scripts\\gpu_guard.ps1"').strip()
rec("gpu_idle", g.startswith("IDLE"), g.splitlines()[0] if g else "no output")
t = sh('cd C:\\AI\\community && "%s" -m pytest -q %s 2>&1' % (PY, " ".join(GUARD_TESTS)))
m = re.search(r"(\d+) passed", t)
rec("youth_guard_tests_pass", bool(m) and int(m.group(1)) >= 26 and "failed" not in t,
    "pytest test_p6_review.py + test_guard_scope.py: %s" % (t.strip().splitlines()[-1] if t.strip() else "no out"))
# Copy-Item preserves LastWriteTime, so the backup's mtime is the SOURCE's; its ctime is the copy moment.
base_ts = min(os.path.getctime(p) for p in list(BACKUPS_U2) + list(BACKUPS_FIX)) - 120
touched = []
for sub in ("scripts", "p7", "p3", "runs", "specs"):
    for base, dirs, files in os.walk(os.path.join(COMMUNITY, sub)):
        if ".pytest_cache" in base or "__pycache__" in base:
            continue
        for fn in files:
            p = os.path.join(base, fn)
            try:
                if os.path.getmtime(p) >= base_ts:
                    touched.append(os.path.relpath(p, COMMUNITY).replace("\\", "/"))
            except OSError:
                pass
rec("no_scripts_runs_p7_p3_specs_touched", not touched,
    "source files under scripts/, p7/, p3/, runs/, specs/ written since the U2 backups (pytest caches excluded): %s"
    % (touched or "none - the loop code and every run record are untouched"))
changed = []
for base, dirs, files in os.walk(COMMUNITY):
    if ".git" in base:
        continue
    for fn in files:
        p = os.path.join(base, fn)
        try:
            if os.path.getmtime(p) >= base_ts:
                changed.append(os.path.relpath(p, COMMUNITY).replace("\\", "/"))
        except OSError:
            pass
ALLOW = ("skills/h3-prompting/SKILL.md", "skills/h3-prompting/references/examples_archived.md",
         "skills/h3-prompting/SKILL.md.bak-20261029-u2", "skills/h3-prompting/SKILL.md.bak-20261029-u2fix",
         "notes/u2_", "notes/u2fix_", "notes/web/tenstrip_hf77_audio_20261029.md", "notes/2026-10-29-U2",
         "notes/SKILL.md.mid-20261029-u2-examples", ".pytest_cache", "__pycache__", "community.log",
         "notes/actions.log", "notes/u1b_", "notes/u1_")
offlist = [c for c in changed if not c.startswith(ALLOW)]
rec("u2_writes_are_the_allowed_set", not offlist and len(changed) >= 5,
    "%d files written under C:\\AI\\community since the U2 backups, off-allowlist=%s: %s"
    % (len(changed), offlist or "none", sorted(changed)))
rec("evidence_files_present", os.path.exists(NOTE) and os.path.exists(MAX_VERIFY),
    "the DONE note and Max's verify file are both on disk: %s"
    % [os.path.basename(x) for x in (NOTE, MAX_VERIFY)])

print("U2 check v2 2026-10-29 (read-only)  home=%s" % HOME)
fails = 0
for name, ok, detail in results:
    if not ok:
        fails += 1
    print("%-4s %-52s %s" % ("PASS" if ok else "FAIL", name, detail))
print("VERDICT: %s (%d/%d clauses pass)" % ("ALL CLAUSES PASS" if fails == 0 else "%d FAIL" % fails,
                                            len(results) - fails, len(results)))
sys.exit(0 if fails == 0 else 1)
