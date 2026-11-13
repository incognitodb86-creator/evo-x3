"""Package 2 (t122u-t127u addenda, R15-R23) helpers for the H3 writer builder.

Source: /workspace/maxops/research/render-modular-builder-upgrade-2026-11-11.md (closed 8:56 AM CT Nov 12).
Written on the box 2026-11-12 as a self-contained helper so it can be merged onto the live
C:\\AI\\community\\scripts\\parody tree without overwriting build_request.py (the live tree is several
rounds ahead of every box copy). It adds no rule pack, no age rule beyond the existing 18+ floor, no
graph/lock/sampler change, and never writes drug dose or administration.

What lives here (plan wording, no new behavior beyond it):
- partner_type value `futa` (one RefMod for the named face; never rewritten to a man).
- untested acts: male_solo (body count 1, S1 is the man), standing_mf (not carried), airplane, piledriver.
- writer-brief STATES on a named act (never act ids, never unknown-act NOT_READY): sleeping, already_out
  (rufie, same write as sleeping), mdma (state/setting), mind_control, telekinesis.
- writer-brief themes: pregnancy / body niche, caught / shoplifter.
- generic costume words are wardrobe, not INDEX aliases.
- camera_kind values webcam, handheld_sextape, bts_interview (plus third_person, pov, close_up).
- off-screen interviewer: narrated voice, no (Sn), no body, not counted, not credited, never fails closed.
- look line (film looks); still color nouns win.
- register: softcore/romance, comedy/spoof, music_video/slow-mo (no overall_soundscape; music in text only).
- stereo VR: out of format (report-only flag; closest is POV).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

PARTNER_TYPES = ("man", "woman", "futa", "none", "non-human", "faceless")
NO_REFMOD_PARTNER_TYPES = ("none", "non-human", "faceless")
CAMERA_KINDS = ("third_person", "pov", "close_up", "webcam", "handheld_sextape", "bts_interview")
STATE_IDS = ("sleeping", "already_out", "mdma", "mind_control", "telekinesis")
PACKAGE2_ACT_IDS = ("male_solo", "standing_mf", "airplane", "piledriver")

# ---------------------------------------------------------------- registry (acts.yaml)

def _parse_scalar(v: str) -> Any:
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v.strip("'\"")


def load_registry(path: "str | Path") -> Dict[str, Dict[str, Any]]:
    """Load an acts registry file: a YAML list of flat mappings (`- id: x` then `key: value` lines,
    inline `[a, b]` lists). Uses PyYAML when present, else this minimal reader (the box has no PyYAML)."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text)
        rows = data.get("acts", data) if isinstance(data, dict) else data
    except ImportError:
        if re.search(r"(?m)^\s*-\s+id\s*:", text):
            rows, cur = [], None
            for line in text.splitlines():
                s = line.split(" #", 1)[0].rstrip()
                if not s.strip() or s.lstrip().startswith("#") or s.strip() == "acts:":
                    continue
                m = re.match(r"^\s*-\s+(\w+):\s*(.*)$", s)
                if m:
                    cur = {m.group(1): _parse_scalar(m.group(2))}
                    rows.append(cur)
                    continue
                m = re.match(r"^\s+(\w+):\s*(.*)$", s)
                if m and cur is not None:
                    cur[m.group(1)] = _parse_scalar(m.group(2))
        else:
            # Live schema: acts: { id: {id, aliases: [...], ...}, ... }
            rows, cur, cur_list = {}, None, None
            for line in text.splitlines():
                s = line.split(" #", 1)[0].rstrip()
                if not s.strip() or s.lstrip().startswith("#") or s.strip() == "acts:":
                    continue
                m = re.match(r"^  ([\w-]+):\s*$", s)
                if m:
                    key = m.group(1)
                    cur = {"id": key}
                    rows[key] = cur
                    cur_list = None
                    continue
                if cur is None:
                    continue
                m = re.match(r"^    (\w+):\s*$", s)
                if m:
                    cur_list = []
                    cur[m.group(1)] = cur_list
                    continue
                m = re.match(r"^    (\w+):\s*(.+)$", s)
                if m:
                    cur[m.group(1)] = _parse_scalar(m.group(2))
                    cur_list = None
                    continue
                m = re.match(r"^      -\s*(.*)$", s)
                if m and cur_list is not None:
                    cur_list.append(_parse_scalar(m.group(1)))
    if isinstance(rows, dict):
        # Live acts.yaml is a mapping of id -> row (not a list of mappings).
        out = {}
        for k, r in rows.items():
            if isinstance(r, dict):
                out[str(r.get("id") or k)] = r
        return out
    return {str(r["id"]): r for r in (rows or [])}


