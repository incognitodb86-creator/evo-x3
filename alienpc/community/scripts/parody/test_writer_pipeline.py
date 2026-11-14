"""Writer pipeline tests (Max Architect 3, 2026-11-13, Derrick t1409u): linter hard-fail rules (acceptance test 1),
phase-order rules (test 7), talk-only budget (test 9), state self-maintenance, and offline fault drills (test 5) with a
scripted writer and a stubbed dry build. No GPU, no network, no queue."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import build_request as br
import wp_router
import render_writer_pipeline as p
import wp_lint
import wp_state
from wp_llm import WriterDown

READ = {"read": {"room": None, "place": "beach at sunset", "surface": "driftwood log", "bed": False, "sheets": None,
                 "floor": "sand", "pose": "leaning against a log", "facing_camera": True, "framing": "medium shot",
                 "light": "golden hour, sunset glow", "people": 1,
                 "garments": [{"type": "bodysuit", "name": "sheer beige bodysuit", "look": "wet, translucent, tight"}],
                 "build": "athletic, toned", "skin": "wet, glistening", "hair": "blonde, wet, wind-blown"},
        "source": "C:\\AI\\render\\stills\\approved_characters\\POOL\\flow_more_2026-10-19\\POOL_F053.jpg"}

GOOD_SEX = ("[Shot 1] The camera holds a low three-quarter angle at hip height beside the driftwood log. At first, (S1) leans "
            "against the log in the golden hour glow, facing the lens, her sheer beige bodysuit clinging wet to her hips, and the "
            "surf hisses behind her. (S2) steps in from the left and turns her by the waist; she bends forward and drops to her "
            "hands and knees on the sand, her forearms braced on the bleached log as the wood creaks under her weight. He kneels "
            "behind her so his hips line up with hers, hooks the bodysuit at the back and pulls it aside to one hip, where it "
            "stays, and enters her vagina from behind with a low grunt. He sinks his penis in to the hilt and stays buried in her vagina through every "
            "drive. As it builds, PRIMARY MOTION - hard rear thrusts, two strokes a second, from behind with her forearms on the "
            "log; her wet hair swings and her body jolts forward on each slap of skin. (S2) says in a low voice, <d>[English] "
            "Sand on your knees, and you still push back.</d> (S1) says in a breathless voice, <d>[English] Deeper, the log is "
            "shaking.</d> By the end, she is still rocking back onto him and he keeps the same pace, gripping her hips. The wet "
            "slap of skin and her ragged gasps ride over the waves.")
GOOD_ORAL = ("[Shot 1] The camera sits low at her eye line beside the driftwood log. At first, (S1) leans against the log in the "
             "golden hour glow, her sheer beige bodysuit wet against her skin, and the surf hisses at her heels. (S2) steps in "
             "from the left; she slides down the log and kneels on the sand between his legs, palms on his thighs, as the sand "
             "crunches under her knees. She takes him in her hand and parts her lips, and he slides inside her mouth until her "
             "lips seal around the shaft, holding there as she works. As it builds, PRIMARY MOTION - slow deep sucking, one full "
             "cycle every second, her head bobbing along him; her wet hair sways and catches the light with each pull. (S2) says "
             "in a low voice, <d>[English] Look up at me, sand girl.</d> By the end, she is still bobbing at the same steady pace, "
             "his hand resting in her hair. Wet suction and her muffled moans carry over the waves.")
GOOD_TALK = ("[Shot 1] The camera holds a medium two-shot at chest height by the driftwood log. At first, (S1) leans against "
             "the log in the golden hour light, her sheer beige bodysuit dark with seawater, while the surf hisses behind her. "
             "(S2) steps out of the dune grass in a rumpled trench coat and stops an arm's length away, sand crunching under his "
             "shoes. (S1) says in a smoky voice, <d>[English] You tracked sand all the way here.</d> (S2) says in a clipped "
             "voice, <d>[English] Your bodysuit left a wet trail.</d> As it builds, she traces the log with one finger and the "
             "wood creaks softly under her nail. (S1) says in a teasing voice, <d>[English] Then arrest me, Detective.</d> By the "
             "end, he is still stepping closer, tipping his hat back while the waves keep rolling in and the coat flaps.")


def full(dd, kind="sex"):
    slots = {"place": "beach at sunset", "light": "golden hour", "hair": "blonde", "position": "doggy", "surface": "driftwood log"}
    card = {"partners": [{"label": "S2", "sex": "man", "age": 31, "build": "broad build", "attire": "dark swim trunks",
                          "enters_from": "the left"}], "summary": "(S1) and (S2) on the log"}
    return p.assemble_output(dd, card, slots, 2, kind)


def ctx(kind="sex", position="doggy", **kw):
    slots = p.make_slots(READ, "she has sex with him", position, kind, "t1", None)
    c = {"kind": kind, "slots": slots, "blacklist": [], "cloned": ["he sinks in to the base from behind and stays buried in her as the pace climbs"],
         "cfg": {"speech_words_max": 25, "blacklist_ratio": 0.8, "words_min": 90, "words_max": 190}}
    c.update(kw)
    return c


def hard(text, c):
    return wp_lint.lint(text, c)["hard"]


def test_regexes_are_imported_not_copied():
    for name in ("PRIMARY_RE", "TEMPO_RE", "CONTACT_RE", "ASIDE_RE", "OPENER_RE", "ACT_RE", "BODY_SOUND_RE", "PENETRATION_RE"):
        assert getattr(wp_lint, name) is getattr(br, "_" + name)


def test_good_samples_pass():
    assert hard(full(GOOD_SEX), ctx()) == []
    assert hard(full(GOOD_ORAL, "oral"), ctx("oral", "blowjob")) == []
    r = wp_lint.lint(full(GOOD_TALK, "talk"), ctx("talk", "talk"))
    assert r["hard"] == [] and r["spoken_words"] <= 25 and len(r["lines"]) == 3  # acceptance test 9


BAD = [
    ("no_primary", lambda t: t.replace("PRIMARY MOTION - hard rear thrusts,", "hard rear thrusts land")),
    ("no_tempo", lambda t: t.replace("two strokes a second", "harder and harder")),
    ("no_contact", lambda t: t.replace("stays buried in her vagina through every drive", "stays there through every drive")),
    ("clearance", lambda t: t.replace("pulls it aside to one hip", "grips it at one hip")),
    ("shot2", lambda t: t.replace("By the end,", "[Shot 2] By the end,")),
    ("timestamp", lambda t: t.replace("As it builds,", "At 0:03 as it builds,")),
    ("seq_word", lambda t: t.replace("As it builds,", "Then")),
    ("unfilled_slot", lambda t: t.replace("beside the driftwood log", "beside the <surface> log")),
    ("slot_surface", lambda t: t.replace("log", "rock")),
    ("speech_budget", lambda t: t.replace("Deeper, the log is shaking.",
                                          "Deeper, the log is shaking under us and I can feel every single grain of sand now.")),
    ("cloned", lambda t: t.replace("He sinks his penis in to the hilt and stays buried in her vagina through every drive.",
                                   "He sinks in to the base from behind and stays buried in her as the pace climbs.")),
    ("phase_anchor", lambda t: t.replace("At first, (S1) leans against the log", "(S1) waits by the log")),
    ("phase_order", lambda t: t.replace("As it builds, PRIMARY", "By the end, PRIMARY").replace(
        "By the end, she is still rocking", "she is still rocking")),
    ("static_end", lambda t: t.replace("By the end, she is still rocking back onto him and he keeps the same pace, gripping her hips.",
                                       "By the end, her hair is gold in the low sun.")),
]


@pytest.mark.parametrize("code,mut", BAD, ids=[b[0] for b in BAD])
def test_each_hard_rule_trips_alone(code, mut):
    bad = mut(GOOD_SEX)
    assert bad != GOOD_SEX
    r = wp_lint.lint(full(bad), ctx())
    codes = [i["code"] for i in r["issues"]]
    assert code in codes
    if code in wp_lint.SAFETY_HARD:
        got = r["hard"]
        assert got == [code] or (code == "clearance" and set(got) <= {"clearance", "clearance_missing"} and code in got)
    else:
        assert code not in r["hard"]


def test_header_order_and_blacklist():
    f = full(GOOD_SEX)
    swapped = f.replace("summary:", "SUMMARYTMP:").replace("retention_analysis:", "summary:").replace("SUMMARYTMP:", "retention_analysis:")
    assert "header_order" in [i["code"] for i in wp_lint.lint(swapped, ctx())["issues"]]
    assert "header_order" not in hard(swapped, ctx())
    assert hard(f, ctx(blacklist=["Deeper, the log is shaking!"])) == ["blacklist"]
    assert hard(f, ctx(blacklist=["Stay still for me."])) == []


def test_oral_rules():
    bad = GOOD_ORAL.replace("he slides inside her mouth until", "his hips flush, he slides inside her mouth until")
    assert hard(full(bad, "oral"), ctx("oral", "blowjob")) == ["oral_contact"]


def test_talk_rules():
    two = GOOD_TALK.replace(" (S1) says in a teasing voice, <d>[English] Then arrest me, Detective.</d>", "")
    r = wp_lint.lint(full(two, "talk"), ctx("talk", "talk"))
    assert "talk_lines" in r["hard"]
    r2 = wp_lint.lint(full(GOOD_TALK.replace("Then arrest me, Detective.", "Then arrest me, Detective, right now, cuff me to that log and walk me home slowly."), "talk"),
                      ctx("talk", "talk"))
    assert "speech_budget" in [i["code"] for i in r2["issues"]] and "speech_budget" not in r2["hard"]


def test_chain_rules():
    scene = {"done_actions": ["hooks the bodysuit at the back and pulls it aside to one hip"],
             "ending_state": {"garments": {"item:bodysuit": "aside"}, "pov": False}}
    assert "chain_restate" in [i["code"] for i in wp_lint.lint(full(GOOD_SEX), ctx(scene=scene))["issues"]]
    assert "chain_restate" not in hard(full(GOOD_SEX), ctx(scene=scene))
    reset = GOOD_SEX.replace("her sheer beige bodysuit clinging wet to her hips", "her sheer beige bodysuit covering her hips again")
    r_reset = wp_lint.lint(full(reset), ctx(scene={"done_actions": [], "ending_state": {"garments": {"item:bodysuit": "aside"}}}))
    assert "chain_garment_reset" in [i["code"] for i in r_reset["issues"]] and "chain_garment_reset" not in r_reset["hard"]


def test_builder_preview_keeps_writer_lines():
    pv = p.builder_preview_fn(READ, "doggy", "she has sex with him")(full(GOOD_SEX))
    assert "error" not in pv, pv
    added = " | ".join(pv["added"])
    assert "PRIMARY MOTION with tempo" not in added and "contact geometry line" not in added


# ---- state ----------------------------------------------------------------------------------------------------------
def test_blacklist_fifo_and_corrupt(tmp_path):
    bl = tmp_path / "dialogue_blacklist.jsonl"
    for i in range(25):
        wp_state.update_blacklist(bl, [f"line number {i} here"], f"r{i}")
    rows = wp_state.load_blacklist(bl)
    assert len(rows) == 20 and rows[0]["line"] == "line number 5 here"
    bl.write_text("{not json\n", encoding="utf-8")
    events = []
    assert wp_state.load_blacklist(bl, lambda e, d: events.append(e)) == []
    assert events == ["blacklist_corrupt_rebuilt"] and bl.read_text() == ""
    assert list((tmp_path / "_archive").glob("dialogue_blacklist.jsonl.corrupt-*"))


def test_cloned_phrases_and_whitelist():
    prompt = 'Contact keyword. Shape only: "he sinks in to the base from behind". Tempo "two hard strokes a second". "fully sheathed inside her".'
    c = wp_state.build_cloned(prompt, [])
    assert "he sinks in to the base from behind" in c
    assert "fully sheathed inside her" not in c and "two hard strokes a second" not in c


def test_seeds_deterministic():
    assert p.seed_for("run1", "ask", 1) == p.seed_for("run1", "ask", 1) != p.seed_for("run1", "ask", 2)


# ---- offline pipeline drills (scripted writer, stubbed dry build) -----------------------------------------------------
CARD = {"summary": "(S1) taken from behind on the log", "camera": "low three-quarter",
        "partners": [{"label": "S2", "sex": "man", "age": 31, "build": "broad build", "attire": "dark swim trunks", "enters_from": "the left"}],
        "anchor": {"action": "leans on the log", "sound": "surf"},
        "onset": {"exit": "drops to hands and knees", "load": "forearms", "height": "he kneels", "clearance": "bodysuit aside at the back",
                  "entry": "enters from behind", "sound": "wood creak"},
        "development": {"primary_motion": "hard rear thrusts", "tempo_word": "strokes a second", "contact_keyword": "buried in her",
                        "follow_through": ["hair swings"], "sound": "slap", "line_topics": ["S2: urges her on"]},
        "result": {"action": "still rocking", "sound": "gasps"},
        "end_state": {"pose": "hands and knees", "garments": {"bodysuit": "aside"}, "contact": "buried", "camera": "low", "pov": False}}


@pytest.fixture
def home(tmp_path, monkeypatch):
    h = tmp_path / "home"
    (h / "personas").mkdir(parents=True)
    (h / "writer_prompt.md").write_text("WRITER PROMPT\nYou write clips.\n\nCRAFT RULES\n- Rule.\n", encoding="utf-8")
    cfg = {"model_alias": "gemma4_heretic_poly_think", "endpoint": "http://127.0.0.1:9/v1", "retry_backoff_s": [0, 0, 0],
           "timeout_s": 2, "n_candidates": 3, "sampler_arm": "B", "samplers": {"B": {"temperature": 1.0}},
           "judge_sampler": {"temperature": 0.01, "top_k": 1}, "lint": {}, "position_kinds": {"sex": ["doggy"], "talk": ["talk"]}}
    (h / "config.yaml").write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setattr(p, "PIPE_DIR", h)
    monkeypatch.setattr(p, "RUNS_ROOT", tmp_path / "runs")
    return h


def scripted(monkeypatch, prose, down_on=None):
    calls = []

    def chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose=""):
        calls.append(purpose)
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        if down_on and down_on(purpose, len(calls)):
            raise WriterDown("fault drill: writer killed")
        if purpose.startswith("beat_card"):
            return json.dumps(CARD)
        if purpose == "judge":
            return '{"best": "A"}'
        return prose(purpose)
    monkeypatch.setattr(p.Client, "chat", chat)
    return calls


def stub_build(monkeypatch, status="READY"):
    def run_build(run_dir, ask, position, still, character, timeout=300, extra=None):
        rep = {"status": status, "reason": None if status == "READY" else "W5 test", "build": {"added": [], "speech": {"dropped": []},
               "state": {"garments": {"item:bodysuit": "on"}, "writer_aside": ["item:bodysuit"]}}, "frames": 243}
        (Path(run_dir) / "build_report.json").write_text(json.dumps(rep), encoding="utf-8")
        return {"status": status, "rc": 0 if status == "READY" else 3, "stdout": status, "stderr": "", "report": rep,
                "seconds": 0.0, "reason": rep["reason"]}
    monkeypatch.setattr(p, "run_build", run_build)


def job(tmp_path, name, **kw):
    srp = tmp_path / "sr.json"
    srp.write_text(json.dumps(READ), encoding="utf-8")
    j = {"run_dir": str(tmp_path / "runs" / name), "ask": "she has sex with him", "position": "doggy", "still": READ["source"],
         "still_read": str(srp), "character": "FCSydny"}
    j.update(kw)
    return j


def test_happy_path_and_blacklist_update(home, tmp_path, monkeypatch):
    scripted(monkeypatch, lambda purpose: GOOD_SEX)
    stub_build(monkeypatch)
    cfg = p.load_config(home / "config.yaml")
    r = p.run_clip(job(tmp_path, "c1"), cfg, lambda *a: None)
    assert r["status"] == "READY" and r["pick"].startswith("cand_") and r["warnings"] == []
    d = Path(r["run_dir"])
    for f in ("still_read.json", "slots.json", "beat_card.json", "cand_1.txt", "lint_1.json", "pick.json", "writer_output.txt"):
        assert (d / f).exists(), f
    lines = [x["line"] for x in wp_state.load_blacklist(home / "dialogue_blacklist.jsonl")]
    assert "Deeper, the log is shaking." in lines


def test_fault_all_fail_lint_fallback(home, tmp_path, monkeypatch):
    # the normalizer may add a missing label, so the all-fail case drops the label AND the tempo
    bad = GOOD_SEX.replace("PRIMARY MOTION - hard rear thrusts, two strokes a second,", "hard rear thrusts land")
    bad = bad.replace("At first, (S1)", "At first, (S1), 16 years old,")  # youth_hint is a hard ready-blocker (survives normalize)
    calls = scripted(monkeypatch, lambda purpose: bad)
    stub_build(monkeypatch)
    r = p.run_clip(job(tmp_path, "c2"), p.load_config(home / "config.yaml"), lambda *a: None)
    assert "lint_fail_fallback" in r["warnings"] and "rewrite" in calls and r["builds"]  # the build still ran
    # PM acc4 #8: a lint-fail fallback never ships READY; score must be >= 60 with no hard flag
    assert r["status"] == "NOT_READY", r.get("pick_score")


def test_fault_writer_down_next_clip_proceeds(home, tmp_path, monkeypatch):
    scripted(monkeypatch, lambda purpose: GOOD_SEX, down_on=lambda purpose, n: n == 2)
    stub_build(monkeypatch)
    cfg = p.load_config(home / "config.yaml")
    events = []
    r1 = p.run_clip(job(tmp_path, "c3"), cfg, lambda e, d=None: events.append(e))
    r2 = p.run_clip(job(tmp_path, "c4"), cfg, lambda e, d=None: events.append(e))
    assert r1["status"] == "writer_down" and "writer_down" in events
    assert r2["status"] == "READY"


def test_fault_client_retries_then_writer_down(home, monkeypatch):
    """Client path (no socket: the suite's CPU fixture blocks connects): the fault switch fails every try -> WriterDown."""
    from wp_llm import Client
    monkeypatch.setenv("WP_FAULT_WRITER_DOWN_AFTER", "0")
    events = []
    c = Client({"model_alias": "x", "endpoint": "http://127.0.0.1:9/v1", "retry_backoff_s": [0, 0, 0], "timeout_s": 1},
               lambda e, d=None: events.append(e))
    with pytest.raises(WriterDown):
        c.chat([{"role": "user", "content": "hi"}], {}, 1, 5, purpose="probe")
    assert events.count("writer_retry") == 3


def test_fault_corrupt_blacklist_pipeline(home, tmp_path, monkeypatch):
    (home / "dialogue_blacklist.jsonl").write_text("garbage{{\n", encoding="utf-8")
    scripted(monkeypatch, lambda purpose: GOOD_SEX)
    stub_build(monkeypatch)
    events = []
    r = p.run_clip(job(tmp_path, "c5"), p.load_config(home / "config.yaml"), lambda e, d=None: events.append(e))
    assert "blacklist_corrupt_rebuilt" in events and r["status"] == "READY"


def test_beat_card_invalid_twice_skips(home, tmp_path, monkeypatch):
    def chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose=""):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        return "not json" if purpose.startswith("beat_card") else GOOD_SEX
    monkeypatch.setattr(p.Client, "chat", chat)
    stub_build(monkeypatch)
    r = p.run_clip(job(tmp_path, "c6"), p.load_config(home / "config.yaml"), lambda *a: None)
    assert "beat_card_skipped" in r["warnings"] and r["status"] == "READY"


