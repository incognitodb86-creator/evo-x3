"""Render writer pipeline linter (Max Architect 3, 2026-11-13, Derrick t1409u; spec render-writer-pipeline-handoff-20261113.md).

Deterministic, CPU only. Scores one candidate 0-100 and lists hard fails. Every builder regex is IMPORTED from
build_request.py (never copied), so the linter follows the builder when its regexes change.
"""
from __future__ import annotations

import difflib
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

import build_request as br

# --- imported builder regexes (spec section 5; live line numbers re-checked 2026-11-13) -------------------------------
PRIMARY_RE = br._PRIMARY_RE
TEMPO_RE = br._TEMPO_RE
CONTACT_RE = br._CONTACT_RE
ASIDE_RE = br._ASIDE_RE
REMOVE_VERB_RE = br._REMOVE_VERB_RE
PENETRATION_RE = br._PENETRATION_RE
OPENER_RE = br._OPENER_RE
ACT_RE = br._ACT_RE
BODY_SOUND_RE = br._BODY_SOUND_RE
SECTION_RE = br._SECTION_RE
CAMERA_SENTENCE_RE = br._CAMERA_SENTENCE_RE
NEG_WORD_RE = br._NEG_WORD_RE
D_RE = br._D_RE

# --- pipeline-only patterns (not in the builder) -------------------------------------------------------------------
SHOT2_RE = re.compile(r"\[Shot\s*(?:[2-9]|\d{2,})\]", re.I)
TIMESTAMP_RE = re.compile(r"\b\d{1,2}:\d{2}(?:\.\d+)?\b|\b\d+(?:\.\d+)?\s*(?:s|sec|secs|seconds)\b|~\s*\d", re.I)
SEQ_WORD_RE = re.compile(r"\b(then|after|afterwards|afterward|next)\b", re.I)
ALLOWED_TOKEN_RE = re.compile(r"^</?d>$|^<(?:Picture|Subject|Audio) \d+>$", re.I)
ANGLE_TOKEN_RE = re.compile(r"<[^<>\n]{1,60}>")
POSE_CHAIN_RE = re.compile(r"(?i)\b(?:lies? back|lying back|lowers? (?:herself|her)|turns?|bends?|kneels?|kneeling|climbs?|"
                           r"braces?|drops? (?:to|onto|down)|rolls?|straddl\w*|sinks? (?:down|onto)|leans? (?:over|forward|back)|"
                           r"steps?|walks?|crosses|shuts?|closes? the|slams?|sets? (?:down|the)|reaches?|tosses?|grabs?|pulls?|pushes?|"
                           r"enters?|comes? in|stops?|rises?|sits?|stands? up|opens?|slides?|hooks?|tugs?|hikes?|spreads?|"
                           r"guides?|positions?|lifts?|parts?|arches?|presses?)\b")
RESULT_RE = re.compile(r"(?i)\b(?:by the end|as the clip ends|on the last frame|by the last frame|as the take ends|at the end)\b")
SOUND_NOUN_RE = re.compile(r"(?i)\b(?:sound\w*|creak\w*|rustl\w*|thud\w*|click\w*|hum\w*|waves?|slap\w*|rasp\w*|crackl\w*|"
                           r"hiss\w*|patter\w*|echo\w*|knock\w*|thump\w*|scrape\w*|squeak\w*|whisper\w*|rattl\w*|jingl\w*|"
                           r"splash\w*|surf|wind|rain|traffic|siren\w*|footsteps?|door\w*|fabric|rumbl\w*|buzz\w*|tick\w*|drip\w*)\b")
CONTINUE_RE = re.compile(r"(?i)\b(?:\w+ing|keeps?|still|continues?|on and on|without stopping)\b")
SUBJECT_START_RE = re.compile(r"^\s*(\(S[123]\)|<Subject [123]>|she|he|her|his|they|the camera)\b", re.I)
WORD_RE = re.compile(r"[a-z0-9']+")