def get_act(registry: Dict[str, Dict[str, Any]], act_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Registry row or None. None for an unknown id = NOT_READY at the caller (never a blowjob default)."""
    if not act_id:
        return None
    return registry.get(act_id)


def effective_status(act: Dict[str, Any], partner_type: Optional[str]) -> str:
    """Existing templates count as untested with a futa partner (plan, partner_type)."""
    if partner_type == "futa":
        return "untested"
    return str(act.get("status", "untested"))


# ---------------------------------------------------------------- brief readers

_FUTA_RE = re.compile(r"(?i)\bfuta(?:nari)?s?\b")
_MALE_SOLO_RE = re.compile(
    r"(?i)\b(?:male[- ]solo|solo (?:guy|man|male)|(?:jerk|jack|wank)(?:s|ed|ing)?(?:[- ]|\s+himself\s+)off|"
    r"edg(?:es|ed|ing)\s+himself|strok(?:es|ing)\s+himself|edging(?:\s+session)?)\b")
_HANDJOB_RE = re.compile(r"(?i)\b(?:(?:jerk|jack|strok|edg|wank)\w*\s+(?:him|his)\b|hand ?job)")
_SECOND_PERSON_RE = re.compile(r"(?i)\b(?:she|her|woman|girl|wife|girlfriend|partner|futa\w*|they|watches? him)\b")
_RUINED_RE = re.compile(r"(?i)\bruined[- ]orgasm\b")
_STANDING_RE = re.compile(r"(?i)\bstanding[- ](?:sex|fuck\w*|missionary|doggy|m\+?f)\b|\b(?:sex|fuck\w*|fucks her)\s+(?:while\s+)?standing(?: up)?\b")
_CARRIED_RE = re.compile(r"(?i)\b(?:carr(?:y|ies|ied|ying)|lifts? her|holds? her up|legs? (?:wrapped|around his waist)|against the wall)\b")
_AIRPLANE_RE = re.compile(r"(?i)\bairplane(?:[- ]position)?\b")
_PILEDRIVER_RE = re.compile(r"(?i)\bpile ?driver\b")

_STATE_RES = {
    "sleeping": re.compile(r"(?i)\b(?:asleep|sleeping|sleeps|passed out|out cold|unconscious)\b"),
    "already_out": re.compile(r"(?i)\b(?:roof|ruf)(?:f)?ie(?:s|d)?\b|\b(?:roof|ruf)ied\b"),
    "mdma": re.compile(r"(?i)\b(?:mdma|molly|ecstasy|rolling on (?:molly|e))\b"),
    "mind_control": re.compile(r"(?i)\b(?:mind[- ]?control(?:led|s)?|hypno(?:sis|ti[sz]ed|tic|ti[sz]es?|ti[sz]ing)|entranced|"
                               r"in a trance|brainwash\w*)\b"),
    "telekinesis": re.compile(r"(?i)\b(?:telekine(?:sis|tic(?:ally)?)|levitat\w*|psychic force)\b"),
}
_THEME_RES = {
    "pregnancy": re.compile(r"(?i)\bpregnan\w*\b"),
    "body_niche": re.compile(r"(?i)\b(?:bbw|hirsute|hairy)\b"),
    "caught_shoplifter": re.compile(r"(?i)\b(?:shoplift\w*|caught (?:stealing|in the act|shoplifting))\b"),
}
_CAMERA_RES = (
    ("webcam", re.compile(r"(?i)\b(?:web ?cam\w*|cam ?show|cam ?girl|laptop camera)\b")),
    ("bts_interview", re.compile(r"(?i)\b(?:behind[- ]the[- ]scenes|bts|interview(?:er|ed|s)?)\b")),
    ("handheld_sextape", re.compile(r"(?i)\b(?:sex[- ]?tape|handheld|home video|v[ée]rit[ée]|films? (?:it )?(?:on|with) (?:a|his|her) phone)\b")),
    ("pov", re.compile(r"(?i)\b(?:pov|point[- ]of[- ]view|first[- ]person)\b")),
    ("close_up", re.compile(r"(?i)\bclose[- ]?up\b")),
)
_OFFSCREEN_ASK_RE = re.compile(r"(?i)\b(?:interview(?:er|ed|s)?|off[- ]?screen (?:voice|interviewer|director|camera ?man|narrator))\b")
_LOOK_RES = (
    ("noir", re.compile(r"(?i)\bnoir\b")),
    ("black-and-white", re.compile(r"(?i)\b(?:black[- ]and[- ]white|b&w|b/w|monochrome)\b")),
    ("16mm found footage", re.compile(r"(?i)\b(?:16 ?mm|found[- ]footage)\b")),
    ("silent film", re.compile(r"(?i)\bsilent[- ]film\b")),
    ("VHS", re.compile(r"(?i)\bvhs\b")),
    ("80s", re.compile(r"(?i)\b(?:19)?80s\b|\beighties\b")),
    ("90s", re.compile(r"(?i)\b(?:19)?90s\b|\bnineties\b")),
    ("90s Hong Kong wuxia", re.compile(r"(?i)\bwuxia\b")),
)
_REGISTER_RES = (
    ("softcore_romance", re.compile(r"(?i)\b(?:softcore|sensual|romantic|romance|implied)\b")),
    ("comedy_spoof", re.compile(r"(?i)\b(?:comedy|comedic|spoof|funny|sitcom)\b")),
    ("music_video", re.compile(r"(?i)\b(?:music[- ]video|montage|slow[- ]?mo(?:tion)?)\b")),
)
_STEREO_VR_RE = re.compile(r"(?i)\b(?:stereo(?:scopic)?\s*(?:3d\s*)?vr|vr180|vr ?porn|side[- ]by[- ]side 3d|\bvr\b)")

# Plan list (vampire, zombie, witch, cowboy, Christmas, Halloween) plus plurals. 'cowgirl' is an act, never here.
GENERIC_COSTUMES = ("vampire", "zombie", "witch", "cowboy", "christmas", "halloween")
_COSTUME_FILLER = {"a", "an", "the", "sexy", "hot", "costume", "costumes", "outfit", "cosplay", "girl", "woman", "lady",
                   "man", "guy", "boy", "babe", "themed", "theme"}


def _norm_tokens(name: str) -> List[str]:
    return [t for t in re.split(r"[^a-z]+", name.lower()) if t]


def _costume_root(tok: str) -> Optional[str]:
    for c in GENERIC_COSTUMES:
        if tok in (c, c + "s", c + "es"):
            return c
    return None


def is_generic_costume_name(name: Optional[str]) -> bool:
    """True when a parody-CLI --name (or hook text name) is only a generic costume word, e.g. 'vampire',
    'sexy witch', 'Christmas outfit'. Those are wardrobe and still nouns, never INDEX aliases (R17)."""
    toks = _norm_tokens(name or "")
    if not toks:
        return False
    roots = [_costume_root(t) for t in toks]
    return any(roots) and all(r or t in _COSTUME_FILLER for r, t in zip(roots, toks))


def costume_words_in(text: str) -> List[str]:
    """Generic costume words in free text: wardrobe for the writer, never an INDEX lookup."""
    out = []
    for t in _norm_tokens(text or ""):
        r = _costume_root(t)
        if r and r not in out:
            out.append(r)
    return out


class GenericCostumeNotAlias(ValueError):
    """A generic costume word was given where a named INDEX character/actor is required."""


def guard_parody_name(name: Optional[str]) -> None:
    """Call before INDEX/alias resolve on every parody-CLI name (--name/--name2/--name3/--character...)."""
    if name and is_generic_costume_name(name):
        raise GenericCostumeNotAlias(
            f"'{name}' is a generic costume (wardrobe and still nouns), not an INDEX alias; write it as an OC "
            "writer-brief costume. A named character in the index still uses the parody lane.")


def _gender_near(sentence: str, start: int) -> Optional[str]:
    lead = sentence[:start]
    hits = list(re.finditer(r"(?i)\b(she|her|woman|girl|wife|girlfriend|he|him|his|man|guy|husband|boyfriend)\b", lead))
    if not hits:
        tail = sentence[start:start + 60]
        hits = list(re.finditer(r"(?i)\b(she|her|woman|girl|wife|girlfriend|he|him|his|man|guy|husband|boyfriend)\b", tail))[:1]
    if not hits:
        return None
    w = hits[-1].group(1).lower()
    return "woman" if w in ("she", "her", "woman", "girl", "wife", "girlfriend") else "man"


def sleeper_gender(ask: str) -> Optional[str]:
    """Gender of the asleep / already-out person from the brief sentence, or None if the brief does not say."""
    for sent in re.split(r"(?<=[.!?;])\s+", ask or ""):
        for sid in ("sleeping", "already_out"):
            m = _STATE_RES[sid].search(sent)
            if m:
                return _gender_near(sent, m.start())
    return None


def resolve_brief(ask: str, act_id: Optional[str] = None, registry: Optional[Dict[str, Dict[str, Any]]] = None,
                  partner_type: Optional[str] = None, still_people: Optional[int] = None) -> Dict[str, Any]:
    """Package-2 read of a writer brief. Returns only what package 2 decides; everything else (non-human /
    faceless, three-person counts, known act aliases) stays with the live hook. Keys:
      act_id, act_status, not_ready (reason or None), body_count (None = live decides), partner_type,
      s1_gender, states, sleeper_gender, themes, camera_kind, offscreen_voice, look, register,
      costume_words, first_beat_talk_ok, flags."""
    ask = ask or ""
    registry = registry or {}
    out: Dict[str, Any] = {"act_id": act_id, "act_status": None, "not_ready": None, "body_count": None,
                           "partner_type": partner_type, "s1_gender": None, "states": [], "sleeper_gender": None,
                           "themes": [], "camera_kind": None, "offscreen_voice": False, "look": [], "register": [],
                           "costume_words": costume_words_in(ask), "first_beat_talk_ok": False, "flags": []}
    # partner: futa is a partner_type value, never rewritten to a man (R15)
    if _FUTA_RE.search(ask) and partner_type in (None, "man", "woman"):
        out["partner_type"] = "futa"
    # package-2 acts, only when the caller did not name an act
    if not act_id:
        if _MALE_SOLO_RE.search(ask) and not _HANDJOB_RE.search(ask):
            if _SECOND_PERSON_RE.search(_STATE_RES["sleeping"].sub("", ask)):
                out["flags"].append("male-solo words with a second person named: not resolved as male_solo here")
            else:
                out["act_id"] = "male_solo"
        elif _PILEDRIVER_RE.search(ask):
            out["act_id"] = "piledriver"
        elif _AIRPLANE_RE.search(ask):
            out["act_id"] = "airplane"
        elif _STANDING_RE.search(ask) and not _CARRIED_RE.search(ask):
            out["act_id"] = "standing_mf"
    if out["act_id"] == "male_solo":
        out.update(body_count=1, s1_gender="man", partner_type="none")
        if _RUINED_RE.search(ask):
            out["flags"].append("finish: ruined_orgasm")
    if out["act_id"]:
        row = get_act(registry, out["act_id"]) if registry else None
        if registry and row is None:
            out["not_ready"] = f"unknown act '{out['act_id']}' (not in acts registry); never a blowjob default"
        elif row is not None:
            out["act_status"] = effective_status(row, out["partner_type"])
            if out["body_count"] is None and row.get("bodies") is not None:
                out["body_count"] = int(row["bodies"])
    # states on a named act: never act ids, never unknown-act NOT_READY (R20-R22)
    out["states"] = [sid for sid in STATE_IDS if _STATE_RES[sid].search(ask)]
    if "already_out" in out["states"] and "sleeping" not in out["states"]:
        out["flags"].append("already_out uses the sleeping write")
    if {"sleeping", "already_out"} & set(out["states"]):
        out["sleeper_gender"] = sleeper_gender(ask)
        if out["sleeper_gender"] is None:
            out["flags"].append("sleeping/already-out person not identifiable from the brief")
    out["themes"] = [k for k, rx in _THEME_RES.items() if rx.search(ask)]
    for kind, rx in _CAMERA_RES:
        if rx.search(ask):
            out["camera_kind"] = kind
            break
    out["camera_kind"] = out["camera_kind"] or "third_person"
    out["offscreen_voice"] = bool(_OFFSCREEN_ASK_RE.search(ask))
    out["look"] = [name for name, rx in _LOOK_RES if rx.search(ask)]
    out["register"] = [name for name, rx in _REGISTER_RES if rx.search(ask)]
    out["first_beat_talk_ok"] = "comedy_spoof" in out["register"] or out["offscreen_voice"]
    if _STEREO_VR_RE.search(ask):
        out["flags"].append("stereo VR is out of format; closest option is POV (unpromised)")
    if still_people is not None and out["body_count"] is not None and still_people > out["body_count"]:
        out["not_ready"] = out["not_ready"] or (
            f"still shows {still_people} people, brief asks for {out['body_count']}: NOT_READY")
    return out


def refmod_plan(resolved: Dict[str, Any], named_faces: Sequence[str]) -> Dict[str, Any]:
    """One RefMod per named face. futa partner and male-solo S1 get one; none / non-human / faceless get none.
    The off-screen interviewer is not a subject and gets none. >8 named faces = NOT_READY."""
    faces = list(named_faces)
    if len(faces) > 8:
        return {"slots": {}, "not_ready": f"{len(faces)} named faces > 8 RefMod slots"}
    slots = {f"mod_{i}": "(none)" for i in range(1, 9)}
    for i, face in enumerate(faces, 1):
        slots[f"mod_{i}"] = face
    return {"slots": slots, "not_ready": None}


def look_line(resolved: Dict[str, Any]) -> Optional[str]:
    """Writer-brief look line. Never tells the model to drop color: still nouns win on wardrobe color (R19)."""
    if not resolved.get("look"):
        return None
    return "Look: " + ", ".join(resolved["look"]) + " film look; wardrobe colors stay as in the still."


# ---------------------------------------------------------------- prompt checks

_D_RE = re.compile(r"<d>(.*?)</d>", re.S)
_SN_RE = re.compile(r"\(S([1-8])\)|<Subject ([1-8])>")
_OFFSCREEN_LEAD_RE = re.compile(r"(?i)\boff[- ]?screen\b[^.<]{0,40}\b(?:voice|interviewer|director|camera ?man|narrator)\b|"
                                r"\b(?:interviewer|director|camera ?man)\b[^.<]{0,30}\boff[- ]?screen\b")
_BODY_RE = re.compile(r"(?i)\b(?:steps? into (?:the )?frame|his (?:hand|body|cock|hips|face)|walks? in|enters? (?:the )?frame|"
                      r"touch(?:es)?|grabs?)\b")
_WAKE_RE = re.compile(r"(?i)\b(?:wakes?(?: up)?|woke|waking|snaps? awake|jolts? awake|eyes (?:snap|fly|flutter) open|"
                      r"opens? (?:her|his) eyes)\b")
_DOSE_RE = re.compile(r"(?i)\b(?:\d+(?:\.\d+)?\s*(?:mg|mcg|ml|milligrams?|grams?)\b|dos(?:e|es|ed|age|ing)\b|"
                      r"crush(?:es|ed|ing)?\s+(?:a |the |up )?(?:pill|tablet)|"
                      r"(?:slips?|drops?|pours?|mix(?:es)?)\s+(?:a |the |some |something )?(?:pill|tablet|powder|drug)\w*|"
                      r"spik(?:e|es|ed|ing)\s+(?:her |his |the )?drink|dissolv\w+|snort\w*|"
                      r"swallows? (?:a |the )?(?:pill|tablet)|injects?|syringe)")
_DRINK_RE = re.compile(r"(?i)\b(?:drinks?|drinking|glass|cocktail|sips?|cup)\b")
_CONTROLLER_RE = re.compile(r"(?i)\b(?:device|collar|pendant|pocket ?watch|app|remote|implant|ray|helmet|visor|chip|signal|"
                            r"headset|amulet|ring)\b|\((?:S[1-8])\)[^.]{0,60}\b(?:commands?|controls?|orders?|hypnoti[sz]es?|wills?)\b|"
                            r"<Subject [1-8]>[^.]{0,60}\b(?:commands?|controls?|orders?|hypnoti[sz]es?|wills?)\b|"
                            r"\b(?:his|her) (?:command|voice|gaze|will)\b")
_FORCE_RE = re.compile(r"(?i)\b(?:telekinetic (?:force|grip|pull|hold)|invisible force|(?:his|her) (?:mind|power|will|outstretched hand)|"
                       r"psychic force|force (?:field|from)|glow\w*)\b")
_HOLD_RE = re.compile(r"(?i)\b(?:\d+(?:\.\d+)?\s*(?:cm|centimet\w+|inch(?:es)?|in|feet|foot|ft|seconds?|s)\b|"
                      r"(?:a|one|two|three|a few|several)\s+(?:inch(?:es)?|hand'?s?[- ]?widths?|palm'?s?[- ]?widths?|feet|seconds?)\b|"
                      r"(?:waist|knee|hip|chest|shoulder)[- ]height)")
_COLOR_RE = re.compile(r"(?i)\b(?:red|black|white|blue|navy|green|pink|purple|yellow|orange|grey|gray|silver|gold|beige|"
                       r"cream|brown|tan|teal|maroon|burgundy|lavender|ivory|crimson|scarlet)\b")
_MAN_WORDS_RE = re.compile(r"(?i)\b(?:he|him|his|himself|the man|a man)\b")
_SHE_RE = re.compile(r"(?i)\b(?:she|her|herself)\b")


def _units(prompt: str) -> List[str]:
    return [u for u in re.split(r"(?:(?<=[.!?])|(?<=</d>))\s+(?=[A-Z(<])", prompt or "") if u.strip()]


def is_offscreen_voice_sentence(sentence: str) -> bool:
    """A narrated off-screen voice line: names an off-screen voice/interviewer, carries no (Sn)/<Subject N>."""
    return bool(_OFFSCREEN_LEAD_RE.search(sentence)) and not _SN_RE.search(sentence)


def speaker_of(sentence: str, s_count: int = 2) -> str:
    """Speaker credit for a spoken sentence: 'OFFSCREEN' for a narrated off-screen voice (no Sn, never
    credited to S1/S2/S3, never fails closed), 'Sn' from an explicit label, else 'UNATTRIBUTED' (caller
    fails closed; no he/she guessing, plan B1)."""
    if is_offscreen_voice_sentence(sentence):
        return "OFFSCREEN"
    labels = list(_SN_RE.finditer(sentence.split("<d>", 1)[0])) or list(_SN_RE.finditer(sentence))
    if labels:
        n = int(labels[-1].group(1) or labels[-1].group(2))
        return f"S{n}" if n <= s_count else "UNATTRIBUTED"
    return "UNATTRIBUTED"


def body_count_in_prompt(prompt: str) -> int:
    """Distinct (Sn)/<Subject N> bodies in the prompt; off-screen voice sentences never count (R18)."""
    seen = set()
    for u in _units(prompt):
        if is_offscreen_voice_sentence(u):
            continue
        for m in _SN_RE.finditer(u):
            seen.add(m.group(1) or m.group(2))
    return len(seen)


def _issue(code: str, hard: bool, why: str, unit: str = "") -> Dict[str, Any]:
    return {"code": code, "hard": hard, "why": why, "unit": unit[:160]}


def check_prompt(prompt: str, resolved: Dict[str, Any], ask: str = "", still_read: Optional[Dict[str, Any]] = None,
                 sleeper_sn: Optional[str] = None, request_fields: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Package-2 checks on a finished writer prompt. Nothing is rewritten. hard=True -> NOT_READY / send back;
    hard=False -> flag only (the plan does not say these block)."""
    issues: List[Dict[str, Any]] = []
    units = _units(prompt)
    states = set(resolved.get("states") or [])
    ask = ask or ""
    # sleeping / already-out: no spoken lines, no snap awake unless asked (R20)
    if states & {"sleeping", "already_out"}:
        for u in units:
            if sleeper_sn and _D_RE.search(u) and speaker_of(u, 8) == sleeper_sn:
                issues.append(_issue("P2-SLEEP-SPEAK", True, f"{sleeper_sn} is asleep/already out and has no spoken lines", u))
            if _WAKE_RE.search(u) and not _WAKE_RE.search(ask):
                issues.append(_issue("P2-SLEEP-WAKE", True, "the sleeping/already-out body stays at rest; no snap awake unless the brief asks", u))
    # MDMA / rufie: never dose or administration; rufie drink stays off camera unless the brief asks (R15-R23 addendum)
    if states & {"mdma", "already_out"}:
        for u in units:
            if _DOSE_RE.search(_D_RE.sub(" ", u)) or _DOSE_RE.search(u):
                issues.append(_issue("P2-DOSE", True, "no drug dose or administration in the prompt", u))
        if "already_out" in states and not _DRINK_RE.search(ask):
            for u in units:
                if _DRINK_RE.search(u):
                    issues.append(_issue("P2-DRINK", True, "rufie is written already out; the drink stays off camera unless the brief asks for it", u))
    if "mind_control" in states and not _CONTROLLER_RE.search(prompt):
        issues.append(_issue("P2-MC-AGENT", False, "mind control: name who or what applies the control (partner in frame or a device in the brief)"))
    if "telekinesis" in states:
        if not _FORCE_RE.search(prompt):
            issues.append(_issue("P2-TK-FORCE", False, "telekinesis: name who or what applies the force"))
        if not _HOLD_RE.search(prompt):
            issues.append(_issue("P2-TK-HOLD", False, "telekinesis: give a measurable hold so the body floats or turns, not snaps or freezes"))
    # male solo: S1 is the man; no female partner injected (R16)
    if resolved.get("act_id") == "male_solo":
        if body_count_in_prompt(prompt) > 1:
            issues.append(_issue("P2-SOLO-PARTNER", True, "male solo is body count 1; a second subject was injected"))
        for u in units:
            if _SN_RE.search(u) and speaker_of(u, 8) in ("S1",) and _SHE_RE.search(_D_RE.sub(" ", u)) and not _MAN_WORDS_RE.search(_D_RE.sub(" ", u)):
                issues.append(_issue("P2-SOLO-S1-WOMAN", True, "on a male-solo job S1 is the man; S1 is written as a woman", u))
    # futa partner: never rewritten as a man (R15)
    # (only when no man is in the scene: S1 not a man and no S3, so any he/his/the man can only be the futa partner)
    if resolved.get("partner_type") == "futa" and resolved.get("s1_gender") != "man" and not re.search(r"\(S3\)|<Subject 3>", prompt):
        for u in units:
            body = _D_RE.sub(" ", u)
            if re.search(r"\(S2\)|<Subject 2>", body) and _MAN_WORDS_RE.search(body):
                issues.append(_issue("P2-FUTA-AS-MAN", True, "futa partner is written as a man (he/his/the man)", u))
    # off-screen interviewer: no (Sn), no body, not a third body (R18)
    if resolved.get("offscreen_voice"):
        for u in units:
            if _OFFSCREEN_LEAD_RE.search(u) and _SN_RE.search(u):
                issues.append(_issue("P2-OFFSCREEN-SN", True, "the off-screen interviewer has no (Sn) credit", u))
            if is_offscreen_voice_sentence(u) and _BODY_RE.search(_D_RE.sub(" ", u)):
                issues.append(_issue("P2-OFFSCREEN-BODY", True, "the off-screen interviewer has no body in frame", u))
    # look line: still color nouns win (R19)
    if resolved.get("look") and still_read:
        still_colors = {c.lower() for g in _still_garments(still_read) for c in _COLOR_RE.findall(g)}
        prompt_colors = {c.lower() for c in _COLOR_RE.findall(prompt)}
        lost = sorted(still_colors - prompt_colors)
        if lost:
            issues.append(_issue("P2-LOOK-COLOR", False, "still wardrobe color nouns dropped under a look line: " + ", ".join(lost)))
    # music: never overall_soundscape (lock bans that field) (addendum)
    if request_fields and _has_soundscape(request_fields):
        # Max Architect 3, 2026-11-13 (Derrick t1355): a warning like S6, not a stop; the field is not used by the graph.
        issues.append(_issue("P2-SOUNDSCAPE", False, "overall_soundscape is banned by the lock; music stays in prompt text only"))
    return issues


def _still_garments(still_read: Dict[str, Any]) -> List[str]:
    g: List[str] = []
    for key in ("garments", "wardrobe", "clothes"):
        v = still_read.get(key)
        if isinstance(v, str):
            g.append(v)
        elif isinstance(v, list):
            g += [str(x) for x in v]
    people = still_read.get("people")
    if isinstance(people, list):
        for p in people:
            if isinstance(p, dict):
                v = p.get("garments")
                g += [str(x) for x in v] if isinstance(v, list) else ([str(v)] if v else [])
    return g


def _has_soundscape(obj: Any) -> bool:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "overall_soundscape" and v not in (None, "", [], {}):
                return True
            if _has_soundscape(v):
                return True
    elif isinstance(obj, list):
        return any(_has_soundscape(x) for x in obj)
    return False


def not_ready_from(resolved: Dict[str, Any], issues: Iterable[Dict[str, Any]]) -> Optional[str]:
    """First hard reason, or None."""
    if resolved.get("not_ready"):
        return resolved["not_ready"]
    for i in issues:
        if i["hard"]:
            return f"{i['code']}: {i['why']}"
    return None
