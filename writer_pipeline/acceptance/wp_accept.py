"""Acceptance harness for the Render writer pipeline (all DRY: the pipeline has no queue option).
Runs cases through render_writer_pipeline.py in an isolated WP_HOME so setup runs never touch the live blacklist/state.
usage: wp_accept.py <suite> <out_root> [--home DIR] [--arm A|B] [--persona NAME] [--reps N] [--fresh]"""
import argparse, json, os, re, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

PY = sys.executable
PARODY = Path(r"C:\AI\community\scripts\parody")
LIVE_HOME = Path(r"C:\AI\render\writer_pipeline")
PM6 = Path(r"C:\AI\community\runs\u6_gemma_heretic_20261113\gemma_pmfix6")
POOL = Path(r"C:\AI\render\stills\approved_characters\POOL\flow_more_2026-10-19")
FOUR = [
    ("missionary", "she has sex with him", "missionary", POOL / "POOL_F034.jpg", PM6 / "u6_01_missionary" / "still_read.json"),
    ("doggy", "she has sex with him", "doggy", POOL / "POOL_F053.jpg", PM6 / "u6_02_doggy" / "still_read.json"),
    ("blowjob", "she gives him a blowjob", "blowjob", POOL / "POOL_F058.jpg", PM6 / "u6_03_blowjob" / "still_read.json"),
    ("talk", "short spoof noir banter only, no sex: she teases a detective who just walked in, three to five short lines",
     "talk", POOL / "POOL_F034.jpg", PM6 / "u6_04_talk" / "still_read.json"),
]
S034, S053, S058 = (FOUR[0][3], FOUR[0][4]), (FOUR[1][3], FOUR[1][4]), (FOUR[2][3], FOUR[2][4])
# Cowgirl / reverse-cowgirl on the waist-high S034 sideboard is a real surface_mismatch hard stop.
# Those asks run on a bed still; still_read is None so the pipeline vision-reads it. Never browse PixlStash.
SBED = (Path(r"C:\AI\render\stills\approved_characters\BEDROOM01\01_BEDROOM_LINGERIE.jpg"), None)
EXTRA = [  # six more asks for the 10-ask sampler A/B, same three stills
    ("cowgirl", "she rides him", "cowgirl", *SBED),
    ("doggy_rough", "he takes her rough from behind", "doggy", FOUR[1][3], FOUR[1][4]),
    ("bj_tease", "she teases him then gives him a slow blowjob", "blowjob", FOUR[2][3], FOUR[2][4]),
    ("missionary_slow", "slow sensual sex, she pulls him in", "missionary", FOUR[0][3], FOUR[0][4]),
    ("talk_spoof", "spoof infomercial banter only, no sex: she sells a ridiculous product to the camera, three short lines",
     "talk", FOUR[1][3], FOUR[1][4]),
    ("standing", "he takes her standing against the wall", "standing_mf", FOUR[2][3], FOUR[2][4]),
]