SEX_KINDS = ("sex", "oral")
# Per-mode act rules (one block per mode; a new mode is one entry here plus one in the pipeline's MODES).
# primary: PRIMARY MOTION with a tempo word is required; contact: a _CONTACT_RE join word is required;
# banned_contact: join words that are wrong for the mode; clearance: a garment over the join must go aside;
# dev: what marks the development phase (the PRIMARY line, or the second spoken line for talk).
MODE_RULES: Dict[str, Dict[str, Any]] = {
    "sex": {"primary": True, "contact": True, "contact_hint": "inside her, buried in her, deep in her or hips flush",
            "banned_contact": None, "clearance": True, "dev": "primary", "min_lines": 0},
    "oral": {"primary": True, "contact": True, "contact_hint": "inside her mouth", "banned_contact": r"\b(?:hips flush|sheathed)\b",
             "banned_hint": "oral contact names the mouth (inside her mouth), never hips flush or sheathed",
             "clearance": False, "dev": "primary", "min_lines": 0},
    # partner present but no penetration join (titjob, finish): motion and tempo yes, join keyword no
    "partner": {"primary": True, "contact": False, "banned_contact": None, "clearance": False, "dev": "primary", "min_lines": 0},
    "solo": {"primary": True, "contact": False, "banned_contact": None, "clearance": False, "dev": "primary", "min_lines": 0},
    "talk": {"primary": False, "contact": False, "banned_contact": None, "clearance": False, "dev": "lines", "min_lines": 3},
    # strip (--position tease): PRIMARY MOTION is the removal with a tempo word, 1-3 removals, no contact
    "strip": {"primary": True, "contact": False, "banned_contact": None, "clearance": False, "dev": "primary", "min_lines": 0,
              "removals": (1, 3)},
    # position change: the landing in the new pose is the development; contact may be held, no full PRIMARY MOTION needed
    "transition": {"primary": False, "contact": False, "banned_contact": None, "clearance": True, "dev": "pos", "min_lines": 0},
}

# imported builder regexes for the builder-parity rules (coverage addendum B3)
DIAL_RE = br._DIAL_RE
THROAT_RE = br._THROAT_RE
CAMERA_MOTION_RE = br._CAMERA_MOTION_RE
ORAL_ACT_RE = br._ORAL_ACT_RE
MOUTH_FREE_RE = br._MOUTH_FREE_RE
RISE_RE, SINK_RE, HIS_LIFT_RE, MEET_RE = br._RISE_RE, br._SINK_RE, br._HIS_LIFT_RE, br._MEET_RE
SPEAKER_D_RE = re.compile(r"\((S[123])\)[^<]{0,120}?<d>|<d>")
SHALLOW_RE = re.compile(r"(?i)\b(?:shallow\w*|at the entrance|just the tip|half[- ]depth|only the tip)\b")
NARR_RE = re.compile(r"(?i)\b(?:dominates? her|submits?|feels? (?:humiliated|ashamed|degraded)|she (?:orgasms|cums|climaxes))\b")
PANEL_RE = re.compile(r"(?i)\bpanels?\b")
CAM_BIG_RE = re.compile(r"(?i)\b(?:orbit\w*|360|whip[- ]?pan\w*|crane\w*|\barcs?\b|arcing)\b")
SAFEWORD_RE = re.compile(r"(?i)\bsafe ?word\b")
RELEASE_RE = re.compile(r"(?i)\b(?:unties?|untied|unbuckl\w*|uncuff\w*|releases? her (?:wrists|ankles|hands)|frees? her (?:wrists|hands))\b")
RESTRAINT_RE = re.compile(r"(?i)\b(?:tied|bound|cuff\w*|rope\w*|strap\w*|restrain\w*|pinned|pins? her wrists)\b")
ROLE_RE = re.compile(r"(?i)\b(?:daddy|step-?(?:brother|sister|dad|mom|father|mother|son|daughter)|brother|sister|uncle|cousin)\b")
WET_RE = re.compile(r"(?i)\b(?:wet\w*|oil\w*|oily|sweat\w*|glisten\w*|slick\w*)\b")
PER_SEC_RE = re.compile(r"(?i)\b(one|two|three|four|five|\d+(?:\.\d+)?)\s+(?:\w+\s+){0,3}?(?:strokes?|thrusts?|beats?|cycles?|bobs?|drives?|moves?)\s+(?:a|per|every)\s+(half\s+)?second")
_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def tempo_rate(text: str) -> Optional[float]:
    m = PER_SEC_RE.search(text or "")
    if not m:
        return None
    n = _NUM.get(m.group(1).lower()) or float(m.group(1))
    return n * (2 if m.group(2) else 1)


