"""item 5 U1 (2026-10-29): append the one progress.md line (the actions.log lines landed; this line
failed before because it carried a U+2026 ellipsis - here every non-ASCII form is normalised to ASCII
and the result is asserted ASCII before writing). Append-only, LF-terminated."""
from pathlib import Path

PROGRESS = Path(r"C:/Users/derek/5slock/ralph-community/notes/progress.md")
p = r"C:/AI/community/notes/item5_u1_check.py"

line = (
    "- 2026-10-29 [MAX item 5 = U1 quick fixes, 2 of 3 landed, 1 BLOCKED, no GPU] Derek 8:52 AM CT via Max2. "
    "[U1b DONE] PROMPT.md 0a fixed: it claimed 'fix_plan.md (pinned in ralph.ps1 argv)'; the measured truth is ralph.ps1:51 = pi --print ... '@$K\\PROMPT.md', i.e. ONLY PROMPT.md is passed, so 0a now tells the pass to read fix_plan.md (the queue) and specs\\* itself. Proof: %s parses ralph.ps1's argv and PROMPT.md's 0a (clause PASS) and Compare-Object vs PROMPT.md.bak-20261029-u1 shows exactly one line changed. "
    "[U1c DONE] C:/Users/derek/.pi/agent/skills/alienpc-hardcore-i2v-director/SKILL.md L25: the beta6_int8 line is now 'RETIRED / SUPERSEDED (was production 2026-10-09..2026-10-28; retired 2026-10-28 13:05 CT by Derek \"Use beta 7 always\"; superseded by the beta7 CURRENT KEEP above; history only, never for a new render)'. The U1 scan beta6_int8 over BOTH skill trees (~/.pi/agent/skills and C:/AI/community/skills) = 2 hits, both marked, 0 unmarked (the other is alienpc-local-video-ops L20, already PRIOR KEEP). That skills tree is NOT a git repo, so SKILL.md.bak-20261029-u1 is the only rollback there. "
    "[U1a BLOCKED] ralph.ps1 is protected for this agent: edit denied (matched 'edit:C:/Users/derek/5slock/ralph-community/ralph.ps1'); the enforcing rules are pi-permissions.jsonc:226-227 (edit/write ralph.ps1 = deny, overriding the older allow at :223-224), and :465 denies 'git -C ralph-community add -- ralph.ps1'. ralph.ps1 is byte-identical to ralph.ps1.bak-20261029-u1 (sha8 C7D98FE0) = untouched; per the brief's revert-on-fail, PROMPT.md 1b was reverted to coding_swift15_iq3s (verified byte-identical to the pre-U1 line), so the model pair stays consistent, just not on esp. "
    "Paste-ready for Max: flip pi-permissions.jsonc:226-227 to allow (as the 8:20 AM PROMPT.md removal at :171 did), then ralph.ps1 L6 $Model = 'coding_swift15_iq3s' -> 'coding_swift15_iq3s_esp' (+ the L3 usage comment) and PROMPT.md 1b -> '(coding_swift15_iq3s_esp, the ralph.ps1 default)'. Target id is real: models.json lists coding_swift15_iq3s_esp and settings.json defaultModel/model are already coding_swift15_iq3s_esp. "
    "Item-5 check: %s (parses the live files: ralph.ps1 param default, PROMPT.md 1b, 0a-vs-argv, and marks every beta6_int8 line across both skill trees). It exits 1 today because of the blocked sub-item, so the record is honest rather than a silent pass. Item 3 left exactly as written. The plan of record 'box brain 40_projects/max-fix-tests/plans/2026-10-29-forge-chat-tone-and-prompt-skill.md @4fbcfc9' is not on this box (searched C:\\ to depth 6), so it was not read. "
    "Commits: ralph-community fc2945b (PROMPT.md 0a), community e384abe (preflight, the check, the record script). No GPU, no render, no ComfyUI/llama-swap call.\n"
) % (p, p)

for a, b in (("\u2026", "..."), ("\u2192", "->"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " ")):
    line = line.replace(a, b)
add = line.encode("ascii")  # asserts ASCII
raw = PROGRESS.read_bytes()
assert raw.endswith(b"\n")
PROGRESS.write_bytes(raw + add)
print("appended 1 progress line (+%d B, ASCII-clean)" % len(add))