# coverage addendum B5: one dry ask per mode/overlay (name, ask, position, still, still_read[, scene, continue_from])
MODES18 = [
    ("m01_sex", "missionary on the bed, she's eager", "missionary", *S034),
    ("m02_oral", "blowjob on the sand, he talks, she's eager", "blowjob", *S058),
    ("m03_talk", "noir detective banter at the sideboard", "talk", *S034),
    ("m04_strip", "slow striptease, she peels the slip", "tease", *S034),
    ("m05_transition", "he turns her over from missionary to doggy", "doggy", *S034),
    ("m06_edge", "doggy, he edges her, denial", "doggy", *S053),
    ("m07_forced", "missionary, forced orgasm, she's restrained", "missionary", *S034),
    ("m08_cinematic", "cinematic doggy by the window light", "doggy", *S034),
    ("m09_gonzo", "gonzo amateur cowgirl on the couch", "cowgirl", *SBED),
    ("m10_pov", "POV blowjob, she looks up into the lens", "blowjob", *S058),
    ("m11_cnc", "reluctant CNC, he pins her wrists, doggy", "doggy", *S053),
    ("m12_taboo", "stepbrother roleplay, missionary, bratty", "missionary", *S034),
    ("m13_defeat", "defeated superheroine pinned on the rooftop", "missionary", *S034),
    ("m14_toy_solo", "solo with a wand on the bed", "female_solo", *S034),
    ("m15_toy_partner", "doggy, wand pressed to her while he thrusts", "doggy", *S053),
    ("m16_threesome", "MMF, she's on all fours, one behind, one in her mouth", "mmf", *S053),
    ("m17_spoof", "space-captain spoof, cowgirl, 16mm grain", "cowgirl", *SBED),
    ("m18_futa", "futa partner, missionary", "missionary", *S034),
    ("m19_titjob", "titjob, he talks to her", "titjob", *S058),
    ("m20_finish", "he finishes on her, facial", "finish", *S058),
]
# lost-features audit section 5 (Derrick, Prompt maker t243s811), dry only, NOT RUN YET. Pregnancy dropped. Sleep, mind-control
# and drugged are back as agreed roleplay (Derrick t1454u-t1457u): one consent line or wink in clip 1 before the sex.
# Telekinesis only as consensual play. No orc/fairy still
# found under the stills/ComfyUI input dirs (COND_ORC_POOL_EDGE_SUNSET.jpg), so the pool stills stand in until one is picked.
LOSTFEAT = [
    ("lf01_orc_doggy", "orc partner, standing doggy at the pool edge", "standing_mf", *S053),
    ("lf02_oversized", "massive oversized cock, slow missionary", "missionary", *S034),
    ("lf03_fairy", "tiny adult fairy rides him", "cowgirl", *SBED),
    ("lf04_giant_carry", "giant lifts the tiny woman, standing carry", "standing_mf", *S034),
    ("lf05_tentacles", "tentacles wrap her, solo still", "female_solo", *S034),
    ("lf06_telekinesis", "consensual telekinesis play: she asked him to hold her floating, missionary", "missionary", *S034),
    ("lf07_webcam", "webcam solo with a wand", "female_solo", *S034),
    ("lf08_bts", "BTS interview, off-screen interviewer asks her questions", "talk", *S034),
    ("lf09_vhs", "VHS 90s sex-tape doggy", "doggy", *S053),
    ("lf10_vampire", "vampire roleplay in her sheer white halter dress, missionary", "missionary", *S034),
    ("lf11_shoplift", "caught shoplifting roleplay, office desk", "standing_mf", *S034),
    ("lf12_ff_cunni", "FF cunnilingus on the bed", "ff_cunnilingus", *S034),
    ("lf13_ff_scissor", "FF scissoring on the bed", "ff_scissoring", *S034),
    ("lf14_anal_doggy", "anal doggy", "mf_anal", *S053),
    ("lf15_spooning", "spooning on the bed", "spooning", *S034),
    ("lf16_prone", "prone bone on the bed", "prone_bone", *S034),
    ("lf17_airplane", "airplane position", "airplane", *S034),
    ("lf18_piledriver", "piledriver", "piledriver", *S034),
    ("lf19_reverse", "reverse cowgirl", "reverse cowgirl", *SBED),
    ("lf20_twerk", "she twerks for him", "dance", *S034),
    ("lf21_male_solo", "male solo edging", "male_solo", *S034),
    ("lf22_ffm", "FFM on the bed", "ffm", *S034),
    ("lf23_mmf_double_bj", "MMF double blowjob", "mmf_double_blowjob", *S058),
    ("lf25_sleep", "sleep roleplay, she asked him to wake her up like that, spooning", "spooning", *S034),
    ("lf26_hypno", "hypnosis roleplay gag, she obeys his command, cowgirl", "cowgirl", *SBED),
    ("lf27_mdma", "two adults chose MDMA together, slow missionary", "missionary", *S034),
    ("lf24_handjob", "handjob", "handjob", *S058),  # expect a clean NOT_READY or a warning, not a silent closest-name blowjob
]
# long-scene spec section 7 (acc4, dry). T1: no KEEP-mp4 extension step exists yet, so the chain runs on --continue and is
# labelled chain_unverified. T3 needs the planner (wp_scene.py), which is not built, so it is not in this list.
def _fr(n, shots=None, k=1):
    return ["--frames", str(n)] + (["--shots", shots, "--shot-count", str(k)] if shots else [])
