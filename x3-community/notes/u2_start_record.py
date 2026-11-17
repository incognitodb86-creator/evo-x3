import time
from pathlib import Path

NOW = time.strftime("%Y-%m-%d %H:%M")
ACTIONS = Path(r"C:/AI/community/notes/actions.log")

line = (
    "%s CT Pi (MAX block item 1 = U2 PROMPT-SKILL MERGE) START (Max brief 09:56 CT, Derrick's go 'Go, brief Forge on "
    "step 2'; plan C:/AI/community/notes/2026-10-29-forge-cleanup-plan.md section Units -> U2). File edits only, no "
    "GPU, no render, no model load. Scope: make C:\\AI\\community\\skills\\h3-prompting\\SKILL.md the single home for "
    "prompt rules (numbered rules R1-R30, 'output only the prompt', adults only 18+, plain wording + a detail "
    "checklist ONLY because notes\\p15_writer_skill.md already carries them - that file is at "
    "C:\\Users\\derek\\5slock\\ralph-community\\notes\\p15_writer_skill.md, not C:\\AI\\community\\notes; Wan "
    "prompt_extend.py is NOT on this box (searched C:\\ depth 6 and both ComfyUI-WanVideoWrapper trees) so the T-6 "
    "gate is satisfied by p15 alone); 3-6 examples - p15 carries exactly 2 few-shots, so 2 verbatim from p15 + the "
    "rest from proven run records, counted by the check script. ref2va-prompt, h3-ref2va-prompt-chain and the "
    "alienpc-hardcore-i2v-director prompt sections become short pointers. Repoint the dead PROMPT.md L16 scripts: "
    "p15_writer_batch.py and p15_driver.ps1 do not exist anywhere (measured), bk26_judge_harness.py does. Audio "
    "rule from TenStrip HF 10Eros-Max discussion #77 (Owner): 'overall_soundcape ... should be deleted. Prompt very "
    "normal audio queues in prompt or at the end of the main prompt.' - saved to notes/web/"
    "tenstrip_hf77_audio_20261029.md. Check to pass: each rule string appears in exactly one skill. Backups before "
    "every edit: 4 x SKILL.md.bak-20261029-u2 (the three C:\\Users\\derek\\.pi\\agent\\skills files are NOT a git "
    "repo, so the .bak is the only rollback) + PROMPT.md.bak-20261029-u2-l16. No existing prompt file, graph, run "
    "record or p15 file is rewritten: the audio change is forward-looking, the beta7 B2 default graph is untouched."
) % NOW


def norm(s):
    for a, b in (("\u2026", "..."), ("\u2192", "->"), ("\u2190", "<-"), ("\u2019", "'"), ("\u2018", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2014", "--"), ("\u2013", "-")):
        s = s.replace(a, b)
    return s


data = ACTIONS.read_bytes()
assert data.endswith(b"\n")
add = (norm(line) + "\n").encode("ascii")  # asserts ASCII
ACTIONS.write_bytes(data + add)
print("appended U2 START line to %s (+%d B, ASCII-clean)" % (ACTIONS, len(add)))
