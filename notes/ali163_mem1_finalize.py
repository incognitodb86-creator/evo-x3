#!/usr/bin/env python3
"""MEM1 finalize (CPU only): append the pass record to forge-learnings.md + self_diagnosis.md and
tick the MEM1 line in ralph-community/TASKS.md as ONE physical CRLF line.

Self-checks after writing: control-char scan per line, the tick line count (exactly 1 MEM1 line,
ticked, no new bullets), TASKS.md keeps CRLF, and the ticked line contains the required facts.
"""
import io
import sys

HIST = "C:/AI/community/notes/forge-learnings.md"
DIAG = "C:/AI/community/notes/self_diagnosis.md"
TASKS = "C:/Users/derek/5slock/ralph-community/TASKS.md"

REC = """
## MEM1 memory + skills update 2026-10-23T19:06 CT (ALI-163 loop 08, CPU only: 0 GPU calls, 0 renders)
- Built 3 Pi skills under C:/AI/community/skills (h3-hc-render, h3-prompting, forge-self-diagnose). Agent Skills form: a directory + SKILL.md with frontmatter name (lowercase, hyphens, <=64) and description (<=1024). Pi injects only name+description+path at startup and reads the body on demand; /skill:<name> forces a load, /reload re-scans.
- notes/skills_wiring.md documents the discovery paths (settings "skills" list = C:/Users/derek/.pi/agent/settings.json, .agents/skills/ upward from cwd, .pi/skills/, packages), the !/+ list syntax, the project-trust gate, and the one-line setting Max adds. Forge never edits Pi config (AGENTS.md Scope).
- skills/h3-prompting/SKILL.md = the v2 chunk skeleton, the body/face reference wording, positive body/skin vocabulary (the r3r/r3b vocabulary row), the 20 s refusal, per-chunk audio, and the PQ1/IM1 open list: PQ1 research first, then ONE-variable A/B (skin_text=off, everything else byte-identical, same seeds 51140011/51140111) - the write-up is in the skill, so the next pass cannot lose it.
- AGENTS.md Learnings rewritten to 15 dense bullets (longest 269 chars, 0 control chars) with Max's 3 audit items: ref_image_1 = the approved full-body start still vs ref_image_2/3 = face crops only; Derrick 2026-10-23 6:12 PM CT no KEEP on r1-r6/r3r/r3b -> learn + improve (IM1), KEEP is his; 243 frames = 10.125 s at 24 fps on the (frames-5) % 17 == 0 grid. Builder notes/ali163_mem1_agents.py, 5/5 self-destruct probes (0x07/0x08 control chars, 16-bullet cap, dropped body-reference line, CR-split line, clean artifact silent).
- notes/ali163_mem1_no_loss.py proved all 15 pre-MEM1 bullets survive verbatim in this file. Its FIRST version had a slicing bug: it extracted 0 bullets, reported "missing: 0" and printed OK - a green check that cannot fail. The fix (P0 gate on the extracted count, sentinel probe P1) is the lesson of loop 07 applied to a new builder.
- 4 self-inflicted denies this pass (denies.log 675-678): cat/tail/python-probe commands whose text contained a protected canon path or the deny log line echoed it = fiction-lock. Fix: read the deny log with the read tool only, and keep protected path text out of command strings; the rule is now a line in skills/forge-self-diagnose/SKILL.md.
- Budget untouched by MEM1: C:/Users/derek/5slock/ralph-community/logs/p7_budget.json used_min 472.9 / jobs 38 / cap 615 min / 45 jobs at 18:53:47.
"""

DIAGREC = """
## 2026-10-23T19:07 CT MEM1 pass (loop 08, ALI-163, CPU only)
- STEP 0 breaker: last line of logs/ralph.log = iter 01 start 2026-10-23 18:55:41 (iter 07 exited status=ok exit=0 ticks=+1 wall=39.8m denies=0 checkfails=0 scope=0 open=16). No STOP_RALPH at start, none written by this pass.
- denies.log read with the read tool (tail/cat of that file is what tripped the fiction lock 4 times this pass: 675-678, all self-inflicted command text, 0 guard bugs). Last 3 deny classes seen: fiction-lock x3, secret env probe x1 (EV1 test), protected-paths ralph.ps1 x1 (earlier pass, SCOPE fail + STOP_RALPH).
- Action: MEM1. 3 skills built (C:/AI/community/skills/{h3-hc-render,h3-prompting,forge-self-diagnose}/SKILL.md), notes/skills_wiring.md (Pi discovery paths + the setting Max adds; Pi config untouched = Max's), AGENTS.md Learnings merged 16 -> 15 with Max's 3 items, no-loss proof of the 15 old bullets in notes/forge-learnings.md, PQ1 one-variable A/B design written down.
- Health: TASKS.md 0 control chars (per-line scan), 18 CRLF lines, 16 open tasks after this tick; budget gate file read-only; 0 GPU calls this pass, GPU lock respected.
- Next: PQ1 (research, 144p proxy videos are fine), then IM1 (one-variable A/B render, same seeds). MEM1 left no open question for the next loop.
"""

