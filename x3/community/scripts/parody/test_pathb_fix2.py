"""Unit tests for Path B Fix 2 (assemble_output, tempo_unparsed, hashed clone gate, backend proof)."""
from __future__ import annotations

import io
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

import build_request as br
import render_writer_pipeline as p
import wp_lint
import wp_state
from test_writer_pipeline import READ, home, job, scripted, stub_build  # noqa: F401


def _local_still(tmp_path: Path) -> tuple[str, str]:
    still = tmp_path / "still.jpg"
    still.write_bytes(b"\xff\xd8\xff\xe0dummy")
    sr = tmp_path / "local_sr.json"
    sr.write_text(json.dumps({**READ, "source": str(still)}), encoding="utf-8")
    return str(still), str(sr)


# ---- Fix 1: prose-file builder ---------------------------------------------------------------------------------------

def test_fix1a_widened_removal_verbs_and_aside_precedence():
    slots = {
        "place": "bedroom",
        "light": "soft window light",
        "hair": "dark hair",
        "position": "missionary",
        "surface": "bed",
        "still_mode": "guide",
        "garment": "sheer dress",
    }
    card = {"partners": [{"label": "S2", "sex": "man", "age": 30, "build": "athletic build"}], "summary": "(S1) on the bed"}
    out = p.assemble_output(
        "[Shot 1] Medium shot. At first, the dress glides down and pools around her ankles. By the end, soft breath.",
        card, slots, 2, "sex",
    )
    ret = out.split("retention_analysis:", 1)[1].split("detailed_description:", 1)[0]
    assert "removed during the clip" in ret
    assert "fully_preserved - stays on her body" not in ret

    # Pulled aside still wins over removal when both appear
    out_aside = p.assemble_output(
        "[Shot 1] Medium shot. At first, (S1) pulls her sheer dress aside at her hip before it slides down. By the end, soft breath.",
        card, slots, 2, "sex",
    )
    ret_aside = out_aside.split("retention_analysis:", 1)[1].split("detailed_description:", 1)[0]
    assert "pulled aside" in ret_aside


def test_fix1b_hermes_retention_never_downgraded():
    slots = {
        "place": "bedroom",
        "light": "soft window light",
        "hair": "dark hair",
        "position": "missionary",
        "surface": "bed",
        "still_mode": "guide",
        "garment": "sheer dress",
    }
    card = {"partners": [{"label": "S2", "sex": "man", "age": 30, "build": "athletic build"}], "summary": "(S1) on the bed"}
    hermes_sec = {
        "subject_definitions": "",
        "retention_analysis": "<Subject 1>: fully_preserved - face and hair.\nThe sheer dress: partially_preserved - removed during the clip.",
    }
    out = p.assemble_output(
        "[Shot 1] Medium shot. At first, (S1) stands bare by the bed. By the end, soft breath.",
        card, slots, 2, "sex", hermes_sections=hermes_sec,
    )
    ret = out.split("retention_analysis:", 1)[1].split("detailed_description:", 1)[0]
    assert "removed during the clip" in ret
    assert "fully_preserved - stays on her body" not in ret


def test_fix1c_guide_mode_r11_binding_and_hand_lock():
    expected_r11_guide = br.R11_SUBJECT.replace("<Picture 1> of the reference pictures", "the opening frame")
    slots_guide = {
        "place": "beach",
        "light": "hard golden rim light",
        "hair": "dark hair",
        "position": "doggy",
        "surface": "driftwood log",
        "still_mode": "guide",
        "garment": "bikini",
    }
    card = {"partners": [{"label": "S2", "sex": "man", "age": 30, "build": "athletic build"}], "summary": "(S1) and (S2) on the log"}
    out = p.assemble_output(
        "[Shot 1] Medium shot. At first, (S1) and (S2) are on the sand. By the end, soft breath.",
        card, slots_guide, 2, "sex",
    )
    sd = out.split("summary:", 1)[0]
    summary = out.split("summary:", 1)[1].split("retention_analysis:", 1)[0]
    assert expected_r11_guide in sd
    assert br.R11_HAND in sd
    assert "<Subject 2>" in sd
    assert "<Picture 1>" not in out
    assert "[reference generation]" not in summary

    # Named parody guide branch
    slots_parody = {**slots_guide, "identity": {"character": "Alice", "actor": "Bobbi", "is_oc": False}}
    out_parody = p.assemble_output("[Shot 1] Medium shot.", card, slots_parody, 2, "sex")
    sd_p = out_parody.split("summary:", 1)[0]
    assert expected_r11_guide in sd_p and br.R11_HAND in sd_p and "<Picture 1>" not in sd_p

    # Male-solo guide branch: HAND lock only, no woman R11 clause
    slots_male = {**slots_guide, "position": "male_solo"}
    out_male = p.assemble_output("[Shot 1] Medium shot.", card, slots_male, 1, "sex")
    sd_m = out_male.split("summary:", 1)[0]
    assert br.R11_HAND in sd_m and expected_r11_guide not in sd_m and "<Picture 1>" not in sd_m