def speaker_counts(dd: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for m in SPEAKER_D_RE.finditer(dd or ""):
        spk = m.group(1) or "?"
        out[spk] = out.get(spk, 0) + 1
    return out


def oral_mouth_talk(dd: str) -> bool:
    """True when (S1) has a <d> line while her mouth is on him (the builder's D1 rule, imported regexes)."""
    masked = D_RE.sub(lambda x: " " * len(x.group(0)), dd)
    ev = sorted([(m.start(), "on") for m in ORAL_ACT_RE.finditer(masked)] + [(m.start(), "off") for m in MOUTH_FREE_RE.finditer(masked)]
                + [(m.start(), "d") for m in SPEAKER_D_RE.finditer(dd) if (m.group(1) or "") == "S1"])
    on = False
    for _, k in ev:
        if k == "on":
            on = True
        elif k == "off":
            on = False
        elif on:
            return True
    return False


def mode_checks(dd: str, full: str, sents: List[str], plain: str, ctx: Dict[str, Any], kind: str, prim_idx: Optional[int]) -> List[Dict[str, Any]]:
    """Builder-parity and overlay rules (coverage addendum B3); hard unless marked soft."""
    out: List[Dict[str, Any]] = []
    cast = ctx.get("cast") or {}
    ov = set(ctx.get("overlays") or [])
    ask = ctx.get("ask") or ""
    act = ctx.get("act_id") or ""
    cfg = ctx.get("cfg") or {}
    # L-POS: the act's landing words (builder position_check) in the prose
    pc = cast.get("position_check")
    if pc and kind != "talk" and not re.search(pc, plain, re.I):
        out.append(_fix("pose_landing", f"land the pose in the builder's words for {act} (e.g. one of: {pc[:120]})"))
    # L-PARTNER: an off-still partner must be defined (builder writer_defined_missing_person)
    if cast.get("off_still_s2") and not br.writer_defined_missing_person(full, 2):
        out.append(_fix("partner_gate", "define (S2) when he enters: look or clothes and 'enters from' in one sentence"))
    if cast.get("off_still_s3") and not br.writer_defined_missing_person(full, 3):
        out.append(_fix("partner_gate_s3", "define (S3) when they enter: look or clothes and 'enters from' in one sentence"))
    # L-VOICE (acceptance-1 f): a speaker the builder has no voice for gets 'a distinct adult voice for (Sn)'
    if cast:
        for n in sorted(set(re.findall(r"\(S([23])\)[^<.!?]{0,120}<d>", dd))):
            if not cast.get(f"voice_s{n}"):
                out.append(_fix("voice_missing", f"(S{n}) has no voice in this clip's cast (talk/solo act); give the line to (S1) "
                                                 f"or make it an off-screen voice"))
    # L-FUTA: builder P2-FUTA-AS-MAN
    if re.search(r"(?i)\bfuta\b", ask) and re.search(r"(?i)\b(?:he|his|him|himself|the man)\b", plain):
        out.append(_fix("futa_pronoun", "the futa partner is she/her; no he, his, him or the man"))
    # L-SPK2: the builder keeps at most 2 lines per speaker
    for spk, n in speaker_counts(dd).items():
        if n > 2:
            out.append(_fix("speaker_cap", f"({spk}) has {n} lines; the builder keeps two per speaker, so give at most two"))
    if kind == "oral":
        first_contact = next((i for i, x in enumerate(sents) if re.search(r"(?i)\b(?:inside her mouth|into her mouth|in her mouth)\b|"
                                                                    r"\blips (?:close|wrap|seal|part)\w* (?:around|over)", outside_d(x))), None)
        if first_contact is not None and any(re.search(r"\(S1\)[^<]{0,120}<d>", x) for x in sents[first_contact:]):
            out.append(_fix("oral_silence", "after her mouth is on him only (S2) speaks; give (S1) wet suction and breath instead"))
        if re.search(r"(?i)\b(?:slap\w* of skin|skin (?:on|against) skin|hips? slap\w*|slapping|flesh slap\w*|thighs? slap\w*)\b", plain):
            out.append(_fix("oral_sound", "oral foley is wet suction, a gag on the deep stroke and breath through her nose, not skin slaps"))
    if re.search(r"<d>[^<]*<d>|</d>\s*</d>", dd):
        out.append(_fix("nested_d", "one <d>...</d> pair per spoken line, never nested"))
    if kind == "oral" and oral_mouth_talk(dd):
        out.append(_fix("oral_mouth_full", "(S1) speaks only while her mouth is free; move her line before he enters her mouth or after she pulls off"))
    pm_s = outside_d(sents[prim_idx]) if prim_idx is not None else ""
    if act == "cowgirl" and not (RISE_RE.search(pm_s) and SINK_RE.search(pm_s) and HIS_LIFT_RE.search(pm_s)
                                 and br._LIFT_MEASURE_RE.search(pm_s) and MEET_RE.search(pm_s)):
        out.append(_fix("ride_both", "in the PRIMARY MOTION sentence itself: her rise and her sink, and his hips lifting a few inches off the surface to meet her as she sinks"))
    if DIAL_RE.search(plain):
        out.append(_fix("dial", f"remove the technical term '{DIAL_RE.search(plain).group(0)}'; film look is light, lens and grain words"))
    if THROAT_RE.search(plain):
        out.append(_fix("throat", "write throat contact exactly as 'his hand on her throat' (the builder drops other throat wording)"))
    if kind in ("sex", "partner") and SHALLOW_RE.search(plain):
        out.append(_fix("shallow", "the builder keeps full entry; show denial with tempo or a full pull-out pause"))
    if NARR_RE.search(plain):
        out.append(_fix("narrate", "show the dynamic in grip, gaze and breath instead of naming it"))
    if PANEL_RE.search(plain):
        out.append(_fix("panel", "name the garment by the still's own noun, never 'panel'"))
    cam = [s for s in sents if re.search(r"(?i)\bcamera\b", s) and CAMERA_MOTION_RE.search(outside_d(s))]
    if len(cam) > 1:
        out.append(_fix("camera_jobs", f"one camera job per clip; {len(cam)} camera-move sentences"))
    big = CAM_BIG_RE.search(" ".join(s for s in sents if re.search(r"(?i)\bcamera\b", s)))
    if big and not CAM_BIG_RE.search(ask):
        out.append(_fix("camera_big", f"use a stable camera move (held, slow push-in, slow pull-out); drop '{big.group(0)}'"))
    fillers = [norm(f) for f in (cfg.get("filler_lines") or [])]
    for l in spoken_lines(dd):
        if l in fillers and l not in norm(ask):
            out.append(_fix("filler", f"line '{l}' is a stock filler; write a line about the still"))
    if "pov" in ov:
        if re.search(r"(?i)\bhand-?held\b", " ".join(cam)) or re.search(r"(?i)\bextreme close", plain):
            out.append(_fix("pov_camera", "POV: eye line of the dominant, medium or medium-close, one simple move, no handheld lead"))
    if "restraints" in ov:
        if not RESTRAINT_RE.search(plain):
            out.append(_fix("restraint_named", "name the restraint, who set it and its limit once"))
        if RELEASE_RE.search(plain) and not RELEASE_RE.search(ask):
            out.append(_fix("restraint_release", "the restraint stays on to the last frame"))
    if "cnc" in ov and SAFEWORD_RE.search(dd) and not SAFEWORD_RE.search(ask):
        out.append(_fix("safeword", "no safeword unless the ask names one"))
    if "taboo_role" in ov:
        titles = {m.group(0).lower().replace("-", "") for m in ROLE_RE.finditer(dd)}
        if len(titles) > 1:
            out.append(_fix("role_titles", f"one role per clip; titles used: {', '.join(sorted(titles))}"))
    rules = mode_rules(kind)
    if rules.get("removals"):
        n = len([s for s in sents if REMOVE_VERB_RE.search(outside_d(s))])
        lo, hi = rules["removals"]
        if not (lo <= n <= hi):
            out.append(_fix("strip_removals", f"a strip clip has {lo}-{hi} removal steps, each with where the garment lands; found {n}"))
        if CONTACT_RE.search(plain):
            out.append(_fix("strip_contact", "a strip clip has no penetration contact"))
    op = opening_sentence(dd)
    for prev in ctx.get("recent_openings") or []:
        if op and prev and difflib.SequenceMatcher(None, op, prev).ratio() >= float(cfg.get("opening_ratio", 0.85)):
            out.append(_fix("opening_repeat", "the 'At first' sentence repeats a recent clip; open on a different detail of the still"))
            break
    # soft
    if (ctx.get("slots") or {}).get("surface_height") == "waist" and re.search(r"(?i)\b(?:he|\(S2\))\b[^.]{0,40}\bkneel\w*", plain):
        out.append(_fix("height", "the surface is waist-high: he stands at its edge instead of kneeling on it", False, 10))
    if WET_RE.search(plain) and not (ctx.get("wet_ok")):
        out.append(_fix("wet_unasked", "wet, oil or sweat words only when the still or the ask has them", False, 5))
    rate = tempo_rate(sents[prim_idx]) if prim_idx is not None else None
    tr = (cfg.get("tempo_range") or {}).get("edge" if "edge" in ov else kind)
    if rate is not None and tr and not (tr[0] <= rate <= tr[1]):
        out.append(_fix("tempo_range", f"tempo {rate:g}/s is outside {tr[0]}-{tr[1]}/s for this mode", False, 5))
    return out


def mode_rules(kind: str) -> Dict[str, Any]:
    return MODE_RULES.get(kind) or MODE_RULES["sex"]
HARD_WEIGHT = 20


def norm(s: str) -> str:
    s = re.sub(r"\[English\]", " ", s or "", flags=re.I)
    return " ".join(WORD_RE.findall(s.lower()))


def spoken_lines(text: str) -> List[str]:
    return [norm(m.group(1)) for m in D_RE.finditer(text or "") if norm(m.group(1))]


def spoken_words(text: str) -> int:
    return sum(len(l.split()) for l in spoken_lines(text))


def outside_d(text: str) -> str:
    return D_RE.sub(" ", text or "")


def split_sentences(dd: str) -> List[str]:
    """Sentences of detailed_description, with <d> spans kept inside their sentence."""
    body = re.sub(r"^\s*\[Shot 1\]\s*", "", (dd or "").strip())
    spans: List[str] = []

    def keep(m):
        spans.append(m.group(0))
        return f"\x00{len(spans) - 1}\x00"
    masked = D_RE.sub(keep, body)
    parts = [p.strip() for p in re.split(r"(?:(?<=[.!?])|(?<=\x00))\s+(?=[A-Z(<\x00\"])", masked) if p.strip()]
    out = []
    for p in parts:
        out.append(re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], p))
    # a sentence that is only a <d> span joins its speaker lead
    merged: List[str] = []
    for s in out:
        if merged and s.lstrip().lower().startswith("<d>"):
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    return merged


