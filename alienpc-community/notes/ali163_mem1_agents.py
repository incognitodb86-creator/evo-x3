#!/usr/bin/env python3
"""MEM1 2026-10-23 (CPU only): rewrite AGENTS.md "## Learnings" as 15 merged bullets.

Keeps every operational command line that exists today, merged so the file's own cap
(<=15 bullets) is honest, and adds the three items Max's 6:40 PM CT audit found missing:
  1. body = the approved start still as the body/scene reference, face crop = face-only
     reference (r3r-r6 shipped face crops only, start still absent from the graph);
  2. Derrick 6:12 PM CT: no KEEP on r1-r6/r3r/r3b -> learn + improve (IM1), KEEP is his;
  3. the chunking line: 243 f = 10.125 s at 24 fps on the (frames-5) % 17 == 0 grid.

Self-checks + self-destruct probes at the end: the control-char scanner MUST fire on the
exact historical bug shape (0x07/0x08 from a non-raw C:\\ path), the bullet-count gate MUST
fire on 16 bullets, and the required-text gate MUST fire when the body-reference line is dropped.
"""
import io
import os
import sys

AGENTS = "C:/Users/derek/5slock/AGENTS.md"
HEADER = ("## Learnings (ALI-160 Huntley Ralph pattern: one dense operational line each, max 15, aim <=275 "
          "chars; MEM1 2026-10-23 merged 16 -> 15 and added Max's 3 audit items; verbatim history = "
          "C:/AI/community/notes/forge-learnings.md; skills = C:/AI/community/skills/)")

BULLETS = [
    r"- Full learnings (verbatim, append-only): C:/AI/community/notes/forge-learnings.md. Pi skills: C:/AI/community/skills/<name>/SKILL.md (MEM1); notes/skills_wiring.md = the pi setting Max adds.",
    r"- H3 refs (BQ1): 3 slots on c0 AND c1 - ref_image_1 = the approved start still (<Picture 1>, bodies/scene), ref_image_2/3 = face crops (face+hair); r3r-r6 shipped face crops only = no body reference. Read slots fullmatch r'ref_images\.ref_image_\d+'; seed = noise_seed.",
    r"- Chunk math: 243 f = 10.125 s at 24 fps on the (frames-5) % 17 == 0 grid (c0 length 124, window overlap 22 + extension 119, c1 141 generated/22 hidden, 124+119 = 243); 481 f = the 20 s shape Derrick rejected; duration = round(frames/24, 6).",
    r"- Graph internals: steps s0_sched/s1_sched, sampler ksel (euler), shift m_shift 10 video / 3 audio, NO cfg key at all; MiniMaxH3ImageToVideo has NO audio_vae (static rc 2); clips_json validated MUST be false; LoadImage resolves inside ComfyUI/input.",
    r"- Continuum 3.10.2: canvas multiple of 32 (1024x576, not 832x468), target_frames = chunks*chunk_seconds*fps, sampler has NO negative/CFG (append no: lines); ComfyUI 0.19.2 dropped sparse_blocks/sparse_size/max_dims = r3b nodes 10/11 schema-STALE.",
    r"- Derrick 2026-10-23 6:12 PM CT: NO KEEP on r1-r6/r3r/r3b - write notes/hc_lessons_20261023.md, improve ONE variable per render, re-render the same seeds (IM1). KEEP is Derrick's alone; no vision judge on explicit output.",
    r"- Render task = write C:/AI/community/p7/JOB_REQUEST.json (absolute path), tick, print DONE, END the iteration; proof/notes in the NEXT pass. A request is submittable only while p7/jobs/<id>.result.json is absent.",
    r"- Budget gate = C:/Users/derek/5slock/ralph-community/logs/p7_budget.json (used_min, jobs, cap_min 615, job_cap 45; R-lines 495/35, the +120 min/10 jobs = ALI-173 bakeoff). No ledger under C:/AI/community.",
    r"- Proof: ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0; audio = test ',audio' in the -show_streams csv line; sha256 = certutil.exe -hashfile <path> SHA256; graphs: plain cmp a b.",
    r"- Web saves: scripts/web_fetch.py picks the extension from the bytes (.json only if json.loads accepts, .html, .txt, non-200 -> .403.txt), then end every research pass with scripts/check_web_saves.py (rc 1 = offender, --fix renames).",
    r"- Deny classes seen: the fiction lock matches COMMAND TEXT, so never tail/cat the deny log in a shell (use the read tool); a credential-shaped env name in a command line = secret deny (probe env inside a .ps1). Never retry a deny.",
    r"- Notes/ticks: append with a quoted heredoc (cat >> f <<'EOF') or a python RAW string, forward slashes - a plain string with C:\ paths eats \n, \r, \a, \b (0x07 0x08 0x0A 0x0D). A TASKS.md tick is ONE physical line; TASKS.md is CRLF.",
    r"- A green check that cannot fail is worthless: every builder/self-check gets a self-destruct probe (restore the OLD wiring/wording in a clone; every detector MUST fire there and 0 on the real artifact). Builders + FINAL generators = notes/*.py.",
    r"- Forge owns diagnosing its own loop: each pass read ralph.log + notes/denies.log, write notes/self_diagnosis.md, fix what is in reach (Derrick 2026-10-23 1:48 PM CT). ralph.ps1 stays Max's - editing it = SCOPE fail; ask [!] Max.",
    r"- EV1 (ALI-179): Send-MaxEvent in scripts/max_event.ps1 = notes/events.log 6-key JSON always, webhook POST only when the env pair is set; 6 emit sites in ralph.ps1; tests notes/ev1_test.ps1 + notes/ev1_sites_test.ps1.",
]