def test_two_clip_chain_scene_state(home, tmp_path, monkeypatch):
    scripted(monkeypatch, lambda purpose: GOOD_SEX)
    stub_build(monkeypatch)
    cfg = p.load_config(home / "config.yaml")
    r1 = p.run_clip(job(tmp_path, "s1c1", scene="scn1"), cfg, lambda *a: None)
    assert r1["status"] == "READY"
    st = json.loads(wp_state.scene_path(tmp_path / "runs", "scn1").read_text())
    assert len(st["clips"]) == 1 and st["clips"][0]["ending_state"]["garments"]["item:bodysuit"] == "aside"
    for k in ("clip_id", "primary_beat", "opening_state", "ending_state", "anchors", "camera", "spoken_dialogue", "ambient_sfx",
              "frame_budget", "method", "done_actions"):
        assert k in st["clips"][0], k
    r2 = p.run_clip(job(tmp_path, "s1c2", scene="scn1", **{"continue": r1["run_dir"]}), cfg, lambda *a: None)
    # clip 2 inherits clip 1: same prose restates done actions and repeats lines -> lint flags them (fallback warning)
    lint1 = json.loads((Path(r2["run_dir"]) / "lint_1.json").read_text())
    assert "blacklist" in lint1["hard"]
    assert json.loads((Path(r2["run_dir"]) / "slots.json").read_text())["inherited"]["garments"]["item:bodysuit"] == "aside"


