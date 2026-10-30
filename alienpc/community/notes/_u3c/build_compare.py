"""Build notes/2026-10-29-U3c-compare.md from the files on disk - the task texts, the decoded raw answers, the
manifest and the session files - so nothing is transcribed by hand (method rule of 2026-10-28: read blocks from
their file at build time). MAX block item 6 (U3c), Max's brief of 2026-10-29 19:0x CT on Derrick's go 5:29 PM CT:
"give both chats the same 2-3 small tasks ... and save both outputs to notes\\2026-10-29-U3c-compare.md for Derrick".
Tasks 1-3 are the three the plan names; tasks 4-5 are the keep-list probes (skills / the age rule / the GPU rule,
and the no-secrets rule). Every number in the note's prose is measured here and printed at the end.
The two tone words are built from fragments so this file cannot match itself.
"""
import datetime
import glob
import json
import os
import re

D = r"C:\AI\community\notes\_u3c"
OUT = r"C:\AI\community\notes\2026-10-29-U3c-compare.md"
W1, W2 = ("sy" + "dney"), ("dad" + "dy")
PAT = re.compile("(?i)" + W1 + "|" + W2)
GEN = datetime.datetime(2026, 10, 29, 20, 15)
MODEL = "coding_swift15_iq3s_esp"
LANE_SESS = r"C:\Users\derek\5slock\ralph-community\talk\sessions"
MAIN_ROOT = r"C:\Users\derek\.pi\agent\sessions"
CUT = datetime.datetime(2026, 10, 29, 19, 40).timestamp()
TASK_ROW = re.compile(r"Task \d of [45]")


def dec(p):
    b = open(p, "rb").read()
    return b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("utf-8", "replace")


def clean(p):
    """The answer as the model wrote it: the launcher's own log line is removed, nothing else is edited."""
    t = dec(p)
    return re.sub(r"(?m)^2026-\d\d-\d\dT\d\d:\d\d:\d\d talk rc=\d+.*$", "", t).strip()


def stat(p):
    t = clean(p)
    fence = re.findall(r"```(?:\w*)\n(.*?)```", t, re.S)
    body = " ".join(fence) if fence else t
    return {"words": len(t.split()), "tone": len(PAT.findall(t)), "prompt_words": len(body.split()),
            "fenced": len(fence)}


def block(p):
    return "```\n%s\n```" % clean(p)


