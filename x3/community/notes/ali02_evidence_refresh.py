"""
ali02_evidence_refresh.py - put the evidence bodies the inventory cites back on disk
under a fresh, attributable prefix (03y_) so citations resolve, and dump the installed
Continuum pack docs (README.md, version.py, V39 doc, civitai_desc.html, driving_nodes V39
class) from C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes/... into notes/web.

Why 03y_ and not 02v_: notes/web is git-tracked and shared; names that already existed in
git reverted to the 2026-10-23 committed copy after my fetches (per-iteration restore), and
`web_fetch.py --clean` deleted the 2026-10-24/25 bodies. A new prefix keeps new evidence
attributable to this pass. Local dumps are byte-exact copies (size + sha256 printed) so a
quoted line in the inventory can be tied to an installed file, not a web claim.

Writes: C:/AI/community/notes/web/03y_cont_readme.txt, 03y_cont_version.txt,
03y_cont_v39_doc.txt, 03y_cont_civitai_desc.html, 03y_cont_driving_nodes.txt.
Fetches go through scripts/web_fetch.py (extension is chosen from the body).
Read-only on the ComfyUI tree.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

COMMUNITY = Path("C:/AI/community")
WEB = COMMUNITY / "notes" / "web"
PROBE_PY = r"C:/AI/director/.venv/Scripts/python.exe"
WEB_FETCH = COMMUNITY / "scripts" / "web_fetch.py"
PACK = Path("C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes/ComfyUI-H3-Continuum")

# (installed file, saved name, phrase the inventory quotes from it)
DUMPS = [
    (PACK / "README.md", "03y_cont_readme.txt", ["V39", "3.9.0"]),
    (PACK / "version.py", "03y_cont_version.txt", ["__version__"]),
    (PACK / "v3" / "README_V38_4.md", "03y_cont_v39_doc.txt", ["V39", "20 s"]),
    (PACK / "v3" / "civitai_desc.html", "03y_cont_civitai_desc.html", ["V39"]),
    (PACK / "v3" / "driving_nodes.py", "03y_cont_driving_nodes.txt", ["V39", "V310"]),
    (PACK / "v3" / "resolution.py", "03y_cont_resolution.txt", ["H3_CANVAS_MULTIPLE", "Balanced"]),
    (PACK / "hardening.py", "03y_cont_hardening.txt", ["target_frames does not match"]),
]

FETCHES = [
    ("https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md", "03y_mc_readme.txt"),
    ("https://huggingface.co/TenStrip/10Eros-Max/raw/main/h3_graft_methodology.md", "03y_graft_md.txt"),
    ("https://huggingface.co/TenStrip/10Eros-Max/api/discussions?reviewed=false&sort=newest", "03y_mc_discussions.json"),
    ("https://huggingface.co/lightx2v/MiniMax-H3-33B-Turbo-Single-Step/raw/main/README.md", "03y_lightx2v_readme.txt"),
    ("https://huggingface.co/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/raw/main/README.md", "03y_pack_readme.txt"),
    ("https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA/raw/main/README.md", "03y_fal_realism_card.txt"),
    ("https://huggingface.co/MiniMaxAI/MiniMax-H3/api/main", "03y_minimax_base_api.json"),
    ("https://raw.githubusercontent.com/Comfy-Org/ComfyUI/main/tools/comfy_json_handler.py", "03y_comfy_json_handler.txt"),
    ("https://github.com/Comfy-Org/ComfyUI/issues/15529", "03y_issue15529.json"),
    ("https://raw.githubusercontent.com/SeanMesh/ComfyUI-MiniMax-H3-Continuation/main/README.md", "03y_continuation_readme.txt"),
    ("https://civitai.com/api/v1/models/2860061", "03y_civ_continuum.json"),
    ("https://civitai.com/api/v1/models/2906001", "03y_civ_2906001.json"),
    ("https://civitai.com/api/v1/models/2833322", "03y_civ_multishot.json"),
    ("https://civitai.com/api/v1/models/2967166", "03y_civ_llmvision.json"),
    ("https://civitai.com/api/v1/models/1635185", "03y_civ_antiburn.json"),
    ("https://civitai.com/api/v1/models/2905999", "03y_civ_face.json"),
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def main() -> int:
    WEB.mkdir(parents=True, exist_ok=True)
    for src, name, phrases in DUMPS:
        if not src.is_file():
            print("DUMP-SKIP missing installed file: %s" % src)
            continue
        data = src.read_bytes()
        out = WEB / name
        out.write_bytes(data)
        text = data.decode("utf-8", "replace")
        lines = text.splitlines()
        found = {p: next((i + 1 for i, ln in enumerate(lines) if p in ln), None) for p in phrases}
        print("dumped %-28s %10d B sha=%s lines=%d %s" % (name, len(data), sha(out), len(lines), found))

    manifest = []
    for url, name in FETCHES:
        cmd = [PROBE_PY, str(WEB_FETCH), "--url", url, "--name", name]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
        line = (proc.stdout or "").strip().splitlines()
        print("fetch %-28s %s" % (name, line[-1] if line else (proc.stderr or "")[:80]))
        stem = name.rsplit(".", 1)[0]
        hits = sorted(p for p in WEB.iterdir() if p.name == name or p.name.startswith(stem + "."))
        if hits:
            manifest.append({"name": hits[-1].name, "bytes": hits[-1].stat().st_size,
                             "sha256_16": sha(hits[-1]), "url": url})
    (COMMUNITY / "notes" / "ali02_evidence_refresh.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print("manifest notes/ali02_evidence_refresh.json entries=%d" % len(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