def test_normalize_prose_label_and_brackets():
    dd = ("[Shot 1] The camera holds. At first, (S1) sits. (S1) says in a sharp voice, <d>[Look at my top]</d>. "
          "As it builds, he drives into her at one stroke every second, steady. By the end, she arches.")
    out = p.normalize_prose(dd, "sex")
    assert "As it builds, PRIMARY MOTION - he drives" in out and "<d>Look at my top</d>" in out
    assert p.normalize_prose(dd, "talk").count("PRIMARY MOTION") == 0
    assert "<d>[English] hi</d>" in p.normalize_prose("<d>[English] hi</d>", "talk")
    assert "PRIMARY MOTION" not in p.normalize_prose("[Shot 1] As it builds, he drives into her hard.", "sex")


def test_partner_line_from_ask_not_card():
    slots = {"ask": "she has sex with him", "garments_all": ["sheer mesh crop top"], "build": "curvy", "position": "doggy",
             "surface": "log", "place": "driftwood log", "light": "golden hour", "hair": "blonde"}
    card = {"partners": [{"sex": "woman", "age": 28, "build": "curvy", "attire": "wet sheer mesh crop top", "enters_from": "still"}]}
    out = p.assemble_output("[Shot 1] x.", card, slots, 2, "sex")
    assert ("<Subject 2> is the man, an adult, 28 years of age, athletic build, in a dark t-shirt and jeans, who enters from "
            "the right and he is (S2).") in out
    assert "and the driftwood log," in out