def test_fix1c_ref_mode_unchanged():
    slots_ref = {
        "place": "bedroom",
        "light": "soft window light",
        "hair": "blonde hair",
        "position": "doggy",
        "surface": "bed",
        "still_mode": "ref",
        "garment": "satin slip",
    }
    card = {"partners": [{"label": "S2", "sex": "man", "age": 30, "build": "athletic build"}], "summary": "(S1) on the bed"}
    out = p.assemble_output("[Shot 1] Medium shot. At first, (S1) stands. By the end, soft breath.", card, slots_ref, 2, "sex")
    assert "<Picture 1>" in out
    assert "[reference generation]" in out


def test_fix1d_partner_from_hermes_and_prose_in_frame():
    slots = {
        "place": "bedroom",
        "light": "soft light",
        "hair": "dark hair",
        "position": "missionary",
        "surface": "bed",
        "still_mode": "guide",
        "garment": "dress",
    }
    card = {"partners": [{"label": "S2", "sex": "man", "age": 30, "build": "athletic build"}], "summary": "(S1) and (S2)"}
    hermes_sec = {
        "subject_definitions": "<Subject 1> is S1.\n<Subject 2> is the man, 32 years old, shirtless, already kneeling in frame at the start from <Picture 1>.",
        "retention_analysis": "",
    }
    out = p.assemble_output(
        "[Shot 1] Medium shot. At first, (S2) is already kneeling beside the bed. By the end, soft breath.",
        card, slots, 2, "sex", hermes_sections=hermes_sec,
    )
    sd = out.split("summary:", 1)[0]
    assert "t-shirt and jeans" not in sd
    assert "enters from" not in sd
    assert "<Picture 1>" not in sd
    assert "(S2)" in sd

    # Without Hermes <Subject 2> line: derive attire & already-in-frame from prose
    out_derived = p.assemble_output(
        "[Shot 1] Medium shot. At first, (S2) in black boxers kneels beside (S1). By the end, soft breath.",
        card, slots, 2, "sex",
    )
    sd_d = out_derived.split("summary:", 1)[0]
    assert "black boxers" in sd_d
    assert "already in frame at the start" in sd_d
    assert "enters from" not in sd_d


def test_fix1e_summary_bare_subject_normalized():
    slots = {"place": "room", "light": "soft light", "hair": "dark hair", "position": "doggy", "surface": "bed", "still_mode": "guide"}
    card = {"partners": [{"label": "S2", "sex": "man"}], "summary": "Subject 1 and Subject 2 on the bed"}
    out = p.assemble_output("[Shot 1] Medium shot.", card, slots, 2, "sex")
    summary = out.split("summary:", 1)[1].split("retention_analysis:", 1)[0]
    assert "(S1) and (S2)" in summary
    assert "Subject 1" not in summary and "Subject 2" not in summary


# ---- Fix 2: tempo_unparsed hard fail ---------------------------------------------------------------------------------

def _sex_prompt(primary_sentence: str) -> str:
    return (
        "subject_definitions:\n"
        "<Subject 1> is the woman, 25 years of age; she is (S1).\n"
        "<Subject 2> is the man, 30 years of age; he is (S2).\n\n"
        "summary:\n(S1) and (S2) on the bed.\n\n"
        "retention_analysis:\n<Subject 1>: fully_preserved.\n\n"
        "detailed_description:\n"
        "[Shot 1] Medium two shot at hip height in soft window light. "
        "At first, (S1) lies on the bed while (S2) kneels between her legs and pushes his penis into her vagina until his hips are flush. "
        f"{primary_sentence} "
        "By the end, he stays buried inside her.\n"
    )


