#!/usr/bin/env python
"""TR5S caption pass - a NEW approved start still read by the uncensored vision model.

Derrick 2026-10-26 12:37 PM CT (plan MAX block): "commit it and have forge do a test run, it needs to pick
out a new image and animate it, 5 seconds". The MAX block's TEST RUN names the mechanism: "caption it with
your own vision model (llama-swap `vl_judge`)". This file adds no new transport and no new ask: it registers
its own tag on the shipped CARD-VL base (C:/AI/community/notes/top_card_vl_build.py), which runs the 3.17
instrument C:/AI/community/notes/ali163_vision_probe.ask (guard, dims, sha, no-thinking rows, the record
shape), with the shipped ask A (CARD-VL, 2026-10-25) and ask C (CARD-VL2, 2026-10-26, the region rows).
L21 is applied by that instrument: reasoning_effort=none + enable_thinking=false + max_tokens 3000.

What is new is only the SCOPE: a scene id outside the three GI cards. A scene id is resolved by the shipped
picker's own rules - it must live in an approved GROK_IMAGINE folder and its sha256 must match that
folder's MANIFEST.csv (the rule notes/hc_pick_scan_20261023.py enforces) - and its bytes must be copied to
the ComfyUI input dir before the ask, because the base record proves the render input equals the approved
file (row field comfy_copy_sha_match).

Tag "tr5s" owns its record and its raw captions:
  record   C:/AI/community/notes/tr5s_caption_results.json
  captions C:/AI/community/notes/scenes/raw/<ID>_tr5s_<ASK>.txt
  specs    C:/AI/community/notes/tr5s_facts/<ID>.json
It never writes over the 2025 (tag "") or CARD-VL2 (tag "2") records those cards cite.

  python C:/AI/community/notes/tr5s_caption.py --state                 # what exists, no model call
  python C:/AI/community/notes/tr5s_caption.py --run GI076,GI102 --asks A   # the shortlist (GPU window)
  python C:/AI/community/notes/tr5s_caption.py --check                 # the record's own rows
GPU discipline: gpu_guard.ps1 rc 0 IDLE in front of EVERY request (the base does this), one model at a time,
no render, no queue post, no ComfyUI/llama-swap control call. KEEP is Derrick's: no score, rank, best.
"""
import csv
import glob
import json
import os
import shutil
import sys

sys.path.insert(0, "C:/AI/community/notes")
import top_card_vl_build as tc  # the CARD-VL base: record shape, asks, guard, run, gates
import card_vl2_build as cv2    # the shipped ask C (the region rows), registered on tc by its own import

TAG = "tr5s"
RECORD = os.path.join(tc.NOTES, "tr5s_caption_results.json")
SPEC_DIR = os.path.join(tc.NOTES, "tr5s_facts")
POOL_DIRS = ("C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19",
             "C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19b")

# the three shipped asks, no new ask text: A (the inventory, CARD-VL 2026-10-25), B (the non-sexual
# identity + composition record, CARD-VL 2026-10-25), C (the region rows, CARD-VL2 2026-10-26). The record's
# scope is every scene it captions x every one of these asks, so a pick shortlist is captioned whole.
tc.TAGS[TAG] = {"record": RECORD, "spec_dir": SPEC_DIR, "raw_suf": "_tr5s_", "mark": "tr5s",
                "asks": ["A", "B", "C"], "item": "TR5S test run, Derrick 2026-10-26 12:37 PM CT"}