def test_slot_word_double_s_and_sound_tail():
    import wp_lint
    assert wp_lint._has_word("her white dress clings", "dress") and wp_lint._has_word("on the logs", "logs")
    assert wp_lint._has_word("on the log", "logs") and not wp_lint._has_word("a dre", "dress")


def test_every_act_routes_to_a_mode():
    """All acts in acts.yaml map to a mode with a beat schema, a prose block and lint rules (no silent 'sex' default).
    Reads the installed config.yaml (the real position_kinds map)."""
    import wp_lint
    if not p.CONFIG_PATH.exists():
        pytest.skip("no installed config.yaml")
    cfg = p.load_config(p.CONFIG_PATH)
    acts = br.load_acts_registry()
    mapped = {a for v in cfg["position_kinds"].values() for a in v}
    assert set(acts) <= mapped, sorted(set(acts) - mapped)
    want = {"talk": "talk", "blowjob": "oral", "mmf_double_blowjob": "oral", "ff_cunnilingus": "oral", "titjob": "partner",
            "finish": "partner", "tease": "solo", "dance": "solo", "female_solo": "solo", "male_solo": "solo", "doggy": "sex",
            "mmf": "sex", "ffm": "sex", "threesome": "sex"}
    for act in acts:
        k = p.position_kind(act, cfg)
        assert k in p.MODES and k in wp_lint.MODE_RULES, (act, k)
        if act in want:
            assert k == want[act], (act, k)
    assert p.position_kind("strip", cfg) == "solo"
    assert br.get_act("strip") is br.get_act("tease")
    assert not wp_lint.mode_rules("partner")["contact"] and not wp_lint.mode_rules("solo")["contact"]
    assert "inside her mouth" in p.MODES["oral"]["prose_req"] and "inside her" not in p.MODES["solo"]["prose_req"]
    assert "contact_keyword" not in p.MODES["partner"]["schema"]["properties"]["development"]["required"]


# ---- coverage addendum: router + mode rules -------------------------------------------------------------------------
def _cfg():
    return p.load_config(p.CONFIG_PATH) if p.CONFIG_PATH.exists() else {"position_kinds": {"talk": ["talk"], "oral": ["blowjob"], "sex": ["doggy", "missionary"], "solo": ["tease", "female_solo"]}}


