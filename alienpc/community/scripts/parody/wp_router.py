"""Mode router for the Render writer pipeline (coverage addendum B0, Python, no LLM).

route_mode(ask, position, still_read, cfg, continued) -> {act_id, position, mode, overlays, mode_blocks, warnings}
- act: --position by id/alias (acts.yaml via the builder), else an act alias named in the ask, else the closest act name,
  else a still-pose guess; every fallback is logged as a warning and never blocks.
- mode: one base block per clip (talk, strip, transition, oral, partner, solo, sex) keyed off the act + ask keywords.
- overlays: cinematic, gonzo, pov, edge, forced_orgasm, defeat, cnc, taboo_role, spoof, restraints, toy, threesome,
  continued, nonhuman, scale. Overlays add notes to the base card and turn on their lint rules; they are never new acts.
"""
from __future__ import annotations

import difflib
import re
from typing import Any, Dict, List, Optional

import build_request as br

OVERLAY_RE = [  # (overlay, pattern) - first-match order does not matter; every hit is an overlay
    ("cinematic", r"\bcinematic|\bmovie\b|\bfilm\b|high-end"),
    ("gonzo", r"\bgonzo\b|\bamateur\b|\braw\b"),
    ("pov", r"\bpov\b|point of view|into the lens"),
    ("edge", r"\bedg(?:e|es|ing)\b|\bdenial\b|\bteas(?:e|es|ing)\b"),
    ("forced_orgasm", r"forced orgasm|overstim\w*"),
    ("defeat", r"superheroine|\bheroine\b|\bperil\b|\bdefeated\b"),
    ("cnc", r"\bcnc\b|reluctan\w*|\bresist\w*|non-?con\w*"),
    ("taboo_role", r"\bdaddy\b|\bstep-?(?:brother|sister|dad|mom|father|mother|son|daughter)\b|\b(?:brother|sister|uncle|cousin)\b|roleplay"),
    ("spoof", r"\bspoof\b|\bparody\b|infomercial|\bnoir\b|space-captain|sitcom"),
    ("restraints", r"\brestrain\w*|\btied\b|\bcuff\w*|\bbound\b|\bropes?\b|strapped"),
    ("toy", r"\btoys?\b|vibrator|dildo|\bplug\b|\bwand\b"),
    # lost-features audit (Derrick, Prompt maker t243s811): creature partners and size play, no literal 'non-human' needed
    ("nonhuman", br._CREATURE_RE.pattern.replace("(?i)", "")),
    # Derrick t1454u/t1455u: sleep, hypnosis/mind-control and sedative themes are agreed adult roleplay: one consent line or wink in clip 1 (t1457u)
    ("consent_setup", r"\basleep\b|\bsleep(?:ing|s)?\b|\bhypno\w*|mind[- ]?control\w*|\btrance\b|\bsedat\w*|\bdrugged\b|\bmdma\b"),
    ("scale", r"\btiny\b|\bfair(?:y|ies)\b|\bpixie|\bminiature\b|\bgiant(?:ess)?\b|\boversized\b|"
              r"\b(?:massive|huge|enormous) (?:cock|dick|shaft|size)\b|size difference|\bcarr(?:y|ies|ied|ying)\b|"
              r"held in (?:the )?air|\blifts? (?:her (?:up|off|into)|the tiny)\b"),
]
TRANSITION_RE = re.compile(r"(?i)position change|\bswitch(?:es)? to\b|turns her over|\bfrom (?:missionary|doggy|cowgirl|spooning)\b[^.]{0,30}\bto\b|rolls her (?:over|onto)")
STRIP_RE = re.compile(r"(?i)\bstrip\w*|\bundress\w*|slow reveal|\bpeels?\b")
SEX_WORDS_RE = re.compile(r"(?i)\b(?:sex|fucks?|takes her|thrusts?|rides?|riding|penetrat\w*|inside her)\b")
# mode-block labels in writer_prompt.md MODES (only the blocks for this clip are kept)
BLOCK_FOR = {"cinematic": "Cinematic", "gonzo": "Gonzo", "pov": "Gonzo", "edge": "Teasing and edging",
             "forced_orgasm": "Forced orgasm", "strip": "Strip and undress", "defeat": "Superheroine defeat", "toy": "Toys"}