def pool_rows():
    """id -> (path, manifest sha256) from every approved GROK_IMAGINE folder's MANIFEST.csv."""
    out = {}
    for d in POOL_DIRS:
        mf = os.path.join(d, "MANIFEST.csv")
        if not os.path.isfile(mf):
            continue
        with open(mf, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                out[r["new_name"]] = (os.path.join(d, r["new_name"]).replace("\\", "/"), r["sha256"])
    return out


def resolve(still_id):
    """An approved pool id, verified against its folder manifest. Nothing is invented: an id that is not in
    a MANIFEST.csv, whose bytes are not on disk, or whose sha does not match is refused."""
    rows = pool_rows()
    key = still_id if still_id.lower().endswith(".jpg") else still_id + ".jpg"
    if key not in rows:
        raise SystemExit("REFUSE %s: not a file in any approved GROK_IMAGINE MANIFEST.csv" % still_id)
    path, want = rows[key]
    if not os.path.isfile(path):
        raise SystemExit("REFUSE %s: MANIFEST names %s and it is not on disk" % (still_id, path))
    got = tc.sha_file(path)
    if got != want:
        raise SystemExit("REFUSE %s: sha256 %s != MANIFEST %s" % (still_id, got[:16], want[:16]))
    return path, want


def ensure_comfy_copy(still_id):
    """The render input must be the approved bytes: copy once, never overwrite, and prove the match.
    The base record's row gate (comfy_copy_sha_match) reads this pair, so a caption row can only pass when
    the file the render will load is byte-identical to the approved file."""
    path, _ = resolve(still_id)
    dst = tc.comfy_copy(still_id)
    if os.path.exists(dst):
        if tc.sha_file(dst) != tc.sha_file(path):
            raise SystemExit("REFUSE %s: ComfyUI input copy %s has different bytes (never overwrite)"
                             % (still_id, dst))
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(path, dst)
    return path, dst


def sync_asks():
    """The record declares the asks it covers, and every declared ask carries its text + sha + provenance
    (base `scope_faults`/`doc_faults`: 'a declared ask with no text is unaskable'). When this tag's ask set
    grows, the record's `asks` block is filled from the registered asks the run actually sends - the same text
    bytes, so a row's ask_sha256 still matches. Rows are never rewritten: a paid caption is never re-asked."""
    doc = tc.load_doc(TAG)
    if not doc:
        return None
    added = []
    for ak in tc.TAGS[TAG]["asks"]:
        if (doc.get("asks") or {}).get(ak, {}).get("text") == tc.ASKS[ak]:
            continue
        doc.setdefault("asks", {})[ak] = {"text": tc.ASKS[ak], "sha256": tc.sha_text(tc.ASKS[ak]),
                                          "provenance": tc.ASK_PROVENANCE.get(ak, "UNDECLARED")}
        added.append(ak)
    if added:
        doc["scope"] = {"scenes": sorted({r.get("scene") for r in doc["rows"]}),
                        "asks": sorted(tc.TAGS[TAG]["asks"])}
        tc.save_doc(doc)
        print(f"record asks filled from the registered asks: {added}; scope re-declared "
              f"{doc['scope']['scenes']} x {doc['scope']['asks']}")
    return tc.load_doc(TAG)


def do_state(args):
    ids = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(POOL_DIRS[0], "GI*.jpg")))
    ids += sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(POOL_DIRS[1], "GI*.jpg")))
    print("TR5S tag=%s record=%s exists=%s" % (TAG, RECORD, os.path.isfile(RECORD)))
    print("pool ids=%d (two approved GROK_IMAGINE folders, manifest-verified)" % len(ids))
    print("raw captions:", sorted(os.path.basename(p) for p in
                                  glob.glob(os.path.join(tc.RAW_DIR, "*_tr5s_*.txt"))))
    doc = tc.load_doc(TAG)
    if doc:
        for r in doc["rows"]:
            print("  row %s/%s model=%s http=%s finish=%s words=%s declines=%s guard_rc=%s raw=%s"
                  % (r["scene"], r["ask_id"], r["model_id"], r["http_status"], r["finish_reason"],
                     r["caption_words"], r["decline_markers"], r["guard_rc"],
                     os.path.basename(r.get("raw_path") or "")))
    print("asks registered: %s" % sorted(tc.TAGS[TAG]["asks"]))
    return 0