@pytest.mark.parametrize("ask,pos,mode,ov", [
    ("POV blowjob, she looks up into the lens", "blowjob", "oral", "pov"),
    ("reluctant CNC, he pins her wrists, doggy", "doggy", "sex", "cnc"),
    ("slow striptease, she peels the slip", "tease", "strip", None),
    ("turns her over from missionary to doggy", "doggy", "transition", None),
    ("doggy, he edges her, denial", "doggy", "sex", "edge"),
    ("doggy, wand on her clit while he thrusts", "doggy", "sex", "toy"),
    ("tied to the headboard, forced orgasm", "missionary", "sex", "forced_orgasm"),
    ("stepbrother roleplay, missionary, bratty", "missionary", "sex", "taboo_role"),
    ("defeated superheroine pinned on the rooftop", "missionary", "sex", "defeat"),
    ("cinematic doggy by the window light", "doggy", "sex", "cinematic"),
])
def test_router_keywords(ask, pos, mode, ov):
    r = wp_router.route_mode(ask, pos, READ, _cfg())
    assert r["mode"] == mode and (ov is None or ov in r["overlays"]), r


@pytest.mark.parametrize("ask,pos", [("something sensual on the balcony", "sensual"), ("zzz qqq", "blorp"), ("", "x"),
                                     ("he takes her standing against the wall", "standing"), ("make it pretty", "pretty")])
def test_router_fallback_never_raises(ask, pos):
    r = wp_router.route_mode(ask, pos, READ, _cfg())
    assert br.get_act(r["position"]) and any(w["warn"] == "mode_fallback" for w in r["warnings"])


def test_mode_rules_builder_parity():
    c = ctx("oral", "blowjob")
    bad = GOOD_ORAL.replace("(S2) says in a low voice, <d>[English] Look up at me, sand girl.</d>",
                            "(S1) says in a muffled voice, <d>[English] Mmm, yes.</d>")
    assert "oral_mouth_full" in hard(full(bad, "oral"), c)
    three = GOOD_SEX + " (S2) says in a low voice, <d>[English] Arch for me.</d> (S2) says in a low voice, <d>[English] Lower.</d> (S2) says in a low voice, <d>[English] Now.</d>"
    assert "speaker_cap" in [i["code"] for i in wp_lint.lint(full(three), ctx())["issues"]]
    assert "shallow" in [i["code"] for i in wp_lint.lint(full(GOOD_SEX.replace("He sinks his penis in to the hilt", "He stays shallow at the entrance")), ctx())["issues"]]
    assert "panel" in [i["code"] for i in wp_lint.lint(full(GOOD_SEX.replace("hooks the bodysuit", "hooks the bodysuit panel")), ctx())["issues"]]
    assert "dial" in [i["code"] for i in wp_lint.lint(full(GOOD_SEX.replace("At first,", "At 24 fps, at first,")), ctx())["issues"]]
    cpos = ctx(cast={"position_check": r"\bon her back\b"})
    assert "pose_landing" in [i["code"] for i in wp_lint.lint(full(GOOD_SEX), cpos)["issues"]]
    assert "pose_landing" not in hard(full(GOOD_SEX), cpos)
    cpart = ctx(cast={"off_still_s2": True})
    assert "partner_gate" not in hard(full(GOOD_SEX), cpart)  # the pipeline-owned S2 line satisfies the builder gate
    assert wp_lint.tempo_rate("two hard strokes a second") == 2 and wp_lint.tempo_rate("one stroke every half second") == 2


def test_acceptance1_fixes(home):
    import render_writer_pipeline as p
    import wp_lint
    # a: judge letter parsing
    assert p.judge_letter({"best": "CANDIDATE A"}, ["A", "B", "C"]) == "A"
    assert p.judge_letter({"best": "Candidate: B"}, ["A", "B", "C"]) == "B"
    assert p.judge_letter({"ranking": ["C", "A"]}, ["A", "B", "C"]) == "C"
    assert p.judge_letter({"scores": {"CANDIDATE A": 18, "CANDIDATE B": 22}}, ["A", "B"]) == "B"
    # b: beat card carries line topics, not words
    s = json.dumps(p.MODES["talk"]["schema"])
    assert '"lines"' not in s and "line_topics" in s
    # k: blanks filled, waist height
    assert "beach" in p.normalize_prose("At first, (S1) waits on the <place> in the <light>.", "sex",
                                         {"place": "beach", "light": "dusk glow"})
    assert p.surface_height("a wooden sideboard") == "waist" and p.surface_height("bed") == "low"
    # i: vocal sound sentence ends are not static
    assert wp_lint.is_sound_sentence("(S1) lets out a defiant huff.")
    # e: near-duplicate dialogue
    hits = wp_lint.blacklist_hits(["Fill me up, I want all of it"], ["fill me up i want it all"], 0.95)
    assert hits


def test_judge_nested_scores_and_format(home):
    import render_writer_pipeline as p
    jd = {"scores": {"A": {"rhythm": 4, "total": 21}, "B": {"rhythm": 5, "total": 24}}}
    assert p.judge_letter(jd, ["A", "B"]) == "B"
    f = p.judge_format(["A", "B", "C"])
    assert f["json_schema"]["schema"]["properties"]["best"]["enum"] == ["A", "B", "C"]


def test_bunched_clearance_survives_builder(home):
    import render_writer_pipeline as p
    out = p.normalize_prose("(S2) pulls the sheer white halter dress aside to her waist where it stays bunched.", "sex", {})
    assert "stays gathered" in out and "bunched" not in out


def test_acceptance2_fixes(home):
    import render_writer_pipeline as p
    import wp_lint
    # 1: the label never lands inside <d>
    dd = "(S2) says in a low voice, <d>[English] does the log feel good?</d> As it builds, he thrusts at two strokes a second."
    out = p.normalize_prose(dd, "sex", {})
    assert "PRIMARY MOTION" not in "".join(__import__("re").findall(r"<d>.*?</d>", out))
    assert "As it builds, PRIMARY MOTION - he thrusts" in out
    # cowgirl word order, tag words, shiny skin
    assert "his hips lift" in p.normalize_prose("(S2) lifts his hips a few inches.", "sex", {})
    o2 = p.normalize_prose("A cinematic shot of glistening skin.", "sex", {})
    assert "cinematic" not in o2 and "glistening" not in o2
    # 9: still read cleanup
    d, ch = p.clean_still_read({"read": {"floor": "unseen", "skin": "glistening wet skin"}})
    assert d["read"]["floor"] == "the floor" and "visible pores" in d["read"]["skin"] and ch
    # 10: CONTINUE_RE knows 'maintains'
    assert wp_lint.CONTINUE_RE.search("as (S2) maintains the heavy tempo")
    assert wp_lint.MOUTH_CONTACT_RE.search("he slides past her lips")


