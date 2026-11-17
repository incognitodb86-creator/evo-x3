#!/usr/bin/env python3
r"""ali02_node_inventory_probe.py - fix_plan 0.2: reproduce, with a committed script, the
box-local rows that 0.2 filed under "gaps I will not fake".

Reads METADATA ONLY: directory and file NAMES plus size/mtime from stat. It never opens a
file inside ComfyUI/custom_nodes - the read tool is denied there (PROMPT.md 3) and fix_plan
0.2 f forbids circumventing that with open(). The pack list is `os.scandir` names; the
install-wide walk is `os.walk` names. What a pack's NODES are is never inferred from local
source: for FaceDetailer the primary source is the pack README saved in notes/web.

Questions it answers (each one was an un-reproducible row in self_setup_20261023.md):
  1. "FaceRefine is installed in custom_nodes"          -> installed pack-name inventory
  2. "a FaceDetailer node is available on this box"     -> its provider pack (Impact) is installed
  3. "a Vagina Fix / PP Vagina Detailer pack is installed, a <anatomy> lora exists in the
     install (install-wide filename walk)"              -> names-only walk of 7 roots
  4. the Civitai-blocked "h3_antiburn_universal_v1" and "refcontrol_pose" items -> on-disk presence
  5. the SELF_MEASURED cost-A/B label                   -> runs/ali147_pool_hc_r4a_1min_v2b is
     gone and r3b survives, so the label is checkable, not folklore

Honesty rule (AGENTS.md L10: a green check that cannot fail is worthless): every ABSENT
verdict needs a positive control in the same tree. A walk that finds nothing and cannot prove
that it can find *something* reports WALK_DEAD, never "absent". So each pattern has a CONTROL
pattern that must match on the real tree, and the tree sizes have floors.

FINDINGS (the anatomy names that ARE on disk, e.g. the penis-named loras) are data written to
the artifact, not failures: --check fails when the live tree drifts from the committed
artifact, so a row that quotes a count cannot go quietly stale.

Artifact: notes/ali02_local_inventory_20261026.json (cited as evidence by 0.2 rows).
Usage:
  python C:/AI/community/notes/ali02_node_inventory_probe.py            # write the artifact
  python C:/AI/community/notes/ali02_node_inventory_probe.py --check    # rescan, compare to it
  python C:/AI/community/notes/ali02_node_inventory_probe.py --selftest # seed faults, must fire
Read-only, CPU only. No GPU, no ComfyUI/llama-swap request, no render, no queue.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
COMM = os.path.dirname(HERE)                      # C:/AI/community
COMFY = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
NODES = COMFY + "/custom_nodes"
LORAS = COMFY + "/models/loras"
OUT = os.path.join(HERE, "ali02_local_inventory_20261026.json")

ROOTS = [COMFY + "/models", COMFY + "/input", COMFY + "/output", NODES, COMFY + "/user/default",
         "C:/Users/derek/5slock/approved_characters", COMM + "/runs"]

# Patterns live in this file so no shell command line has to carry them.
PACK_PATTERNS = {
    "facerefine_pack": r"facerefine",
    "facedetailer_provider_pack": r"comfyui-impact-(pack|subpack)$",
    "h3_family_pack": r"(h3|continuum|extender|upscale)",
}
PACK_CONTROLS = {"facerefine_pack": r"impact", "facedetailer_provider_pack": r"impact",
                 "h3_family_pack": r"impact"}

# Name terms for the install-wide walk. Patterns, not words, so the walk is one regex pass.
NAME_TERMS = {
    "vagina": r"vagina", "vulva": r"vulva", "clit": r"clit", "testicl": r"testicl",
    "dick": r"dick", "cock": r"\bcock", "penis": r"penis", "semen": r"semen",
}
# The 0.2 rows claim these are ABSENT from the install; a match makes the row false, so the
# detector fires. Terms outside this set are findings recorded in the artifact (penis IS on
# disk), and drift catches it when the set changes.
EXPECT_ABSENT = ("vagina", "vulva", "clit", "testicl", "dick", "cock", "semen")

# Files the 0.1 pass cited from Civitai (fetch refused). Their local presence is checkable.
PRESENCE_FILES = {
    "h3_antiburn_universal_v1.safetensors": True,     # Derrick's community-settings list (IM1)
    "refcontrol_pose.safetensors": True,              # the RM1 refmods-adjacent control LoRA
    "ZI_Hands_v2.1.safetensors": True,
    "VaginaFix.safetensors": False,                   # the 0.1 "Vagina Fix" claim
}

# The 0.2 SELF_MEASURED cost A/B names these run dirs; the label claims r4a is gone.
RUN_DIRS = {"ali147_pool_hc_r4a_1min_v2b": False, "ali147_pool_hc_r3b_s51130003": True}

MIN_FILES = {"models": 100, "input": 500, "output": 500, "custom_nodes": 1000,
             "user/default": 10, "approved_characters": 50, "runs": 100}


def pack_names(nodes=NODES):
    """Directory names under custom_nodes. Names only - no open(), no read tool."""
    return sorted(e.name for e in os.scandir(nodes) if e.is_dir())


def root_label(root):
    if root.startswith(COMFY):
        return root[len(COMFY) + 1:]
    return root


def walk_root(root):
    """(names, dir count) under root; names only, no file is opened."""
    names, dirs = [], 0
    for base, _ds, fs in os.walk(root):
        dirs += 1
        names.extend(fs)
    return names, dirs


def scan():
    packs = pack_names()
    pack_hits = {k: [p for p in packs if re.search(v, p, re.I)] for k, v in PACK_PATTERNS.items()}
    pack_controls = {k: [p for p in packs if re.search(v, p, re.I)] for k, v in PACK_CONTROLS.items()}
    per_root, hits, total = {}, {k: [] for k in NAME_TERMS}, 0
    for root in ROOTS:
        if not os.path.isdir(root):
            per_root[root_label(root)] = {"files": -1, "dirs": 0, "missing": True}
            continue
        names, dirs = walk_root(root)
        total += len(names)
        per_root[root_label(root)] = {"files": len(names), "dirs": dirs}
        for base in names:
            for term, pat in NAME_TERMS.items():
                if re.search(pat, base, re.I):
                    hits[term].append(os.path.join(root, base).replace("\\", "/")[len(COMFY) + 1:])
    hits = {k: sorted(v) for k, v in hits.items()}
    loras = []
    for e in os.scandir(LORAS):
        if e.is_file():
            st = e.stat()
            loras.append({"name": e.name, "bytes": st.st_size,
                          "date": datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y-%m-%d")})
    presence = {n: os.path.isfile(os.path.join(LORAS, n)) for n in PRESENCE_FILES}
    runs = {n: os.path.isdir(os.path.join(COMM, "runs", n)) for n in RUN_DIRS}
    return {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "probe": "notes/ali02_node_inventory_probe.py",
        "method": "os.scandir + os.walk NAME listings and stat only; no file under "
                  "ComfyUI/custom_nodes is opened, and no node type is inferred from local source",
        "roots_scanned": {k: v for k, v in per_root.items()},
        "files_scanned_total": total,
        "packs": {"count": len(packs), "names": packs},
        "pack_hits": pack_hits,
        "pack_controls": {k: sorted(set(v)) for k, v in pack_controls.items()},
        "name_term_hits": hits,
        "name_term_expect_absent": list(EXPECT_ABSENT),
        "loras_inventory": sorted(loras, key=lambda x: x["name"]),
        "presence_files": presence,
        "runs": runs,
    }


def facts(s):
    """Checked content (timestamp/prose excluded, so --check compares stable facts)."""
    return {
        "roots_scanned": s["roots_scanned"],
        "files_scanned_total": s["files_scanned_total"],
        "pack_count": s["packs"]["count"],
        "pack_names": s["packs"]["names"],
        "pack_hits": s["pack_hits"],
        "name_term_hits": s["name_term_hits"],
        "loras_inventory": s["loras_inventory"],
        "presence_files": s["presence_files"],
        "runs": s["runs"],
    }


def verify(s):
    """Detectors. Integrity first: they gate every ABSENT verdict, so they run before claims."""
    p = []
    for k, hits in s["roots_scanned"].items():
        if hits.get("missing"):
            p.append("ROOT_MISSING: %s is not a directory - the install moved, so 'absent' "
                     "rows citing this walk are not measured" % k)
        elif hits["files"] < MIN_FILES.get(k, 10):
            p.append("WALK_DEAD: %s listed only %d files (floor %d) - the walk did not run, "
                     "so a 0-hit term there is not an absence finding"
                     % (k, hits["files"], MIN_FILES.get(k, 10)))
    for k, ctl in s["pack_controls"].items():
        if not ctl:
            p.append("PACK_CONTROL_DEAD: no pack name matches the control for %r - the pack "
                     "listing is empty, so the FaceRefine ABSENT verdict means nothing" % k)
    if s["packs"]["count"] < 20:
        p.append("PACKS_MISSING: only %d packs under custom_nodes - the listing is not the install"
                 % s["packs"]["count"])
    control_names = [x["name"] for x in s["loras_inventory"] if x["name"].endswith(".safetensors")]
    if len(control_names) < 10:
        p.append("LORA_WALK_DEAD: only %d .safetensors in models/loras - the LoRA inventory "
                 "cannot support an absence claim" % len(control_names))
    # claims the 0.2 rows make
    if s["pack_hits"]["facerefine_pack"]:
        p.append("FACEREFINE_INSTALLED: %s is installed - the 0.2 row 'no FaceRefine pack is "
                 "installed' is now false, re-audit it" % ", ".join(s["pack_hits"]["facerefine_pack"]))
    if not s["pack_hits"]["facedetailer_provider_pack"]:
        p.append("PROVIDER_PACK_GONE: no Impact pack under custom_nodes - the FaceDetailer-"
                 "availability row needs re-auditing")
    for term in EXPECT_ABSENT:
        if s["name_term_hits"].get(term):
            p.append("NAME_PRESENT: %d file name(s) match the term the 0.2 row says is absent "
                     "from the install (%s: %s...)"
                     % (len(s["name_term_hits"][term]), term,
                        ", ".join(s["name_term_hits"][term][:2])))
    for name, want in PRESENCE_FILES.items():
        if s["presence_files"].get(name) != want:
            p.append("PRESENCE_FLIP: %s on disk = %s, the 0.2 row says %s"
                     % (name, s["presence_files"].get(name), want))
    for name, want in RUN_DIRS.items():
        if s["runs"].get(name) != want:
            p.append("RUNDIR_MISMATCH: runs/%s on disk = %s, the self-measured label says %s"
                     % (name, s["runs"].get(name), want))
    return p


def synth(packs, root_files, lora_files=None, runs=None, presence=None):
    """A scan-shaped dict from supplied listings - how --selftest seeds faults without
    touching the real install. root_files: {root_label: [names]}."""
    pack_hits = {k: [p for p in packs if re.search(v, p, re.I)] for k, v in PACK_PATTERNS.items()}
    pack_controls = {k: sorted(set(p for p in packs if re.search(v, p, re.I)))
                     for k, v in PACK_CONTROLS.items()}
    hits = {k: [] for k in NAME_TERMS}
    roots = {}
    for label, names in root_files.items():
        if names is None:                      # seeded ROOT_MISSING: the root vanished
            roots[label] = {"files": -1, "dirs": 0, "missing": True}
            continue
        roots[label] = {"files": len(names), "dirs": 10}
        for base in names:
            for term, pat in NAME_TERMS.items():
                if re.search(pat, base, re.I):
                    hits[term].append(label + "/" + base)
    loras = [{"name": n, "bytes": 1, "date": "2026-01-01"} for n in (lora_files or [])]
    return {
        "roots_scanned": roots, "files_scanned_total": sum(len(v) for v in root_files.values() if v),
        "packs": {"count": len(packs), "names": sorted(packs)},
        "pack_hits": pack_hits, "pack_controls": pack_controls,
        "name_term_hits": {k: sorted(v) for k, v in hits.items()},
        "loras_inventory": loras,
        "presence_files": dict(PRESENCE_FILES if presence is None else presence),
        "runs": dict(RUN_DIRS if runs is None else runs),
    }


def selftest():
    real = scan()
    real_problems = verify(real)
    packs = list(real["packs"]["names"])
    ctl_loras = [x["name"] for x in real["loras_inventory"] if x["name"].endswith(".safetensors")]
    good_roots = {k: (["a.safetensors", "b.png"] * 600) for k in real["roots_scanned"]}
    seeds = [
        ("facerefine-pack-installed",
         synth(packs + ["ComfyUI-H3-FaceRefine"], good_roots, ctl_loras), "FACEREFINE_INSTALLED"),
        ("provider-pack-gone",
         synth([p for p in packs if "Impact" not in p], good_roots, ctl_loras), "PACK_CONTROL_DEAD"),
        ("packs-vanished",
         synth(packs[:6], good_roots, ctl_loras), "PACKS_MISSING"),
        ("walk-dead-one-root",
         synth(packs, dict(good_roots, **{"models": ["a.safetensors"]}), ctl_loras), "WALK_DEAD"),
        ("root-missing",
         synth(packs, dict(good_roots, **{"input": None}), ctl_loras),
         "ROOT_MISSING"),
        ("lora-walk-dead",
         synth(packs, good_roots, ["a.safetensors", "b.safetensors"]), "LORA_WALK_DEAD"),
        ("anatomy-term-present",
         synth(packs, dict(good_roots, **{"models": good_roots["models"] + ["vagina_detailer_v1.safetensors"]}),
               ctl_loras), "NAME_PRESENT"),
        ("antiburn-lora-gone",
         synth(packs, good_roots, ctl_loras, presence=dict(PRESENCE_FILES, **{"h3_antiburn_universal_v1.safetensors": False})),
         "PRESENCE_FLIP"),
        ("vaginafix-lora-appears",
         synth(packs, good_roots, ctl_loras, presence=dict(PRESENCE_FILES, **{"VaginaFix.safetensors": True})),
         "PRESENCE_FLIP"),
        ("r4a-run-dir-back",
         synth(packs, good_roots, ctl_loras, runs=dict(RUN_DIRS, **{"ali147_pool_hc_r4a_1min_v2b": True})),
         "RUNDIR_MISMATCH"),
        ("r3b-run-dir-gone",
         synth(packs, good_roots, ctl_loras, runs=dict(RUN_DIRS, **{"ali147_pool_hc_r3b_s51130003": False})),
         "RUNDIR_MISMATCH"),
    ]
    fired = 0
    for tag, s, want in seeds:
        got = verify(s)
        hit = [g for g in got if g.startswith(want)]
        fired += bool(hit)
        print("  seed %-26s want %-18s -> %s" % (tag, want, (hit[0].split(":")[0] if hit
                                                             else "SILENT (detector is dead weight)")))
    silent = [t for t, s, _ in seeds if not verify(s)]
    print("SELFTEST: %d/%d seeds fire; silent seeds: %s" % (fired, len(seeds), silent or "none"))
    print("REAL TREE: %d detector(s) fired: %s"
          % (len(real_problems), sorted({p.split(":")[0] for p in real_problems})))
    for p in real_problems:
        print("   real ->", p[:160])
    if fired < len(seeds) or silent:
        print("SELFTEST FAILED: a seeded fault went silent")
        return 1
    if real_problems:
        print("SELFTEST FAILED: the real tree is not clean - the committed artifact is stale "
              "or the install moved; re-run the probe and re-audit the rows")
        return 1
    print("SELFTEST PASS: every detector fires on its seed and 0 fire on the real tree")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    s = scan()
    problems = verify(s)
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  " + p)
        return 1
    if "--check" in args:
        if not os.path.isfile(OUT):
            print("CHECK FAIL: %s is not on disk - run the probe first" % OUT)
            return 1
        committed = facts(json.load(open(OUT, encoding="utf-8")))
        now = facts(s)
        bad = [k for k in sorted(set(committed) | set(now)) if committed.get(k) != now.get(k)]
        if bad:
            print("CHECK FAIL: the live tree drifted from the committed artifact in %s" % bad)
            for k in bad:
                c, l = committed.get(k), now.get(k)
                if isinstance(l, dict) and isinstance(c, dict):
                    dk = [x for x in sorted(set(c) | set(l)) if c.get(x) != l.get(x)]
                    print("   %s -> %s: committed %r live %r" % (k, dk, [c.get(x) for x in dk], [l.get(x) for x in dk]))
                else:
                    print("   %s: committed %s entries/val, live %s" % (k, _n(c), _n(l)))
            return 1
        print("check ok: %d packs, %d files over %d roots, %d name terms (%d expected absent), "
              "%d loras inventoried, %d presence files, runs label matches disk - artifact == live tree"
              % (s["packs"]["count"], s["files_scanned_total"], len(s["roots_scanned"]),
                 len(NAME_TERMS), len(EXPECT_ABSENT), len(s["loras_inventory"]), len(PRESENCE_FILES)))
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote %s: %d packs, %d files over %d roots; term hits %s; presence %s; runs %s"
          % (OUT, s["packs"]["count"], s["files_scanned_total"], len(s["roots_scanned"]),
             {k: len(v) for k, v in s["name_term_hits"].items()}, s["presence_files"], s["runs"]))
    return 0


def _n(v):
    return len(v) if hasattr(v, "__len__") else v


if __name__ == "__main__":
    sys.exit(main())
