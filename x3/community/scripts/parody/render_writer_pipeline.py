"""Render writer autonomous pipeline (Max Architect 3, 2026-11-13; Derrick t1409u "lets do both", spec
/workspace/maxops/prompts/render-writer-pipeline-handoff-20261113.md sha256 08993e6e...).

One clip, end to end, no human step:
  still read -> slots -> four-phase beat card (json_schema) -> N prose candidates -> linter -> one targeted rewrite ->
  rank (+ judge on a tie) -> build_request dry run (submit_parody_run.py writer-run, never --queue) -> blacklist,
  recent outputs and scene_state updates.
Failures degrade (fallback pick + warning, NOT_READY recorded, writer_down) and never block the next ask.

Usage (Render's pi chat or Derrick):
  python3 /home/derekboone/AI/community/scripts/parody/render_writer_pipeline.py <run_dir>
      --ask "<ask>" --position <act> --still <still path> --character FCSydny [--scene <id> | --continue <prev_run_dir>]
  Batch: render_writer_pipeline.py --batch <asks.jsonl>
This script has no queue option: queueing stays Derrick's yes through submit_parody_run.py writer-run --queue.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import yaml  # noqa: E402

import build_request as br  # noqa: E402
import scene_addenda  # noqa: E402
import wp_router  # noqa: E402
from writer_sys import build_writer_system_prompt  # noqa: E402
import wp_lint  # noqa: E402
import wp_state  # noqa: E402
from wp_llm import Client, WriterDown  # noqa: E402

_AI_ROOT = Path(__file__).resolve().parents[3]
PIPE_DIR = Path(os.environ.get("WP_HOME", str(_AI_ROOT / "render" / "writer_pipeline")))
CONFIG_PATH = PIPE_DIR / "config.yaml"
RUNS_ROOT = _AI_ROOT / "community" / "runs"
SUBMIT_PY = PARODY_DIR / "submit_parody_run.py"
VERSION = "wp-2026-11-13.1"

TONES = ("ashamed", "bratty", "reluctant", "eager", "silent")
TONE_WORDS = [
    ("spoof", r"spoof|parody|noir|banter|genre|detective|cowboy|vampire|space captain"),
    ("ashamed", r"asham\w*|shame\w*|embarrass\w*|humiliat\w*"),
    ("bratty", r"bratt?y|brat\b|mouthy|sassy|defiant|cheeky"),
    ("reluctant", r"reluctan\w*|cnc|resist\w*|protest\w*|unwilling|struggl\w*"),
    ("eager", r"eager\w*|begs?|begging|desperate|needy|willing"),
    ("silent", r"silent|silently|quiet\w*|mute|gagged|no talking"),
]
MODE_TRIGGERS = [
    ("- Cinematic", r"cinematic|movie|film\b|high-end"),
    ("- Gonzo", r"gonzo|amateur|\bpov\b|\braw\b"),
    ("- Teasing and edging", r"\btease|\bedg(?:e|ing)\b|denial"),
    ("- Forced orgasm", r"forced orgasm|overstimulat"),
    ("- Strip and undress", r"\bstrip|undress|slow reveal"),
    ("- Superheroine defeat", r"superheroine|peril|defeated heroine"),
    ("- Toys", r"\btoy|vibrator|dildo|\bplug\b|\bwand\b"),
]


# ---------------------------------------------------------------------------------------------------------------------
def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    cfg["_path"] = str(path)
    return cfg


def seed_for(run_id: str, ask: str, k: int) -> int:
    s = int(hashlib.sha256(f"{run_id}{ask}{k}".encode("utf-8")).hexdigest()[:8], 16)
    return s or 1


def position_kind(position: str, cfg: Dict[str, Any]) -> str:
    kinds = cfg.get("position_kinds") or {}
    act = (br.get_act(position) or {}).get("id") or position
    for kind, acts in kinds.items():
        if act in (acts or []):
            return kind
    return "sex"


def acts_bodies(position: str) -> int:
    a = br.get_act(position) or {}
    return int(a.get("bodies") or 2)


# ---- slots ----------------------------------------------------------------------------------------------------------
def pick_tone(ask: str, rng: random.Random, last: Optional[str], overlays: Optional[List[str]] = None) -> str:
    """Reluctant/ashamed only when the ask or a cnc/defeat/forced overlay names it (PM acc4 #15)."""
    for tone, pat in TONE_WORDS:
        if re.search(r"(?i)\b(?:" + pat + r")", ask or ""):
            return tone
    overlays = overlays or []
    named = any(o in overlays for o in ("cnc", "defeat", "forced_orgasm"))
    choices = [t for t in TONES if t != last]
    if not named:
        choices = [t for t in choices if t not in ("ashamed", "reluctant")]
    if not choices:
        choices = ["eager", "bratty", "silent"]
    return rng.choice(choices)


def first_phrase(s: str) -> str:
    return re.split(r"[,;]", s or "")[0].strip()



_SHEATHED_MOUTH_RE = re.compile(r"(?i)\b(?:fully\s+)?sheathed in her mouth\b")
_NO_CONTACT_RE = re.compile(r"(?i)^(?:no contact|none|null|-)\.?$")


def normalize_ending_state(es: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Clean inherited end state before a continued opener (PM acc4d #4): never 'sheathed' in the mouth."""
    out = dict(es or {})
    for k in ("pose", "contact"):
        v = out.get(k)
        if not v:
            continue
        s = str(v)
        s = _SHEATHED_MOUTH_RE.sub("inside her mouth", s)
        s = re.sub(r"(?i)\bsheathed\b(?=[^.;]{0,40}\b(?:mouth|throat|lips)\b)", "inside", s)
        if _NO_CONTACT_RE.match(s.strip()):
            s = ""
        out[k] = s
    return out


def make_slots(still_read: Dict[str, Any], ask: str, position: str, kind: str, run_id: str, last_tone: Optional[str],
               scene_prev: Optional[Dict[str, Any]] = None, overlays: Optional[List[str]] = None) -> Dict[str, Any]:
    f = br.still_facts(still_read)
    inv = br.garment_inventory(still_read)
    read = br._unwrap_still_read(still_read)
    rng = random.Random(seed_for(run_id, ask, 99))
    g0 = (read.get("garments") or [{}])[0] if read.get("garments") else {}
    garment = (f"{g0.get('name', '')} ({g0['look']})" if g0.get("look") else g0.get("name", "")) if g0 else ""
    gnoun = wp_lint._head_noun(g0.get("name", "")) if g0 else ""
    # join garments = the builder's W5 set (br._cast_items: key in _JOIN_KEYS or slot full-body), plus one-piece garments
    # the W5 slot map files as accessory but that still cover the join (bodysuit, teddy, leotard, catsuit, one-piece)
    try:
        items = br._cast_items(make_cast(still_read, position, ask)[0])
    except Exception:
        items = inv
    join = [g["name"] for g in items if g.get("key") in br._JOIN_KEYS or g.get("slot") in ("bottom", "full-body")
            or re.search(r"(?i)\b(?:bodysuit|teddy|leotard|catsuit|one-piece|swimsuit|bikini(?!\s+top))\b", g["name"])]
    is_male_solo = (position == "male_solo") or re.search(r"(?i)\bmale solo\b", ask or "")
    focus_opts = ["his body", "the act", "the tone"] if is_male_solo else ["his body", "her body", "the act", "the tone"]  # acceptance-2 item 9
    if not f["props"]:
        focus_opts = [x for x in focus_opts if x != "still prop"]
    if not inv:
        focus_opts = [x for x in focus_opts if x != "garment state"]
    focus = rng.choice(focus_opts)
    focus_text = {
        "his body": "his body and how he feels" if is_male_solo else "his body and what he does to her (never his hands, grip or strength)",
        "her body": "her body and how it feels",
        "the act": "the act itself and what comes next",
        "the tone": "the tone slot, spoken aloud" if is_male_solo else "the tone slot, said straight to the partner",
        "garment state": f"the {g0.get('name', 'garment')} and where it is now",
        "still prop": (f["props"][0] if f["props"] else "his body"),
    }[focus]
    slots = {
        "surface": re.sub(r"(?i)^(?:the|a|an)\s+", "", f.get("surface") or ""),
        "garment": garment, "garment_noun": gnoun, "garments_all": [g["name"] for g in inv], "join_garments": join,
        "light": first_phrase(f.get("light") or ""), "place": re.sub(r"(?i)^(?:on|in|at|by|inside|near|against|beside|under)\s+(?:the|a|an)?\s*", "",
                          f.get("place") or f.get("setting") or ""), "ask": ask,
        "surface_height": surface_height(f.get("surface") or ""),
        "floor": f.get("floor") or "", "pose": f.get("pose") or "", "facing_camera": bool(read.get("facing_camera")),
        "framing": read.get("framing") or "", "hair": read.get("hair") or "", "skin": read.get("skin") or "",
        "build": read.get("build") or "", "props": f["props"], "restraints": f["restraints"],
        "tone": pick_tone(ask, rng, last_tone, overlays), "line_focus": focus, "line_focus_text": focus_text,
        "position": position, "kind": kind,
        "opening_lead": rng.choice(MALE_OPENING_LEADS if is_male_solo else OPENING_LEADS),
    }
    if is_male_solo:
        # setting-only still: never leak her hair, skin, clothes or pose onto the man
        for k in ("hair", "skin", "build", "garment", "garment_noun", "pose"):
            slots[k] = ""
        slots["facing_camera"] = False
        slots["garments_all"] = []
        slots["join_garments"] = []
    if scene_prev:
        es = normalize_ending_state(scene_prev.get("ending_state") or {})
        slots["inherited"] = {"pose": es.get("pose"), "garments": es.get("garments"), "contact": es.get("contact"),
                              "camera": es.get("camera"), "pov": es.get("pov"), "done_actions": scene_prev.get("done_actions") or []}
    return slots


# ---- prompt assembly ------------------------------------------------------------------------------------------------
def section_split(text: str) -> List[Tuple[str, List[str]]]:
    out: List[Tuple[str, List[str]]] = []
    for ln in text.splitlines():
        if re.match(r"^[A-Z][A-Z ,&/-]{3,}(?:\s*\(.*\))?$", ln.strip()) and not ln.startswith("-"):
            out.append((ln.strip(), []))
        elif out:
            out[-1][1].append(ln)
        else:
            out.append(("", [ln]))
    return out


def assemble_system(cfg: Dict[str, Any], ask: str, persona: str, blocks: Optional[List[str]] = None) -> Tuple[str, Dict[str, Any]]:
    """writer_prompt.md with the chosen persona and only the mode block(s) the ask names (spec section 4 item 10)."""
    wp = Path(cfg.get("writer_prompt") or "writer_prompt.md")
    if not wp.is_absolute():
        wp = PIPE_DIR / wp
    text, meta = build_writer_system_prompt([wp])  # refuses AGENTS.md names and agent-only markers
    text = text.split("=====\n", 1)[-1]
    parts = section_split(text)
    out = []
    modes_used = []
    for head, lines in parts:
        if head == "PERSONA" and persona and persona != "current":
            pfile = PIPE_DIR / "personas" / f"{persona}.md"
            lines = ["", pfile.read_text(encoding="utf-8").strip(), ""]
        if head.startswith("MODES"):
            keep = []
            cur_ok = False
            for ln in lines:
                if ln.startswith("- "):
                    cur_ok = False
                    for label, pat in MODE_TRIGGERS:
                        hit = (label[2:] in blocks) if blocks is not None else bool(re.search(r"(?i)" + pat, ask or ""))
                        if ln.startswith(label) and hit:
                            cur_ok = True
                            modes_used.append(label[2:])
                if cur_ok or not ln.strip():
                    keep.append(ln)
            if not modes_used:
                continue
            lines = keep
        out.append(((head + "\n") if head else "") + "\n".join(lines).strip("\n"))
    sysprompt = "\n\n".join(o for o in out if o.strip())
    meta = {"writer_prompt": str(wp), "writer_prompt_sha256": wp_state.sha256_file(wp), "persona": persona or "current",
            "modes": modes_used}
    return sysprompt, meta


BEAT_SCHEMA_SEX = {
    "type": "object",
    "required": ["summary", "camera", "partners", "anchor", "onset", "development", "result", "end_state"],
    "properties": {
        "clip_seconds": {"type": "number"},
        "look": {"type": "string"},
        "arousal_stage": {"type": "integer"},
        "summary": {"type": "string"},
        "camera": {"type": "string"},
        "partners": {"type": "array", "items": {"type": "object", "required": ["label", "sex", "age", "build", "attire", "enters_from"],
                                                 "properties": {"label": {"type": "string"}, "sex": {"type": "string"},
                                                                "age": {"type": "integer"}, "build": {"type": "string"},
                                                                "attire": {"type": "string"}, "enters_from": {"type": "string"},
                                                                "hair": {"type": "string"},
                                                                "species": {"type": "string"}, "scale_anchor": {"type": "string"},
                                                                "anatomy": {"type": "string"}, "matches_still": {"type": ["string", "boolean"]},
                                                                "still": {"type": "string"}}}},
        "anchor": {"type": "object", "required": ["action", "sound"], "properties": {"action": {"type": "string"}, "sound": {"type": "string"}}},
        "onset": {"type": "object", "required": ["exit", "load", "height", "clearance", "entry", "sound"],
                  "properties": {k: {"type": "string"} for k in ("exit", "load", "height", "clearance", "entry", "sound")}},
        "development": {"type": "object", "required": ["primary_motion", "tempo_word", "contact_keyword", "follow_through", "sound", "line_topics"],
                        "properties": {"primary_motion": {"type": "string"}, "tempo_word": {"type": "string"},
                                       "contact_keyword": {"type": "string"},
                                       "follow_through": {"type": "array", "items": {"type": "string"}},
                                       "sound": {"type": "string"},
                                       "line_topics": {"type": "array", "items": {"type": "string"}}}},
        "result": {"type": "object", "required": ["action", "sound"], "properties": {"action": {"type": "string"}, "sound": {"type": "string"}}},
        "end_state": {"type": "object", "required": ["pose", "garments", "contact", "camera", "pov"],
                      "properties": {"pose": {"type": "string"}, "garments": {"type": "object"}, "contact": {"type": "string"},
                                     "camera": {"type": "string"}, "pov": {"type": "boolean"}, "prop_hand": {"type": "string"}}},
    },
}
BEAT_SCHEMA_TALK = {
    "type": "object",
    "required": ["summary", "camera", "partners", "anchor", "onset", "development", "result", "end_state"],
    "properties": {
        "clip_seconds": {"type": "number"},
        "look": {"type": "string"},
        "summary": {"type": "string"}, "camera": {"type": "string"},
        "partners": BEAT_SCHEMA_SEX["properties"]["partners"],
        "anchor": BEAT_SCHEMA_SEX["properties"]["anchor"],
        "onset": {"type": "object", "required": ["action", "sound"], "properties": {"action": {"type": "string"}, "sound": {"type": "string"}}},
        "development": {"type": "object", "required": ["line_topics", "sound"],
                        "properties": {"line_topics": {"type": "array", "minItems": 2, "maxItems": 3,
                                                       "items": {"type": "string"}},
                                       "sound": {"type": "string"}}},
        "result": {"type": "object", "required": ["action", "sound"],
                   "properties": {"action": {"type": "string"}, "sound": {"type": "string"},
                                  "line_topics": {"type": "array", "items": {"type": "string"}}}},
        "end_state": BEAT_SCHEMA_SEX["properties"]["end_state"],
    },
}


def _schema_variant(base: Dict[str, Any], onset_req: List[str], dev_req: List[str]) -> Dict[str, Any]:
    v = json.loads(json.dumps(base))
    v["properties"]["onset"]["required"] = onset_req
    v["properties"]["development"]["required"] = dev_req
    return v


# no penetration join: the onset has no clearance/entry requirement and the development has no contact keyword
BEAT_SCHEMA_NOJOIN = _schema_variant(BEAT_SCHEMA_SEX, ["exit", "load", "height", "sound"],
                                     ["primary_motion", "tempo_word", "follow_through", "sound", "line_topics"])

_SEX_BEAT = ("Plan this clip as a beat card in JSON. Four phases: anchor (the still pose exactly as shown), onset (exit from the "
             "still pose into the position, what carries each body's weight, how the surface height lines up the hips, the one "
             "clearance move using the still's garment noun and the word aside, and the entry), development (the PRIMARY MOTION "
             "with one tempo word the builder reads, the contact keyword, one or two follow-through cues, one or two short lines), "
             "result (the end state with the motion still running). Each phase has one diegetic sound tied to its action. "
             "Stay within the brief's clip-length spoken-word budget.")
_PRIMARY_REQ = ("- One sentence that begins exactly 'As it builds, PRIMARY MOTION - ' followed by the motion, its intensity and one "
                "tempo word (per second, every second, cycle, strokes a second), then one follow-through cue.\n")
_CLEAR_REQ = ("- If a garment covers the join: one active clearance sentence BEFORE the entry, in this form: '(S2) pulls her "
              "<garment> aside to one side at her hip, where it stays.' (the still's garment noun; never 'bunched'). Only the garment "
              "over the join gets 'aside to one side at her hip'; a top is pushed up off her breasts.\n")
_JOIN_REQ = _CLEAR_REQ + ("- One literal contact sentence with one join keyword (inside her, inside her vagina, inside her mouth, buried in her, deep in her, hips flush, flush "
             "against) that holds through the motion. Never write sheathed.\n")
# One block per mode (keyed by config position_kinds). Lint rules for the same mode live in wp_lint.MODE_RULES.
MODES: Dict[str, Dict[str, Any]] = {
    "sex": {"schema": BEAT_SCHEMA_SEX, "beat_task": _SEX_BEAT, "prose_req": _JOIN_REQ + _PRIMARY_REQ,
            "onset_hint": "The onset: the exit from that pose (and the clearance with the word aside, and the entry).\n"},
    "oral": {"schema": BEAT_SCHEMA_SEX,
             "beat_task": _SEX_BEAT.replace("the contact keyword", "the contact keyword inside her mouth"),
             "prose_req": ("- The contact sentence, in these words: 'his shaft slides past her lips deep inside her mouth, and she keeps "
                           "her lips sealed around it' (never hips flush, never sheathed). Only (S2) speaks in this clip; "
                           "(S1)'s side is wet suction and breath through her nose.\n"
                           "- The PRIMARY MOTION sentence, in these words: 'PRIMARY MOTION - her head bobs along his shaft about one "
                           "stroke every second.' (you may add one follow-through clause after a semicolon).\n"
                           "- Write the act's landing words once, inside a real clause (e.g. 'and kneels in front of him on the "
                           "<surface>'); never a list of aliases.\n"),
             "onset_hint": "The onset: the exit from that pose down to the mouth's height (and the entry into her mouth).\n"},
    "partner": {"schema": BEAT_SCHEMA_NOJOIN,
                "beat_task": ("Plan this clip as a beat card in JSON. Four phases: anchor (the still pose exactly as shown), onset "
                              "(exit from the still pose into the position and what carries each body's weight), development (the "
                              "PRIMARY MOTION with one tempo word, the body parts that touch, one or two follow-through cues, one or "
                                  "two short lines), result (the end state with the motion still running). No penetration. Each phase "
                                  "has one diegetic sound tied to its action. Stay within the brief's clip-length spoken-word budget."),
                    "prose_req": ("- One literal sentence naming the body parts that touch and how they move (no penetration).\n") + _PRIMARY_REQ,
                    "onset_hint": "The onset: the exit from that pose into the position.\n"},
    "solo": {"schema": BEAT_SCHEMA_NOJOIN,
             "beat_task": ("Plan this solo clip as a beat card in JSON. Four phases: anchor (the still pose exactly as shown), onset "
                           "(the first move out of the still pose), development (the PRIMARY MOTION with one tempo word, one or two "
                           "follow-through cues, at most two short lines), result (the end state with the motion still running). "
                           "One person, no partner contact. Each phase has one diegetic sound. Stay within the brief's clip-length spoken-word budget."),
             "prose_req": _PRIMARY_REQ + "- The camera keeps her face and body in frame (she is alone). Foley is breath, fabric, wet "
                                         "skin or the toy's hum, never a slap.\n",
             "onset_hint": "The onset: the first move out of that pose (any garment move uses aside or a removal verb).\n"},
    "strip": {"schema": BEAT_SCHEMA_NOJOIN,
              "beat_task": ("Plan this strip clip as a beat card in JSON. Four phases: anchor (the still pose exactly as shown), onset "
                            "(the first move toward the first garment), development (the PRIMARY MOTION is the removal itself with one "
                            "tempo word, one to three removal steps, each naming the still's garment noun, where it lands and that it "
                            "stays there, with a short hold between steps), result (the end state still moving). One person, no "
                            "contact. Each phase has one diegetic sound. Stay within the brief's clip-length spoken-word budget."),
              "prose_req": ("- One to three removal steps with a removal verb (slides down, pulls off, peels), each naming the garment "
                            "noun, where it lands (the floor at her feet, or a named surface) and that it stays there; no contact; "
                            "a garment that is off stays off.\n"
                            "- The PRIMARY MOTION in this form: 'PRIMARY MOTION - she peels the <garment> down past her hips about one "
                            "slow pull cycle every two seconds; it drops to the floor at her feet and stays there.'\n"
                            "- The camera keeps her face and body in frame (no join, she is alone).\n"),
              "onset_hint": "The onset: the first move out of that pose toward the first garment.\n"},
    "transition": {"schema": _schema_variant(BEAT_SCHEMA_SEX, ["exit", "load", "height", "sound"],
                                             ["follow_through", "sound", "lines"]),
                   "beat_task": ("Plan this position-change clip as a beat card in JSON. Four phases: anchor (the current pose "
                                 "exactly as shown or as the last clip ended), onset (the exit from that pose and who moves whom), "
                                 "development (the bodies landing in the new pose in the act's own words, contact held if it was "
                                 "held), result (the new pose landed with a slow first motion). Each phase has one diegetic sound. "
                                 "Stay within the brief's clip-length spoken-word budget."),
                   "prose_req": _CLEAR_REQ + ("- One sentence that lands the new pose in the act's own words (on her back, hands and knees, "
                                 "astride, on her side, face down); any motion stays slow.\n"),
                   "onset_hint": "The onset: the exit from that pose and who moves whom.\n"},
    "talk": {"schema": BEAT_SCHEMA_TALK,
             "beat_task": ("Plan this talk-only clip as a beat card in JSON. Four phases: anchor (the still pose exactly as shown), onset "
                           "(the one physical action that moves the story), development (two or three short spoken lines), result (the last "
                           "line and an end state that is still moving). Three to five lines in total, about five to eight words each, "
                           "within the brief's clip-length spoken-word budget. Each phase has one diegetic sound tied to its action. No sex, no contact."),
             "prose_req": ("- Three or four short spoken lines across the phases, within the brief's clip-length spoken-word budget; "
                           "no contact and no PRIMARY MOTION.\n"),
             "onset_hint": "The onset: the one physical action that moves the story.\n"},
}


def mode(kind: str) -> Dict[str, Any]:
    return MODES.get(kind) or MODES["sex"]


# Overlays ride on the base card (never new acts): one plan note + one prose note each.
OVERLAY_NOTES: Dict[str, str] = {
    "bts": ("BTS interview: the off-screen interviewer has no body, no <Subject 2> entry and no (Sn) label; "
            "script two short interviewer questions as 'An off-screen interviewer asks, <d>[English] ...</d>' "
            "(without (S2)), and (S1) answers on screen with two short spoken lines of her own (4 spoken lines total). Do not skip the beat card."),
    "cinematic": "Film look (never write the words cinematic or beautiful): one motivated camera job (held, a slow push-in, a locked medium or a low angle), light that separates the bodies, at most one line per speaker.",
    "gonzo": "Gonzo: closer framing (medium-close), light handheld energy, a faster tempo, lens looks written in the action prose.",
    "pov": "POV: the camera is the dominant's eye line, medium or medium-close, (S1) looks toward the lens, only his hands or forearms enter frame (named once). Write no camera sentence of your own; the builder's POV camera line is the only one.",
    "edge": "Edge: the denial is tempo or one full pull-out pause with entry kept full; one denial moment.",
    "forced_orgasm": "Forced orgasm: one or two overstimulation cues in the body, PRIMARY MOTION keeps going through the result, her lines are fragments of three words or fewer.",
    "defeat": "Superheroine defeat: an original adult heroine, one strength beat, one break moment, one costume move that stays, her voice drops; no named hero and no quoted line. Her lines and her face carry the tone slot from the first line to the last frame.",
    "cnc": "Consensual non-consent fantasy between adults: one protest beat inside the action and his override by grip or command; no safeword unless asked.",
    "taboo_role": "Role-play between adults: one role for the clip, at most one title per line, tied to something visible.",
    "spoof": "Spoof: original characters only, one genre flavour and cadence, one visual nod; film look as light, lens and grain words, no real names and no famous quotes.",
    "vhs": "VHS camcorder look: soft analog camcorder video with slight colour bleed and tracking lines, handheld camcorder energy, never a phone or smartphone.",
    "states": "States / fantasy setup: keep every character an adult; any consent/roleplay agreement belongs in its own separate setup clip, never inside the sex clip.",
    "restraints": "Restraints: name the restraint, who set it and its limit once; it stays on to the last frame. Tie her wrists to the {surface} she lies on, or he holds them; name no other anchor.",
    "toy": "Toy: define it once (type, size, who controls it); solo, the toy is the PRIMARY MOTION with tempo; with a partner, penetration is the PRIMARY MOTION and the toy rides in the follow-through; insertion or removal is one move each with where it rests.",
    "threesome": "Three adults at most: define (S3) (look, clothes, entrance), give each hand an owner such as (S3)'s left hand, at most two lines per speaker.",
    "continued": "Continued clip: open from the previous end state; never restate a finished action or reset a garment.",
    "nonhuman": ("Non-human partner: (S2) is a creature (no RefMod); describe his look once in the card, keep it the same all clip, "
                 "never call him a man. Still nouns win on costume, place, roles, wardrobe, races and scale."),
    "consent_setup": ("Agreed roleplay (porn-style, Derrick t1457u): in the opening clip, before any sex, give one quick consent beat: "
                      "a short playful line from her (e.g. <d>Wake me up like that tonight.</d>) or a nod or wink before a sleep/hypnosis/sedative setup; "
                      "for an awake MDMA/party setup chosen together, show mutual awake eagerness (smiles, pulls him close, touch-seeking hands, or an eager line)."),
    "scale": ("Size play: fix one measurable scale anchor in the card (e.g. 'she is no taller than his forearm') and keep it all clip. "
              "A tiny or fairy woman is an adult woman at miniature scale: write her adult face, full adult breasts, wide adult hips "
              "and an adult woman's proportions. Oversized anatomy is named once, with a slow entry and a firm grip. A carry or "
              "held-in-air pose has a measurable hold (his hands locked under her thighs) and her weight on his arms. "
               "(S2)'s definition uses the partner type from the ask (a giant adult man, about twice her height; oversized)."),
}


def overlay_text(overlays: List[str], surface: Optional[str] = None) -> str:
    notes = [OVERLAY_NOTES[o].replace("{surface}", surface or "surface") for o in overlays if o in OVERLAY_NOTES]
    return ("\nOVERLAYS (apply to this clip):\n" + "\n".join("- " + n for n in notes) + "\n") if notes else ""


def _lines_to_topics(schema: Any) -> Any:
    """Dialogue is written per prose candidate (acceptance-1 fix b): the beat card carries line topics, never the words."""
    if isinstance(schema, dict):
        out = {}
        for k, v in schema.items():
            if k == "properties":
                out[k] = {("line_topics" if kk == "lines" else kk): ({"type": "array", "items": {"type": "string"},
                          **({"minItems": vv["minItems"]} if "minItems" in vv else {}), **({"maxItems": vv["maxItems"]} if "maxItems" in vv else {})}
                          if kk == "lines" else _lines_to_topics(vv)) for kk, vv in v.items()}
            elif k == "required":
                out[k] = ["line_topics" if r == "lines" else r for r in v]
            else:
                out[k] = _lines_to_topics(v)
        return out
    return schema


def schema_errors(obj: Any, schema: Dict[str, Any], path: str = "$") -> List[str]:
    errs: List[str] = []
    t = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool}
    allowed = [t] if isinstance(t, str) else (list(t) if isinstance(t, list) else [])
    if allowed:
        ok = any(a in types and isinstance(obj, types[a]) and not (a in ("integer", "number") and isinstance(obj, bool))
                 for a in allowed)
        if not ok:
            return [f"{path}: expected {t}"]
    if isinstance(obj, dict) and (t == "object" or "object" in allowed):
        for k in schema.get("required", []):
            if k not in obj:
                errs.append(f"{path}.{k}: missing")
        for k, sub in (schema.get("properties") or {}).items():
            if k in obj:
                errs += schema_errors(obj[k], sub, f"{path}.{k}")
    if isinstance(obj, list) and (t == "array" or "array" in allowed):
        if len(obj) < schema.get("minItems", 0) or len(obj) > schema.get("maxItems", 10 ** 6):
            errs.append(f"{path}: {len(obj)} items")
        for i, it in enumerate(obj):
            errs += schema_errors(it, schema.get("items") or {}, f"{path}[{i}]")
    if isinstance(obj, str) and not obj.strip():
        leaf = path.rsplit(".", 1)[-1]
        if leaf not in ("contact", "hair", "species", "scale_anchor", "anatomy", "matches_still", "still", "prop_hand"):
            errs.append(f"{path}: empty")
    return errs


for _m in MODES.values():
    _m["schema"] = _lines_to_topics(_m["schema"])
    _m["beat_task"] += (" For talk, give line_topics only (who speaks and what the line is about, from the still or the line "
                        "focus), never the spoken words; the words are written fresh in the prose.")


def parse_json(text: str) -> Any:
    t = re.sub(r"```(?:json)?", "", text or "")
    a, b = t.find("{"), t.rfind("}")
    return json.loads(t[a:b + 1]) if a >= 0 and b > a else json.loads(t)


# builder-required words per act (consistency gate), written into the brief so the card and the prose carry them
ACT_NOTES = {
    "cowgirl": ("write this clause word for word inside the PRIMARY MOTION sentence: 'she rises and sinks on him, his hips "
                "lifting a few inches off the {surface} to meet her as she sinks'. Contact: 'his penis inside her vagina'."),
    "finish": ("(S1) kneels on the {surface} in front of him, weight on both knees, sitting back on her heels, face tilted up; "
               "(S2) stands with his hips level with her face; she is silent from the moment he is at her lips. Foley is breath "
               "and wet sounds, never a slap. Contact: his penis at her lips; the glans as he releases; the semen lands on her cheeks "
               "and lips and stays."),
    "titjob": ("(S1) kneels on the {surface}, sitting back on her heels, weight on both knees, and presses her breasts together "
               "around his shaft with both palms; (S2) stands, hips level with her chest; she is silent from the moment he is at "
               "her lips. Contact: his shaft pressed between her breasts (never 'sheathed')."),
    "mmf": ("(S3) kneels behind her between her knees; (S2) kneels in front of her head, his hips level with her face; she is "
            "silent while (S2) is in her mouth (her side is wet suction and breath through her nose). Contact: '(S2)'s penis is "
            "inside her mouth, her lips sealed around his shaft' (never sheathed, never hips flush for the mouth). (S3) has no "
            "spoken line; give (S3) a full look in the card (age 25 or older, build, hair, attire)."),
    "doggy": ("If the surface is a log or the place is sand: (S1) is on her knees in the sand, forearms on the log, not kneeling on top of the log. "
               "The end pose of the clip is knees in the sand, forearms on the log, so the next clip inherits that (never 'all fours on the log'). "
               "Never write 'seats himself'."),
    "handjob": "Contact: her fist wrapped around his shaft; this is not a titjob.",
    "ff_cunnilingus": ("(S1) sits on the {surface} edge, thighs apart; (S2) kneels between them, her mouth sealed over (S1)'s vulva, tongue on her clitoris. "
                        "Never use blowjob or 'in her mouth' wording."),
    "ff_scissoring": ("Both lie on their sides facing opposite ways, legs interlocked in an X. Contact sentence, word for word: "
                        "'vulva pressed to vulva'."),
    "ffm": ("Contact: '(S2)'s penis inside (S1)'s vagina' and '(S3)'s mouth on (S1)'s breast or vulva'. Name those anatomy nouns in the entry sentence."),
}
LINE_ANGLES = ["a command about what he does next", "a reaction to the pace", "a plea or a dare in the tone slot",
               "praise or teasing about his body", "a question to him that the action answers", "a short gasped fragment"]
CONTINUE_NOTE = ("CONTINUED: the 'At first' sentence is the inherited end state (pose, join, garments) word for word: "
                 "'At first, {state}.' There is no move out of the still and no re-entry; the motion is already running. If the previous "
                 "clip had no join, write the entry before the PRIMARY; the 'At first' sentence is a full clause with (S1) as its subject.")
# acceptance-2 e: openings rotate (not every clip 'At first, (S1) leans/sits/stands')
OPENING_LEADS = ["her hands", "her gaze toward the lens", "her hair", "the light on her skin", "her hips", "her garment",
                 "her breath", "her bare shoulders"]
MALE_OPENING_LEADS = ["his hands", "his gaze toward the side", "the light in the room", "his stance", "his shoulders", "his breath"]
SURFACE_HEIGHT = [("waist", r"sideboard|table|counter|desk|dresser|vanity|bar|kitchen island|washing machine|piano"),
                  ("low", r"bed|sofa|couch|log|sand|mattress|bench|chaise|futon|lounger|rug|blanket|towel"),
                  ("floor", r"floor|ground|carpet|grass|deck")]


def surface_height(surface: str) -> str:
    for h, pat in SURFACE_HEIGHT:
        if re.search(r"(?i)\b(?:" + pat + r")\b", surface or ""):
            return h
    return "low"


def shots_line(n: int, frames: int) -> str:
    """B1 (long-scene spec): cut clocks for an n-shot clip, evenly spaced on the R8 grid."""
    secs = frames / 24.0
    cuts = [round(secs * i / n, 3) for i in range(1, n)]
    clk = ", ".join(f"[Shot {i + 2}] At 00:{c:06.3f}" for i, c in enumerate(cuts))
    return (f"SHOTS: this clip has {n} shots. Write [Shot 1] as usual, then each cut in order as its own sentence group: {clk}, "
            "the camera cuts to <a new size or angle on the same action>. The action, tempo and screen sides never change at a cut.")


def brief_block(ask: str, position: str, kind: str, slots: Dict[str, Any], bodies: int) -> str:
    lines = [f"ASK: {ask}", f"POSITION: {position} ({kind})", "STILL FACTS (Picture 1):"]
    for k in ("place", "surface", "floor", "light", "pose", "framing", "garment", "hair", "skin", "build"):
        if slots.get(k):
            lines.append(f"- {k}: {slots[k]}")
    if slots.get("props"):
        lines.append("- props: " + ", ".join(slots["props"]))
    if slots.get("restraints"):
        lines.append("- restraints: " + ", ".join(slots["restraints"]))
    lines.append(f"- facing the camera: {'yes' if slots.get('facing_camera') else 'no'}")
    if slots.get("join_garments") and wp_lint.mode_rules(kind)["clearance"]:
        lines.append("- covers the join: " + ", ".join(slots["join_garments"]))
        if wp_lint._join_inherited_clear(slots, None):
            lines.append("CLEARANCE: the " + wp_lint.join_noun(slots) + " is already aside from the last clip; keep it there, no new clearance sentence.")
        else:
            jn = wp_lint.join_noun(slots)
            if re.search(r"(?i)\b(?:top|bra|halter)\b", jn):
                lines.append(f"CLEARANCE (before any entry or contact sentence): '(S2) pushes her {jn} up off her breasts, where it stays.' Only the garment over the join is pulled aside at her hip.")
            else:
                lines.append(f"CLEARANCE (before any entry or contact sentence): '(S2) pulls her {jn} aside to one side at her hip, where it stays.' A top is pushed up off her breasts, never aside at her hip.")
    act = br.get_act(position) or {}
    if partner_sex(ask, "") == "futa":
        lines.append("PARTNER: (S2) is a futa woman; refer to her as she/her, never he, his, him or the man (builder P2). "
                     "Contact: '(S2)'s penis is fully sheathed inside her vagina, hips flush.'")
    if ACT_NOTES.get(act.get("id")):
        lines.append(f"ACT RULE ({act.get('id')}): " + ACT_NOTES[act["id"]].format(surface=slots.get("surface") or "surface"))
    ask_l = ask or ""
    if re.search(r"(?i)\b(?:asleep|sleep(?:ing|s)?|wake her)\b", ask_l):
        lines.append("SLEEP: after the agreement line, she lies still, eyes closed, breathing slow; she wakes during PRIMARY MOTION.")
    if re.search(r"(?i)\btelekinesis\b|\bfloat", ask_l):
        lines.append("TELEKINESIS: (S1) floats on her back at his hip height, held in the air by his raised hand; nothing is under her.")
    if re.search(r"(?i)\btentacles?\b", ask_l):
        lines.append("TENTACLES: tentacles coil around her thighs and wrists and hold; one tentacle is fully inside her vagina and thrusts at the tempo.")
    if re.search(r"(?i)\bvhs\b|16mm|film grain|camcorder", ask_l):
        lines.append("VHS LOOK: write the film look as grain, colour bleed and tracking; never the words cinematic or beautiful.")
    if re.search(r"(?i)\b(?:vampire|costume|uniform|nurse|maid)\b", ask_l):
        lines.append("ROLE COSTUME: name the costume item from the still or the ask once and keep it on unless the ask removes it.")
    if re.search(r"(?i)\bgiant", ask_l):
        lines.append("SCALE: (S2) is a giant adult man, about twice her height; say that once in his definition and keep the anchor.")
    if re.search(r"(?i)\boversized|massive oversized", ask_l):
        lines.append("SCALE: name the oversized anatomy once with a measurable size, slow entry, and a firm grip.")
    lines.append("Never write 'seats himself'; land the pose in (S1)'s own words.")
    surf_noun = re.sub(r'^(?:the|a|an)\s+', '', (slots.get('surface') or 'surface').strip(), flags=re.I)
    if slots.get("surface_height") == "waist" and kind in ("sex", "transition") and act.get("id") in ("missionary", "mf_anal"):
        lines.append(f"HEIGHT: the {surf_noun} is waist-high, so (S1) lies back on it and (S2) stands at its edge "
                     "between her legs; he does not kneel on it. Write this pose in your own full sentence with (S1) as its subject; do not paste it.")
    if slots.get("surface_height") == "waist" and act.get("id") == "standing_mf":
        lines.append(f"HEIGHT: the {surf_noun} is waist-high, so (S1) stands at its edge, bends forward at the hips and "
                     "lays her forearms and chest on it, weight on both feet; (S2) stands behind her. Write this pose in your own full sentence with (S1) as its subject; do not paste it.")
    if act.get("id") == "standing_mf":  # #4
        lines.append(f"LANDING: land it as 'bent forward over the {surf_noun}, both feet planted'; never write "
                     "hands and knees, all fours or doggy.")
    if slots.get("surface_height") == "waist" and act.get("id") == "mmf":  # #6
        sf = surf_noun
        lines.append(f"HEIGHT: (S1) bends forward over the {sf}, feet planted; (S3) stands behind her; (S2) stands at the far side, "
                     "hips level with her face; she is silent while (S2) is in her mouth; (S2) holds her head and her head bobs "
                     "along his shaft." + " Write this pose in your own full sentence with (S1) as its subject; do not paste it.")
    if slots.get("place"):
        lines.append(f"PLACE: name only the still's place ({slots['place']}); never add a room, balcony, headboard or location.")
    lines.append("LINES: line_topics never name the surface, the floor or the furniture, never his grip, his hands or his strength, "
                 "and never the word deep; each line is "
                 "spoken to the partner about the act, his body or hers, in the tone slot.")
    if slots.get("opening_lead") and not slots.get("inherited"):
        if (position == "male_solo") or re.search(r"(?i)\bmale solo\b", ask or ""):
            lines.append(f"OPENING: the 'At first' sentence has (S1) as its subject, keeps the still's setting and {surf_noun} "
                         f"surface noun, and never starts with 'breathes heavily'; it may add a detail about {slots['opening_lead']}.")
        else:
            lines.append(f"OPENING: the 'At first' sentence has (S1) as its subject, keeps the still's pose and surface noun "
                         f"('(S1) leans against the {surf_noun}'), and never starts with 'breathes heavily'; "
                         f"it may add a detail about {slots['opening_lead']}.")
    lines.append("SUMMARY: summary is one plain sentence: who, where, the act; never the camera line, 'At first' or 'As it builds'.")
    if act.get("contact_verbs") or act.get("motion_verbs"):  # the act's own vocabulary from acts.yaml (routing data, no new rule)
        lines.append(f"ACT {act.get('id')}: contact words {', '.join(act.get('contact_verbs') or [])}; motion words "
                     f"{', '.join(act.get('motion_verbs') or [])}")
    clip_frames = int(slots.get("frames") or br.SINGLE_CLIP_MAX_FRAMES)
    clip_secs = float(slots.get("clip_seconds") or round(clip_frames / float(br.H3_FPS), 1))
    word_max = int(slots.get("speech_words_max") or max(1, int(round((clip_frames / float(br.H3_FPS)) * 2.5))))
    lines_max = int(slots.get("max_lines_per_speaker") or max(1, int(round((clip_frames / float(br.H3_FPS)) / 5.0))))
    lines += [f"TONE (the submissive's reaction tone for this clip): {slots['tone']}",
              f"LINE FOCUS (what the talk is about): {slots['line_focus_text']}",
              f"PEOPLE: (S1) is the woman in the still{'; (S2) is her partner, defined by you' if bodies >= 2 else ''}"
              f"{'; (S3) is a third adult, defined by you' if bodies >= 3 and kind != 'talk' else ''}. Everyone is an adult, 25 or older.",
              f"CLIP LENGTH: T = {clip_secs:.1f} s ({clip_frames} frames); spoken words total at most {word_max} "
              f"(at most {lines_max} short line(s) per speaker)."]
    if slots.get("inherited"):
        inh = slots["inherited"]
        def _nz(x):
            s = str(x or "").strip()
            return s if s and s.lower() not in ("none", "null", "-", "no contact", "no contact.") else ""
        state = "; ".join(filter(None, (_nz(inh.get("pose")), _nz(inh.get("contact")))))
        lines.append(CONTINUE_NOTE.format(state=state or "the previous clip's end pose"))
        done = [d for d in (inh.get("done_actions") or []) if _nz(d)]
        lines += ["CONTINUED CLIP: open from the previous clip's end state, already in progress:",
                  f"- pose: {inh.get('pose')}", f"- garments: {json.dumps(inh.get('garments'))}"]
        if _nz(inh.get("contact")):
            lines.append(f"- contact: {inh.get('contact')}")
        lines.append(f"- camera: {inh.get('camera')} (POV: {inh.get('pov')})")
        if done:
            lines.append("- already done (continue from these, the camera already saw them): " + "; ".join(done))
    return "\n".join(lines)


def beat_messages(sysprompt: str, brief: str, kind: str, overlays: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    task = mode(kind)["beat_task"] + overlay_text(overlays or [])
    return [{"role": "system", "content": sysprompt},
            {"role": "user", "content": brief + "\n\n" + task + "\nAnswer with the JSON object only."}]


def prose_messages(sysprompt: str, brief: str, card: Optional[Dict[str, Any]], kind: str,
                   overlays: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    plan = ("BEAT CARD (plan; seconds never appear in the prose):\n" + json.dumps(card, indent=1, ensure_ascii=False)) if card else \
        "BEAT CARD: none (plan the four phases yourself from the still facts)."
    req = mode(kind)["prose_req"] + overlay_text(overlays or [])
    task = ("Write ONLY the detailed_description paragraph for this clip. Required, in this order:\n"
            "- [Shot 1] and one camera sentence.\n"
            "- A sentence that begins 'At first, ' with the still's exact pose, on the still's surface.\n"
            "- " + mode(kind)["onset_hint"] + req +
            "- A sentence that begins 'By the end, ' with the end state, the motion still going.\n"
            "- One to three plain sound sentences tied to the action.\n"
            "Write every spoken line fresh in this paragraph from the card's line_topics (one <d> pair per line, no quotes inside it). "
            "Dialogue format: (S2) says in a <short voice> voice, <d>[English] words</d>. Write every sentence in your own words; "
            "copy no example phrase from the instructions. Plain text, one paragraph, no header, no Markdown.")
    return [{"role": "system", "content": sysprompt},
            {"role": "user", "content": brief + "\n\n" + plan + "\n\n" + task}]


def clean_prose(text: str) -> str:
    t = re.sub(r"```\w*", "", text or "").strip()
    t = re.sub(r"(?im)^\s*detailed_description\s*:\s*", "", t)
    i = t.find("[Shot 1]")
    if i > 0:
        t = t[i:]
    # keep the paragraph only (drop any trailing notes / headers)
    t = re.split(r"\n\s*\n(?=[A-Za-z_ ]+:)", t)[0]
    t = " ".join(t.split())
    if not t.startswith("[Shot 1]"):
        t = "[Shot 1] " + t
    return t


_LANG_TAG_RE = re.compile(r"^\[(?:English|Spanish|French|German|Italian|Portuguese|Japanese|Korean|Chinese|Russian)\]", re.I)


def normalize_prose(dd: str, kind: str, slots: Optional[Dict[str, Any]] = None) -> str:
    """Mechanical fixes only (no new content): unwrap <d>[words]</d> brackets, and put the literal 'PRIMARY MOTION - '
    label on the 'As it builds' sentence when the writer wrote the motion with a tempo word but left the label off."""
    def _d(m: "re.Match[str]") -> str:
        inner = m.group(1).strip()
        if not _LANG_TAG_RE.match(inner):
            mm = re.fullmatch(r"\[(.+)\]", inner)
            if mm:
                inner = mm.group(1).strip()
        return f"<d>{inner}</d>"
    # builder _HIS_CLOTHES_RE (build_request.py:795) matches 'stays bunched' and drops the whole clause, which deletes the
    # clearance and trips W5 (final4_c missionary/doggy). Same meaning, a word the builder keeps:
    dd = re.sub(r"(?i)\b(stay(?:s|ing)?|left|remain(?:s|ing)?) bunched\b", r"\1 gathered", dd)
    # builder _HIS_LIFT_RE (build_request.py:2233) wants 'his hips ... lift' (m09): same meaning, builder word order
    dd = re.sub(r"\((S2)\) lifts his (hips|pelvis)\b", r"his \2 lift", dd)
    dd = re.sub(r"(?i)\bhe lifts his (hips|pelvis)\b", r"his \1 lift", dd)
    # dry-matte skin (Derrick floor): shiny skin words from the read or the writer -> damp
    dd = re.sub(r"(?i)\b(?:glistening|glossy|oily|oiled|shimmering)\b", "damp", dd)
    dd = re.sub(r"(?i)\bdamp,? damp\b", "damp", dd)
    # act ids never ship as prose (c8b 'At first, standing_mf;'): builder ids -> plain words
    surf = (slots or {}).get("surface") or "surface"
    for aid, words in (("standing_mf", f"standing, bent forward over the {surf}"), ("reverse_cowgirl", "reverse cowgirl"),
                       ("mf_anal", "anal"), ("female_solo", "alone"), ("standing_ff", "standing")):
        dd = re.sub(r"\b" + aid + r"\b", words, dd)
    # strip/solo tempo 'every two seconds' is not a builder tempo word (_TEMPO_RE): same tempo, with 'cycle'
    if wp_lint.mode_rules(kind)["primary"] and not br._TEMPO_RE.search(re.sub(r"<d>.*?</d>", "", dd, flags=re.S)):
        dd = re.sub(r"(?i)\b(?:about\s+)?(?:one\s+)?(?:slow\s+|smooth\s+|steady\s+)?(?:move|pull|tug|motion|stroke|peel|step)?\s*"
                    r"every (two|three|four|five|2|3|4|5) seconds\b", r"one slow cycle every \1 seconds", dd, count=1)
    # acceptance-3 (m18): 'two thrusts a second' / 'pumps a second' -> the builder tempo word 'strokes a second'
    dd = re.sub(r"(?i)\b(thrusts?|pumps?|bobs?|pushes|drives|slams?|bounces?)( a second)\b", "strokes a second", dd)
    # tag words never ship (Derrick floor): 'cinematic'/'beautiful' -> drop the adjective
    dd = re.sub(r"(?i)\s*\b(?:cinematic|beautiful(?:ly)?)\b,?", "", dd)
    for k in ("place", "light", "surface", "hair"):  # pmfix6: SHAPE blanks left literal -> fill from still_read slots
        if (slots or {}).get(k):
            dd = re.sub(r"<\s*" + k + r"\s*>", str(slots[k]), dd, flags=re.I)
    for _ in range(3):  # unwrap nested <d><d>..</d></d> the writer sometimes produces
        dd = re.sub(r"<d>\s*(?:\[English\]\s*)?<d>(.*?)</d>\s*</d>", r"<d>\1</d>", dd, flags=re.S)
    dd = re.sub(r"<d>(.*?)</d>", _d, dd, flags=re.S)
    dd = re.sub(r"<d>(\s*(?:\[English\]\s*)?)[\"\u201c\u201d']+(.*?)[\"\u201c\u201d']+</d>", r"<d>\1\2</d>", dd, flags=re.S)
    dd = re.sub(r"(?<![(\w<])S([123])(?![\w)>])", r"(S\1)", dd)  # bare S1 -> (S1)
    # acceptance-3 (m16): once her mouth is on him she is silent (builder D1): drop (S1)'s spoken units after that point
    _mk = re.sub(r"<d>.*?</d>", lambda mm: "\x00" * len(mm.group(0)), dd, flags=re.S)
    _mc = wp_lint.MOUTH_CONTACT_RE.search(_mk)
    if _mc:
        head, tail = dd[:_mc.end()], dd[_mc.end():]
        tail = re.sub(r"(?:(?<=[.!?>])|^)\s*\(S1\)[^<.!?]{0,120}<d>.*?</d>[.!?]?", "", tail, flags=re.S)
        dd = head + tail
    if wp_lint.mode_rules(kind)["primary"] and not br._PRIMARY_RE.search(dd):
        # the first sentence (outside <d>) that carries a tempo word gets the label, after a leading 'As it builds,'
        # acceptance-2 bug 1: mask every <d>...</d> span first, so a line ending in '?' or '!' never puts the label
        # inside the dialogue; a chunk that holds a masked span is only searched after its last span
        masked = re.sub(r"<d>.*?</d>", lambda mm: "\x00" * len(mm.group(0)), dd, flags=re.S)
        for m in re.finditer(r"[^.!?]*[.!?]", masked):
            sent = m.group(0)
            off = sent.rfind("\x00") + 1
            sent = sent[off:]
            if "<d>" in sent or "</d>" in sent or not br._TEMPO_RE.search(sent):
                continue
            lead = re.match(r"(?i)\s*(?:as it builds,\s*)?", sent)
            at = m.start() + off + lead.end()
            dd = dd[:at] + "PRIMARY MOTION - " + dd[at:]
            break
    return glue_fix(dd)


def glue_fix(dd: str) -> str:
    """acceptance-3 review (PM) #1: text glue the lint does not see."""
    dd = re.sub(r"(</d>\s*)(?:\(S\d\) )?adds in an? [^<]{0,40}?(?:tone|voice), and ", r"\1", dd)
    dd = re.sub(r"(?i)\b(the) the\b", r"\1", dd)
    dd = re.sub(r"(?i)\s*;\s*none\.?", "", dd)
    dd = re.sub(r"(?i)\s*;\s*no contact\.?", "", dd)
    dd = re.sub(r"(?i)\b(?:fully\s+)?sheathed in her mouth\b", "inside her mouth", dd)
    dd = re.sub(r"(?i)(?:(?<=[.!?>])|^)\s*(?:none|no contact)\.(?=\s|$)", "", dd)
    dd = re.sub(r"(?i)\bher skin (?:glistening|glistens|glistened|glistening with \w+)\b", "her damp skin", dd)
    dd = re.sub(r"(?i)\b(damp)\b((?:[ ,]+\w+){0,4}?)[ ,]+damp\b", r"\1\2", dd)
    return re.sub(r"\s{2,}", " ", dd).strip()


_S1_ONLY = re.compile(r"(?i)\b(?:bikini|bra|panties|thong|lingerie|stockings|crop top|bodysuit|dress|skirt|slip|teddy|mesh)\b")
_SIDE_RE = re.compile(r"(?i)\b(?:frame )?(?:left|right|behind(?: her)?|the door(?:way)?|off[- ]?screen)\b")


def partner_sex(ask: str, card_sex: str, label: Optional[str] = None) -> str:
    """The ask decides the partner's sex; respects S3 female in FFM and card futa when appropriate."""
    a = (ask or "").lower()
    cs = (card_sex or "").lower().strip()
    if re.search(r"\bffm\b", a):
        if label == "S3":
            return "woman"
        if label == "S2":
            return "futa" if re.search(r"\bfuta\b", cs) else "man"
    if re.search(r"\bmmf\b", a):
        return "man"
    if re.search(r"\bfuta\b", a) and (label != "S3" or re.search(r"\bfuta\b", cs)):
        return "futa"
    if not a and cs == "futa":
        return "futa"
    if re.search(r"\b(?:woman|girl|lesbian|girlfriend|her friend|another woman|second woman|two women|two girls)\b", a):
        if re.search(r"\b(?:him|man|guy|he)\b", a):
            if re.search(r"\b(?:female|woman|girl|f)\b", cs) or label == "S3":
                return "woman"
            return "man"
        return "woman"
    return "man"


def _pick_partner(partners: List[Any], label: str, idx: int) -> Dict[str, Any]:
    """Match partner entry by S2/S3 label first, skipping any S1 entry Gemma placed at index 0."""
    dicts = [p for p in partners if isinstance(p, dict)]

    def _lbl(item: Dict[str, Any]) -> str:
        return re.sub(r"\W", "", str(item.get("label", ""))).upper()

    exact = next((p for p in dicts if _lbl(p) == label), None)
    if exact is not None:
        return exact
    non_s1 = [p for p in dicts if _lbl(p) != "S1"]
    return non_s1[idx] if idx < len(non_s1) else {}


def _clean_attr(s: str, default: str) -> str:
    s = re.sub(r"[<>]", "", (s or "").strip()).rstrip(".")
    return s or default


def _partner_match_clause(p: Dict[str, Any], idx: int, slots: Dict[str, Any]) -> str:
    val = p.get("matches_still") if "matches_still" in p else (p.get("matches") or p.get("still"))
    if isinstance(val, bool):
        if val and idx == 1 and slots.get("s3_still"):
            return "matches <Picture 2>"
        return ""
    raw = str(val or "").strip()
    if not raw and idx == 1 and slots.get("s3_still"):
        raw = "matches <Picture 2>"
    if not raw:
        return ""
    if re.fullmatch(r"(?i)(?:true|false|yes|no|none|null|n/?a|same)", raw):
        if idx == 1 and slots.get("s3_still") and raw.lower() in ("true", "yes", "same"):
            return "matches <Picture 2>"
        return ""
    m = re.search(r"<?\bPicture\s+(\d+)\b>?", raw, flags=re.I)
    if m:
        pic = f"<Picture {m.group(1)}>"
        return raw if raw.lower().startswith("matches") and pic in raw else f"matches {pic}"
    cleaned = _clean_attr(raw, "")
    if not cleaned or not re.match(r"(?i)^matches\b", cleaned):
        return ""
    return cleaned


def assemble_output(dd: str, card: Optional[Dict[str, Any]], slots: Dict[str, Any], bodies: int, kind: str,
                    continuation: Optional[str] = None) -> str:
    place = slots.get("place") or "setting"
    light = slots.get("light") or "light"
    hair = slots.get("hair") or "her hair as shown"
    position = slots.get("position") or ""
    is_male_solo = (position == "male_solo") or re.search(r"(?i)\bmale solo\b", slots.get("ask") or "")
    if is_male_solo:
        sd = [f"<Picture 1> is the reference image defining the {place}, its {light} and the opening framing.",
              f"<Subject 1> is an adult man, twenty-four years of age, of solid adult build; he is (S1), and "
              f"<Audio 1> defines his voice timbre."]
    else:
        sd = [f"<Picture 1> is the reference image defining the exact appearance, face and hairstyle of <Subject 1>, and the {place}, "
              f"its {light} and the opening framing.",
              f"<Subject 1> is the exact same woman shown in <Picture 1>; an adult woman, 25 years of age, {hair}; she is (S1), and "
              f"<Audio 1> defines her voice timbre."]
    partners = (card or {}).get("partners") or []
    want = 1 if bodies == 2 or kind == "talk" else (2 if bodies >= 3 else 0)
    if kind == "talk" and not re.search(r"\(S2\)", dd):
        want = 0
    for i in range(want):
        label = f"S{i + 2}"
        p = _pick_partner(partners, label, i)
        sex = partner_sex(slots.get("ask") or "", str(p.get("sex") or ""), label=label)
        age = p.get("age") if isinstance(p.get("age"), int) and not isinstance(p.get("age"), bool) else 30
        age = max(25, min(int(age), 60))
        pron = "he" if sex == "man" else "she"
        # Derrick t1411u SHAPE form (one sentence, "and he is"): the builder's partner gate splits on ';' (shapes2)
        build = _clean_attr(p.get("build"), "athletic build")
        if build.lower() == (slots.get("build") or "").lower() or re.search(r"(?i)\b(?:curvy|petite|busty)\b", build):
            build = "athletic build" if sex == "man" else "slim build"
        attire = _clean_attr(p.get("attire"), "")
        same_as_s1 = any(g.lower() in attire.lower() for g in (slots.get("garments_all") or []) if g)
        bad_man_attire = (sex == "man") and bool(_S1_ONLY.search(attire))
        if not attire or bad_man_attire or same_as_s1:
            attire = "a dark t-shirt and jeans" if sex == "man" else "a black dress"
        sm = _SIDE_RE.search(str(p.get("enters_from") or ""))
        side = ("the " + sm.group(0).lower()) if sm and not sm.group(0).lower().startswith(("the", "behind", "off")) else (
            sm.group(0).lower() if sm else "the right")
        species = _clean_attr(p.get("species"), "")
        if species and species.lower() not in ("human", "person"):
            role = f"the {species}, an adult" if sex == "man" else (
                f"the {species} futa woman, an adult" if sex == "futa" else f"the {species} woman, an adult"
            )
        else:
            role = {"man": "the man, an adult", "woman": "the woman, an adult", "futa": "the woman, an adult futa"}[sex]
        anat = _clean_attr(p.get("anatomy") or p.get("futa_anatomy"), "")
        scale = _clean_attr(p.get("scale_anchor") or p.get("scale"), "")
        match_str = _partner_match_clause(p, i, slots)
        extras = ", ".join(x for x in (anat, scale, match_str) if x)
        extra_part = f", {extras}" if extras else ""
        sd.append(f"<Subject {i + 2}> is {role}, {age} years of age, {build}{extra_part}, in {attire}, who enters from {side} "
                  f"and {pron} is ({label}).")
    _sum_surf = re.sub(r'^(?:the|a|an)\s+', '', (slots.get('surface') or 'surface').strip(), flags=re.I)
    _pos_id = str(slots.get('position') or 'scene').strip()
    _POS_SUMMARY = {
        "standing_mf": "standing", "ff_scissoring": "scissoring", "ff_cunnilingus": "cunnilingus",
        "mmf_double_blowjob": "double blowjob", "mmf_dp": "double penetration",
        "reverse_cowgirl": "reverse cowgirl", "prone_bone": "prone bone",
        "female_solo": "solo", "male_solo": "male solo",
    }
    _pos_human = _POS_SUMMARY.get(_pos_id, _pos_id.replace("_", " "))
    summary = _clean_attr((card or {}).get("summary"), f"(S1) in a {_pos_human} scene on the {_sum_surf}")
    # #2: one plain sentence of who, where and the act; never the camera line or the phase scaffold
    _ss = [x for x in re.split(r"(?<=[.!?])\s+", summary) if x.strip() and not re.match(r"(?i)\s*the camera\b", x)]
    summary = re.sub(r"(?i)\b(?:at first|as it builds|by the end),?\s*", "", (_ss[0] if _ss else summary)).strip().rstrip(".")
    summary = (summary[:1].upper() + summary[1:]) if summary else f"(S1) in a {slots.get('position')} clip"
    # acceptance-3 (m08): tag words and shine words never ship in the summary either
    summary = re.sub(r"\s{2,}", " ", re.sub(r"(?i)\b(?:cinematic|beautiful(?:ly)?)\b,?\s*", "", summary)).strip()
    summary = re.sub(r"(?i)\b(?:glistening|glossy|oily|oiled|shimmering)\b", "damp", summary)
    summary = re.sub(r"\b(?:A|An) (?=[aeiou])", "An ", re.sub(r"\bAn (?=[^aeiouAEIOU])", "A ", summary))
    ret_line = ("<Subject 1>: not_in_clip - clip is male solo, (S1) is the man. <Picture 1>: fully_preserved - the "
                f"{place}, the light and the opening framing." if is_male_solo else
                "<Subject 1>: fully_preserved - face, hair and body from <Picture 1>. <Picture 1>: fully_preserved - the "
                f"{place}, the light and the opening framing.")
    out = ["subject_definitions:", *sd, "", "summary:", summary + ".", "", "retention_analysis:",
           ret_line, "", "detailed_description:", dd]
    if continuation:
        out += ["", "continuation:", continuation]
    return "\n".join(out) + "\n"


def rewrite_messages(sysprompt: str, brief: str, card: Optional[Dict[str, Any]], dd: str, notes: List[str],
                     kind: str = "sex", overlays: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    msg = prose_messages(sysprompt, brief, card, kind, overlays)
    msg[1]["content"] += ("\n\nYOUR DRAFT:\n" + dd + "\n\nRewrite the draft once. Fix exactly these points and keep everything "
                          "else that works:\n" + "\n".join(f"- {n}" for n in notes) +
                          "\nAnswer with the rewritten detailed_description paragraph only.")
    return msg


def judge_format(letters: List[str]) -> Dict[str, Any]:
    """Totals only (no per-criterion objects, which ran past max_tokens) and a strict ranking of the letters."""
    sch = {"type": "object", "required": ["scores", "ranking", "best"],
           "properties": {"scores": {"type": "object", "required": letters,
                                     "properties": {l: {"type": "integer", "minimum": 5, "maximum": 25} for l in letters}},
                          "ranking": {"type": "array", "items": {"type": "string", "enum": letters},
                                      "minItems": len(letters), "maxItems": len(letters)},
                          "best": {"type": "string", "enum": letters}}}
    return {"type": "json_schema", "json_schema": {"name": "judge", "schema": sch}}


def judge_letter(jd: Dict[str, Any], letters: List[str]) -> str:
    """'CANDIDATE A', 'A', 'Candidate: B', ranking[0] or the top score -> one letter that exists (fixes 'CANDIDATE A' -> 'C')."""
    def one(v: Any) -> str:
        t = str(v or "").strip().upper()
        m = re.fullmatch(r"(?:CANDIDATE\s*[:#-]?\s*)?([A-Z])\.?", t) or re.search(r"\b([A-Z])\b(?!.*\b[A-Z]\b)", t)
        return m.group(1) if m and m.group(1) in letters else ""
    b = one(jd.get("best"))
    if not b and isinstance(jd.get("ranking"), list) and jd["ranking"]:
        b = one(jd["ranking"][0])
    if not b and isinstance(jd.get("scores"), dict):
        tot = lambda v: v if isinstance(v, (int, float)) else (v.get("total") if isinstance(v, dict) and isinstance(v.get("total"), (int, float))
                                                                else sum(x for x in v.values() if isinstance(x, (int, float))) if isinstance(v, dict) else None)
        sc = {one(k): tot(v) for k, v in jd["scores"].items() if one(k) and tot(v) is not None}
        if sc:
            b = max(sc, key=sc.get)
    return b


def judge_messages(cands: List[Tuple[str, str]], brief: str) -> List[Dict[str, Any]]:
    body = "\n\n".join(f"CANDIDATE {name}:\n{dd}" for name, dd in cands)
    return [{"role": "system", "content": "You judge short adult video clip prompts. Score each candidate 1-5 on five points: "
             "still-specific (uses the still's own place, surface, garment and light), fresh talk (lines written for this scene), "
             "power dynamic (clear and consistent), physical continuity (bodies move in a possible order), rhythm (varied "
             "sentences, reads as one take). Use the full 1-5 range and give the candidates different totals. Answer JSON only: "
             "{\"scores\": {\"A\": <total 5-25>, ...}, \"ranking\": [\"<letter best first>\", ...], \"best\": \"<letter>\"}."},
            {"role": "user", "content": brief + "\n\n" + body}]


# ---- builder preview + build ----------------------------------------------------------------------------------------
def make_cast(still_read: Dict[str, Any], position: str, ask: str, continued: bool = False,
              inherited_garments: Optional[Dict[str, str]] = None) -> Tuple[Dict[str, Any], str]:
    still_people = None
    rd = br._unwrap_still_read(still_read)
    if rd.get("people"):
        still_people = len(rd["people"]) if isinstance(rd["people"], list) else rd["people"]
    hook_act = (br.get_act(position) or {}).get("id") if position else None
    brief = scene_addenda.resolve_brief(ask or "", act_id=hook_act, registry=br.load_acts_registry(),
                                        still_people=still_people if isinstance(still_people, int) else None)
    if not hook_act and brief.get("act_id") and br.get_act(brief["act_id"]):
        position = brief["act_id"]
    mk: Dict[str, Any] = {}
    if brief.get("partner_type"):
        mk["partner_type"] = brief["partner_type"]
    if br._CREATURE_RE.search(ask or ""):
        mk["partner_type"] = "non-human"  # nonhuman overlay (G1)
    if partner_type_for(position, ask) and not mk.get("partner_type"):
        mk["partner_type"] = partner_type_for(position, ask)
    if partner_type2_for(position, ask):
        mk["partner_type2"] = partner_type2_for(position, ask)
    if continued:
        mk["continued"] = True
    if inherited_garments:
        mk["inherited_garments"] = dict(inherited_garments)
    if re.search(r"(?i)\bgiant", ask or ""):
        mk["man"] = "a giant adult man, about twice her height, twenty-six years of age, of solid adult build"
    ck = brief.get("camera_kind")
    if ck and ck not in ("third_person", "third-person"):
        mk["camera_kind"] = br._CAM_KIND_MAP.get(ck, ck)
    if (brief.get("s1_gender") == "man") or ((hook_act or brief.get("act_id") or position) == "male_solo"):
        still_read, _ = strip_male_solo_still_read(still_read)
        mk["voice_s1"] = "a deep, steady adult man's voice, low and hoarse"
    return br.make_cast(still_read, position, ask, **mk), position


def builder_preview_fn(still_read: Dict[str, Any], position: str, ask: str, continued: bool = False,
                       inherited_garments: Optional[Dict[str, str]] = None):
    def preview(full: str) -> Dict[str, Any]:
        try:
            cast, _ = make_cast(still_read, position, ask, continued=continued, inherited_garments=inherited_garments)
            _, rep = br.finalize_writer_prompt(full, cast, strict=True)
            return {"added": rep.get("added", []), "violations": rep.get("violations", []),
                    "dropped": (rep.get("speech") or {}).get("dropped", []), "state": rep.get("state"),
                    "not_ready": rep.get("not_ready") or ""}
        except br.WriterPromptError as e:
            return {"error": str(e), "added": []}
        except Exception as e:  # preview is advisory; the real dry build decides
            return {"preview_exception": f"{type(e).__name__}: {e}", "added": []}
    return preview


MMF_FACELESS_ACTS = ("mmf", "mmf_double_blowjob", "threesome")


def partner_type2_for(position: str, ask: str) -> Optional[str]:
    """Derrick t1437s5374 / t1467: MMF S2 and S3 are faceless by default (look text or a still, no RefMod)."""
    act = ((br.get_act(position) or {}).get("id") if position else None) or position
    if act in MMF_FACELESS_ACTS and not re.search(r"(?i)\b(?:ffm|two (?:women|girls)|another (?:woman|girl))\b", ask or ""):
        return "faceless"
    return None


def partner_type_for(position: str, ask: str) -> Optional[str]:
    """S2 on an MMF job stays a regular man (not faceless) unless the ask names a futa or non-human partner."""
    return None


_COLOUR_END_RE = re.compile(r"(?i)\b(?:dark|black|brown|blond|blonde|red|grey|gray|white|silver|auburn|copper|light|short|long)\s*,?$")


def s3_look_from_card(card: Optional[Dict[str, Any]]) -> Optional[str]:
    return partner_look_from_card(card, "S3")


def partner_look_from_card(card: Optional[Dict[str, Any]], label: str = "S3") -> Optional[str]:
    """MMF S3 (Derrick t1440), S2 too (#14): the card's partner as one fixed look line; None when the card has none."""
    p3 = next((p for p in ((card or {}).get("partners") or []) if re.sub(r"\W", "", str(p.get("label", ""))).upper() == label), None)
    if not p3 or not (p3.get("build") or p3.get("attire")):
        return None
    try:
        age = max(25, int(p3.get("age") or 30))
    except (TypeError, ValueError):
        age = 30
    sex = "woman" if re.search(r"(?i)\b(?:female|woman|f)\b", str(p3.get("sex", ""))) else "man"
    species = _clean_attr(p3.get("species"), "")
    if species and species.lower() not in ("human", "person"):
        head = f"an adult {species}" if sex == "man" else f"an adult {species} woman"
    else:
        head = f"an adult {sex}"
    bits = [f"{head}, {age} years of age", f"of {_clean_attr(p3.get('build'), 'solid')} build".replace("build build", "build")]
    if p3.get("anatomy") or p3.get("futa_anatomy"):
        bits.append(_clean_attr(p3.get("anatomy") or p3.get("futa_anatomy"), ""))
    if p3.get("scale_anchor") or p3.get("scale"):
        bits.append(_clean_attr(p3.get("scale_anchor") or p3.get("scale"), ""))
    if p3.get("hair"):
        h3 = _clean_attr(p3.get('hair'), '').rstrip(" ,")
        if _COLOUR_END_RE.search(h3):  # #14: 'short dark' keeps its noun
            h3 += " hair"
        bits.append(f"with {h3}" + ("" if re.search(r"(?i)\b(?:hair|bald|shaved|buzz|cut|crop|beard)\b", h3) else " hair"))
    if p3.get("attire"):
        bits.append(f"in {re.sub(r'(?i)^(?:in|wearing)\s+', '', _clean_attr(p3.get('attire'), ''))}")
    return re.sub(r"(?i)\b(?:cinematic|beautiful)\b\s*", "", ", ".join(b for b in bits if b.strip()))


def run_build(run_dir: Path, ask: str, position: str, still: str, character: Optional[str], timeout: int = 300,
              extra: Optional[List[str]] = None) -> Dict[str, Any]:
    """Existing dry-run hook. Never passes --queue."""
    cmd = [sys.executable, str(SUBMIT_PY), "writer-run", str(run_dir), "--ask", ask, "--position", position, "--still", still]
    cmd += list(extra or [])
    if character:
        cmd += ["--character", character]
    if partner_type_for(position, ask) and "--partner-type" not in cmd:
        cmd += ["--partner-type", partner_type_for(position, ask)]
    if partner_type2_for(position, ask) and "--partner-type2" not in cmd:
        cmd += ["--partner-type2", partner_type2_for(position, ask)]
    assert "--queue" not in cmd
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(PARODY_DIR))
    rep = {}
    try:
        rep = json.loads((run_dir / "build_report.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    line = (p.stdout or "").strip().splitlines()[-1] if (p.stdout or "").strip() else ""
    status = "READY" if p.returncode == 0 and rep.get("status") == "READY" else "NOT_READY"
    return {"status": status, "rc": p.returncode, "stdout": line[:600], "stderr": (p.stderr or "")[-600:], "report": rep,
            "seconds": round(time.time() - t0, 2), "reason": rep.get("reason") or line}


def kept_lines(full: str, rep: Dict[str, Any]) -> List[str]:
    dropped = {wp_lint.norm(d.get("line", "")) for d in ((rep.get("build") or {}).get("speech") or {}).get("dropped", [])}
    return [m.group(1).replace("[English]", "").strip() for m in br._D_RE.finditer(wp_lint.get_dd(full))
            if wp_lint.norm(m.group(1)) and wp_lint.norm(m.group(1)) not in dropped]


# ---- still handling -------------------------------------------------------------------------------------------------
def auto_still(cfg: Dict[str, Any], run_id: str, ask: str) -> str:
    pool = []
    for g in cfg.get("still_pool") or []:
        pool += [p for p in glob.glob(os.path.expanduser(g), recursive=True) if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    if not pool:
        raise RuntimeError("still auto: the still pool is empty")
    return random.Random(seed_for(run_id, ask, 7)).choice(sorted(pool))


_SHINE_RE = re.compile(r"(?i)\b(?:glistening|glisten\w*|oily|oiled|glossy|shiny|shimmering|slick)\b(?:\s+(?:with\s+)?(?:wet\s+)?skin)?")
MATTE_SKIN = "damp skin with a soft natural sheen and visible pores"


def clean_still_read(d: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """acceptance-2 item 9: 'unseen' floor -> 'the floor'; shiny skin words -> the dry-matte wording. Pipeline data only."""
    changed: List[str] = []
    rd = d.get("read") if isinstance(d.get("read"), dict) else d

    def fix(v: Any, key: str) -> Any:
        if isinstance(v, str):
            nv = v
            if key == "floor" and re.fullmatch(r"(?i)\s*(?:unseen|not visible|unknown|none|n/?a|out of frame)\s*", v):
                nv = "the floor"
            if _SHINE_RE.search(nv):
                nv = re.sub(r"(?i)\bher skin (?=glisten)", "", nv)
                nv = _SHINE_RE.sub(MATTE_SKIN, nv, count=1)
                nv = _SHINE_RE.sub("", nv)  # #1: never 'damp ... damp'
                nv = re.sub(r"\s*,\s*(?:,\s*)+", ", ", re.sub(r"\b(?:wet|damp),\s*(?=,|$)", "", nv)).strip(" ,")
            if nv != v:
                changed.append(f"{key}: {v[:60]} -> {nv[:60]}")
            return nv
        if isinstance(v, dict):
            return {k: fix(x, k) for k, x in v.items()}
        if isinstance(v, list):
            return [fix(x, key) for x in v]
        return v
    new = fix(rd, "read")
    if rd is d:
        return new, changed
    out = dict(d)
    out["read"] = new
    return out, changed


def strip_male_solo_still_read(d: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Strip the still woman's personal attributes/garments so a male_solo still_read stays setting-only."""
    rd = d.get("read") if isinstance(d.get("read"), dict) else d
    nr = dict(rd)
    changed: List[str] = []
    for k, empty in (("hair", ""), ("skin", ""), ("build", ""), ("pose", ""), ("garments", []), ("facing_camera", False), ("people", 0)):
        if nr.get(k) not in (empty, None):
            changed.append(k)
            nr[k] = empty
    if rd is d:
        return nr, changed
    out = dict(d)
    out["read"] = nr
    return out, changed


def ensure_still_read(run_dir: Path, still: str, still_read_src: Optional[str], client: Client, cfg: Dict[str, Any], log) -> Dict[str, Any]:
    d = _ensure_still_read_raw(run_dir, still, still_read_src, client, cfg, log)
    nd, changed = clean_still_read(d)
    if changed:
        p = run_dir / "still_read.json"
        raw = run_dir / "still_read.raw.json"
        if not raw.exists():
            wp_state.atomic_write(raw, json.dumps(d, indent=2, ensure_ascii=False))
        nd["cleaned"] = changed
        wp_state.atomic_write(p, json.dumps(nd, indent=2, ensure_ascii=False))
        log("still_read_cleaned", {"run": run_dir.name, "changed": changed})
    return nd


def _ensure_still_read_raw(run_dir: Path, still: str, still_read_src: Optional[str], client: Client, cfg: Dict[str, Any], log) -> Dict[str, Any]:
    p = run_dir / "still_read.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    if still_read_src:
        d = json.loads(Path(still_read_src).read_text(encoding="utf-8"))
        if "read" not in d:
            d = {"read": d}
        d["source"] = still
        d["copied_from"] = str(still_read_src)
        wp_state.atomic_write(p, json.dumps(d, indent=2, ensure_ascii=False))
        return d

    def vision_chat(messages):
        return client.chat(messages, {"temperature": 0.2, "top_k": 20, "top_p": 0.9}, 7, 1024, purpose="vision_read")
    read = br.vision_read(still, vision_chat)
    d = {"read": read, "source": still, "how": "pipeline vision_read via " + cfg["model_alias"]}
    wp_state.atomic_write(p, json.dumps(d, indent=2, ensure_ascii=False))
    log("still_read_vision", {"run": run_dir.name, "still": still})
    return d


def chain_start_still(prev_run: Path, still: str, run_dir: Path, log) -> str:
    mp4s = sorted(prev_run.glob("**/*.mp4"), key=lambda p: p.stat().st_mtime)
    if not mp4s:
        log("chain_dry_still", {"prev": str(prev_run), "still": still})
        return still
    out = run_dir / "start_still_from_prev.png"
    ff = shutil.which("ffmpeg") or "ffmpeg"
    r = subprocess.run([ff, "-y", "-sseof", "-0.1", "-i", str(mp4s[-1]), "-frames:v", "1", str(out)], capture_output=True, timeout=120)
    if r.returncode == 0 and out.exists():
        log("chain_last_frame", {"prev_mp4": str(mp4s[-1]), "still": str(out)})
        return str(out)
    log("chain_last_frame_failed", {"prev_mp4": str(mp4s[-1])})
    return still


# ---- run dir + start-still guard (Max Architect 2026-11-15, Derrick "Yes, make the fixes and rerun the Q8 vs Q4 test") ----
def resolve_run_dir(raw: Any) -> Path:
    """An absolute run dir is used as given. A relative one resolves under RUNS_ROOT (it used to land under the chat's
    cwd, outside runs/ and past the pi write sandbox). A leading '.../runs/' prefix is dropped; '..' is refused."""
    s = str(raw or "").strip()
    if not s:
        raise ValueError("run_dir is empty")
    rp = Path(s)
    if rp.is_absolute():
        return rp
    parts = [x for x in re.split(r"[\\/]+", s) if x not in ("", ".")]
    if "runs" in parts:
        parts = parts[len(parts) - parts[::-1].index("runs"):]
    if not parts or ".." in parts or re.match(r"^[A-Za-z]:", parts[0]):
        raise ValueError(f"run_dir '{s}' does not resolve under {RUNS_ROOT}; pass an absolute path under runs/")
    return RUNS_ROOT.joinpath(*parts)


def _file_sha256(path: Path) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _norm_still(x: Any) -> str:
    return os.path.normcase(os.path.normpath(os.path.expanduser(str(x).strip())))


def still_read_mismatch(still: str, run_dir: Path, still_read_src: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """(not_ready_reason, warning) for the still read the pipeline is about to use (run_dir/still_read.json if present,
    else --still-read). It must belong to the start still: same path, or the same file bytes (sha256). A read with no
    "source" (and no "source_sha256") cannot be checked and only warns."""
    existing = run_dir / "still_read.json"
    srp = existing if existing.exists() else (Path(still_read_src) if still_read_src else None)
    if srp is None:
        return None, None
    try:
        d = json.loads(srp.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return f"still read {srp} is not valid JSON ({e})", None
    d = d if isinstance(d, dict) else {}
    sha = str(d.get("source_sha256") or "").strip().lower()
    src = d.get("source")
    if sha:
        have = _file_sha256(Path(still))
        if have and have == sha:
            return None, None
        return (f"still read does not belong to the start still: {srp} source_sha256 does not match --still '{still}'"), None
    if not src:
        return None, "still_read_unverified (no source in the still read)"
    if _norm_still(src) == _norm_still(still):
        return None, None
    try:
        if os.path.realpath(os.path.expanduser(str(src))) == os.path.realpath(os.path.expanduser(str(still))):
            return None, None
    except Exception:  # noqa: BLE001
        pass
    a, b = _file_sha256(Path(os.path.expanduser(str(src)))), _file_sha256(Path(still))
    if a and b and a == b:
        return None, None
    return (f"still read does not belong to the start still: {srp.name} describes '{src}' but --still is '{still}'; "
            "pass the still that read describes, or remove the read so the pipeline reads the new still"), None


# ---- one clip -------------------------------------------------------------------------------------------------------
class _Stop(Exception):
    """A hard stop that ends the clip as NOT_READY with result['not_ready_reason'] already set."""


def run_clip(job: Dict[str, Any], cfg: Dict[str, Any], log, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ov = overrides or {}
    t_start = time.time()
    try:
        run_dir = resolve_run_dir(job.get("run_dir"))
    except ValueError as e:
        return {"run": str(job.get("run_dir")), "run_dir": str(job.get("run_dir")), "ask": job.get("ask"),
                "position": job.get("position"), "status": "NOT_READY", "not_ready_reason": str(e), "warnings": [],
                "version": VERSION, "seconds": 0.0}
    run_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_dir.name
    ask, position = job["ask"], job["position"]
    character = job.get("character") or cfg.get("default_character")
    kind = position_kind(position, cfg)  # provisional; the router below decides after the still read
    bodies = acts_bodies(position)
    overlays: List[str] = []
    arm = ov.get("sampler_arm") or cfg.get("sampler_arm", "B")
    sampler = dict(cfg["samplers"][arm])
    persona = ov.get("persona") or cfg.get("persona", "current")
    client = Client(cfg, log)
    result: Dict[str, Any] = {"run": run_id, "run_dir": str(run_dir), "ask": ask, "position": position, "kind": kind,
                              "status": None, "warnings": [], "version": VERSION, "sampler_arm": arm, "persona": persona}
    state_dir = Path(cfg["shared_state_dir"]) if cfg.get("shared_state_dir") else PIPE_DIR  # one global blacklist
    state_dir.mkdir(parents=True, exist_ok=True)
    bl_path = state_dir / "dialogue_blacklist.jsonl"
    recent_path = state_dir / "recent_outputs.jsonl"
    cloned_path = state_dir / "cloned_phrases.txt"
    try:
        # lost-features audit (Derrick t243s811): a youth hint in the ask is a hard stop before any writer call
        _yh = wp_lint.YOUTH_RE.search(ask or "")
        if _yh:
            result.update(status="NOT_READY", not_ready_reason=f"youth hint in the ask: '{_yh.group(0)}' (every person is an adult, 18+)")
            raise _Stop()
        # scene / chain
        scene_id = job.get("scene")
        prev_run = Path(job["continue"]) if job.get("continue") else None
        if prev_run and not scene_id:
            try:
                scene_id = json.loads((prev_run / "pick.json").read_text(encoding="utf-8")).get("scene_id") or prev_run.name
            except Exception:
                scene_id = prev_run.name
        sp = wp_state.scene_path(RUNS_ROOT, scene_id) if scene_id else None
        is_continue = bool(prev_run or job.get("extend"))
        if scene_id and sp and not is_continue:
            wp_state.reset_scene(sp, scene_id)  # PM acc4 #3: clip 1 starts a fresh scene_state
        scene_clips = wp_state.load_scene(sp) if sp and is_continue else []
        scene_prev = scene_clips[-1] if scene_clips and is_continue else None
        if is_continue and prev_run:
            try:
                parent = json.loads((prev_run / "pick.json").read_text(encoding="utf-8"))
            except Exception:
                parent = {}
            if parent.get("status") == "NOT_READY" or (prev_run / "clip_NOT_READY.txt").exists() and parent.get("status") != "READY":
                result.update(status="NOT_READY", not_ready_reason="parent clip is NOT_READY; continued clip blocked",
                              chain="blocked_parent")
                raise _Stop()
            result["chain"] = "dry_chain"
            if not list(prev_run.glob("*.mp4")):
                result["warnings"] = list(result.get("warnings") or []) + ["chain_unverified"]
        still = str(job.get("still") or "").strip()
        if not still and is_continue:
            if scene_prev and scene_prev.get("still"):
                still = str(scene_prev["still"]).strip()
            elif prev_run and (prev_run / "pick.json").is_file():
                try:
                    still = str(json.loads((prev_run / "pick.json").read_text(encoding="utf-8")).get("still") or "").strip()
                except Exception:
                    still = ""
        if not still:  # hard fail when --still is missing (never silently fall back to auto)
            result.update(status="NOT_READY", not_ready_reason="start still missing: pass --still '<the start still path>' "
                          "(or --still auto for a pool pick plus a fresh vision read)")
            raise _Stop()
        if still != "auto" and Path(still).is_absolute() and not Path(still).is_file():
            result.update(status="NOT_READY", not_ready_reason=f"start still file not found: {still}")
            raise _Stop()
        if still == "auto":
            if job.get("still_read") and not is_continue:
                result.update(status="NOT_READY", not_ready_reason="start still missing: --still-read was given with "
                              "--still auto; pass --still '<the still that read describes>'")
                raise _Stop()
            still = auto_still(cfg, run_id, ask)
        if scene_prev and scene_prev.get("run_dir"):
            still = chain_start_still(Path(scene_prev["run_dir"]), scene_prev.get("still") or still, run_dir, log)
        else:
            _why, _warn = still_read_mismatch(still, run_dir, job.get("still_read"))
            if _why:
                result.update(status="NOT_READY", not_ready_reason=_why)
                raise _Stop()
            if _warn:
                result["warnings"] = list(result.get("warnings") or []) + [_warn]
        _still_mode = br.normalize_still_mode(job.get("still_mode"))
        _still_size = br.read_still_size(still)
        _cw, _ch = br.resolve_canvas(job.get("aspect"), job.get("size"), still_size=_still_size)
        _shape_warn = br.check_still_canvas_shape(
            _still_size, _cw, _ch, aspect=job.get("aspect"), size=job.get("size"), still_mode=_still_mode,
        ) if _still_size else None
        if _shape_warn:
            print(_shape_warn, file=sys.stderr)
            result["warnings"] = list(result.get("warnings") or []) + [_shape_warn]
            log("still_shape_mismatch", {"run": run_id, "warning": _shape_warn, "canvas": [_cw, _ch],
                                         "still_size": list(_still_size)})
        # 1 still read
        still_read = ensure_still_read(run_dir, still, job.get("still_read"), client, cfg, log)
        # 2b mode router (coverage B0): act + base mode + overlays; fallbacks are logged, never block
        route = wp_router.route_mode(ask, position, still_read, cfg, continued=bool(scene_prev))
        # acceptance-2 item 3: doggy on a waist-high-only surface is standing_mf (bent over its edge); cowgirl there warns
        _sf = br.still_facts(still_read).get("surface") or ""
        if surface_height(_sf) == "waist" and route["act_id"] == "doggy" and br.get_act("standing_mf"):
            route = dict(route, position="standing_mf", act_id="standing_mf",
                         warnings=list(route["warnings"]) + [{"warn": "waist_high_reroute", "from": "doggy", "to": "standing_mf", "surface": _sf}])
        elif surface_height(_sf) == "waist" and route["act_id"] in ("cowgirl", "reverse_cowgirl"):
            # #5: riding on a waist-high top is NOT_READY (surface_mismatch), not a warning
            result.update(status="NOT_READY", not_ready_reason=f"surface_mismatch: {route['act_id']} on a waist-high {re.sub(r'(?i)^(?:the|a|an)\s+', '', _sf)}; "
                                                               "use a still with a bed, couch or floor, or a standing act")
            raise _Stop()
        if route["position"] != position:
            log("mode_fallback", {"run": run_id, "position": position, "chosen": route["position"]})
        position, kind, overlays = route["position"], route["mode"], route["overlays"]
        if (position == "male_solo") or (route.get("act_id") == "male_solo") or re.search(r"(?i)\bmale solo\b", ask or ""):
            raw_sr = run_dir / "still_read.raw.json"
            if not raw_sr.exists() and (run_dir / "still_read.json").exists():
                wp_state.atomic_write(raw_sr, (run_dir / "still_read.json").read_text(encoding="utf-8"))
            still_read, ms_changed = strip_male_solo_still_read(still_read)
            if ms_changed:
                still_read = dict(still_read, male_solo_stripped=ms_changed)
                wp_state.atomic_write(run_dir / "still_read.json", json.dumps(still_read, indent=2, ensure_ascii=False))
                log("male_solo_still_stripped", {"run": run_id, "fields": ms_changed})
        bodies = acts_bodies(position)
        for w in route["warnings"]:
            result["warnings"].append(w["warn"])
            log(w["warn"], dict(w, run=run_id))
        result.update(position=position, kind=kind, mode=kind, overlays=overlays, act_id=route["act_id"], route=route)
        wp_state.atomic_write(run_dir / "route.json", json.dumps(route, indent=2, ensure_ascii=False))
        # 2 slots
        last_tone = (state_dir / "last_tone.txt").read_text(encoding="utf-8").strip() if (state_dir / "last_tone.txt").exists() else None
        slots = make_slots(still_read, ask, position, kind, run_id, last_tone, scene_prev, overlays=overlays)
        if is_continue and scene_prev:
            _inh_pose = str(((slots.get("inherited") or {}).get("pose")) or "").strip()
            if not _inh_pose or _inh_pose.lower() in ("none", "null", "-", "the previous clip's end pose"):
                result.update(status="NOT_READY", not_ready_reason="continued clip missing inherited ending_state.pose")
                raise _Stop()
        _explicit_frames = bool(job.get("frames"))
        if _explicit_frames:
            clip_frames = int(job["frames"])
        elif kind == "talk":
            clip_frames = br.snap_h3_frames(8.0)
        else:
            clip_frames = br.SINGLE_CLIP_MAX_FRAMES
        clip_seconds = round(clip_frames / float(br.H3_FPS), 1)
        speech_words_max = max(1, int(round((clip_frames / float(br.H3_FPS)) * 2.5)))
        max_lines_spk = max(2 if kind == "talk" else 1, int(round((clip_frames / float(br.H3_FPS)) / 5.0)))
        slots["frames"] = clip_frames
        slots["clip_seconds"] = clip_seconds
        slots["speech_words_max"] = speech_words_max
        slots["max_lines_per_speaker"] = max_lines_spk
        s3_still_pre = job.get("partner2_still") or (scene_prev or {}).get("s3_still")
        if s3_still_pre:
            slots["s3_still"] = s3_still_pre
        wp_state.atomic_write(run_dir / "slots.json", json.dumps(slots, indent=2, ensure_ascii=False))
        sysprompt, pmeta = assemble_system(cfg, ask, persona, route["mode_blocks"])
        result.update(pmeta)
        # self-maintenance: cloned phrases follow the prompt sha + recent outputs
        cloned = wp_state.refresh_cloned(cloned_path, sysprompt, pmeta["writer_prompt_sha256"], wp_state.load_recent(recent_path))
        blacklist = [r["line"] for r in wp_state.load_blacklist(bl_path, log)]
        # MMF S3 (Derrick t1440): reuse the scene's S3 look, use a given S3 still, else the card invents one (faceless fallback)
        s3_still = s3_look = None
        s2_look_saved = None
        s3_in_frame = False
        if bodies >= 2:
            s2_look_saved = (scene_prev or {}).get("s2_look")
        if bodies >= 3:
            s3_still = job.get("partner2_still") or (scene_prev or {}).get("s3_still")
            s3_look = (scene_prev or {}).get("s3_look")
            s3_in_frame = bool(s3_look) if partner_type2_for(position, ask) else False
        _inh_g = (slots.get("inherited") or {}).get("garments") if scene_prev else None
        try:
            cast_l, _ = make_cast(still_read, position, ask, continued=bool(scene_prev), inherited_garments=_inh_g)
        except Exception as e:
            cast_l = {}
            result["warnings"].append("cast_preview_failed")
            log("cast_preview_failed", {"run": run_id, "error": str(e)[:300]})

        def _build_full_brief() -> str:
            b = brief_block(ask, position, kind, slots, bodies)
            if (position == "male_solo") or ((br.get_act(position) or {}).get("id") == "male_solo"):
                b += ("\nMALE SOLO: (S1) is the man. The start still is setting only: use its place, light and surface, never the person\'s hair, skin, clothes or pose. The person in the still is not (S1) and is not in this clip.")
            if (job.get("shots") or cfg.get("shots_default", "single")) == "multi" and int(job.get("shot_count") or 1) > 1:
                b += "\n" + shots_line(int(job["shot_count"]), clip_frames)
            if bodies >= 2 and s2_look_saved:  # #14
                b += f"\nPARTNER (S2), the same person as the last clip, every detail kept: {s2_look_saved}."
            if bodies >= 3:
                if s3_look:
                    b += f"\nTHIRD PERSON (S3), the same person as the last clip, every detail kept: {s3_look}."
                if s3_still:
                    b += "\nTHIRD PERSON (S3): his face and body come from his own reference picture; name only his clothes."
            if cast_l and not cast_l.get("voice_s2"):
                # acceptance-1 f: no partner voice for this ask (builder would print 'a distinct adult voice for (S2)')
                b += ("\nVOICE: no partner voice is set for this ask, so only (S1) speaks (at most two lines); (S2) stays silent "
                      "or off the clip." if kind == "talk" else "\nVOICE: only (S1) speaks in this clip.")
            return b

        brief = _build_full_brief()
        rd_ = br._unwrap_still_read(still_read)
        wet_ok = bool(wp_lint.WET_RE.search(json.dumps(rd_)) or wp_lint.WET_RE.search(ask))
        lint_cfg = dict(cfg.get("lint") or {})
        lint_cfg["speech_words_max"] = speech_words_max
        lint_cfg["max_lines_per_speaker"] = max_lines_spk
        lint_ctx = {"kind": kind, "slots": slots, "blacklist": blacklist, "cloned": cloned, "cfg": lint_cfg,
                    "scene": scene_prev, "builder_preview": builder_preview_fn(still_read, position, ask, continued=bool(scene_prev), inherited_garments=_inh_g),
                    "cast": cast_l, "overlays": overlays, "ask": ask, "act_id": route["act_id"], "wet_ok": wet_ok,
                    "recent_openings": [wp_lint.opening_sentence(d) for d in wp_state.load_recent(recent_path)[-10:]]}
        # 3 beat card
        card = None
        schema = mode(kind)["schema"]
        bc = dict(sampler, **(cfg.get("beat_card_sampler") or {}))
        for attempt in (1, 2):
            raw = client.chat(beat_messages(sysprompt, brief, kind, overlays), bc, seed_for(run_id, ask, 0) + attempt - 1,
                              cfg.get("beat_card_max_tokens", 1400),
                              response_format={"type": "json_schema", "json_schema": {"name": "beat_card", "schema": schema}},
                              purpose=f"beat_card_{attempt}")
            try:
                c = parse_json(raw)
                errs = schema_errors(c, schema)
                if errs:
                    raise ValueError("; ".join(errs[:6]))
                card = c
                break
            except Exception as e:
                log("beat_card_invalid", {"run": run_id, "attempt": attempt, "error": str(e)[:300]})
                wp_state.atomic_write(run_dir / f"beat_card_invalid_{attempt}.txt", raw or "")
        if card is not None and not _explicit_frames:
            cs = card.get("clip_seconds")
            if isinstance(cs, (int, float)) and not isinstance(cs, bool) and float(cs) > 0:
                req_s = float(cs)
                if kind == "talk":
                    req_s = max(5.2, min(req_s, 8.7))
                else:
                    req_s = max(2.3, min(req_s, float(br.SINGLE_CLIP_MAX_FRAMES) / float(br.H3_FPS)))
                new_frames = br.snap_h3_frames(req_s)
                if new_frames != clip_frames:
                    clip_frames = new_frames
                    clip_seconds = round(clip_frames / float(br.H3_FPS), 1)
                    speech_words_max = max(1, int(round((clip_frames / float(br.H3_FPS)) * 2.5)))
                    max_lines_spk = max(2 if kind == "talk" else 1, int(round((clip_frames / float(br.H3_FPS)) / 5.0)))
                    slots["frames"] = clip_frames
                    slots["clip_seconds"] = clip_seconds
                    slots["speech_words_max"] = speech_words_max
                    slots["max_lines_per_speaker"] = max_lines_spk
                    lint_cfg["speech_words_max"] = speech_words_max
                    lint_cfg["max_lines_per_speaker"] = max_lines_spk
                    wp_state.atomic_write(run_dir / "slots.json", json.dumps(slots, indent=2, ensure_ascii=False))
                    brief = _build_full_brief()
            card["clip_seconds"] = clip_seconds
        elif card is not None:
            card["clip_seconds"] = clip_seconds
        s2_look = s2_look_saved or (partner_look_from_card(card, "S2") if (bodies >= 2 and "nonhuman" not in overlays) else None)
        if bodies >= 3 and not s3_look:
            s3_look = s3_look_from_card(card)
        if bodies >= 3 and partner_type2_for(position, ask):
            result["s3"] = {"look": s3_look, "still": s3_still,
                            "mode": "still" if s3_still else ("generated" if s3_look else "faceless_default")}
            log("s3_mode", dict(result["s3"], run=run_id))
        _bx: List[str] = (["--s2-look", s2_look] if s2_look else []) + \
            (["--s3-look", s3_look] if s3_look else []) + (["--partner2-still", s3_still] if s3_still else []) + \
            (["--frames", str(int(clip_frames))] if (_explicit_frames or card is not None or kind == "talk") else []) + \
            (["--partner-type", "non-human"] if "nonhuman" in overlays else []) + (["--s3-in-frame"] if s3_in_frame else []) + \
            (["--shots", "multi"] if (job.get("shots") or cfg.get("shots_default", "single")) == "multi" else []) + \
            (["--continued"] if scene_prev else []) + \
            (["--inherited-garments", json.dumps(_inh_g, separators=(",", ":"))] if scene_prev and _inh_g else []) + \
            (["--aspect", str(job["aspect"])] if job.get("aspect") else []) + \
            (["--size", str(job["size"])] if job.get("size") else []) + \
            (["--still-mode", str(job["still_mode"])] if job.get("still_mode") else [])
        if card is None and kind == "talk":
            # BTS/talk: never skip the beat card; use a minimal valid card and keep writing
            card = {
                "clip_seconds": clip_seconds,
                "summary": "talk-only beat",
                "camera": "held medium shot, her face in frame",
                "partners": [],
                "anchor": {"pose": slots.get("pose") or "as shown"},
                "onset": {"action": "she turns toward the interviewer", "sound": "room tone"},
                "development": {"line_topics": ["her answer about the scene", "a follow-up from her", "a last short reply"],
                                "sound": "her voice"},
                "result": {"action": "she holds the look", "sound": "room tone",
                           "line_topics": ["a closing line from her"]},
                "end_state": {"pose": slots.get("pose") or "standing as shown", "motion": "still speaking"},
            }
            result["warnings"].append("beat_card_fallback")
        if card is None:
            result["warnings"].append("beat_card_skipped")
        else:
            card.setdefault("clip_seconds", clip_seconds)
            if route["act_id"] == "doggy" and isinstance(card.get("end_state"), dict):
                place = " ".join(filter(None, [slots.get("place"), slots.get("surface"), slots.get("floor"), ask]))
                if re.search(r"(?i)\b(?:log|sand)\b", place):
                    card["end_state"]["pose"] = "on her knees in the sand, forearms on the log"
            if route["act_id"] == "standing_mf" and isinstance(card.get("end_state"), dict) and \
                    not re.search(r"(?i)\bstand", str(card["end_state"].get("pose") or "")):
                # c8b: a rerouted doggy card still ended 'doggy, hands and knees'; the next clip inherits that pose
                _end_surf = re.sub(r'^(?:the|a|an)\s+', '', (slots.get('surface') or 'surface').strip(), flags=re.I)
                card["end_state"]["pose"] = (f"standing at the edge of the {_end_surf}, bent forward at the hips, "
                                             "forearms and chest on it, weight on both feet, (S2) standing behind her")
            wp_state.atomic_write(run_dir / "beat_card.json", json.dumps(card, indent=2, ensure_ascii=False))
        # 4 prose x N
        n = int(cfg.get("n_candidates", 3))
        cands: Dict[str, Dict[str, Any]] = {}
        for k in range(1, n + 1):
            angle = LINE_ANGLES[(seed_for(run_id, ask, 50) + k) % len(LINE_ANGLES)]  # acceptance-2 b: lines differ per draft
            raw = client.chat(prose_messages(sysprompt, brief + f"\nLINE ANGLE for this draft: {angle}", card, kind, overlays),
                              sampler, seed_for(run_id, ask, k),
                              cfg.get("prose_max_tokens", 1100), purpose=f"prose_{k}")
            dd = normalize_prose(clean_prose(raw), kind, slots)
            full = assemble_output(dd, card, slots, bodies, kind)
            wp_state.atomic_write(run_dir / f"cand_{k}.txt", full)
            lr = wp_lint.lint(full, lint_ctx)
            wp_state.atomic_write(run_dir / f"lint_{k}.json", json.dumps(lr, indent=2, ensure_ascii=False, default=str))
            cands[f"cand_{k}"] = {"full": full, "dd": dd, "lint": lr, "seed": seed_for(run_id, ask, k)}
        # 6 single rewrite of the best failing candidate
        best_name = max(cands, key=lambda c: cands[c]["lint"]["score"])
        if not any(c["lint"]["pass"] for c in cands.values()):
            notes = wp_lint.notes_for_rewrite(cands[best_name]["lint"])
            raw = client.chat(rewrite_messages(sysprompt, brief, card, cands[best_name]["dd"], notes, kind, overlays), sampler,
                              seed_for(run_id, ask, n + 1), cfg.get("prose_max_tokens", 1100), purpose="rewrite")
            dd = normalize_prose(clean_prose(raw), kind, slots)
            full = assemble_output(dd, card, slots, bodies, kind)
            wp_state.atomic_write(run_dir / "rewrite.txt", full)
            lr = wp_lint.lint(full, lint_ctx)
            wp_state.atomic_write(run_dir / "lint_rewrite.json", json.dumps(lr, indent=2, ensure_ascii=False, default=str))
            cands["rewrite"] = {"full": full, "dd": dd, "lint": lr, "seed": seed_for(run_id, ask, n + 1), "notes": notes,
                                "from": best_name}
        # 6b acceptance-3: every draft still carries a READY-blocking code -> one more targeted rewrite on those codes only
        _blk = set((cfg.get("lint") or {}).get("block_ready") or [])
        if cands and all(set(c["lint"]["hard"]) & _blk for c in cands.values()):
            src_name = "rewrite" if "rewrite" in cands else best_name
            src_l = cands[src_name]["lint"]
            notes = ["FIX THESE FIRST (they block READY): " + "; ".join(i["note"] for i in src_l["issues"] if i["code"] in _blk)]
            notes += [x for x in wp_lint.notes_for_rewrite(src_l, 3) if x not in notes]
            raw = client.chat(rewrite_messages(sysprompt, brief, card, cands[src_name]["dd"], notes, kind, overlays), sampler,
                              seed_for(run_id, ask, n + 3), cfg.get("prose_max_tokens", 1100), purpose="rewrite_block")
            dd = normalize_prose(clean_prose(raw), kind, slots)
            full = assemble_output(dd, card, slots, bodies, kind)
            wp_state.atomic_write(run_dir / "rewrite_block.txt", full)
            lr = wp_lint.lint(full, lint_ctx)
            wp_state.atomic_write(run_dir / "lint_rewrite_block.json", json.dumps(lr, indent=2, ensure_ascii=False, default=str))
            cands["rewrite_block"] = {"full": full, "dd": dd, "lint": lr, "seed": seed_for(run_id, ask, n + 3), "notes": notes,
                                      "from": src_name}
            result["warnings"].append("block_rewrite")
        # 7 rank and pick
        min_score = float(cfg.get("min_ready_score", 60))
        passing = [c for c in cands if cands[c]["lint"]["pass"] and float(cands[c]["lint"].get("score") or 0) >= min_score and not cands[c]["lint"]["hard"]]
        pool = passing or list(cands)
        if not passing:
            worst = cands[max(cands, key=lambda c: cands[c]["lint"]["score"])]["lint"]["hard"]
            result["warnings"].append("lint_fail_fallback")
            result["fallback_reasons"] = worst
            log("lint_fail_fallback", {"run": run_id, "reasons": worst})
        pool.sort(key=lambda c: cands[c]["lint"]["score"], reverse=True)
        top = cands[pool[0]]["lint"]["score"]
        tied = [c for c in pool if top - cands[c]["lint"]["score"] <= int(cfg.get("tie_points", 3))]
        pick, judge = pool[0], None
        if len(tied) > 1:
            names = [(chr(65 + i), c) for i, c in enumerate(tied)]
            try:
                jr = client.chat(judge_messages([(a, cands[c]["dd"]) for a, c in names], brief), cfg["judge_sampler"],
                                 int(cfg.get("judge_seed", 1234567)), 600, response_format=judge_format([a for a, _ in names]),
                                 purpose="judge")
                jd = parse_json(jr)
                best = judge_letter(jd, [a for a, _ in names])
                m = dict(names)
                if best in m:
                    pick = m[best]
                judge = {"names": dict(names), "reply": jd}
            except WriterDown:
                raise
            except Exception as e:
                judge = {"error": str(e)[:200]}
                result["warnings"].append("judge_failed_score_pick")
        chosen = cands[pick]
        wp_state.atomic_write(run_dir / "writer_output.txt", chosen["full"])
        # 8 build (dry); on NOT_READY one more rewrite from its message, then rebuild once
        build = run_build(run_dir, ask, position, still, character, extra=_bx)
        builds = [build]
        if build["status"] != "READY":
            nr = run_dir / "clip_NOT_READY.txt"
            if nr.exists():
                shutil.move(str(nr), str(run_dir / "clip_NOT_READY_attempt1.txt"))
            notes = ["the builder said: " + str(build["reason"])[:400]] + wp_lint.notes_for_rewrite(chosen["lint"], 4)
            raw = client.chat(rewrite_messages(sysprompt, brief, card, chosen["dd"], notes, kind, overlays), sampler,
                              seed_for(run_id, ask, n + 2), cfg.get("prose_max_tokens", 1100), purpose="rewrite_builder")
            dd = normalize_prose(clean_prose(raw), kind, slots)
            full = assemble_output(dd, card, slots, bodies, kind)
            lr = wp_lint.lint(full, lint_ctx)
            wp_state.atomic_write(run_dir / "rewrite_builder.txt", full)
            wp_state.atomic_write(run_dir / "lint_rewrite_builder.json", json.dumps(lr, indent=2, ensure_ascii=False, default=str))
            cands["rewrite_builder"] = {"full": full, "dd": dd, "lint": lr, "seed": seed_for(run_id, ask, n + 2), "notes": notes}
            pick, chosen = "rewrite_builder", cands["rewrite_builder"]
            wp_state.atomic_write(run_dir / "writer_output.txt", full)
            build = run_build(run_dir, ask, position, still, character, extra=_bx)
            builds.append(build)
        status = build["status"]
        # acceptance-1 fix c: these hard rules block READY even when the builder passes (others fall back with a warning)
        # PM acc3 #8: youth_hint and scale_adult always block (in code, not only config)
        # PM acc4 #8: READY needs score >= 60 and no hard flag; never ship ready_with_lint_fail
        min_score = float(cfg.get("min_ready_score", 60))
        blocking = sorted(set(chosen["lint"]["hard"] or []))
        if status == "READY" and float(chosen["lint"].get("score") or 0) < min_score:
            blocking = sorted(set(blocking) | {"low_score"})
        if status == "READY" and (blocking or not chosen["lint"].get("pass")):
            status = "NOT_READY"
            why = ", ".join(blocking) if blocking else "lint failed"
            build = dict(build, reason="lint hard rule: " + why)
            wp_state.atomic_write(run_dir / "clip_NOT_READY.txt", "NOT_READY: lint hard rule(s) block READY: " + why
                                  + "\n" + "\n".join(i["note"] for i in chosen["lint"]["issues"] if i.get("hard") or i["code"] in blocking) + "\n")
            result["warnings"].append("lint_blocked_ready")
        result.update(status=status, pick=pick, pick_score=chosen["lint"]["score"], pick_pass=chosen["lint"]["pass"],
                      pick_hard=chosen["lint"]["hard"], judge=judge, still=still, scene_id=scene_id,
                      frames=clip_frames, clip_seconds=clip_seconds,
                      candidates={c: {"score": v["lint"]["score"], "pass": v["lint"]["pass"], "hard": v["lint"]["hard"],
                                      "seed": v["seed"]} for c, v in cands.items()},
                      seeds={"beat_card": seed_for(run_id, ask, 0), **{c: v["seed"] for c, v in cands.items()}},
                      sampler=sampler, beat_card_sampler=bc, judge_sampler=cfg.get("judge_sampler"), model=cfg["model_alias"],
                      thinking=bool(cfg.get("thinking", False)), slots_tone=slots["tone"], line_focus=slots["line_focus"],
                      builds=[{k: b[k] for k in ("status", "rc", "stdout", "seconds")} for b in builds],
                      build_added=((build["report"].get("build") or {}).get("added") or []),
                      cloned_hits=wp_lint.cloned_hits(chosen["dd"], cloned), spoken_words=chosen["lint"]["spoken_words"],
                      llm_calls=client.calls)
        if status != "READY":
            result["not_ready_reason"] = build["reason"]
            log("clip_not_ready", {"run": run_id, "reason": str(build["reason"])[:500]})
        else:
            # 9 self-maintenance on READY
            kl = kept_lines(chosen["full"], build["report"])
            wp_state.update_blacklist(bl_path, kl, run_id, int(cfg.get("blacklist_cap", 20)), log)
            wp_state.append_recent(recent_path, run_id, chosen["dd"])
            wp_state.atomic_write(state_dir / "last_tone.txt", slots["tone"])
            result["kept_lines"] = kl
            if scene_id:
                es = dict((card or {}).get("end_state") or {})
                bstate = (build["report"].get("build") or {}).get("state") or {}
                garments = dict(bstate.get("garments") or {})
                for g in bstate.get("writer_aside") or []:
                    garments[g] = "aside"
                for g in (bstate.get("writer_removed") or []) + (bstate.get("builder_removed") or []):
                    garments[g] = "off"
                prev_done = (scene_prev or {}).get("done_actions") or []
                onset = (card or {}).get("onset") or {}
                done = prev_done + [v for k, v in onset.items() if k in ("exit", "clearance", "entry", "action") and v]
                entry = {"clip_id": run_id, "run_dir": str(run_dir), "still": still, "primary_beat": ((card or {}).get("development") or {}).get("primary_motion") or (card or {}).get("summary"),
                         "opening_state": (scene_prev or {}).get("ending_state") or {"pose": slots["pose"], "garments": {g: "on" for g in slots["garments_all"]},
                                                                                     "contact": None, "camera": slots.get("framing"), "pov": False},
                         "ending_state": {"pose": str(es.get("pose") or "").strip() or slots.get("pose") or ((card or {}).get("anchor") or {}).get("pose") or "as shown",
                                          "garments": garments, "contact": es.get("contact"),
                                          "camera": es.get("camera"), "pov": bool(es.get("pov"))},
                         "anchors": {"identity": character, "wardrobe": slots["garments_all"], "location": slots["place"],
                                     "prop": slots["props"], "prop_hand": es.get("prop_hand")},
                         "camera": "continuity", "spoken_dialogue": kl,
                         "ambient_sfx": [((card or {}).get(p) or {}).get("sound") for p in ("anchor", "onset", "development", "result") if ((card or {}).get(p) or {}).get("sound")],
                         "frame_budget": (build["report"].get("frames") or clip_frames),
                         "method": "planned cut", "done_actions": done, "ts": wp_state.now_ct(),
                         "s3_look": s3_look, "s3_still": s3_still,
                         "s2_look": s2_look_saved or partner_look_from_card(card, "S2")}
                wp_state.append_scene(sp, scene_id, entry)
                result["scene_state"] = str(sp)
    except _Stop:
        log("hard_stop", {"run": run_id, "reason": result.get("not_ready_reason")})
    except WriterDown as e:
        result.update(status="writer_down", error=str(e), llm_calls=client.calls)
        log("writer_down", {"run": run_id, "error": str(e)})
    except Exception as e:
        tb = traceback.format_exc()
        result.update(status="error", error=f"{type(e).__name__}: {e}", traceback=tb[-3000:], llm_calls=client.calls)
        log("clip_exception", {"run": run_id, "traceback": tb[-3000:]})
    result["seconds"] = round(time.time() - t_start, 1)
    result["llm_seconds"] = round(sum(c.get("seconds") or 0 for c in client.calls), 1)
    result["at"] = wp_state.now_ct()
    wp_state.atomic_write(run_dir / "pick.json", json.dumps(result, indent=2, ensure_ascii=False, default=str))
    log("clip_done", {"run": run_id, "status": result["status"], "seconds": result["seconds"], "pick": result.get("pick"),
                      "warnings": result["warnings"]})
    return result


def summary_line(r: Dict[str, Any]) -> str:
    st = r.get("status")
    extra = f"reason={str(r.get('not_ready_reason') or r.get('error') or '')[:300]}" if st != "READY" else \
        (f"pick={r.get('pick')} score={r.get('pick_score')} spoken_words={r.get('spoken_words')}"
         + (f" lint_fail={r.get('pick_hard')}" if r.get("pick_hard") else ""))
    return (f"{st} run={r.get('run_dir')} {extra} warnings={r.get('warnings')} seconds={r.get('seconds')} "
            f"pick_json={Path(r.get('run_dir', '.')) / 'pick.json'} queued=False")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="render_writer_pipeline.py", description="Render writer pipeline (dry builds only, never queues)")
    ap.add_argument("run_dir", nargs="?")
    ap.add_argument("--ask")
    ap.add_argument("--position")
    ap.add_argument("--still", default=None, help="start still path (required), or auto (pool pick + vision read)")
    ap.add_argument("--still-read", help="existing still_read.json to copy into the run dir")
    ap.add_argument("--character", default=None)
    ap.add_argument("--scene", help="scene id for a multi-clip scene (scene_state.json)")
    ap.add_argument("--continue", dest="cont", help="previous run dir this clip continues")
    ap.add_argument("--partner2-still", help="MMF: (S3) reference still (ComfyUI input path, e.g. community/x.jpg)")
    ap.add_argument("--frames", type=int, help="optional frame cap for VRAM (two reference stills)")
    ap.add_argument("--aspect", default=None, help="9:16 (default), 16:9, 1:1, 4:3, 3:4, portrait, landscape, widescreen, square, or auto")
    ap.add_argument("--size", default=None, help="Explicit canvas WxH (multiples of 32, 256..2048)")
    ap.add_argument("--still-mode", default=None, choices=list(br.STILL_MODES),
                    help="How start still is wired: guide (default frame-0 AddGuide) or ref (un-resized c0 reference, not frame-0 pinned)")
    ap.add_argument("--shots", choices=["single", "multi"], help="B1: multi keeps the writer's [Shot N] cuts (default single)")
    ap.add_argument("--shot-count", type=int, default=1, help="B1: shots in a multi clip")
    ap.add_argument("--batch", help="JSONL of jobs {run_dir, ask, position, still, still_read, character, scene, continue}")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--sampler-arm", help="setup A/B only")
    ap.add_argument("--persona", help="setup persona arm only (current, option1, option2)")
    a = ap.parse_args(argv)
    cfg = load_config(Path(a.config))
    log = wp_state.Log(PIPE_DIR / "logs", int(cfg.get("log_retention_days", 14)), int(cfg.get("log_cap_mb", 50)))
    moved = wp_state.archive_old_scenes(RUNS_ROOT, int(cfg.get("scene_archive_days", 30)))
    if moved:
        log("scenes_archived", {"scenes": moved})
    ov = {"sampler_arm": a.sampler_arm, "persona": a.persona}
    jobs: List[Dict[str, Any]] = []
    if a.batch:
        for ln in Path(a.batch).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                jobs.append(json.loads(ln))
    else:
        if not (a.run_dir and a.ask and a.position):
            print("NOT_READY usage: render_writer_pipeline.py <run_dir> --ask \"...\" --position <act> --still <path|auto> --character FCSydny")
            return 3
        if not Path(a.run_dir).is_absolute():
            print(f"NOT_READY run_dir must be an absolute path: {a.run_dir}")
            return 3
        if a.cont and not Path(a.cont).is_absolute():
            print(f"NOT_READY --continue must be an absolute path: {a.cont}")
            return 3
        jobs.append({"run_dir": a.run_dir, "ask": a.ask, "position": a.position, "still": a.still, "still_read": a.still_read,
                     "character": a.character, "scene": a.scene, "continue": a.cont,
                     "partner2_still": a.partner2_still, "frames": a.frames, "shots": a.shots, "shot_count": a.shot_count,
                     "aspect": a.aspect, "size": a.size, "still_mode": a.still_mode})
    results = []
    for job in jobs:  # one failing clip never blocks the next
        r = run_clip(job, cfg, log, ov)
        results.append(r)
        print(summary_line(r), flush=True)
    return 0 if all(r.get("status") == "READY" for r in results) else 3


if __name__ == "__main__":
    sys.exit(main())