def test_acceptance3_fixes():
    import render_writer_pipeline as r
    import wp_lint as L
    out = r.normalize_prose("She peels the dress down past her hips, one slow move every two seconds. At first, standing_mf; held.",
                            "strip", {"surface": "sideboard"})
    assert "PRIMARY MOTION - " in out and "cycle every two seconds" in out and "standing_mf" not in out
    assert not L.SHALLOW_RE.search("her strained, shallow breathing")
    assert L.SHALLOW_RE.search("shallow thrusts at the entrance")
    assert L.join_noun({"join_garments": ["sheer mesh bikini bottom"]}) == "bikini bottom"
    assert L._join_inherited_clear({"join_garments": ["sheer white halter dress"], "inherited": {"garments": {"dress": "aside"}}}, None)
    assert not L._join_inherited_clear({"join_garments": ["sheer white halter dress"], "inherited": {"garments": {"dress": "on"}}}, None)
    req = L.required_slots({"garment_noun": "top", "garments_all": ["string top", "sheer mesh bikini bottom"],
                            "join_garments": ["sheer mesh bikini bottom"]})
    assert "bottom" in req["garment"] and "top" in req["garment"]


def test_acceptance3_round2():
    import render_writer_pipeline as r
    import wp_lint as L
    out = r.normalize_prose("As it builds, she drives at two thrusts a second, her chest jolting.", "sex", {})
    assert "strokes a second" in out and "PRIMARY MOTION - " in out
    assert not L.SLAP_RE.search("The wet, rhythmic sliding of skin on skin.") and L.SLAP_RE.search("the wet slap of skin")
    assert L._join_inherited_clear({"join_garments": ["sheer mesh bikini bottom"],
                                    "inherited": {"garments": {"top": "on", "panties": "aside"}}}, None)
    full = r.assemble_output("[Shot 1] At first, (S1) sits.", {"summary": "A cinematic medium shot of a glistening woman"},
                             {"place": "beach", "light": "dusk", "hair": "blonde"}, 2, "sex")
    summ = full.split("summary:\n", 1)[1].split("\n", 1)[0]
    assert "cinematic" not in summ.lower() and "glistening" not in summ and summ.startswith("A medium shot")
    assert r.partner_type2_for("mmf", "mmf on the log") == "faceless" and r.partner_type2_for("missionary", "x") is None


def test_acceptance3_mouth_full_s1_line_dropped():
    import render_writer_pipeline as r
    dd = ("(S2) slides into her mouth as (S3) enters her. (S2) says in a low voice, <d>Like that?</d> "
          "(S1) says in a bratty voice, <d>Harder.</d> By the end, she keeps moving.")
    out = r.normalize_prose(dd, "sex", {})
    assert "Harder" not in out and "Like that?" in out and "By the end" in out


def test_mmf_s3_look_from_card():
    import render_writer_pipeline as r
    card = {"partners": [{"label": "S2", "sex": "male", "age": 30, "build": "athletic", "attire": "jeans", "enters_from": "left"},
                         {"label": "(S3)", "sex": "male", "age": 19, "build": "lean", "hair": "short dark hair",
                          "attire": "wearing grey linen trousers", "enters_from": "behind"}]}
    look = r.s3_look_from_card(card)
    assert look == "an adult man, 25 years of age, of lean build, with short dark hair, in grey linen trousers"
    assert r.s3_look_from_card({"partners": []}) is None


def test_router_nonhuman_and_scale_overlays():
    import wp_router as R
    r = R.route_mode("orc partner, standing doggy at the pool edge", "doggy", {}, {}, continued=False)
    assert "nonhuman" in r["overlays"]
    for ask in ("tiny adult fairy rides him", "giant lifts the tiny woman, standing carry", "massive oversized cock, slow missionary"):
        assert "scale" in R.route_mode(ask, "missionary", {}, {}, continued=False)["overlays"], ask
    assert "nonhuman" in R.route_mode("tentacles wrap her", "female_solo", {}, {}, continued=False)["overlays"]
    plain = R.route_mode("he takes her on her back", "missionary", {}, {}, continued=False)["overlays"]
    assert "nonhuman" not in plain and "scale" not in plain


def test_scale_lint_adult_proportions_and_youth_stop():
    import wp_lint as L
    hdr = "detailed_description:\n[Shot 1] "
    ctx = {"kind": "sex", "slots": {}, "overlays": ["scale"], "ask": "tiny adult fairy rides him", "cfg": {}}
    bad = L.lint(hdr + "At first, (S1), a tiny fairy no taller than his forearm, sits on his chest. She rides him.", ctx)
    assert "scale_adult" in bad["hard"]
    good = L.lint(hdr + "At first, (S1), a tiny fairy no taller than his forearm, sits on his chest: her adult face, full adult "
                        "breasts, wide adult hips and an adult woman's proportions at miniature scale. She rides him.", ctx)
    assert "scale_adult" not in good["hard"] and "scale_anchor" not in [i["code"] for i in good["issues"]]
    young = L.lint(hdr + "At first, (S1) sits.", dict(ctx, ask="tiny schoolgirl fairy"))
    assert "youth_hint" in young["hard"]


def test_youth_hint_hard_stop_before_any_writer_call(home, tmp_path, monkeypatch):
    calls = scripted(monkeypatch, lambda purpose: GOOD_SEX)
    cfg = p.load_config(home / "config.yaml")
    r = p.run_clip(job(tmp_path, "y1", ask="tiny schoolgirl fairy rides him"), cfg, lambda *a: None)
    assert r["status"] == "NOT_READY" and "youth hint" in r["not_ready_reason"] and not calls