T1EXT = [
    ("t1_c1", "he takes her from behind", "doggy", *S053, "t1", None, _fr(192)),
    ("t1_c2", "keep going, he speeds up", "doggy", *S053, "t1", "t1_c1", _fr(141)),
    ("t1_c3", "keep going, harder, toward the end", "doggy", *S053, "t1", "t1_c2", _fr(226)),
]
def _t2(shots):
    sc, m = f"t2{shots[0]}", (lambda k: shots if shots == "multi" else None)
    return [
        (f"t2{shots[0]}_c1_talk", "short flirty banter only, no sex, three lines", "talk", *S034, sc, None, _fr(158)),
        (f"t2{shots[0]}_c2_reveal", "slow reveal, she lets the sheer white dress strap fall", "tease", *S034, sc, f"t2{shots[0]}_c1_talk", _fr(73)),
        (f"t2{shots[0]}_c3_strip", "she strips the sheer white dress", "tease", *S034, sc, f"t2{shots[0]}_c2_reveal", _fr(124)),
        (f"t2{shots[0]}_c4_transition", "he turns her onto her back, missionary", "missionary", *S034, sc, f"t2{shots[0]}_c3_strip", _fr(141)),
        (f"t2{shots[0]}_c5_act", "missionary, he takes her", "missionary", *S034, sc, f"t2{shots[0]}_c4_transition", _fr(243, m(1), 3)),
        (f"t2{shots[0]}_c6_ext", "keep going, faster", "missionary", *S034, sc, f"t2{shots[0]}_c5_act", _fr(192, m(1), 2)),
    ]
# acceptance-3 MMF S3 runs (generated, continued, S3 still) and the Render-pi asks with no still read (the pipeline
# reads the still itself). acc4 runs these through the same CLI Render runs, not through the pi chat.
MMF3 = [
    ("mmf1_generated", "MMF threesome on the log: one man in her mouth, one behind her", "mmf", *S053, "mmf", None, []),
    ("mmf2_continued", "MMF threesome, keep going, faster", "mmf", *S053, "mmf", "mmf1_generated", []),
    ("mmf3_s3_still", "MMF threesome on the log: one man in her mouth, one behind her", "mmf", *S053, None, None,
     ["--partner2-still", "community/flux_p1_20261030/M01_body.jpg", "--frames", "124"]),
]
PI = [
    ("pi_doggy_f001", "he takes her from behind.", "doggy", POOL / "POOL_F001.jpg", None),
    ("pi_missionary_f002", "he takes her on her back.", "missionary", POOL / "POOL_F002.jpg", None),
]
FANTASY = [  # spec 9.5
    ("f1_oversized", "massive oversized cock, slow missionary", "missionary", *S034, None, None, _fr(243)),
    ("f2a_orc", "orc partner takes her from behind", "doggy", *S053, "f2", None, _fr(243)),
    ("f2b_orc_ext", "orc partner keeps going, faster", "doggy", *S053, "f2", "f2a_orc", _fr(243)),
    ("f3_fairy", "tiny adult fairy with wings rides him", "cowgirl", *SBED, None, None, _fr(192)),
    ("f4_carry", "giant lifts the tiny woman, standing carry", "standing_mf", *S034, None, None, _fr(175)),
    ("f5_youth_seed", "tiny teen fairy rides him", "cowgirl", *S034, None, None, _fr(192)),  # must be blocked
]
COMBOS = [
    ("c1a_pov_doggy", "POV doggy", "doggy", *S053, "combo_pov", None),
    ("c1b_pov_continue", "POV doggy, keep going, faster", "doggy", *S053, "combo_pov", "c1a_pov_doggy"),
    ("c2_mmf_spitroast", "MMF spitroast on the bed", "mmf", *S034),
    ("c3a_strip", "she strips the slip, then he takes her on the sideboard", "tease", *S034, "combo_strip", None),
    ("c3b_sex_after_strip", "he takes her on the sideboard", "standing_mf", *S034, "combo_strip", "c3a_strip"),
    ("c4_defeat_cnc", "defeated heroine resists, he pins her, missionary", "missionary", *S034),
    ("c5_toy_partner", "doggy, wand on her clit while he thrusts", "doggy", *S053),
    ("c6_edge_oral", "teasing blowjob, she stops just before", "blowjob", *S058),
    ("c7_restraint_forced", "tied to the headboard, forced orgasm", "missionary", *S034),
    ("c8a_transition", "he turns her over from missionary to doggy", "doggy", *S034, "combo_trans", None),
    ("c8b_extension", "keep going, harder, he grabs her hair", "doggy", *S034, "combo_trans", "c8a_transition"),
    ("c9_unknown", "something sensual on the balcony", "sensual", *S034),
]


def comfy_busy():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=4) as r:
            q = json.loads(r.read())
        return bool(q.get("queue_running") or q.get("queue_pending"))
    except Exception:
        return False  # ComfyUI down = no H3 job