_ACTOR_VERB_RE = re.compile(r"(?i)(?:\b(?:he|she|they)|\(S[123]\)|<Subject [123]>)\s+(?:\w+ly\s+)?\w+(?:s|es)\b")


def _sound_words(s: str) -> List[str]:
    hits = [m.group(0) for m in BODY_SOUND_RE.finditer(s)] + [m.group(0) for m in SOUND_NOUN_RE.finditer(s)]
    return [h for h in hits if not h.lower().startswith("wet")]


VOCAL_SOUND_RE = re.compile(r"(?i)\b(?:huff\w*|groan\w*|moan\w*|gasp\w*|sigh\w*|whimper\w*|grunt\w*|pant\w*|"
                            r"breath\w*|giggl\w*|laugh\w*|whine\w*|squeal\w*|hiss\w*|creak\w*|slap\w*|squelch\w*|thud\w*|"
                            r"rustl\w*|murmur\w*|chuckl\w*|purr\w*|exhal\w*|inhal\w*)\b")


def opening_sentence(dd: str) -> str:
    m = re.search(r"(?i)\bat first,[^.!?]*[.!?]", dd or "")
    return norm(m.group(0)) if m else ""


def is_sound_sentence(s: str) -> bool:
    """A closing / ambient sound sentence (no speaker, no actor doing an action)."""
    if D_RE.search(s) or OPENER_RE.search(s) or PRIMARY_RE.search(s):
        return False
    if VOCAL_SOUND_RE.search(s) and not RESULT_RE.search(s) and len(s.split()) <= 22:
        return True  # 'S1 lets out a defiant huff.', 'A low groan from (S2) accompanies ...'
    if _ACTOR_VERB_RE.search(s):
        return False
    if re.search(r"(?i)\b(?:sound|sounds|is heard|are heard|fills? the|carr(?:y|ies) over)\b", s):
        return True
    return bool(_sound_words(s)) and len(s.split()) <= 20