def test_consent_setup_overlay_needs_consent_beat_before_sex():
    import wp_router as R, wp_lint as L
    assert "consent_setup" in R.route_mode("sleep roleplay, spooning", "spooning", {}, {}, continued=False)["overlays"]
    hdr = "detailed_description:\n[Shot 1] "
    ctx = {"kind": "sex", "slots": {}, "overlays": ["consent_setup"], "ask": "sleep roleplay, spooning", "cfg": {}}
    bad = L.lint(hdr + "At first, (S1) lies on her side, eyes closed. (S2) slides into her from behind.", ctx)
    good = L.lint(hdr + "At first, (S1) lies on her side and says in a sleepy voice, <d>Wake me up like that tonight.</d> "
                        "Later (S2) slides into her from behind.", ctx)
    assert "consent_setup" in bad["hard"] and "consent_setup" not in good["hard"]
    assert "consent_setup" not in L.lint(hdr + "(S2) slides into her.", dict(ctx, overlays=["consent_setup", "continued"]))["hard"]


def test_acc4_oral_sheathed_lint_in_mmf_mode():
    import wp_lint as L
    hdr = "detailed_description:\n[Shot 1] "
    ctx = {"kind": "sex", "slots": {}, "overlays": ["threesome"], "ask": "MMF spitroast", "cfg": {}}
    r = L.lint(hdr + "At first, (S1) kneels. (S2) is fully sheathed in her mouth while (S3) is buried in her.", ctx)
    assert "oral_contact" in r["hard"]
    ok = L.lint(hdr + "At first, (S1) kneels. (S2) is deep inside her mouth while (S3) is buried in her.", ctx)
    assert "oral_contact" not in ok["hard"]


def test_pm_acc3_glue_summary_and_lints():
    import wp_lint as L
    g = p.glue_fix("<d>[English] Is that all?</d> adds in a teasing, sharp tone, and (S1) says in a low voice, <d>[English] More.</d> "
                   "It stays on the the floor. none. Her damp skin, slick and damp, shines.")
    assert "adds in" not in g and "the the" not in g and "none." not in g and g.count("damp") == 1, g
    out = p.assemble_output("[Shot 1] x.", {"summary": "The camera holds wide. At first, (S1) kneels on the sand."},
                            {"place": "beach", "surface": "sand", "position": "blowjob"}, 2, "oral")
    summ = out.split("summary:\n", 1)[1].split("\n", 1)[0]
    assert "At first" not in summ and "camera" not in summ, summ
    hdr = "detailed_description:\n[Shot 1] "
    ctx = {"kind": "sex", "act_id": "standing_mf", "slots": {}, "overlays": [], "ask": "he takes her at the sideboard", "cfg": {}}
    r = L.lint(hdr + "At first, (S1) leans on the sideboard. She settles onto her hands and knees. (S2) is buried in her.", ctx)
    assert "act_mismatch" in r["hard"]
    assert "youth_hint" in L.lint(hdr + "(S1), 16 years old, sits.", dict(ctx, act_id="missionary"))["hard"]
    assert p.partner_look_from_card({"partners": [{"label": "S3", "age": 31, "build": "lean", "hair": "short dark,"}]}, "S3").endswith("short dark hair")


def test_little_sister_role_word_is_not_a_youth_hint():
    import wp_lint as L
    hdr = "detailed_description:\n[Shot 1] "
    ctx = {"kind": "sex", "act_id": "missionary", "slots": {}, "overlays": ["taboo_role"], "ask": "little sister roleplay, missionary", "cfg": {}}
    r = L.lint(hdr + "At first, (S1), an adult woman playing his little sister, lies on the bed.", ctx)
    assert "youth_hint" not in r["hard"]
    assert "youth_hint" in L.lint(hdr + "At first, (S1), 17 years old, lies on the bed.", ctx)["hard"]

def test_lint_craft_is_soft_and_score_stays_above_ready():
    """Craft codes (phase_anchor, static_end, ...) are soft ~5 pts; three of them stay >= min_ready_score 50.
    Safety codes in SAFETY_HARD stay hard at 20 and still block lint pass."""
    assert wp_lint.SOFT_WEIGHT == 5 and wp_lint.HARD_WEIGHT == 20
    soft = wp_lint._fix("phase_anchor", "x")
    assert soft["hard"] is False and soft["penalty"] == 5
    assert wp_lint._fix("youth_hint", "x")["hard"] and wp_lint._fix("voice_missing", "x")["hard"]
    assert wp_lint._fix("clearance_missing", "x")["hard"] and wp_lint._fix("blacklist", "x")["hard"]
    bad = GOOD_SEX.replace("At first, (S1) leans against the log", "(S1) waits by the log")
    bad = bad.replace("By the end, she is still rocking back onto him and he keeps the same pace, gripping her hips.",
                      "By the end, her hair is gold in the low sun.")
    r = wp_lint.lint(full(bad), ctx())
    assert "phase_anchor" in [i["code"] for i in r["issues"]]
    assert "static_end" in [i["code"] for i in r["issues"]]
    assert r["score"] >= 50 and r["pass"] and not r["hard"]

def test_pm_acc4_router_handjob_sensual_and_pool_edge():
    import wp_router as R
    cfg = {"position_kinds": {"talk": ["talk"], "oral": ["blowjob"], "partner": ["titjob", "finish", "handjob"],
                                "solo": ["tease", "female_solo"], "sex": ["doggy", "missionary"]}}
    h = R.route_mode("handjob", "handjob", {}, cfg)
    assert h["act_id"] == "handjob" and h["mode"] == "partner"
    s = R.route_mode("something sensual on the balcony", "sensual", {}, cfg)
    assert s["act_id"] == "tease"
    e = R.route_mode("she leans on the pool edge", "missionary", {}, cfg)
    assert "edge" not in e["overlays"]
    e2 = R.route_mode("edging, she stops just before", "missionary", {}, cfg)
    assert "edge" in e2["overlays"]


def test_pm_acc4_tone_not_ashamed_on_neutral_ask():
    rng = __import__("random").Random(1)
    for i in range(20):
        t = p.pick_tone("missionary on the bed, she is eager", rng, None, overlays=[])
        assert t not in ("ashamed", "reluctant"), t
    assert p.pick_tone("forced orgasm, she resists", __import__("random").Random(0), None, overlays=["forced_orgasm", "cnc"]) in p.TONES