def do_run(args):
    scenes = args["--scenes"]
    asks = args["--asks"]
    for sc in scenes:                      # refuse before the first model call, not in the middle
        ensure_comfy_copy(sc)
    sync_asks()
    tc.SCENES = tuple(scenes)             # this process only: the base registry gains this pass's scope
    tc.still_path = lambda sc: resolve(sc)[0]
    argv = ["--run", "--tag", TAG, "--model", tc.MODEL_DEFAULT, "--scenes", ",".join(scenes),
            "--asks", ",".join(asks), "--max-tokens", "3000", "--timeout", "600"]
    if args.get("--rerun"):
        argv.append("--rerun")
    rc = tc.main(argv)
    print("run rc=%s record=%s" % (rc, RECORD))
    return rc


def do_check(args):
    sync_asks()
    rc = tc.main(["--check", "--tag", TAG])
    doc = tc.load_doc(TAG)
    if not doc:
        print("RED no record at %s" % RECORD)
        return 1
    need = {"model_id", "command", "image_path", "image_sha256", "image_dims", "http_status",
            "finish_reason", "decline_markers", "guard_rc", "guard_text", "caption", "caption_words",
            "raw_path", "raw_sha256", "ask_sha256", "request_options", "max_tokens", "comfy_copy_sha_match"}
    bad = []
    for r in doc["rows"]:
        miss = sorted(k for k in need if k not in r)
        if miss:
            bad.append("ROW_FIELDS %s/%s missing %s" % (r.get("scene"), r.get("ask_id"), miss))
        if r.get("http_status") != 200:
            bad.append("ROW_HTTP %s/%s %s" % (r.get("scene"), r.get("ask_id"), r.get("http_status")))
        if r.get("guard_rc") != 0:
            bad.append("ROW_GUARD %s/%s rc=%s" % (r.get("scene"), r.get("ask_id"), r.get("guard_rc")))
        if r.get("decline_markers"):
            bad.append("ROW_DECLINE %s/%s %s" % (r.get("scene"), r.get("ask_id"), r["decline_markers"]))
        if r.get("finish_reason") != "stop":
            bad.append("ROW_FINISH %s/%s %s" % (r.get("scene"), r.get("ask_id"), r.get("finish_reason")))
        if not r.get("comfy_copy_sha_match"):
            bad.append("ROW_COMFY_BYTES %s/%s the render input is not the approved bytes"
                       % (r.get("scene"), r.get("ask_id")))
        rp = r.get("raw_path")
        if not rp or not os.path.isfile(rp) or tc.sha_file(rp) != r.get("raw_sha256"):
            bad.append("ROW_RAW %s/%s raw caption file drift" % (r.get("scene"), r.get("ask_id")))
    for b in bad:
        print("  " + b)
    print("VERDICT TR5S CAPTION %s rows=%d problems=%d"
          % ("CLEAN" if not bad else "RED", len(doc["rows"]), len(bad)))
    return 0 if not bad else 1


def main(argv=None):
    argv = argv or sys.argv[1:]
    mode = argv[0] if argv else "--state"
    ap = {"--scenes": [], "--asks": ["A"], "--rerun": False}
    i = 1
    while i < len(argv):
        if argv[i] in ("--scenes", "--asks") and i + 1 < len(argv):
            ap[argv[i]] = [s for s in argv[i + 1].split(",") if s]
            i += 2
        elif argv[i] == "--rerun":
            ap["--rerun"] = True
            i += 1
        elif not argv[i].startswith("--") and mode == "--run":
            # the documented usage is `--run GI076,GI102 --asks A`; a positional list is that id list
            ap["--scenes"] = [s for s in argv[i].split(",") if s]
            i += 1
        else:
            i += 1
    if mode == "--state":
        return do_state(ap)
    if mode == "--run":
        return do_run(ap)
    if mode == "--check":
        return do_check(ap)
    print("usage: --state | --run <IDS> --asks A,C [--rerun] | --check")
    return 2


if __name__ == "__main__":
    sys.exit(main())
