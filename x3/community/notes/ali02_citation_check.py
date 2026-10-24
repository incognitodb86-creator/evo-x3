"""
ali02_citation_check.py - self-check for notes/ali02_claim_inventory_20261025.md.

Every citation in the inventory must resolve in a body that is ON DISK in
C:/AI/community/notes/web. Two hazards this exists to catch:
  1. `scripts/web_fetch.py --clean` deleted this pass's cached bodies, and notes/web is
     git-tracked, so names that already existed in git came back as the 2026-10-23
     committed copy. Line numbers recorded while fetching are therefore untrustworthy.
  2. Cards get edited: TenStrip/10Eros-Max README on main is now 3,698 B, the 15,125 B
     copy quoted in the notes is gone, so old line numbers (87-92, 141, 211, 294) fail.
This script locates each quoted phrase in the file it cites and prints the real line.
Three lists:
  CITES   positive citations - the phrase MUST be in the named file on disk.
  BANNED  negative controls - the phrase MUST NOT be in the file (this is how a
          refuted quote stays recorded: e.g. "50-100 words" is quoted in our notes
          as the lightx2v card's line, and the card on disk has no such text, so the
          check FAILS if anyone ever restores that citation without re-verifying it).
  BLOCKED citations we could not resolve because the source refused the fetch
          (401/404 stamp on disk). Printed as unverifiable, never counted as a pass.
Exit 0 = all CITES resolve and all BANS hold; 1 = any MISSING-FILE / MISSING-TEXT /
BAN-HOLDS (inventory must be fixed).
--selftest: runs the same detectors on a seeded set that MUST fail (2 cites + 1 ban).
Probe-only: reads files, prints, mutates nothing.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent / "web"

# (label, file, phrase)
CITES = [
    # --- official ComfyUI MiniMax H3 docs (committed 2026-10-23 copies) ---
    ("docs-lock-identity", "02v_docs_h3.txt", "Lock identity, style, motion, camera, or voice"),
    ("docs-templates-0.4mp", "02v_docs_h3.txt", "Templates open at"),
    ("docs-native-0.98mp", "02v_docs_h3.txt", "For 16:9 native quality, set"),
    ("docs-avoid-1.0mp", "02v_docs_h3.txt", "Avoid **1.0** MP"),
    ("docs-latent-upscaler", "02v_docs_h3.txt", "Use a **latent upscaler** on the 24-channel video latent"),
    ("docs-refine-denoise", "02v_docs_h3.txt", "**0.1–0.5**"),
    ("docs-latents-separate", "02v_docs_h3.txt", "Video and audio latents are separate"),
    ("docs-trained-range", "02v_docs_h3.txt", "124–362 frames"),
    ("docs-frame-grid", "02v_docs_h3.txt", "17k+5` at 24 fps (124 frames = 5 s)"),
    ("docs-errors-compound", "02v_docs_h3.txt", "Errors compound (faces lose texture first)"),
    ("docs-steps-12-16", "02v_docs_h3.txt", "**12–16** steps"),
    ("docs-steps-50", "02v_docs_h3.txt", "little visible change past"),
    ("docs-audio-12", "02v_docs_h3.txt", "Speech and timbre need **12+** steps"),
    ("docs-sampler-template", "02v_docs_h3.txt", "**`res_multistep`** + **`simple`**"),
    ("docs-sage-2x", "02v_docs_h3.txt", "can roughly **2×** speed"),
    ("docs-int8-morph", "02v_docs_h3.txt", "INT8 attention quantization"),
    ("docs-kitchen-noint8", "02v_docs_h3.txt", "Comfy Kitchen does not support them"),
    ("docs-kitchen-bf16", "02v_docs_h3.txt", "cannot run `int8_convrot` checkpoints"),
    ("docs-sol-attn", "02v_docs_h3.txt", "`sol-attn`"),
    ("docs-vsa-keep10", "02v_docs_h3.txt", "FastH3 uses **`vsa`** at `keep_percent` **10**"),
    ("docs-version-reqs", "02v_docs_h3.txt", "0.30.0+"),
    ("docs-native-1344", "02v_docs_h3_native.txt", "**1344×768** (768px short edge); round to multiples of **32**"),
    ("docs-ref-image-size-max", "02v_docs_h3_native.txt", "keeps 2048px short edge and is much slower"),
    ("docs-prescale-2048", "02v_docs_h3_native.txt", "Pre-scale to 2048 short edge"),
    ("docs-turbo-20steps", "02v_docs_h3_native.txt", "Default **20** steps"),
    ("docs-raise-25", "02v_docs_h3_native.txt", "Raise steps (e.g. **25**)"),
    ("docs-r2v-turbo4", "02v_docs_h3_native.txt", "**4**-step Lightn"),
    ("docs-firstframe-aspect", "02v_docs_h3_native.txt", "resized to the canvas without keeping its aspect ratio"),
    ("docs-fasth3-8steps", "02v_docs_h3_fastvideo.txt", "trained for exactly 8 steps"),
    ("docs-fasth3-vsa", "02v_docs_h3_fastvideo.txt", "`keep_percent` 10 starting at 20%"),
    ("docs-fasth3-cap", "02v_docs_h3_fastvideo.txt", "capped at 768x1344"),
    ("docs-fasth3-noref2va", "02v_docs_h3_fastvideo.txt", "Ref2VA (multi-reference"),
    # --- 10Eros-Max card, current main revision (3,698 B) ---
    ("mc-beta6-10/3", "03y_mc_readme.txt", "Samples on 10/3 shift"),
    ("mc-beta6-8-12", "03y_mc_readme.txt", "slow 8-12 step reference model"),
    ("mc-beta6-sla", "03y_mc_readme.txt", "SLA sparsity seems to destroy it"),
    ("mc-turbo-on-top", "03y_mc_readme.txt", "4step turbo loras can be run on top"),
    ("mc-samplers", "03y_mc_readme.txt", "er_sde, euler, LCM, res_multistep"),
    ("mc-lora-strength", "03y_mc_readme.txt", "needing lower strength 0.2-0.6"),
    ("mc-audio-nonturbo", "03y_mc_readme.txt", "Non-turbo full step audio will always be better"),
    ("mc-resmulti", "03y_mc_readme.txt", "res_multistep/simple 6-8 steps"),
    ("mc-lcm-audio", "03y_mc_readme.txt", "LCM/simple 6-8 steps (best turbo audio)"),
    ("mc-euler", "03y_mc_readme.txt", "Euler/simple 4-8 steps"),
    # graft write-up: supports ONLY "the 10Eros builds are a structured cross-arch
    # graft" - it has NO "beta" string and NO frame counts, so it is not the source
    # for the 124/243/362 frame claim (that is MiniMax discussion 28 + the docs).
    ("graft-structured-transfer", "03y_graft_md.txt", "structured cross-architecture transfer"),
    ("disc28-frame-grid-124", "02x_minimax_disc28.json", "124"),
    ("disc28-frame-grid-362", "02x_minimax_disc28.json", "362"),
    # --- Continuum: installed-code copies (byte-exact dumps) + fetched docs ---
    ("cont-version-3102", "03y_cont_version.txt", 'PACKAGE_VERSION = "3.10.2"'),
    ("cont-readme-v39", "03y_cont_readme.txt", "MiniMax_H3_Continuum_V39.json"),
    ("cont-driving-v39", "03y_cont_driving_nodes.txt", "class H3ContinuumSamplerV39"),
    ("cont-resolution-multiple32", "03y_cont_resolution.txt", "H3_CANVAS_MULTIPLE"),
    ("cont-resolution-balanced", "03y_cont_resolution.txt", "Balanced"),
    ("cont-hardening-frames", "03y_cont_hardening.txt", "target_frames does not match"),
    ("cont-v39-refdoc", "03y_cont_v39_ref_inline.txt", "has a new Reference Images input"),
    ("cont-v39-draft030", "03y_cont_v39_ref_inline.txt", "Draft 0.30 MP"),
    ("cont-v39-nogate", "03y_cont_v39_ref_inline.txt", "has not passed a real browser save/reload or GPU acceptance gate"),
    ("cont-v39-seqblank", "03y_cont_v39_ref_inline.txt", "Sequence Prompt is blank"),
    ("cont-v39-workflow", "02x_cont_v39_workflow.json", "H3ContinuumSamplerV39"),
    ("cont-relnotes-3912", "02x_cont_relnotes_3912.txt", "3.9.12"),
    ("cont-repo-265", "02x_cont_repo_api.json", "265"),
    ("cont-repo-owner", "02x_cont_repo_api.json", "ukr8b3g-cmyk/ComfyUI-H3-Continuum"),
    ("cont-registry-3100", "02v_registry_continuum.json", "3.10.0"),
    ("cont-registry-flagged", "02v_registry_continuum.json", "NodeVersionStatusFlagged"),
    # --- continuation node pack (correct repo: ttulttul, 17 stars) ---
    ("continuation-overlap22", "03y_continuation_readme.txt", "overlap_frames   = 22"),
    ("continuation-extension119", "03y_continuation_readme.txt", "extension_frames = 119"),
    ("continuation-mult17", "03y_continuation_readme.txt", "positive multiple of 17"),
    ("extender-subjectdefs", "02v_extender_readme.txt", "subject_definitions"),
    # --- community stats ---
    ("civ-continuum-6942", "02v_civitai_2860061.json", "6942"),
    ("civ-2906001-6489", "02v_civitai_2906001.json", "6489"),
    ("civ-multishot-11067", "02v_civitai_2833322.json", "11067"),
    ("civ-llmvision-517", "02v_civitai_2967166.json", "517"),
    ("minimax-base-4967030", "02x_minimax_base_api.json", "4967030"),
    ("fal-realism-87788", "02v_fal_realism.json", "87788"),
    ("fal-trigger-r34l1sm", "03y_fal_realism_card.txt", "r34l1sm"),
    ("antiburn-1242", "04z_antiburn_api.json", "1242"),
    ("charswap-97293", "04z_charswap_api.json", "97293"),
    ("latentup-273841", "02x_latent_up_api.json", "273841"),
    ("latentup-repo-775", "02x_latent_up_repo.json", "775"),
    ("pe-qwen36", "04z_pe_api.json", "Qwen3.6"),
    ("pe-t2va", "02v_lightx2v_pe_readme.txt", "T2VA"),
    ("pe-short-prompt", "02v_lightx2v_pe_readme.txt", "Short prompt \u2500\u2500\u25ba"),
    ("gemma12b-1499393", "04z_gemma12b_api.json", "1499393"),
    ("gemmae4b-534984", "04z_gemmae4b_api.json", "534984"),
    ("qwen4b-1232630", "04z_qwen4b_api.json", "1232630"),
    ("comfy-repo-142366", "02x_comfyui_repo.json", "142366"),
    ("kijai-repo-3406", "02x_kijai_repo.json", "3406"),
    ("issue15529-int8convrot", "03y_issue15529.html", "int8_convrot"),
    ("disc28-243f", "02x_minimax_disc28.json", "243"),
    ("fal-87788", "04z_fal_api.json", "87788"),
]

# Must NOT be present in the named file (refuted quotes; see docstring).
BANNED = [
    # settings_audit_20261023.md:221-233 / hc_face_research:166-172 attribute
    # "50-100 words" to MiniMax docs AND to the lightx2v rewriter card.
    # grep -rl "50-100 words" over ALL of notes/web = 0 files. Refuted.
    ("pe-50-100-words-absent", "02v_lightx2v_pe_readme.txt", "50-100 words"),
    ("docs-50-100-words-absent", "02v_docs_h3.txt", "50-100 words"),
    ("docs-100-200-words-absent", "02v_docs_h3_native.txt", "100-200 words"),
    ("mc-word-count-absent", "03y_mc_readme.txt", "word"),
    # 02v_docs_h3.txt is the resolution/steps page: FaceRefine was quoted from it.
    ("docs-facerefine-absent", "02v_docs_h3.txt", "facerefine"),
    # 03y_graft_md.txt was cited for the 124/243/362 frame grid and for "beta6".
    ("graft-no-frame-grid", "03y_graft_md.txt", "243"),
    ("graft-no-beta-string", "03y_graft_md.txt", "beta"),
]

# Source refused the fetch this pass; the stamp body is on disk. = unverifiable.
BLOCKED = [
    ("cwb-stars-1", "amirfarzam/CodexBench stars + SKILL.md path",
     "https://api.github.com/repos/amirfarzam/CodexBench -> 401", "04z_codexbench_api.401.txt"),
    ("cwb-skill-file", "cwb2b-minimax-h3-video-prompt/SKILL.md in that repo",
     "raw file 02x_codexbench_skill_raw.txt is NOT on disk", "(no body)"),
    ("tenstrip-concept-loras", "TenStrip/10Eros-Concept-LoRAs-H3 strengths",
     "HF api 401 'Invalid username or password'", "04z_* / 02v_* 401 stamps"),
]

# Seeded failures for --selftest: every detector here MUST fire.
SELFTEST_CITES = [
    ("st-missing-file", "02x_definitely_not_saved.json", "stargazers"),
    ("st-missing-text", "03y_mc_readme.txt", "ZZZ phrase that is not in any body ZZZ"),
]
SELFTEST_BANS = [("st-ban-must-fire", "02v_lightx2v_pe_readme.txt", "T2VA")]


def find_lines(fname: str, phrase: str):
    """Return ('file', []) if the body is absent, else ('lines', [lineno, ...])."""
    path = WEB / fname
    if not path.is_file():
        return "file", []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "lines", [i + 1 for i, ln in enumerate(lines) if phrase in ln]


def run(cites, bans, label="") -> int:
    bad = []
    for lab, fname, phrase in cites:
        kind, hits = find_lines(fname, phrase)
        if kind == "file":
            print("MISSING-FILE  %-28s %s" % (lab, fname)); bad.append(lab)
        elif not hits:
            print("MISSING-TEXT  %-28s %s phrase=%r" % (lab, fname, phrase[:46])); bad.append(lab)
        else:
            print("ok  %-28s %s:%s" % (lab, fname, ",".join(map(str, hits[:4]))))
    for lab, fname, phrase in bans:
        kind, hits = find_lines(fname, phrase)
        if kind == "file":
            print("MISSING-FILE  %-28s %s (ban body absent)" % (lab, fname)); bad.append(lab)
        elif hits:
            print("BAN-HOLDS     %-28s %s:%s phrase=%r" % (lab, fname, ",".join(map(str, hits[:4])), phrase[:40])); bad.append(lab)
        else:
            print("ban-ok  %-24s %s phrase=%r absent" % (lab, fname, phrase[:40]))
    print("\n%schecked %d citations + %d bans, %d problems" % (label, len(cites), len(bans), len(bad)))
    if bad:
        print("failed: " + ", ".join(bad))
    return len(bad)


# Every web/<file> token written in our audit docs must be a body that exists on disk.
# The curated CITES list only proves what I chose to quote; prose accumulates. In this
# pass 7 dead tokens (02v_docs_fastvideo.txt, 02v_lightx2v_readme.txt, 02v_pack_readme.txt,
# 02v_minimax_base_video_prompt_base_en.txt, 02x_minimax_video_prompt_ref_en.txt,
# 02x_gh_search.json, 02x_codexbench_skill_raw.txt) sat in the inventory citing files that
# were never saved - the curated list said "0 problems". This scan closes that hole.
SCAN_DOCS = [
    "ali02_claim_inventory_20261025.md",
    "self_setup_20261023.md",
    "ali02_self_setup_rows_a.py",
    "ali02_self_setup_rows_b.py",
    "ali02_self_setup_rows_c.py",
    "progress_0.2.md",
]
CITE_RE = re.compile(r"(?:notes/)?web/[\w.\-]+\.(?:json|html|txt|md)")
SEED_DOC = "00zz_seed_doc_must_not_exist.md"
SEED_TOKEN = "web/00zz_seed_body_must_not_exist.json"


def scan_docs(doc_paths=SCAN_DOCS, extra_tokens=()) -> int:
    """Cite-token existence scan. Probe-only: reads docs, checks web/, mutates nothing."""
    bad = []
    total = 0
    for name in doc_paths:
        p = Path(__file__).resolve().parent / name
        if not p.is_file():
            print("DOC-MISSING      %-30s (audit doc not on disk)" % name)
            bad.append("DOC " + name)
            continue
        toks = sorted(set(CITE_RE.findall(p.read_text(encoding="utf-8", errors="replace"))))
        total += len(toks)
        for tok in toks:
            if not (WEB / tok.split("/")[-1]).is_file():
                print("AUTO-CITE-MISSING %-25s cited by %s" % (tok, name))
                bad.append("AUTO " + tok)
    for tok in extra_tokens:
        if not (WEB / tok.split("/")[-1]).is_file():
            print("AUTO-CITE-MISSING %-25s (seeded fault)" % tok)
            bad.append("AUTO-SEED " + tok)
    print("auto-cite scan: %d tokens over %d docs, %d problems" % (total, len(doc_paths), len(bad)))
    return len(bad)


def main() -> int:
    if "--selftest" in sys.argv:
        n = run(SELFTEST_CITES, SELFTEST_BANS, label="selftest (must fail 3): ")
        s = scan_docs(doc_paths=[SEED_DOC], extra_tokens=[SEED_TOKEN])
        if n != 3 or s < 2:
            print("SELFTEST FAILED: cite/ban detectors fired %d of 3, scan detectors %d of 2"
                  % (n, s))
            return 1
        print("selftest ok: MISSING-FILE, MISSING-TEXT, BAN-HOLDS, DOC-MISSING, AUTO-CITE-MISSING all fire")
        return 0
    for lab, what, why, stamp in BLOCKED:
        print("BLOCKED  %-24s %s | %s | body: %s" % (lab, what, why, stamp))
    n = run(CITES, BANNED) + scan_docs()
    print("unverifiable (blocked) this pass: %d" % len(BLOCKED))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
