
"""Resolve FCSydny + Adam Jensen H3 RefMod stems. Prints counts only; writes stems.json."""
from __future__ import annotations
import json, sys
from pathlib import Path

REFMODS_DIR = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
ALIASES = Path(r"C:\AI\community\scripts\parody\aliases.json")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("stems.json")

# Import resolve from PYTHONPATH (staged or live parody)
import resolve as res

def _is_audio(stem: str) -> bool:
    s = res._mod_stem(stem).lower()
    return "_refmod_audio" in s or "_audio" in s or s.endswith("_voice") or "_voice_" in s

def _is_trim(stem: str) -> bool:
    s = res._mod_stem(stem).lower()
    return s.endswith("_23s") or "_23s_" in s or s.endswith("_trim")

def names_for(label: str, extras: list[str]) -> list[str]:
    names = [label, *extras]
    if ALIASES.is_file():
        aliases = json.loads(ALIASES.read_text(encoding="utf-8"))
        # aliases may be {alias: canonical} or richer
        def walk(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if str(k).strip().lower().replace(" ", "") == label.lower().replace(" ", ""):
                        if isinstance(v, str):
                            names.append(v)
                        elif isinstance(v, list):
                            names.extend(str(x) for x in v if isinstance(x, str))
                        elif isinstance(v, dict):
                            for vv in v.values():
                                if isinstance(vv, str):
                                    names.append(vv)
                    walk(v)
            elif isinstance(obj, list):
                for x in obj:
                    walk(x)
        walk(aliases)
    # unique preserve order
    seen = set()
    out = []
    for n in names:
        key = res._normalize_key(n) if hasattr(res, "_normalize_key") else n.lower().replace(" ", "")
        if key and key not in seen:
            seen.add(key)
            out.append(n)
    return out

def collect(label: str, extras: list[str]) -> dict:
    files = []
    tried = 0
    for n in names_for(label, extras):
        tried += 1
        norm = res._normalize_key(n) if hasattr(res, "_normalize_key") else n.lower().replace(" ", "")
        found = res.find_refmods_for_name(norm, REFMODS_DIR) or []
        for f in found:
            if f not in files:
                files.append(f)
    visual, audio, other = [], [], []
    for f in files:
        stem = res._mod_stem(str(f))
        if _is_audio(stem):
            audio.append(stem)
        else:
            visual.append(stem)
    # drop trims if a full audio exists
    if audio:
        full = [s for s in audio if not _is_trim(s)]
        if full:
            audio = full
    return {
        "visual_count": len(visual),
        "audio_count": len(audio),
        "match_count": len(files),
        "names_tried": tried,
        "visual_stem": visual[0] if visual else None,
        "audio_stem": audio[0] if audio else None,
        "dir_exists": REFMODS_DIR.is_dir(),
    }



def collect_oc(label: str) -> dict:
    """Resolve an OC trained subject (e.g. FCSydny) via safetensors subject_name metadata, not filename search."""
    mapping = res.trained_oc_subject_keys(REFMODS_DIR)
    ident = res._norm_ident(label)
    key = mapping.get(ident)
    installed = res.installed_oc_refmod_keys(REFMODS_DIR)
    stems = list(installed.get(key, []) if key else [])
    visual, audio = [], []
    for s in stems:
        if _is_audio(s):
            audio.append(s)
        else:
            visual.append(s)
    if audio:
        full = [s for s in audio if not _is_trim(s)]
        if full:
            audio = full
    return {
        "visual_count": len(visual),
        "audio_count": len(audio),
        "match_count": len(stems),
        "names_tried": 1,
        "via_oc_metadata": True,
        "oc_key_found": bool(key),
        "visual_stem": visual[0] if visual else None,
        "audio_stem": audio[0] if audio else None,
        "dir_exists": REFMODS_DIR.is_dir(),
    }

rep = {
    "FCSydny": collect_oc("FCSydny"),
    "Adam Jensen": collect("Adam Jensen", ["AdamJensen", "Jensen"]),
}
# write private stems for the filler (not printed)
private = {
    "stems": [s for s in (rep["FCSydny"].get("visual_stem"), rep["Adam Jensen"].get("visual_stem")) if s],
    "fcsydny_visual": rep["FCSydny"].get("visual_stem"),
    "fcsydny_audio": rep["FCSydny"].get("audio_stem"),
    "adam_jensen_visual": rep["Adam Jensen"].get("visual_stem"),
    "refmods_dir": str(REFMODS_DIR),
}
OUT.write_text(json.dumps(private, indent=2) + "\n", encoding="utf-8")
# stdout: counts only
public = {k: {kk: vv for kk, vv in v.items() if not str(kk).endswith("_stem")} for k, v in rep.items()}
public["wrote"] = str(OUT)
public["stem_slots_ready"] = len(private["stems"])
print(json.dumps(public, indent=2))
if len(private["stems"]) < 2:
    sys.exit(2)