TICK = ("- [x] MEM1 MEMORY + SKILLS UPDATE (29th, loop 08, 2026-10-23 19:07 CT, CPU only: 0 GPU calls, 0 renders, "
        "0 ComfyUI calls): built 3 Pi skills in the Agent Skills form - C:/AI/community/skills/h3-hc-render/SKILL.md "
        "(graph wiring, reference slots, canvas/frame math, budget gate, p7/JOB_REQUEST.json, objective proof) + "
        "C:/AI/community/skills/h3-prompting/SKILL.md (v2 chunk skeleton, body vs face reference wording, positive "
        "body/skin vocabulary, 20 s refusal, per-chunk overall_soundscape, and the PQ1/IM1 plan: research first, then "
        "ONE variable at a time = skin_text=off with everything else byte-identical on seeds 51140011/51140111) + "
        "C:/AI/community/skills/forge-self-diagnose/SKILL.md (per-pass ralph.log + denies.log read, self_diagnosis.md, "
        "deny classes, web-save check bomb, control-char/TASKS tick rules, self-destruct probes); "
        "C:/AI/community/notes/skills_wiring.md = how Pi discovers skills (settings skills list, .agents/skills, "
        ".pi/skills, packages) + the exact one-line setting Max adds (Pi config is Max's, untouched); AGENTS.md "
        "Learnings merged 16 -> 15 dense bullets (longest 269, 0 control chars) adding Max's 3 audit items - body = "
        "the approved full-body start still as the body/scene reference vs face crop = face+hair only (r3r-r6 shipped "
        "face crops only), Derrick 2026-10-23 6:12 PM CT NO KEEP on r1-r6/r3r/r3b so learn + improve one variable per "
        "render and KEEP stays Derrick's, and the chunking line 243 frames = 10.125 s at 24 fps on the (frames-5) % 17 "
        "== 0 grid (13 s at 24 fps = 312 frames); builders C:/AI/community/notes/ali163_mem1_agents.py (5/5 probes) + "
        "C:/AI/community/notes/ali163_mem1_no_loss.py (15/15 old bullets verbatim in notes/forge-learnings.md; the "
        "first version extracted 0 bullets and printed OK, fixed with a count gate + sentinel probe); 4 self-inflicted "
        "denies (denies.log 675-678, protected-path text in a command string) -> the read tool + a skill rule, 0 after; "
        "budget logs/p7_budget.json used_min 472.9 jobs 38 cap 615/45, unchanged by this pass")


def ctrl(text):
    """Per-line scan on CRLF-normalized text: a raw scan of a CRLF file flags every CR (13)."""
    out = []
    for i, l in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        c = [ord(x) for x in l if 0 < ord(x) < 32]
        if c:
            out.append((i, c))
    return out


def main():
    fails = []
    for s in (REC, DIAGREC, TICK):
        if ctrl(s):
            fails.append("control chars in payload: " + str(ctrl(s)[:2]))
        if "\\" in s:
            fails.append("backslash in payload (path-escape trap)")
    if fails:
        print("FAIL payload gates:", "; ".join(fails))
        return 1

    hist_txt = io.open(HIST, encoding="utf-8", newline="").read()
    if "## MEM1 memory + skills update" not in hist_txt:
        with io.open(HIST, "a", encoding="utf-8", newline="\n") as f:
            f.write(REC)
        print("appended the MEM1 record to forge-learnings.md")
    else:
        print("forge-learnings.md already carries the MEM1 record (idempotent re-run)")
    diag_txt = io.open(DIAG, encoding="utf-8", newline="").read()
    if "MEM1 pass (loop 08, ALI-163, CPU only)" not in diag_txt:
        with io.open(DIAG, "a", encoding="utf-8", newline="\n") as f:
            f.write(DIAGREC)
        print("appended the MEM1 pass to self_diagnosis.md")
    else:
        print("self_diagnosis.md already carries the MEM1 pass (idempotent re-run)")

    raw = io.open(TASKS, "r", encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    ids = [i for i, l in enumerate(lines) if l.startswith("- [ ] MEM1")]
    done = [i for i, l in enumerate(lines) if l.startswith("- [x] MEM1")]
    if not ids and len(done) == 1:
        print("TASKS.md already carries the ticked MEM1 line - verify-only pass (idempotent re-run)")
    elif len(ids) != 1:
        print(f"FAIL: {len(ids)} open MEM1 lines in TASKS.md")
        return 1
    else:
        i = ids[0]
        if not lines[i].endswith("Tick when AGENTS.md, forge-learnings.md and the 3 skills exist."):
            print("FAIL: the MEM1 line does not end as expected:", lines[i][-70:])
            return 1
        lines[i] = TICK
        out = nl.join(lines)
        with io.open(TASKS, "w", encoding="utf-8", newline="") as f:
            f.write(out)
        print("ticked MEM1")

    # ---- verify ----
    raw2 = io.open(TASKS, "r", encoding="utf-8", newline="").read()
    L2 = raw2.split(nl)
    opens = [l for l in L2 if l.startswith("- [ ]")]
    mem1 = [l for l in L2 if "MEM1" in l]
    if len(mem1) != 1:
        print(f"FAIL verify: {len(mem1)} lines mention MEM1 (the tick must be ONE physical line)")
        return 1
    if not mem1[0].startswith("- [x] MEM1"):
        print("FAIL verify: MEM1 line not ticked")
        return 1
    if raw2.count("\r\n") != len(L2) - 1:
        print("FAIL verify: TASKS.md is no longer pure CRLF")
        return 1
    if ctrl(raw2):
        print("FAIL verify: control chars in TASKS.md", ctrl(raw2)[:3])
        return 1
    for need in ("10.125 s", "NO KEEP", "skills_wiring.md", "skin_text=off", "472.9", "0 GPU calls",
                 "face crop", "h3-prompting", "forge-self-diagnose", "h3-hc-render"):
        if need not in mem1[0]:
            print(f"FAIL verify: tick text lost {need}")
            return 1
    print(f"OK ticked MEM1 as one physical line; {len(L2)} lines, {raw2.count(chr(13))} CR, "
          f"0 control chars, {len(opens)} open tasks left")
    print("OK appended the pass record to", HIST, "and", DIAG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