def _alias_index() -> Dict[str, str]:
    idx = {}
    for act_id, e in br.load_acts_registry().items():
        idx[act_id.lower()] = act_id
        idx[act_id.lower().replace("_", " ")] = act_id
        for a in e.get("aliases", []) or []:
            idx[a.lower()] = act_id
    return idx


def resolve_act(position: str, ask: str, still_read: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    warnings: List[Dict[str, Any]] = []
    e = br.get_act(position or "")
    if e:
        return {"act_id": e.get("id") or position, "warnings": warnings}
    idx = _alias_index()
    a = (ask or "").lower()
    hits = sorted(((len(k), v) for k, v in idx.items() if re.search(r"(?<![\w-])" + re.escape(k) + r"(?![\w-])", a)), reverse=True)
    if hits:
        act = hits[0][1]
        warnings.append({"warn": "mode_fallback", "why": f"unknown --position {position!r}; act named in the ask", "chosen": act})
        return {"act_id": act, "warnings": warnings}
    close = difflib.get_close_matches((position or "").lower(), list(idx), n=1, cutoff=0.6)
    if not close and position:
        pref = [k for k in idx if k.startswith((position or "").lower()) or (position or "").lower() in k.split(" ")]
        close = sorted(pref, key=len)[:1]
    if close:
        act = idx[close[0]]
        warnings.append({"warn": "mode_fallback", "why": f"unknown --position {position!r}; closest act name", "chosen": act})
        return {"act_id": act, "warnings": warnings}
    rd = br._unwrap_still_read(still_read or {}) if still_read else {}
    pose = str(rd.get("pose") or "").lower()
    act = "missionary" if re.search(r"lying|lies|on her back", pose) else ("blowjob" if "kneel" in pose else "talk")
    warnings.append({"warn": "mode_fallback", "why": f"unknown --position {position!r}, no act in the ask; still pose {pose!r}",
                     "chosen": act})
    return {"act_id": act, "warnings": warnings}


def route_mode(ask: str, position: str, still_read: Optional[Dict[str, Any]], cfg: Dict[str, Any],
               continued: bool = False) -> Dict[str, Any]:
    r = resolve_act(position, ask, still_read)
    act_id, warnings = r["act_id"], r["warnings"]
    kinds = cfg.get("position_kinds") or {}
    base = next((k for k, acts in kinds.items() if act_id in (acts or [])), None)
    if base is None:
        base = "sex"
        warnings.append({"warn": "mode_fallback", "why": f"act {act_id!r} has no position_kinds line", "chosen": "sex"})
    a = ask or ""
    if act_id == "tease" or (base == "solo" and STRIP_RE.search(a)):
        base = "strip"
    elif base in ("sex",) and TRANSITION_RE.search(a):
        base = "transition"
    overlays = [o for o, pat in OVERLAY_RE if re.search(r"(?i)" + pat, a)]
    rd = br._unwrap_still_read(still_read or {}) if still_read else {}
    if "pov" not in overlays and re.search(r"(?i)\bpov\b", str(rd.get("framing") or "")):
        overlays.append("pov")
    if rd.get("restraints") and "restraints" not in overlays:
        overlays.append("restraints")
    if br._THREE_BODY_ASK_RE.search(a) or int((br.get_act(act_id) or {}).get("bodies") or 2) == 3 and base != "talk":
        overlays.append("threesome")
    if br._GROUP_GT3_ASK_RE.search(a):
        warnings.append({"warn": "group_gt3", "why": "more than three people asked; written as a threesome (max 3)", "chosen": "threesome"})
        if "threesome" not in overlays:
            overlays.append("threesome")
    if continued:
        overlays.append("continued")
    # deterministic conflicts: oral/strip/talk keep edge as tempo only; tease act is strip, not edge
    if base in ("strip", "talk", "solo") and "edge" in overlays:
        overlays.remove("edge")
    if base == "strip" and SEX_WORDS_RE.search(a) and act_id == "tease":
        warnings.append({"warn": "strip_then_sex", "why": "strip and sex in one ask: this clip is the strip; run the sex as the next clip on the same --scene"})
    if base == "talk" and "spoof" not in overlays and re.search(r"(?i)spoof|parody", a):
        overlays.append("spoof")
    blocks = sorted({BLOCK_FOR[o] for o in overlays + [base] if o in BLOCK_FOR})
    return {"act_id": act_id, "position": act_id, "mode": base, "overlays": overlays, "mode_blocks": blocks, "warnings": warnings}