def test_fix2_tempo_unparsed_is_hard_fail():
    ctx = {"kind": "sex", "slots": {"surface": "bed", "light": "soft window light", "place": "bedroom", "still_mode": "guide"}, "bodies": 2, "cfg": {"tempo_range": {"sex": [1.0, 3.0]}}}
    bad = _sex_prompt("PRIMARY MOTION - slow thrusts, roughly one cycle per slow breath, keeping the join.")
    r_bad = wp_lint.lint(bad, ctx, minimal=True)
    assert not r_bad["pass"]
    assert "tempo_unparsed" in r_bad["hard"]

    for good_tempo in (
        "PRIMARY MOTION - steady thrusts, one cycle every half second, keeping the join.",
        "PRIMARY MOTION - hard thrusts, two strokes per second, keeping the join.",
        "PRIMARY MOTION - smooth thrusts, 1.5 strokes a second, keeping the join.",
        "PRIMARY MOTION - deep thrusts every second, keeping the join.",
    ):
        r_ok = wp_lint.lint(_sex_prompt(good_tempo), ctx, minimal=True)
        assert "tempo_unparsed" not in r_ok["hard"], good_tempo

    # Non-sex talk kind unaffected
    talk_ctx = {"kind": "talk", "slots": {"surface": "bed", "light": "soft window light", "place": "bedroom"}, "bodies": 1, "cfg": {}}
    talk_prompt = (
        "subject_definitions:\n<Subject 1> is the woman, 25 years of age; she is (S1).\n\n"
        "summary:\n(S1) speaks on the bed.\n\n"
        "retention_analysis:\n<Subject 1>: fully_preserved.\n\n"
        "detailed_description:\n[Shot 1] Medium shot in soft window light. At first, (S1) says, <d>[English] Hello there.</d> By the end, she smiles.\n"
    )
    r_talk = wp_lint.lint(talk_prompt, talk_ctx, minimal=True)
    assert "tempo_unparsed" not in r_talk["hard"]


# ---- Fix 3: clone gate hashes and count+beat only --------------------------------------------------------------------

def test_fix3_hashed_clone_gate_never_leaks_phrases(home, tmp_path, monkeypatch):
    still, sr = _local_still(tmp_path)
    planted = "the brass lantern swings beside the cedar doorframe"
    # Build a synthetic prompt doc containing a worked example with the planted phrase
    prompt_doc = f"SYSTEM PROMPT\n\nEXAMPLES:\nAt first, {planted} as she waits.\n"
    cloned_path = home / "cloned_phrases.txt"
    hashed = wp_state.refresh_cloned(cloned_path, prompt_doc, "sha_test", [])
    assert hashed and all(h.startswith("sha256:") for h in hashed)
    on_disk = cloned_path.read_text(encoding="utf-8")
    assert "brass lantern" not in on_disk
    cs = wp_lint.clone_hit_summary(f"[Shot 1] Medium shot. [Shot 2] At first, {planted}.", hashed)
    assert cs["count"] >= 1 and cs["beats"] == [2]

    # R11_HAND six-grams still excluded
    assert wp_lint.clone_hit_summary(br.R11_HAND, hashed)["count"] == 0

    # End-to-end prose-file run with a planted clone
    # Put our planted phrase into the state dir's cloned_phrases.txt via a stubbed writer_prompt
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    cfg = p.load_config(home / "config.yaml")
    cfg["shared_state_dir"] = str(state_dir)
    # Seed writer_prompt with the planted example
    wp_file = tmp_path / "writer_prompt.md"
    wp_file.write_text(prompt_doc, encoding="utf-8")
    cfg["writer_prompt"] = str(wp_file)

    scripted(monkeypatch, lambda purpose: "WRITER MUST NOT BE CALLED")
    stub_build(monkeypatch)
    prose_txt = (
        "subject_definitions:\n"
        "<Subject 1> is the woman, 25 years of age; she is (S1).\n"
        "<Subject 2> is the man, 30 years of age; he is (S2).\n\n"
        "summary:\n(S1) and (S2) on the log.\n\n"
        "retention_analysis:\n<Subject 1>: fully_preserved.\n\n"
        "detailed_description:\n"
        "[Shot 1] Medium two shot at hip height in bright sunlight. At first, (S1) kneels on the sand beside the log while (S2) kneels behind her and pushes his penis into her vagina until his hips are flush. "
        f"[Shot 2] PRIMARY MOTION - steady thrusts, two strokes a second, while {planted}. "
        "By the end, he stays buried inside her.\n"
    )
    pf = tmp_path / "hermes_prose.txt"
    pf.write_text(prose_txt, encoding="utf-8")
    r = p.run_clip(job(tmp_path, "fix3_run", still=still, still_read=sr, prose_file=str(pf)), cfg, lambda *a: None)
    assert r["status"] == "NOT_READY"
    assert "cloned_hits" not in r
    assert r["clone_hits_count"] >= 1
    assert 2 in r["clone_hit_beats"]

    run_dir = Path(r["run_dir"])
    pick_txt = (run_dir / "pick.json").read_text(encoding="utf-8")
    ctx_txt = (run_dir / "lint_ctx.json").read_text(encoding="utf-8")
    assert "brass lantern" not in pick_txt
    assert "brass lantern" not in ctx_txt
    assert "cloned_hits" not in json.loads(pick_txt)