def get_sections(full: str) -> List[str]:
    return [m.group(1).lower() for m in SECTION_RE.finditer(full or "")]


def get_dd(full: str) -> str:
    m = re.search(r"(?im)^\s*detailed_description\s*:\s*", full or "")
    if not m:
        return (full or "").strip()
    rest = full[m.end():]
    m2 = re.search(r"(?im)^\s*continuation\s*:\s*", rest)
    return (rest[:m2.start()] if m2 else rest).strip()


def _head_noun(phrase: str) -> str:
    words = WORD_RE.findall((phrase or "").lower())
    return words[-1] if words else ""


_STOP = {"the", "a", "an", "and", "of", "with", "at", "in", "on", "soft", "warm", "light", "lit", "glow", "from"}


def required_slots(slots: Dict[str, Any]) -> Dict[str, List[str]]:
    """Words the detailed_description must carry: surface noun AND garment noun AND (light word OR place word)."""
    req: Dict[str, List[str]] = {}
    if slots.get("surface"):
        req["surface"] = [_head_noun(slots["surface"])]
    if slots.get("garment_noun"):
        req["garment"] = [slots["garment_noun"]]
    lp = []
    for k in ("light", "place"):
        for w in WORD_RE.findall((slots.get(k) or "").lower()):
            if len(w) > 3 and w not in _STOP:
                lp.append(w)
    if lp:
        req["light_or_place"] = sorted(set(lp))
    return req


def _has_word(text_norm: str, w: str) -> bool:
    w = w.lower()
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]  # one plural s only: 'dress' stays 'dress' (rstrip made it 'dre')
    return bool(re.search(r"\b" + re.escape(w) + r"(?:s|es)?\b", text_norm))


_BL_STOP = {"the", "a", "an", "and", "you", "your", "i", "me", "my", "it", "is", "it's", "this", "that", "so", "to", "of", "on",
            "in", "for", "be", "are", "don't", "do", "oh", "yes", "god"}