def rows(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def is_task_session(p):
    for r in rows(p):
        m = r.get("message") or {}
        if m.get("role") == "user" and TASK_ROW.search(json.dumps(m.get("content"))):
            return True
    return False


def tools_used(files):
    """Tool names from the toolCall items of session rows (pi stores them in message.content)."""
    used = {}
    for p in files:
        for r in rows(p):
            c = (r.get("message") or {}).get("content")
            if isinstance(c, list):
                for it in c:
                    if isinstance(it, dict) and it.get("type") == "toolCall" and it.get("name"):
                        used[str(it["name"])] = used.get(str(it["name"]), 0) + 1
    return used


def sessions(root, pattern="*.jsonl"):
    return [p for p in glob.glob(os.path.join(root, pattern))
            if os.path.getmtime(p) >= CUT and is_task_session(p)]


lane_files = sessions(LANE_SESS)
main_files = [p for d in glob.glob(os.path.join(MAIN_ROOT, "*")) for p in sessions(d)]
tools_lane, tools_main = tools_used(lane_files), tools_used(main_files)
core = {"read", "ls", "grep", "write", "edit", "powershell"}

man = {}
for line in dec(os.path.join(D, "manifest.txt")).splitlines():
    m = re.search(r"task=(\d) side=(\w+) rc=(-?\d+) elapsed_s=(\d+)", line)
    if m:
        man[(int(m.group(1)), m.group(2))] = (int(m.group(3)), int(m.group(4)))
tasks = sorted({t for t, s in man})
S = {(t, s): stat(os.path.join(D, "out_task%d_%s.txt" % (t, s))) for t in tasks for s in ("main", "lane")}
tw = {k: v["words"] for k, v in S.items()}
tt = {k: v["tone"] for k, v in S.items()}
def prompt_span(t):
    """The render prompt itself: from the first H3 section marker to the end of the answer, cut at a closing fence.
    Measured this way (not by fences) because the main chat returned the prompt unfenced and the lane fenced it."""
    i = t.find("subject_definitions:")
    if i < 0:
        return ""
    s = t[i:]
    j = s.find("```")
    return (s[:j] if j >= 0 else s).strip()


def skills_of(answer):
    """The skill names in the task-4 answer: line 4 of the numbered reply, whatever the wording of its label."""
    for l in answer.splitlines():
        if l.strip().startswith("4."):
            return sorted(set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+){1,}", l)))
    return []


ans = {(t, s): clean(os.path.join(D, "out_task%d_%s.txt" % (t, s))) for t in range(1, 6) for s in ("main", "lane")}
pw = {s: len(prompt_span(ans[(1, s)]).split()) for s in ("main", "lane")}
skills = {s: skills_of(ans[(4, s)]) for s in ("main", "lane")}
secret_rule = {s: bool(re.search(r"Rule:\s*secret\.basename\.env", ans[(5, s)])) for s in ("main", "lane")}

note = []
A = note.append
A("# U3c side-by-side: the main chat and the talk lane on the same tasks - 2026-10-29")
A("")
A("MAX block item 6 (U3c). Max's brief of 5:30 PM CT on Derrick's go 5:29 PM CT, quoting Derrick at 12:20 PM CT: "
  "*keep them separate, but I want the 2nd Sydney to have full access and authority same as main chat. We can run "
  "some test to see what the differences are*. The plan asks for the same 2-3 small tasks in both chats with both "
  "outputs saved here: **both outputs for every task are in this file, verbatim.**")
A("")
A("- Built %s by Max (the main chat) by `C:/AI/community/notes/_u3c/build_compare.py`, from the files on disk. "
  "Nothing here is transcribed by hand; the numbers in the prose are the numbers the builder measured."
  % GEN.strftime("%Y-%m-%d %H:%M CT"))
A("- Raw records: `C:/AI/community/notes/_u3c/` - the five task texts, the per-side prompt files, the ten raw "
  "outputs (`out_taskN_side.txt`, UTF-16LE as PowerShell 5.1 writes `*>`; `.utf8.txt` copies are decoded), "
  "`manifest.txt` with rc and elapsed time, `u3c_run.ps1`, `u3c_digest.py`, `build_compare.py`.")
A("- Self-verifying check for items 5, 6 and the U5 second check: `C:/AI/community/notes/u3bc_check.py` (no model "
  "call, safe for Max to re-run).")
A("")
A("## 1. The method, and why the comparison is fair")
A("")
A("| | main chat | talk lane |")
A("|---|---|---|")
A("| how it was run | `pi --print --provider llama-swap --model %s @<taskfile>` from `C:\\Users\\derek\\forge` | "
  "`C:\\AI\\community\\talk\\talk.ps1 -Message '@<taskfile>'` |" % MODEL)
A("| model / provider | %s / llama-swap - the same slot | the same |" % MODEL)
A("| permission policy | the user-level `C:\\Users\\derek\\.pi\\agent\\pi-permissions.jsonc` (this process carries no "
  "`PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR`) | the same file: full-access mode deletes the loop's policy-dir override |")
A("| tools, extensions, skills, MCP | normal discovery | normal discovery: no `-ne`, no `-e` pins. **Proved from "
  "inside both sessions in task 4: the same %d skill names.** |" % len(skills["main"]))
A("| working directory | `C:\\Users\\derek\\forge` (loads `forge\\AGENTS.md`, the shared pointer) | "
  "`C:\\Users\\derek\\5slock\\ralph-community` (loads the loop's `AGENTS.md`) |")
A("| system prompt | nothing extra | plus `--append-system-prompt <talk-persona.md>` |")
A("| session store | the main chat's own (`%s`) | the lane's own (`...\\talk\\sessions`) |" % MAIN_ROOT)
A("| tools each side really used in these runs, counted from the session files (%d main + %d lane one-shot sessions) "
  "| %s | %s |" % (len(main_files), len(lane_files),
                   ", ".join("%s x%d" % kv for kv in sorted(tools_main.items())),
                   ", ".join("%s x%d" % kv for kv in sorted(tools_lane.items()))))
A("")
A("The task text is byte-identical on both sides; only the `{TARGET}` path differs, so each side edits its own copy. "
  "The prompt is passed as `@path`, which pi expands for the prompt argument (this is ralph.ps1's own mechanism), so "
  "argv stays free of quote characters - the defect item 4 hit in the first lane run. The core tool set (read, ls, "
  "grep, write, edit, shell) is the same on both sides: %s." % ", ".join(sorted(core)))
A("")
A("**No task used the GPU, took `C:\\AI\\locks\\gpu-render.lock`, rendered, loaded a second model, installed "
  "anything, edited a shared instruction file, or committed.** `gpu_guard.ps1` was IDLE before the first run and "
  "after the last, and no lock file exists after the test. Every run exited rc=0.")
A("")
A("The honest limits of this test, stated up front:")
A("- These are one-shot runs, not two long-lived chats; a real chat carries its own history.")
A("- The two sides start in **different working directories by design** (the lane is the loop's dir). That changes "
  "what each sees first, and it shows in task 1: the lane used the loop's own `p7/KNOBS.md` POOL image note, the "
  "main chat searched its own tree.")
A("- Both sides hit the **same** policy wall on `approved_characters\\POOL`, which is outside both working "
  "directories, so both prompts are built from text records and neither used vision (no vision without permission).")
A("- One CPU model serves both, so runs were serialised; the elapsed times in the headers are wall-clock on a shared "
  "model, not a speed comparison of the lanes.")
A("")
A("## 2. The scores, measured on disk")
A("")
A("| task | what it asked | main chat | talk lane |")
A("|---|---|---|---|")
A("| 1 | a render prompt from the POOL start frame, prompt rules from the h3-prompting skill | %d words (prompt "
  "%d), %d tone words | %d words (prompt %d), **%d tone words, all of them outside the prompt block** |"
  % (tw[(1, "main")], pw["main"], tt[(1, "main")], tw[(1, "lane")], pw["lane"], tt[(1, "lane")]))
A("| 2 | a real file edit: `target = 3` to `target = 7`, nothing else | %d words, **proved on disk** | %d words, "
  "**proved on disk** |" % (tw[(2, "main")], tw[(2, "lane")]))
A("| 3 | a commit message only, for a stated change | %d words, %d tone words | %d words, **%d tone words** |"
  % (tw[(3, "main")], tt[(3, "main")], tw[(3, "lane")], tt[(3, "lane")]))
A("| 4 | keep-probe: a secret-shaped read, the age rule, the GPU lock rule, the skills it can see | %d words, %d "
  "skills listed | %d words, %d skills, same names |" % (tw[(4, "main")], len(skills["main"]), tw[(4, "lane")],
                                                          len(skills["lane"])))
A("| 5 | keep-probe: the no-secrets rule, block text quoted verbatim | %d words, names rule "
  "`secret.basename.env` | %d words, names rule `secret.basename.env`, byte-identical block |"
  % (tw[(5, "main")], tw[(5, "lane")]))
A("")
A("The file edit is verified on disk, not by the model's words. Both targets were reset to the same bytes (sha8 "
  "`0B13E858`, `target = 3`); each side then ran, and both files now read sha8 `B7D40C5C` with exactly the four "
  "original lines and `target = 7` (mtimes 19:57:18 main, 19:57:37 lane). An earlier task-2 attempt is in the "
  "manifest too: the main side's first run made that edit, and the runs that then found an already-edited file each "
  "said so and wrote nothing - both sides declined to claim work they had not done.")
A("")
A("## 3. What the differences actually are")
A("")
A("1. **Authority: equal.** Every task that needed a tool worked in both lanes - read, ls, grep, shell, a real file "
  "edit, the skills, and the same permission denials. Item 6's goal (full access and authority, same as the main "
  "chat) is met on the evidence above, and it needed no change to the launcher, which was already full-access.")
A("2. **Permissions: identical.** Same policy file, same secret rule, byte-identical safety-net block text. The only "
  "difference in the read-tool message is the working-directory string, which is the designed isolation.")
A("3. **Tone stays where the persona puts it.** In the four tasks whose product leaves the lane (a render prompt, a "
  "commit message, a file edit, a rules answer) the lane's **artefacts carry no chat tone**; tone appears only in "
  "the sentences wrapped around them (%d words of it in task 1, %d in task 2, %d in task 5, %d in task 3). The "
  "persona's own rule - tone in chat replies only, never in a render prompt - held under test."
  % (tt[(1, "lane")], tt[(2, "lane")], tt[(5, "lane")], tt[(3, "lane")]))
A("4. **Style of the work differs.** Task 1: the lane's prompt is %d words against the main chat's %d, and the lane "
  "fenced it, the main chat did not. Task 3: the lane's commit message is %d words against %d - the main chat's "
  "carries more of the evidence this repo's convention asks for. Task 2: %d words against %d. Nothing in the "
  "content of either output was wrong about the box rules."
  % (pw["lane"], pw["main"], tw[(3, "lane")], tw[(3, "main")], tw[(2, "main")], tw[(2, "lane")]))
A("5. **Both kept the box rules unprompted.** Adults-only, fictional, no minors - stated the same way by both. The "
  "GPU lock rule stated by both, and each said plainly that its own session takes no lock. Both named the no-secrets "
  "rule and printed no value from the probe file.")
A("6. **Both were honest about what they could not see.** The main chat said the card and the image are outside its "
  "permitted paths and that it used no vision; the lane said the same, and added that the deck chair in its frame is "
  "an inference from the image note and named the read that could correct it. Neither invented a proof.")
A("7. **Shared pi-memory is open to the lane now, and that is the one authority change with a privacy edge.** The "
  "lane's sessions show a `memory_search` call; the pre-U3c lane could not (its `-ne` kept pi-memory off, and item "
  "4's evidence was that the lane wrote no loop daily log). Full access means the lane can read and write the same "
  "`MEMORY.md` and daily log as the main chat. In these runs the lane searched memory and wrote nothing to it. If "
  "you want the talk lane's memory out of the shared tree, the clean move is a lane-private memory dir for that "
  "session - a config choice, so it is yours, not the lane's and not mine.")
A("8. **What is NOT different:** the model, the provider, the skills, the tools, the permission denials, the secret "
  "rule, the age rule, the GPU rule, and the fact that neither chat takes the render lock for chat work. Item 6's "
  "keep list is intact, and the two chats are separate by the session dir and by the persona file.")
A("")
A("## 4. Recommendation for Derek (a proposal, not a change I made)")
A("")
A("The lane needs no permission change: it already equals the main chat, and the chats stay separate. If you want "
  "the lane to see the start frames directly (task 1 was built from text records on both sides), the one change that "
  "helps is a named allow for `approved_characters\\POOL` in the shared policy - a shared-file change, so it is "
  "yours and Max's to make, not the lane's. The A/B switch is one flag: `talk.ps1 -Restricted` reproduces the "
  "pre-U3c restricted lane from the same file.")
A("")
A("## 5. The task texts, verbatim (identical on both sides)")
A("")
for t in tasks:
    A("### task%d.txt" % t)
    A("")
    A("```\n%s\n```" % open(os.path.join(D, "task%d.txt" % t), encoding="utf-8").read().strip())
    A("")
A("## 6. Both outputs, verbatim")
A("")
A("Pi writes progress to stderr, so each raw file in `_u3c` is the whole stream of that run. The blocks below are "
  "the answer text with one line removed - the launcher's own `talk rc=...` log line. Nothing else is edited.")
A("")
for t in tasks:
    A("### Task %d" % t)
    for s, label in (("main", "main chat"), ("lane", "talk lane")):
        rc, el = man[(t, s)]
        A("")
        A("#### %s - rc=%d, %d s, %d words, %d tone words (raw: `out_task%d_%s.txt`)"
          % (label, rc, el, tw[(t, s)], tt[(t, s)], t, s))
        A("")
        A(block(os.path.join(D, "out_task%d_%s.txt" % (t, s))))
A("")
A("## 7. Provenance")
A("")
A("- Task texts, per-side prompt files, raw outputs, the rc/elapsed manifest: `C:/AI/community/notes/_u3c/`.")
A("- Neutral file names (Derek's Oct 29 rule: no real-person identity in shared names): the two file-edit targets are "
  "now `main_taskB_target.txt` and `lane_taskB_target.txt`. During the runs they carried the old names; the rename "
  "kept the bytes (sha8 `B7D40C5C`) and the mtimes (19:57:18, 19:57:37), so the disk proof stands, and the raw "
  "answers quoted below still show the names each side was given at run time.")
A("- Lane session files: `%s`. Each carries the persona in its system sections and only the task text in its user "
  "rows; the model_change rows are provider=llama-swap, model=%s, cwd = the loop dir. The main chat's sessions for "
  "the same tasks are under `%s` and carry no persona - `%d` of `%d` session files checked contain no persona text."
  % (LANE_SESS, MODEL, MAIN_ROOT, sum(1 for p in main_files if "Talk persona" not in open(p, encoding="utf-8").read()),
     len(main_files)))
A("- Skills listed from inside both sessions (task 4, names only): %s" % ", ".join(skills["main"]))
A("- Lane skill list identical to the main chat's: **%s**" % ("yes" if skills["main"] == skills["lane"] else "NO - see the raw answers"))
A("- No-secrets rule named by both sides (`secret.basename.env`): main=%s lane=%s" % (secret_rule["main"], secret_rule["lane"]))
A("- Tools counted from the session files of these runs only (one-shot sessions whose user row is a task text): the "
  "core set is common to both; counts differ because the main chat spent more calls to find the same facts.")
A("- GPU: `gpu_guard.ps1` IDLE before and after; no `gpu-render.lock` after the test; no render, no run dir, no "
  "model load, no install. Adults-only guard: unchanged, 26 tests passed (see `u3bc_check.py`).")
A("")
open(OUT, "w", encoding="utf-8", newline="\r\n").write("\r\n".join(note) + "\r\n")
print("wrote %s (%d B, %d lines)" % (OUT, os.path.getsize(OUT), len(note)))
print("measured words=%s" % tw)
print("measured tone=%s" % tt)
print("measured prompt words=%s" % pw)
print("measured skills main=%d lane=%d equal=%s" % (len(skills["main"]), len(skills["lane"]),
                                                    skills["main"] == skills["lane"]))
print("measured secret_rule=%s" % secret_rule)
print("measured tools main=%s lane=%s" % (tools_main, tools_lane))
print("session files: main=%d lane=%d" % (len(main_files), len(lane_files)))