def make_home(home: Path, fresh: bool):
    if fresh and home.exists():
        arch = home.parent / "_archive"
        arch.mkdir(exist_ok=True)
        shutil.move(str(home), str(arch / f"{home.name}-{time.strftime('%Y%m%d-%H%M%S')}"))
    if not home.exists():
        home.mkdir(parents=True)
        for f in ("config.yaml", "writer_prompt.md"):
            shutil.copy2(LIVE_HOME / f, home / f)
        shutil.copytree(LIVE_HOME / "personas", home / "personas")
        for d in ("logs", "_archive", "scenes"):
            (home / d).mkdir(exist_ok=True)


def spoken(text):
    return [re.sub(r"^\[English\]\s*", "", m.strip()) for m in re.findall(r"<d>(.*?)</d>", text, re.S)]



def apply_pick_to_row(row, rd):
    """Flatten pick.json onto a summary row even when the run stopped before writer_output.txt (e.g. youth block)."""
    pk = json.loads((rd / "pick.json").read_text(encoding="utf-8"))
    added = " | ".join(pk.get("build_added") or [])
    row.update(mode=pk.get("mode"), overlays=pk.get("overlays"), act=pk.get("act_id"), status=pk.get("status"),
               pick=pk.get("pick"), score=pk.get("pick_score"), pick_pass=pk.get("pick_pass"),
               pick_hard=pk.get("pick_hard") or [], warnings=pk.get("warnings") or [],
               cloned_hits=pk.get("cloned_hits") or [], spoken_words=pk.get("spoken_words"),
               seconds=pk.get("seconds"), llm_seconds=pk.get("llm_seconds"),
               first_build=(pk.get("builds") or [{}])[0].get("status"), n_builds=len(pk.get("builds") or []),
               not_ready_reason=pk.get("not_ready_reason"), build_added=pk.get("build_added"),
               builder_primary_added=bool(re.search(r"(?i)PRIMARY MOTION", added)),
               builder_contact_added=bool(re.search(r"(?i)contact geometry", added)),
               cand_pass=sum(1 for c in (pk.get("candidates") or {}).values() if isinstance(c, dict) and c.get("pass")),
               tone=pk.get("slots_tone"), line_focus=pk.get("line_focus"))
    wo = rd / "writer_output.txt"
    if wo.exists():
        text = wo.read_text(encoding="utf-8", errors="replace")
        dd = text.split("detailed_description:", 1)[-1].strip() if "detailed_description:" in text else text
        row["lines"] = spoken(dd)
        row["opening"] = opening(dd)
    np_ = rd / "clip_NOT_READY.txt"
    row["not_ready_msg"] = np_.read_text(encoding="utf-8", errors="replace")[:300] if np_.exists() else ""
    return row


def opening(dd):
    m = re.search(r"\[Shot 1\][^.]*\.\s*([^.]*\.)", dd)
    return (m.group(1) if m else dd[:120]).strip()