def blacklist_hits(lines: Sequence[str], blacklist: Iterable[str], ratio: float = 0.8) -> List[Dict[str, Any]]:
    hits = []
    bl = [norm(b) for b in blacklist if norm(b)]
    for l in lines:
        nl = norm(l)
        for b in bl:
            r = 1.0 if nl == b else difflib.SequenceMatcher(None, nl, b).ratio()
            lw, bw = set(nl.split()) - _BL_STOP, set(b.split()) - _BL_STOP
            jac = len(lw & bw) / max(1, len(lw | bw)) if lw and bw else 0.0
            if r >= ratio or (jac >= 0.6 and len(lw & bw) >= 2):
                hits.append({"line": l, "blacklisted": b, "ratio": round(r, 3)})
                break
    return hits


def cloned_hits(dd: str, phrases: Iterable[str]) -> List[str]:
    t = " " + norm(dd) + " "
    out = []
    for p in phrases:
        pn = norm(p)
        if pn and (" " + pn + " ") in t:
            out.append(p)
    return out


def ngrams(words: List[str], n: int) -> List[str]:
    return [" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))]


def _clear_needed(slots: Dict[str, Any], kind: str) -> bool:
    return bool(mode_rules(kind)["clearance"]) and bool(slots.get("join_garments"))


def _fix(code: str, note: str, hard: bool = True, pen: int = 0) -> Dict[str, Any]:
    return {"code": code, "note": note, "hard": hard, "penalty": HARD_WEIGHT if hard else pen}


def lint(full: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    """ctx: kind (sex|oral|talk|solo), slots, blacklist (list[str]), cloned (list[str]), cfg (lint block),
    scene (optional previous scene entry), builder_preview (optional callable full_text -> dict)."""
    cfg = ctx.get("cfg") or {}
    kind = ctx.get("kind", "sex")
    rules = mode_rules(kind)
    slots = ctx.get("slots") or {}
    dd = get_dd(full)
    issues: List[Dict[str, Any]] = []
    sents = split_sentences(dd)
    plain = outside_d(dd)

    # -- format (all) --
    secs = get_sections(full)
    want = ["subject_definitions", "summary", "retention_analysis", "detailed_description"]
    core = [s for s in secs if s in want]
    if core != want or (secs and secs[-1] not in ("detailed_description", "continuation")):
        issues.append(_fix("header_order", "the four headers must appear once each, in order: subject_definitions, summary, "
                           "retention_analysis, detailed_description"))
    if SHOT2_RE.search(dd):
        issues.append(_fix("shot2", "write one [Shot 1] only; a second angle is one camera move in prose"))
    if TIMESTAMP_RE.search(plain):
        issues.append(_fix("timestamp", "remove the timestamp or seconds; order comes from phase words (At first, as it builds, by the end)"))
    m = SEQ_WORD_RE.search(plain)
    if m:
        issues.append(_fix("seq_word", f"replace '{m.group(0)}' with a phase word (as, as it builds, by the end)"))
    for tok in ANGLE_TOKEN_RE.findall(full):
        if not ALLOWED_TOKEN_RE.match(tok):
            issues.append(_fix("unfilled_slot", f"fill the blank {tok} with the real noun"))
            break

    # -- required still slots (all) --
    dn = norm(dd)
    req = required_slots(slots)
    for name, words in req.items():
        if not any(_has_word(dn, w) for w in words):
            issues.append(_fix("slot_" + name, f"name the still's {name.replace('_', ' ')} ({' / '.join(words[:3])}) in the prose"))

    # -- speech budget + freshness (all) --
    lines = spoken_lines(dd)
    words = sum(len(l.split()) for l in lines)
    budget = int(cfg.get("speech_words_max", 25))
    if words > budget:
        issues.append(_fix("speech_budget", f"spoken words total {words}; cut to {budget} or fewer (short lines)"))
    for h in blacklist_hits(lines, ctx.get("blacklist") or [], float(cfg.get("blacklist_ratio", 0.8))):
        focus = slots.get("line_focus_text") or slots.get("line_focus") or "the still"
        issues.append(_fix("blacklist", f"line '{h['line']}' is in the last-20 list; write a new line about {focus}"))
    for p in cloned_hits(dd, ctx.get("cloned") or []):
        issues.append(_fix("cloned", f"the phrase '{p}' is copied from the instructions; say it in your own words"))

    # -- act rules --
    prim_idx = next((i for i, s in enumerate(sents) if PRIMARY_RE.search(s)), None)
    if rules["primary"]:
        if prim_idx is None:
            issues.append(_fix("no_primary", "add one 'PRIMARY MOTION - ...' sentence with the motion and its tempo"))
        else:
            if not TEMPO_RE.search(sents[prim_idx]):
                issues.append(_fix("no_tempo", "PRIMARY MOTION has no tempo word; use 'strokes a second', 'per second' or 'cycle'"))
    if rules["contact"] and not CONTACT_RE.search(plain):
        issues.append(_fix("no_contact", f"the contact sentence needs one join word ({rules['contact_hint']}) and must hold through the motion"))
    if rules.get("banned_contact") and re.search(r"(?i)" + rules["banned_contact"], plain):
        issues.append(_fix(kind + "_contact", rules.get("banned_hint") or "wrong join words for this mode"))
    if _clear_needed(slots, kind):
        gnoun = slots.get("garment_noun") or "garment"
        # builder parity: the builder's own W5 credit (active pull/slide/tug ... aside|up, or a removal verb)
        cleared = br._join_cleared_still_on(plain) or REMOVE_VERB_RE.search(plain)
        if not cleared:
            issues.append(_fix("clearance", f"the {gnoun} covers the join; write '(S2) pulls her {gnoun} aside' (or slides it up) before entry and say where it stays"))

    # -- four phases (t222) --
    content = [i for i, s in enumerate(sents) if not CAMERA_SENTENCE_RE.search(s) and not is_sound_sentence(s)]
    # anchor: the first sentence that matches the builder's opener (the camera sentence comes before it)
    anchor = next((i for i in content[:3] if OPENER_RE.search(sents[i])), None)
    if anchor is None:
        issues.append(_fix("phase_anchor", "open the action with 'At first, ...' and the still's exact pose"))
        anchor = content[0] if content else -1
    onset = next((i for i in content if i > anchor and (ASIDE_RE.search(outside_d(sents[i])) or PENETRATION_RE.search(outside_d(sents[i]))
                                                         or POSE_CHAIN_RE.search(outside_d(sents[i])))), None)
    if rules["dev"] == "lines":
        d_idx = [i for i, s in enumerate(sents) if D_RE.search(s)]
        dev = d_idx[1] if len(d_idx) >= 2 else None
        if dev is None:
            issues.append(_fix("phase_development", "talk development needs at least two spoken lines"))
    elif rules["dev"] == "pos":
        pc = (ctx.get("cast") or {}).get("position_check")
        dev = next((i for i in content if i > (onset if onset is not None else anchor) and pc and re.search(pc, outside_d(sents[i]), re.I)), None)
        if dev is None:
            issues.append(_fix("phase_development", "land the new pose in the builder's words for the act"))
    else:
        dev = prim_idx
    if onset is None:
        issues.append(_fix("phase_onset", "add the onset: the exit from the still pose, the clearance and the entry (or the one physical action)"))
    res = next((i for i in reversed(range(len(sents))) if RESULT_RE.search(outside_d(sents[i]))), None)
    if res is None:
        pure = [i for i in content if not D_RE.search(sents[i])]
        res = pure[-1] if pure else None
    order = [x for x in (anchor, onset, dev, res)]
    if None not in order and not (order[0] < order[1] < order[2] < order[3]):
        issues.append(_fix("phase_order", "keep the four phases in order: At first (still pose), the onset, the development "
                           "(PRIMARY MOTION or the talk), then the result 'by the end ...'"))
    elif res is None:
        issues.append(_fix("phase_result", "close the action with a result sentence ('by the end ...') where the motion is still going"))
    pure_action = [i for i in content if not D_RE.search(sents[i]) and not is_sound_sentence(sents[i])]
    if pure_action:
        last = outside_d(sents[pure_action[-1]])
        if not (ACT_RE.search(last) or CONTINUE_RE.search(last)):
            issues.append(_fix("static_end", "the last action sentence must keep motion alive (a continuing -ing verb, 'keeps', 'still')"))

    # soft: sound per phase
    bounds = [b for b in (anchor if anchor is not None and anchor >= 0 else 0, onset, dev, res) if b is not None]
    pen_sound = int(cfg.get("pen_phase_no_sound", 5))
    if len(bounds) == 4 and bounds == sorted(bounds):
        spans = [(bounds[0], bounds[1]), (bounds[1], bounds[2]), (bounds[2], bounds[3]), (bounds[3], len(sents))]
        closing = " ".join(s for s in sents if is_sound_sentence(s))
        for k, (a, b) in enumerate(spans):
            seg = " ".join(sents[a:max(b, a + 1)])
            if not (BODY_SOUND_RE.search(outside_d(seg)) or SOUND_NOUN_RE.search(outside_d(seg))):
                if not (k == 3 and closing):
                    issues.append(_fix("phase_sound", f"phase {['anchor', 'onset', 'development', 'result'][k]} has no sound", False, pen_sound))

    # -- chain (cross-clip) --
    prev = ctx.get("scene")
    if prev:
        on_text = " ".join(sents[(onset or 0):(dev or len(sents))]).lower()
        for act in prev.get("done_actions") or []:
            a = norm(act)
            for s in split_sentences(on_text):
                if a and difflib.SequenceMatcher(None, a, norm(s)).ratio() >= 0.8 or (a and a in norm(s)):
                    issues.append(_fix("chain_restate", f"'{act}' already happened in the last clip; continue from it"))
                    break
        for noun, pos in ((prev.get("ending_state") or {}).get("garments") or {}).items():
            n = _head_noun(noun.replace("item:", ""))
            if pos and re.search(r"(?i)aside|bunch|off|up|removed", str(pos)) and n:
                if re.search(r"(?i)\b" + re.escape(n) + r"\b[^.]{0,40}\b(?:covers?|covering|back in place|smoothed (?:down|back)|in place)\b", plain):
                    issues.append(_fix("chain_garment_reset", f"the {n} stays {pos} from the last clip; never put it back"))
        if (prev.get("ending_state") or {}).get("pov") and not re.search(r"(?i)\bpov\b|into the lens|toward the lens", plain) \
                and not ctx.get("ask_pov_change"):
            issues.append(_fix("chain_pov", "the last clip was POV; keep the POV angle"))

    # -- soft penalties --
    neg = NEG_WORD_RE.findall(plain)
    if neg:
        issues.append(_fix("negatives", f"{len(neg)} negative word(s) outside <d> ('{neg[0]}'); the builder strips them, state it positively",
                           False, min(15, 3 * len(neg))))
    run, prev_subj, worst = 1, None, 1
    for s in sents:
        m = SUBJECT_START_RE.match(s)
        subj = m.group(1).lower() if m else None
        run = run + 1 if subj and subj == prev_subj else 1
        worst = max(worst, run)
        prev_subj = subj
    if worst >= 3:
        issues.append(_fix("same_subject", f"{worst} sentences in a row open with the same subject; vary the rhythm", False, 5))
    w = WORD_RE.findall(norm(outside_d(dd)))
    grams = ngrams(w, 4)
    rep = {g for g in grams if grams.count(g) > 1 and not set(g.split()) <= {"the", "her", "his", "of", "a", "and", "s1", "s2", "in", "on"}}
    if rep:
        issues.append(_fix("repeat_4gram", f"repeated wording: '{sorted(rep)[0]}'", False, min(10, 2 * len(rep))))
    lo, hi = int(cfg.get("words_min", 90)), int(cfg.get("words_max", 190))
    wc = len(WORD_RE.findall(norm(D_RE.sub(" ", dd))))
    if wc < lo or wc > hi:
        issues.append(_fix("length", f"detailed_description has {wc} words outside speech; aim for {lo}-{hi}", False, 10))
    if rules["min_lines"] and len(lines) < rules["min_lines"]:
        issues.append(_fix("talk_lines", f"talk-only needs three to five short lines; it has {len(lines)}", False, 15))

    issues += mode_checks(dd, full, sents, plain, ctx, kind, prim_idx)

    # -- builder preview (CPU-only finalize on this candidate) --
    bp = ctx.get("builder_preview")
    preview = None
    if callable(bp):
        preview = bp(full)
        if preview.get("error"):
            issues.append(_fix("builder", "the builder rejects it: " + preview["error"][:300]))
        if preview.get("not_ready"):  # finalized-state gates (W5 final, R1, D1, P2 ...) seen before the dry build
            issues.append(_fix("builder", "the builder would return NOT_READY: " + preview["not_ready"][:300]))
        added = " | ".join(preview.get("added") or [])
        if rules["primary"] and "PRIMARY MOTION with tempo" in added:
            issues.append(_fix("builder_primary", "the builder would replace your PRIMARY MOTION; keep the 'PRIMARY MOTION -' form with a tempo word"))
        if rules["contact"] and "contact geometry line" in added:
            issues.append(_fix("builder_contact", "the builder would inject its own contact line; your contact sentence needs a join word"))
    hard = [i for i in issues if i["hard"]]
    score = max(0, 100 - sum(i["penalty"] for i in issues))
    return {"score": score, "pass": not hard, "hard": [i["code"] for i in hard], "issues": issues,
            "spoken_words": words, "lines": lines, "words": wc, "sentences": len(sents),
            "phases": {"anchor": anchor, "onset": onset, "development": dev, "result": res},
            "builder_preview": preview}


def notes_for_rewrite(result: Dict[str, Any], limit: int = 8) -> List[str]:
    return [i["note"] for i in sorted(result["issues"], key=lambda i: (not i["hard"], -i["penalty"]))][:limit]