def test_fix3_skill_text_prohibitions():
    repo_root = Path(__file__).resolve().parents[4]
    for rel in (
        "hosts/x3/hermes/skills/h3-render/SKILL.md",
        "hosts/x3/live/hermes/skills/custom/creative/h3-render/SKILL.md",
    ):
        txt = (repo_root / rel).read_text(encoding="utf-8")
        low = txt.lower()
        assert "count and beat" in low
        assert "scanner" in low
        assert "wp_lint" in txt and "wp_state" in txt and "lint_ctx" in txt
        assert "memory" in low


# ---- Fix 5: backend proof --------------------------------------------------------------------------------------------

def test_fix5_backend_proof_key_auth_redaction_and_journal_fallback(tmp_path, monkeypatch):
    dummy_key = "sk-dummy-secret-test-value-999"
    key_file = tmp_path / "llm.env"
    key_file.write_text(f"# comment\nLLM_KEY_HERMES=\"{dummy_key}\"\n", encoding="utf-8")
    os.chmod(key_file, 0o600)

    seen_auth = []

    class _Resp:
        def __init__(self, body: str):
            self._b = body.encode("utf-8")
        def read(self):
            return self._b
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_urlopen_ok(req, timeout=1.5):
        seen_auth.append(req.headers.get("Authorization"))
        if req.full_url.endswith("/running"):
            return _Resp(json.dumps({"running": [{"model": "flash-next", "state": "ready", "cmd": f"--api-key {dummy_key}"}]}))
        if req.full_url.endswith("/logs"):
            lines = "\n".join(f"log line {i}" for i in range(250))
            return _Resp(lines)
        raise AssertionError(req.full_url)

    monkeypatch.delenv("LLAMA_SWAP_API_KEY", raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen_ok)
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: subprocess.CompletedProcess(a[0], 0, stdout="-- No entries --\n", stderr=""))

    run_dir = tmp_path / "run1"
    run_dir.mkdir()
    cfg = {"llama_swap_url": "http://127.0.0.1:8080", "llama_swap_key_file": str(key_file)}
    proof = p.collect_backend_proof(run_dir, cfg, hermes_slot="flash-next")
    assert seen_auth == [f"Bearer {dummy_key}", f"Bearer {dummy_key}"]
    assert proof["key_source"] == "file"
    assert proof["journal_ok"] is True
    assert proof["journal_source"] == "llama-swap /logs"
    assert proof["llama_swap_running"] == [{"model": "flash-next", "state": "ready"}]
    assert len((run_dir / "llama_swap_journal.txt").read_text(encoding="utf-8").splitlines()) == 200
    assert dummy_key not in (run_dir / "backend.json").read_text(encoding="utf-8")

    # 644 key file must be refused
    os.chmod(key_file, 0o644)
    run_dir2 = tmp_path / "run2"
    run_dir2.mkdir()
    def fake_urlopen_401(req, timeout=1.5):
        raise urllib.error.HTTPError(req.full_url, 401, f"Unauthorized {dummy_key}", hdrs=None, fp=io.BytesIO(b""))
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen_401)
    proof2 = p.collect_backend_proof(run_dir2, cfg, hermes_slot="flash-next")
    assert proof2["key_source"] == "refused: file mode not owner-only"
    assert proof2["journal_ok"] is False

    # 401 with env key: error recorded without key
    monkeypatch.setenv("LLAMA_SWAP_API_KEY", dummy_key)
    run_dir3 = tmp_path / "run3"
    run_dir3.mkdir()
    proof3 = p.collect_backend_proof(run_dir3, cfg, hermes_slot="flash-next")
    assert proof3["key_source"] == "env"
    assert proof3["journal_ok"] is False
    assert "401" in (proof3["llama_swap_error"] or "")
    assert dummy_key not in (run_dir3 / "backend.json").read_text(encoding="utf-8")


def test_fix1d_entrance_verb_needs_a_place_object():
    import render_writer_pipeline as rwp
    # synthetic placeholders only: a bare "enters" is an act verb, not an entrance into the shot
    assert rwp._partner_in_frame_at_start("(S2) kneels by the bench. (S2) enters her slowly.", "S2")
    assert not rwp._partner_in_frame_at_start("(S2) enters the frame from the left. (S2) kneels.", "S2")
    assert not rwp._partner_in_frame_at_start("(S2) walks in from the hall and kneels.", "S2")