def test_pm_acc4d_glue_lint_and_ending_state():
    import render_writer_pipeline as wp
    import wp_lint as L
    assert "; no contact." not in wp.glue_fix("dress bunched at the waist; no contact. She turns.")
    g = wp.glue_fix("He is fully sheathed in her mouth.")
    assert "inside her mouth" in g and "sheathed" not in g.lower()
    es = wp.normalize_ending_state({"pose": "all fours", "contact": "fully sheathed in her mouth"})
    assert es["contact"] == "inside her mouth"

    def _full(dd):
        return ("subject_definitions:\n(S1) is an adult woman.\n(S2) is an adult man.\n\n"
                "summary:\nThey are together on the bed.\n\nretention_analysis:\nkept.\n\n"
                "detailed_description:\n" + dd)

    r = L.lint(_full("[Shot 1] She winks at (S2) and says, (S1) says in a playful voice, <d>[English] Stay close.</d> He enters her vagina. PRIMARY MOTION - he thrusts at one cycle per second. His penis is inside her vagina."),
               {"kind": "sex", "slots": {}, "blacklist": [], "cloned": [], "cfg": {}, "ask": "", "act_id": "missionary"})
    assert "double_says" in [i["code"] for i in r["issues"]]
    r2 = L.lint(_full("[Shot 1] She looks at him and says, <d>[English] Your hands are too tight.</d> PRIMARY MOTION - she sinks at one cycle per second. His penis is inside her vagina."),
                {"kind": "sex", "slots": {}, "blacklist": [], "cloned": [], "cfg": {}, "ask": "", "act_id": "cowgirl"})
    assert "hands_line" in [i["code"] for i in r2["issues"]]
    r3 = L.lint(_full("[Shot 1] PRIMARY MOTION - they grind at one cycle per second. Their vulvas are pressed together."),
                {"kind": "sex", "slots": {}, "blacklist": [], "cloned": [], "cfg": {}, "ask": "FF scissoring", "act_id": "ff_scissoring"})
    assert "contact_anatomy" not in [i["code"] for i in r3["issues"]]
    bts = _full("[Shot 1] She sits. (S2), off-screen, asks, <d>[English] How did that feel?</d> "
                "She says, <d>[English] It felt real.</d> (S2), off-screen, asks, <d>[English] What next?</d> "
                "She says, <d>[English] We keep going.</d> She adds, <d>[English] That's the shot.</d>")
    counted = L.talk_counted_lines(bts, {"ask": "BTS interview"})
    assert len(counted) == 3


def test_part2_item5_partner_fields_and_clip_length_and_modes_header():
    import wp_lint as L

    # section_split must keep bracketed MODES header so assemble_system injects mode blocks
    sys_txt, meta = p.assemble_system({"writer_prompt": str(Path(r"C:\AI\render\writer_pipeline\writer_prompt.md"))},
                                      "tease edge clip on the bed", "current")
    assert "Teasing and edging" in meta["modes"]
    assert "Teasing and edging" in sys_txt

    # partner card species, scale_anchor, anatomy, and matches_still flow into <Subject N>
    card = {
        "summary": "An orc and a futa take her on the stone slab.",
        "partners": [
            {
                "label": "S2", "sex": "man", "age": 35, "build": "towering muscular build",
                "attire": "a leather harness", "enters_from": "left",
                "species": "orc", "scale_anchor": "about twice her height",
            },
            {
                "label": "S3", "sex": "futa", "age": 28, "build": "tall slim build",
                "attire": "a black corset", "enters_from": "behind",
                "anatomy": "with full breasts and a thick penis", "matches_still": "<Picture 2>",
            },
        ],
    }
    slots = {"place": "stone room", "light": "torchlight", "surface": "the slab",
             "tone": "eager", "line_focus_text": "his body",
             "frames": 124, "clip_seconds": 5.2, "speech_words_max": 13, "max_lines_per_speaker": 1}
    out = p.assemble_output("[Shot 1] At first, (S1) lies on the slab.", card, slots, 3, "sex")
    s2_line = [ln for ln in out.splitlines() if ln.startswith("<Subject 2>")][0]
    s3_line = [ln for ln in out.splitlines() if ln.startswith("<Subject 3>")][0]
    assert "the orc, an adult" in s2_line and "the man" not in s2_line.lower()
    assert "about twice her height" in s2_line
    assert "with full breasts and a thick penis" in s3_line
    assert "matches <Picture 2>" in s3_line

    # brief_block passes T and scaled word/line budget; wp_lint honors max_lines_per_speaker
    brief = p.brief_block("missionary on the slab", "missionary", "sex", slots, 2)
    assert "T = 5.2 s (124 frames)" in brief and "at most 13" in brief and "at most 1 short line(s) per speaker" in brief
    dd_2lines = ("[Shot 1] (S1) says in a soft voice, <d>[English] One.</d> "
                 "(S1) says in a soft voice, <d>[English] Two.</d>")
    lr = L.lint(full(dd_2lines), ctx(cfg={"speech_words_max": 13, "max_lines_per_speaker": 1}))
    assert "speaker_cap" in [i["code"] for i in lr["issues"]]


def test_male_solo_strips_female_read_slots_and_voice():
    female_read = {
        "read": {
            "room": "high-rise apartment",
            "place": "by a window",
            "surface": "wooden sideboard",
            "bed": False,
            "sheets": None,
            "floor": "the floor",
            "pose": "leaning, standing",
            "facing_camera": True,
            "framing": "medium shot",
            "light": "soft evening light from window",
            "people": 1,
            "garments": [{"type": "dress", "name": "sheer white halter dress", "look": "white sheer"}],
            "build": "curvy",
            "skin": "fair skin",
            "hair": "blonde, damp, straight",
        }
    }
    stripped, changed = p.strip_male_solo_still_read(female_read)
    assert set(changed) >= {"hair", "skin", "build", "pose", "garments", "facing_camera", "people"}
    assert stripped["read"]["garments"] == [] and stripped["read"]["hair"] == "" and stripped["read"]["pose"] == ""
    slots = p.make_slots(female_read, "male solo edging", "male_solo", "solo", "lf21_test", None)
    assert not slots["opening_lead"].startswith("her ") and "her skin" not in slots["opening_lead"]
    assert "her body" not in slots["line_focus_text"] and slots["garments_all"] == []
    brief = p.brief_block("male solo edging", "male_solo", "solo", slots, 1)
    assert "still's pose" not in brief
    cast, _ = p.make_cast(female_read, "male_solo", "male solo edging")
    assert "man's voice" in (cast.get("voice_s1") or "").lower()
    assert cast.get("inventory") == [] and cast.get("garments_off") == ""