def run_case(home, out_root, name, ask, pos, still, sr, scene=None, cont=None, extra=None, arm=None, persona=None, prior_root=None):
    while comfy_busy():
        print("PAUSE: H3 job in the ComfyUI queue; waiting 60 s", flush=True)
        time.sleep(60)
    rd = out_root / name
    cmd = [PY, str(PARODY / "render_writer_pipeline.py"), str(rd), "--ask", ask, "--position", pos, "--still", str(still),
           *(["--still-read", str(sr)] if sr else []), "--character", "FCSydny", "--config", str(home / "config.yaml")]
    if scene:
        cmd += ["--scene", f"accept_{out_root.name}_{scene}"]
    if cont:
        cont_dir = out_root / cont
        if not cont_dir.exists() and prior_root:
            cont_dir = Path(prior_root) / cont
        cmd += ["--continue", str(cont_dir)]
    cmd += list(extra or [])  # acc4: --frames / --shots / --shot-count
    if arm:
        cmd += ["--sampler-arm", arm]
    if persona:
        cmd += ["--persona", persona]
    assert "--queue" not in cmd
    env = dict(os.environ, WP_HOME=str(home))
    t = time.time()
    p = subprocess.run(cmd, cwd=str(PARODY), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    sec = round(time.time() - t, 1)
    row = {"case": name, "rc": p.returncode, "stdout": p.stdout.strip()[-500:], "stderr": p.stderr.strip()[-500:], "wall_s": sec}
    try:
        apply_pick_to_row(row, rd)
    except Exception as e:
        row["error"] = str(e)[:300]
    print(json.dumps({k: row.get(k) for k in ("case", "mode", "overlays", "act", "pick_hard", "warnings", "status", "first_build", "pick", "score", "seconds", "cloned_hits",
                                               "builder_primary_added", "builder_contact_added")}), flush=True)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("suite", choices=["four", "ten", "repeat", "modes", "combos", "lostfeat", "t1", "t2multi", "t2single", "fantasy", "mmf", "pi"])
    ap.add_argument("out_root")
    ap.add_argument("--home")
    ap.add_argument("--arm")
    ap.add_argument("--persona")
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--case", default="doggy")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--shared-state", help="one state dir (blacklist/recent/last_tone) for all suites, like production")
    ap.add_argument("--only", default="", help="comma-separated case names; empty runs the whole suite")
    ap.add_argument("--prior-root", default="", help="resolve --continue from this suite out dir when the parent is not in out_root")
    a = ap.parse_args()
    out = Path(a.out_root)
    out.mkdir(parents=True, exist_ok=True)
    home = Path(a.home) if a.home else LIVE_HOME / "acceptance" / ("home_" + out.name)
    make_home(home, a.fresh)
    if a.shared_state:
        import yaml
        Path(a.shared_state).mkdir(parents=True, exist_ok=True)
        cp = home / "config.yaml"
        c = yaml.safe_load(cp.read_text(encoding="utf-8"))
        c["shared_state_dir"] = str(a.shared_state)
        cp.write_text(yaml.safe_dump(c, sort_keys=False, allow_unicode=True), encoding="utf-8")
    if a.suite == "four":
        cases = FOUR
    elif a.suite == "modes":
        cases = MODES18
    elif a.suite == "combos":
        cases = COMBOS
    elif a.suite == "lostfeat":
        cases = LOSTFEAT
    elif a.suite == "t1":
        cases = T1EXT
    elif a.suite in ("t2multi", "t2single"):
        cases = _t2(a.suite[2:])
    elif a.suite == "fantasy":
        cases = FANTASY
    elif a.suite == "mmf":
        cases = MMF3
    elif a.suite == "pi":
        cases = PI
    elif a.suite == "ten":
        cases = FOUR + EXTRA
    else:
        base = {c[0]: c for c in FOUR}[a.case]
        cases = [(f"{base[0]}_r{i:02d}",) + base[1:] for i in range(1, a.reps + 1)]
    if a.only:
        want = {x.strip() for x in a.only.split(",") if x.strip()}
        cases = [c for c in cases if c[0] in want]
        missing = want - {c[0] for c in cases}
        if missing:
            raise SystemExit("unknown --only cases for this suite: " + ", ".join(sorted(missing)))
    rows = [run_case(home, out, *c, arm=a.arm, persona=a.persona, prior_root=(a.prior_root or None)) for c in cases]
    summ = {"suite": a.suite, "home": str(home), "arm": a.arm, "persona": a.persona, "rows": rows,
            "ready": sum(r.get("status") == "READY" for r in rows), "n": len(rows),
            "first_build_ready": sum(r.get("first_build") == "READY" for r in rows),
            "lint_pass": sum(bool(r.get("pick_pass")) for r in rows),
            "cloned_hits": sum(len(r.get("cloned_hits") or []) for r in rows),
            "builder_primary_added": sum(bool(r.get("builder_primary_added")) for r in rows),
            "builder_contact_added": sum(bool(r.get("builder_contact_added")) for r in rows),
            "mean_seconds": round(sum(float(r.get("seconds") or 0) for r in rows) / max(1, len(rows)), 1)}
    lines = [l.lower().strip(" .,!?") for r in rows for l in (r.get("lines") or [])]
    summ["spoken_lines"] = len(lines)
    summ["distinct_spoken_lines"] = len(set(lines))
    summ["identical_spoken_lines"] = len(lines) - len(set(lines))
    ops = [r.get("opening", "").lower() for r in rows]
    summ["distinct_openings"] = len(set(ops))
    (out / "summary.json").write_text(json.dumps(summ, indent=2, ensure_ascii=False), encoding="utf-8")
    print("SUMMARY " + json.dumps({k: v for k, v in summ.items() if k != "rows"}), flush=True)


if __name__ == "__main__":
    main()