def ctrl_scan(text):
    """Per-line control-char scan (a whole-file scan false-fails on CRLF 13/10)."""
    bad = []
    for i, line in enumerate(text.split("\n"), 1):
        codes = [ord(c) for c in line if 0 < ord(c) < 32]
        if codes:
            bad.append((i, codes))
    return bad


REQUIRED = ("ref_image_1", "10.125", "NO KEEP", "hc_lessons_20261023.md", "skills/<name>/SKILL.md",
            "p7_budget.json", "check_web_saves.py", "self_diagnosis.md", "ONE physical line")


def gate(bullets, text):
    """The real gates, shared by the writer and the probes (a probe that re-implements a
    weaker check proves nothing). Returns a list of failures; empty = pass."""
    fails = []
    if len(bullets) > 15:
        fails.append(f"bullet count {len(bullets)} > 15")
    for i, b in enumerate(bullets, 1):
        if not b.startswith("- "):
            fails.append(f"bullet {i} is not a '- ' bullet")
        if len(b) > 320:
            fails.append(f"bullet {i} too long: {len(b)} chars")
        prose = "ffprobe" not in b and "web_fetch" not in b and "p7_budget" not in b and "max_event" not in b
        if prose and len(b) > 275:
            fails.append(f"bullet {i} prose too long: {len(b)} chars (>275)")
    bad = ctrl_scan(text)
    if bad:
        fails.append(f"control chars {bad[:4]}")
    for need in REQUIRED:
        if need not in text:
            fails.append(f"required text missing: {need}")
    return fails


def main():
    if not os.path.exists(AGENTS):
        print("FAIL missing", AGENTS)
        return 1
    with io.open(AGENTS, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.replace("\r\n", "\n").split("\n")
    try:
        idx = next(i for i, l in enumerate(lines) if l.startswith("## Learnings"))
    except StopIteration:
        print("FAIL no ## Learnings header in", AGENTS)
        return 1
    head = lines[:idx]
    tail = [l for l in lines[idx + 1:] if l.startswith("## ")]
    if tail:
        print("FAIL unexpected section(s) after Learnings:", tail)
        return 1

    out = head + [HEADER] + BULLETS + [""]
    new_text = nl.join(out)

    fails = gate(BULLETS, new_text)
    if fails:
        print("FAIL gates:", "; ".join(fails))
        return 1

    with io.open(AGENTS, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)
    over230 = [len(b) for b in BULLETS if len(b) > 230]
    print(f"OK wrote {AGENTS}: {len(BULLETS)} bullets, {len(new_text)} bytes, line ending "
          f"{'CRLF' if nl == chr(13) + chr(10) else 'LF'}, 0 control chars")
    print(f"    longest bullet {max(len(b) for b in BULLETS)} chars; bullets over 230: {len(over230)} {over230}")

    # ---- self-destruct probes: the SAME gate() MUST fire on each historical bug shape ----
    bugs = []

    def fires(label, bullets, text, needle):
        hits = gate(bullets, text)
        if not any(needle in h for h in hits):
            bugs.append(f"{label} FAILED: gate stayed silent ({hits[:2]})")

    # probe 1: the historical corruption - one bullet carrying BELL/BACKSPACE from a non-raw C:\ path
    old = list(BULLETS[:15])
    old[12] = old[12] + " runs" + chr(7) + "li173_b2 and notes" + chr(8) + "ody_quality_r3b"
    fires("probe 1 (control chars 0x07/0x08)", old, nl.join(old), "control chars")
    # probe 2: the 16-bullet cap Max enforces, by adding one duplicate line
    fires("probe 2 (bullet count)", BULLETS + [BULLETS[0]], nl.join(BULLETS + [BULLETS[0]]), "bullet count")
    # probe 3: the body/scene reference line dropped (the r3r-r6 failure mode in notes form)
    stripped = new_text.replace("ref_image_1", "ref_slot")
    fires("probe 3 (required text)", BULLETS, stripped, "required text missing: ref_image_1")
    # probe 4: a bullet split by CR = the TASKS.md/tick-shape bug (one line becomes three)
    split = list(BULLETS[:15])
    split[11] = split[11].replace("; TASKS.md is CRLF.", "" + chr(13) + "TASKS.md is CRLF." + chr(13) + "tick shape")
    fires("probe 4 (CR split line)", split, nl.join(split), "control chars")
    # probe 5: non-negativity - the clean artifact must NOT fire any gate
    if gate(BULLETS, new_text):
        bugs.append("probe 5 FAILED: gate fires on the clean artifact")
    if bugs:
        print("PROBE FAIL:", "; ".join(bugs))
        return 1
    print("PROBES 5/5 OK: gate fires on 0x07/0x08 control chars, on 16 bullets, on the dropped "
          "body-reference line, on a CR-split line, and on NOTHING for the clean artifact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
