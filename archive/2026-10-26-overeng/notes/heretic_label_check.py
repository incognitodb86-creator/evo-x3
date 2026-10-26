#!/usr/bin/python3
# heretic_label_check.py - model-name integrity gate for llama-swap on this box.
# schema: heretic-label-1
#
# Item HERETIC-LABEL (Derrick 2026-10-25 6:48 PM CT, MAX pick 4 verbatim: "Fix the coding_heretic27b
# mislabel"). llama-swap's own README (saved body notes/web/01r_llamaswap_readme.txt:320) documents
# `aliases` as the way "to use familiar model names", and :345 that a request's `model` value selects
# the upstream that serves it. So a name IS a route: a familiar name that claims a model family, quant
# or size that the served file is not silently serves a different model. Measured 2026-10-26 00:47 CT:
# `GET /v1/models` advertises only model ids, never aliases, so the alias surface is invisible to a
# client's listing - the substitution is silent and no UI shows it.
#
# The rule this gate enforces (a rule, not a ban - see the two positive-control seeds in --selftest):
#   every model-family / quant / size word in a model id or an alias must be backed by the file that
#   upstream serves. An id's claims are checked against the served file (self-support is vacuous); an
#   alias's claims may be backed by the served file OR by the id it points at (an alias inherits the
#   id's own honest label, e.g. `strata` on the Strata-served upstream).
# Plus: every served path exists; no alias shadows a model id or repeats across upstreams; the live
# /v1/models id set equals the config's served-model id set (the file edit is LIVE, not dead config);
# and with --live, a name that must not resolve is answered LOUDLY (non-200), never served.
#
# GPU discipline: gpu_guard.ps1 (no args) runs in front of every llama-swap call in this script and its
# rc is recorded. 0 renders, 0 queue posts, 0 /load|/unload|/upstream, no vision model, no KEEP.
import argparse
import copy
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.request

import yaml

CFG = "C:/AI/director/config/llama-swap.yaml"
BASE = "http://127.0.0.1:8080"
GPU_GUARD = "C:/AI/director/scripts/gpu_guard.ps1"
CITE_README = "notes/web/01r_llamaswap_readme.txt:320,345"

# Lexicons are the model-identity words that appear in the names on THIS box (measured off
# llama-swap.yaml + the GGUF file names on disk), normalized. A word outside a lexicon is not a claim:
# `sc117`, `esp`, `judge`, `coding`, `auto` name nothing, so they never fire.
FAMILIES = (
    "heretic", "huihui", "darkroast", "defiant", "fable", "abliterated",
    "flashnext", "qwen3.8", "qwen3.5", "qwen3vl", "swift", "mtp",
)
QUANTS = (
    "iq3xxs", "iq3s", "iq4xl", "iq4xs", "q2ks", "q4km", "q4ks", "q5ks", "q6k", "q8",
    "int8", "fp8", "bf16", "f16", "f32",
)
SIZES = ("7b", "8b", "9b", "12b", "14b", "27b", "32b", "70b")


def norm(text):
    """Lowercase and drop the separators that differ between a file name and a model name."""
    return re.sub(r"[\s_\-]+", "", str(text or "").lower())


def sepnorm(text):
    """Lowercase with every separator run collapsed to one '.': the view a SIZE token is matched in,
    so `27b` cannot match inside `7b` and `qwen3.5-9b` still shows its 9b."""
    return re.sub(r"[\s_\-]+", ".", str(text or "").lower())


def _has_size(blob, tok):
    """A size token only counts at a digit boundary: `27b` is not evidence of `7b`. Measured
    2026-10-26: the flat-substring rule read a size 7b claim out of the alias coding_heretic27b."""
    return re.search(r"(?<![0-9])" + re.escape(tok) + r"(?![0-9])", blob) is not None


def _scan(blob, lexicon):
    """Longest-match scan: find lexicon tokens inside a normalized string."""
    hits = []
    for tok in lexicon:
        t = norm(tok)
        if t and t in blob:
            hits.append(t)
    # q8 is a prefix of q80 (Q8_0); keep the longest evidence, drop the shorter prefix of it
    hits = [t for t in hits if not any(o != t and o.startswith(t) for o in hits)]
    return set(hits)


def _scan_sizes(blob):
    """Sizes in the sepnorm view, with the digit-boundary rule (see _has_size)."""
    return {t for t in SIZES if _has_size(blob, t)}


def claims_of(name):
    """(kind, token) claims a name makes about the model it names."""
    flat, sep = norm(name), sepnorm(name)
    out = set()
    for tok in _scan(flat, FAMILIES):
        out.add(("family", tok))
    for tok in _scan(flat, QUANTS):
        out.add(("quant", tok))
    for tok in _scan_sizes(sep):
        out.add(("size", tok))
    return out


def cmd_paths(cmd):
    """Model / projector / config paths a cmd serves. Returns (model, mmproj, extra_paths)."""
    try:
        toks = [t.strip('"') for t in shlex.split(str(cmd or ""), posix=False)]
    except ValueError:
        toks = str(cmd or "").split()
    model = mmproj = None
    extra = []
    for i, tok in enumerate(toks):
        key = tok.lower()
        val = toks[i + 1] if i + 1 < len(toks) else None
        if key in ("-m", "--model", "--model-tokenizer") and val and val.lower().endswith(".gguf"):
            if model is None:
                model = val
        elif key == "--mmproj" and val:
            mmproj = val
        elif key == "--config" and val:
            extra.append(val)
    return model, mmproj, extra


def parse_cfg(text):
    """The upstreams this file defines: id -> {id, aliases, cmd, model, mmproj, extra, kind}."""
    doc = yaml.safe_load(text)
    if not isinstance(doc, dict) or not isinstance(doc.get("models"), dict):
        raise ValueError("llama-swap config has no models: mapping - cannot audit names")
    ups = {}
    for mid, spec in doc["models"].items():
        spec = spec if isinstance(spec, dict) else {}
        model, mmproj, extra = cmd_paths(spec.get("cmd"))
        ups[str(mid)] = {
            "id": str(mid),
            "aliases": [str(a) for a in (spec.get("aliases") or [])],
            "cmd": str(spec.get("cmd") or ""),
            "model": model,
            "mmproj": mmproj,
            "extra": extra,
            "kind": str(spec.get("type") or "local"),
        }
    return ups


def audit(ups, listing=None, exists=os.path.exists, probe=None, probe_name=None, expect="reject"):
    """The whole gate, as pure data in / findings out, so --selftest can seed it.

    ups: parse_cfg output. listing: live /v1/models id set, or None = do not check liveness.
    exists: path probe (seedable). probe: dict(status=int) for a live request; probe_name: the name
    asked for; expect="reject" (that name must NOT resolve) or "serve" (it must).
    """
    f = []
    served_ids = set()
    for up in sorted(ups.values(), key=lambda u: u["id"]):
        mid, aliases, model = up["id"], up["aliases"], up["model"]
        if model is None:  # a non-model upstream (llama-swap ls_comfyui etc.) serves no model file:
            continue       # no model name claims anything, so there is nothing to audit
        served_ids.add(mid)
        for path in [model, up["mmproj"]] + list(up["extra"]):
            if path and not exists(path):
                f.append({"check": "file_missing", "code": "PATH_MISSING",
                          "detail": "%s serves a path that is not on disk: %s" % (mid, path),
                          "cite": "llama-swap.yaml models.%s.cmd" % mid})
        file_flat = norm(os.path.basename(model))
        file_sep = sepnorm(os.path.basename(model))
        proj_flat = norm(os.path.basename(up["mmproj"])) if up["mmproj"] else ""
        proj_sep = sepnorm(os.path.basename(up["mmproj"])) if up["mmproj"] else ""
        served_quants = _scan(file_flat, QUANTS)

        def backed(kind, tok, target_flat, target_sep):
            """Backed = the served file names it (an alias may also inherit the id's own honest label)."""
            if kind == "quant":
                return tok in served_quants
            if tok in file_flat or tok in target_flat:
                return True
            if kind == "family" and tok in proj_flat:
                return True
            if _has_size(file_sep, tok) or _has_size(target_sep, tok):
                return True
            if kind == "family" and _has_size(proj_sep, tok):
                return True
            return False

        # the id's own claims: self-support is vacuous, so only the served file can back them
        for kind, tok in sorted(claims_of(mid)):
            if backed(kind, tok, "", ""):
                continue
            f.append({"check": "id_claim", "code": "MISLABEL_" + kind.upper(),
                      "detail": ("model id %s claims %s %s; it serves %s (served quants: %s)"
                                 % (mid, kind, tok, os.path.basename(model),
                                    ",".join(sorted(served_quants)) or "none named")),
                      "cite": CITE_README})
        for alias in aliases:
            if alias in ups:
                f.append({"check": "alias_taken", "code": "ALIAS_IS_MODEL_ID",
                          "detail": "alias %s on %s is also a model id - a request is ambiguous"
                                    % (alias, mid), "cite": CITE_README})
            for other in ups.values():
                if other["id"] != mid and alias in other["aliases"]:
                    f.append({"check": "alias_taken", "code": "ALIAS_COLLISION",
                              "detail": "alias %s is on both %s and %s" % (alias, mid, other["id"]),
                              "cite": CITE_README})
            id_flat, id_sep = norm(mid), sepnorm(mid)
            for kind, tok in sorted(claims_of(alias)):
                if backed(kind, tok, id_flat, id_sep):
                    continue
                f.append({"check": "alias_claim", "code": "MISLABEL_" + kind.upper(),
                          "detail": ("alias %s on %s claims %s %s; a request naming it is served %s "
                                     "(served quants: %s) - a silent substitution, and /v1/models "
                                     "never advertises aliases so no client listing shows it"
                                     % (alias, mid, kind, tok, os.path.basename(model),
                                        ",".join(sorted(served_quants)) or "none named")),
                          "cite": CITE_README})
    if listing is not None:
        only_live = sorted(set(listing) - served_ids)
        only_cfg = sorted(served_ids - set(listing))
        if only_live or only_cfg:
            f.append({"check": "live_listing", "code": "LIVE_MISMATCH",
                      "detail": ("live /v1/models vs config served-model ids differ: live_only=%s "
                                 "config_only=%s - the file and the running router disagree, so a name "
                                 "fix is not live" % (",".join(only_live) or "-",
                                                       ",".join(only_cfg) or "-")),
                      "cite": CITE_README})
    if probe is not None and probe_name:
        st = probe.get("status")
        if st is None:
            f.append({"check": "name_probe", "code": "PROBE_NOT_RUNNING",
                      "detail": "no HTTP status for %s (transport failed) - the probe did not run, so "
                                "the name's fate is unmeasured, not passing" % probe_name,
                      "cite": CITE_README})
        elif expect == "serve" and st != 200:
            f.append({"check": "name_probe", "code": "NAME_MISSING",
                      "detail": "%s is a name the config defines but the live router answers HTTP %s "
                                "- the honest name does not route, so the rename broke a route" %
                                (probe_name, st), "cite": CITE_README})
        elif expect == "serve":
            pass  # HTTP 200: the honest name routes to its model - that is the pass
        elif st == 200:
            f.append({"check": "name_probe", "code": "NAME_RESOLVES",
                      "detail": "%s is still served live (HTTP 200) - the name routes to a model on "
                                "this box" % probe_name, "cite": CITE_README})
    return f


# --------------------------------------------------------------------------- live reads
def read_cfg():
    with open(CFG, encoding="utf-8-sig") as fh:
        return fh.read()


def gpu_guard():
    """(rc, first line) from gpu_guard.ps1 with NO arguments. rc 0 = IDLE."""
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", GPU_GUARD], capture_output=True, text=True, timeout=120)
        return p.returncode, (p.stdout or "").strip().splitlines()[:1]
    except Exception as exc:  # a guard we cannot run is a red, never a silent pass
        return 99, [type(exc).__name__]


def live_listing(timeout=15):
    with urllib.request.urlopen(BASE + "/v1/models", timeout=timeout) as resp:
        doc = json.loads(resp.read().decode("utf-8", "replace"))
    return {m.get("id") for m in doc.get("data", []) if m.get("id")}


def ask_rejection(model, timeout=120):
    """POST a chat request naming `model`; return the HTTP status. A name that is not a route must
    be answered 4xx by llama-swap; 200 would mean it silently serves something."""
    body = json.dumps({
        "model": model, "max_tokens": 1,
        "messages": [{"role": "user", "content": "Respond with the single word: ok"}],
    }).encode()
    req = urllib.request.Request(BASE + "/v1/chat/completions", data=body,
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()[:200].decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()[:200].decode("utf-8", "replace")
    except Exception as exc:
        return None, type(exc).__name__


# --------------------------------------------------------------------------- seeds (L10)
# Rows are names measured on this box (llama-swap.yaml + the GGUF file names on disk).
UNIT_ROWS = [
    ("coding_heretic27b", {("family", "heretic"), ("size", "27b")}),
    ("coding_huihui27b", {("family", "huihui"), ("size", "27b")}),
    ("qwen3.8-flash-next-iq3_xxs", {("family", "qwen3.8"), ("family", "flashnext"),
                                   ("quant", "iq3xxs")}),
    ("qwen3.8-flash-next-iq3_s", {("family", "qwen3.8"), ("family", "flashnext"),
                                 ("quant", "iq3s")}),
    ("coding_swift15_iq3s", {("family", "swift"), ("quant", "iq3s")}),
    ("qwen3vl_judge", {("family", "qwen3vl")}),
    ("qwen3.5-9b-dark-roast-q8", {("family", "qwen3.5"), ("family", "darkroast"),
                                  ("size", "9b"), ("quant", "q8")}),
    ("vision_9b", {("size", "9b")}),
    ("RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf",
     {("family", "qwen3.8"), ("family", "heretic"), ("family", "mtp"),
      ("quant", "iq3xxs"), ("size", "27b")}),
    ("coding_sc117_strata", set()),
    ("vl_judge", set()),
    ("comfyui_auto", set()),
    ("comfyui_longvideo", set()),
]


def unit_claims():
    """The claim parser itself, probed (L10): the boundary rules ARE the gate, so they get their own
    seeded rows. A parser that matches `7b` inside `27b`, or misses `9b` in `qwen3.5-9b`, would break
    every check above silently."""
    bad = []
    for name, want in UNIT_ROWS:
        got = claims_of(name)
        if got != want:
            bad.append("%s want %s got %s" % (name, sorted(want), sorted(got)))
    return bad


def seeds():
    """Each seed mutates the REAL parsed config and names the check that must fire on it.
    A positive-control seed must stay CLEAN: the gate is a rule about served files, not a ban."""
    ups = parse_cfg(read_cfg())
    base = {m: (list(v["aliases"])) for m, v in ups.items()}

    def reset(u):
        for mid, als in base.items():
            u[mid]["aliases"] = list(als)
        return u

    def mut(fn):
        u = reset(copy.deepcopy(ups))
        fn(u)
        return u

    def clean_cfg(u):
        """the fixed wiring: every alias backed by the file it serves"""
        u["coding_sc117_strata"]["aliases"] = ["strata", "qwen3.8-flash-next-iq3_s"]
        return u

    def fixed(fn=lambda u: None):
        """a control built on the FIXED wiring - a control on the broken config inherits its faults
        (measured 2026-10-26: the 27B control inherited the real coding_heretic27b alias and fired
        ALIAS_IS_MODEL_ID + 3 MISLABELs, which is a true finding about the old wiring, not a control)"""
        u = clean_cfg(reset(copy.deepcopy(ups)))
        fn(u)
        return u

    s = []
    s.append(("alias_heretic_restored", mut(lambda u: u["coding_sc117_strata"]["aliases"].append(
        "coding_heretic27b")), "alias_claim", "MISLABEL_FAMILY", "cfg"))
    s.append(("alias_heretic_size", mut(lambda u: u["coding_sc117_strata"]["aliases"].append(
        "coding_heretic27b")), "alias_claim", "MISLABEL_SIZE", "cfg"))
    s.append(("alias_huihui_restored", mut(lambda u: u["coding_sc117_strata"]["aliases"].append(
        "coding_huihui27b")), "alias_claim", "MISLABEL_FAMILY", "cfg"))
    s.append(("alias_iq3xxs_restored", mut(lambda u: u["coding_sc117_strata"]["aliases"].append(
        "qwen3.8-flash-next-iq3_xxs")), "alias_claim", "MISLABEL_QUANT", "cfg"))
    # an id that claims a 27B Heretic and serves the Flash-Next IQ3_S file = the same fault as the
    # alias, caught at the id layer (the served file exists here, so only id_claim can fire)
    s.append(("id_serves_wrong_family", mut(lambda u: u.__setitem__("coding_heretic27b", {
        "id": "coding_heretic27b", "aliases": [],
        "cmd": "llama-server -m C:/AI/Strata-data/models/qwen38-flash-next-iq3s/IQ3_S/"
               "Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf --port ${PORT}",
        "model": "C:/AI/Strata-data/models/qwen38-flash-next-iq3s/IQ3_S/"
                 "Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf",
        "mmproj": None, "extra": [], "kind": "local"}) if "coding_heretic27b" not in u else None),
        "id_claim", "MISLABEL_FAMILY", "fs"))
    s.append(("true_alias_added", fixed(), "CONTROL", "CONTROL", "cfg"))
    # the positive control that matters most: if the real 27B Heretic is ever wired up with its own
    # honest name, this gate reads it CLEAN. It is a rule about served files, not a ban on the name.
    s.append(("correct_27b_wiring", fixed(lambda u: u.__setitem__("coding_heretic27b", {
        "id": "coding_heretic27b",
        "aliases": ["heretic27b"],
        "cmd": "llama-server -m C:/AI/models/RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf "
               "--mmproj C:/AI/models/mmproj-Qwen3.8-27B-Q8_0.gguf --port ${PORT}",
        "model": "C:/AI/models/RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf",
        "mmproj": "C:/AI/models/mmproj-Qwen3.8-27B-Q8_0.gguf",
        "extra": [], "kind": "local"})), "CONTROL", "CONTROL", "fs"))
    s.append(("served_path_missing", mut(lambda u: u["coding_swift15_iq3s"].__setitem__(
        "model", "C:/AI/models/does-not-exist-heretic27b.gguf")), "file_missing", "PATH_MISSING", "fs"))
    s.append(("alias_is_model_id", mut(lambda u: u["vl_judge"]["aliases"].append(
        "coding_swift15_iq3s")), "alias_taken", "ALIAS_IS_MODEL_ID", "cfg"))
    s.append(("alias_collision", mut(lambda u: u["qwen3vl_judge"]["aliases"].append(
        "vision_9b")), "alias_taken", "ALIAS_COLLISION", "cfg"))
    s.append(("live_missing_one_id", "listing", "live_listing", "LIVE_MISMATCH", "listing"))
    s.append(("live_extra_id", "listing_extra", "live_listing", "LIVE_MISMATCH", "listing"))
    s.append(("probe_serves_the_name", "probe200", "name_probe", "NAME_RESOLVES", "probe"))
    s.append(("probe_not_running", "probefail", "name_probe", "PROBE_NOT_RUNNING", "probe"))
    s.append(("honest_name_does_not_route", "probe404serve", "name_probe", "NAME_MISSING", "probe"))
    s.append(("honest_name_routes", "probe200serve", "CONTROL", "CONTROL", "probe"))
    return s


def run_seed(name, seed, real_ups):
    """Run one seed; returns (fired_code, findings)."""
    kind = seed[4] if len(seed) > 4 else "cfg"
    probe = pname = expect = None
    if kind == "cfg":
        ups, listing, probe, pname = seed[1], None, None, None
    elif kind == "fs":
        ups, listing, probe, pname = seed[1], None, None, None
    elif kind == "listing":
        ups = copy.deepcopy(real_ups)
        served = [u["id"] for u in real_ups.values() if u["model"]]
        listing = set(served[1:]) if seed[1] == "listing" else set(served) | {"a_name_not_in_config"}
        probe, pname = None, None
    else:  # probe
        ups, listing = copy.deepcopy(real_ups), None
        payload = seed[1]
        probe = {"status": {"probe200": 200, "probe404serve": 404, "probe200serve": 200}
                 .get(payload)}
        pname = "coding_heretic27b"
        expect = "serve" if payload.endswith("serve") else "reject"
    if kind == "fs":
        f = audit(ups, listing=None, exists=lambda p: not p.endswith("does-not-exist-heretic27b.gguf"),
                  probe=probe, probe_name=pname, expect=expect)
    else:
        f = audit(ups, listing=listing, probe=probe, probe_name=pname, expect=expect)
    want = seed[3]
    if want == "CONTROL":
        return ("CLEAN" if not f else "FIRED:" + ",".join(sorted({x["code"] for x in f}))), f
    codes = {x["code"] for x in f if x["check"] == seed[2]}
    return (want if want in codes else "NOFIRE:" + ",".join(sorted({x["code"] for x in f}))), f


def main():
    ap = argparse.ArgumentParser(description="llama-swap model-name integrity gate (heretic-label-1)")
    ap.add_argument("--check", action="store_true", help="audit the live config + the live listing")
    ap.add_argument("--offline", action="store_true", help="skip the live /v1/models read")
    ap.add_argument("--selftest", action="store_true", help="seed every fault; each must fire")
    ap.add_argument("--live", action="store_true", help="prove a removed name is answered loudly")
    ap.add_argument("--expect-served", action="store_true",
                    help="with --live: assert the name DOES route (an honest name must not break)")
    ap.add_argument("--probe-model", default="coding_heretic27b",
                    help="name to probe with --live (must NOT resolve)")
    args = ap.parse_args()
    if not (args.check or args.selftest or args.live):
        args.check = True

    ups = parse_cfg(read_cfg())
    rc = 0

    if args.check:
        listing = None
        guard = gpu_guard()
        print("gpu_guard rc=%s %s" % (guard[0], " ".join(guard[1])))
        if not args.offline:
            try:
                listing = live_listing()
                print("live /v1/models ids=%d %s" % (len(listing), ",".join(sorted(listing))))
            except Exception as exc:
                print("live /v1/models UNREACHABLE: %s: %s (liveness is unmeasured, not passing)"
                      % (type(exc).__name__, exc))
        f = audit(ups, listing=listing)
        for x in f:
            print("FIND %s :: %s :: %s [%s]" % (x["check"], x["code"], x["detail"], x["cite"]))
        print("config=%s upstreams=%d served-model-upstreams=%d names_audited=%d findings=%d"
              % (CFG, len(ups), sum(1 for u in ups.values() if u["model"]),
                 sum(1 + len(u["aliases"]) for u in ups.values() if u["model"]), len(f)))
        print("VERDICT NAME_CHECK CLEAN" if not f else "VERDICT NAME_CHECK NOT_CLEAN")
        rc = 0 if not f else 1

    if args.live:
        guard = gpu_guard()
        print("gpu_guard rc=%s %s" % (guard[0], " ".join(guard[1])))
        expect = "serve" if args.expect_served else "reject"
        st, snippet = ask_rejection(args.probe_model)
        print("probe model=%s expect=%s http_status=%s body=%s"
              % (args.probe_model, expect, st, snippet.replace("\n", " ")[:120]))
        f = audit(ups, listing=None, probe={"status": st}, probe_name=args.probe_model,
                  expect=expect)
        for x in f:
            print("FIND %s :: %s :: %s" % (x["check"], x["code"], x["detail"]))
        bad = [x for x in f if x["check"] == "name_probe"]
        print("VERDICT LIVE_PROBE CLEAN - %s behaves as expected (%s)"
              % (args.probe_model, "routes" if expect == "serve" else "answered loudly")
              if not bad else "VERDICT LIVE_PROBE NOT_CLEAN")
        rc = rc or (0 if not bad else 1)

    if args.selftest:
        units = unit_claims()
        for u in units:
            print("UNIT-FAULT %s" % u)
        real = audit(ups, listing=None)
        ctrl = audit(seeds()[5][1], listing=None)
        fired, silent, ctrl_bad = [], [], []
        for seed in seeds():
            got, findings = run_seed(seed[0], seed, ups)
            want = seed[3]
            if want == "CONTROL":
                if got == "CLEAN":
                    fired.append(seed[0])
                else:
                    ctrl_bad.append("%s -> %s" % (seed[0], got))
            elif got == want:
                fired.append("%s->%s" % (seed[0], want))
            elif got.startswith("NOFIRE"):
                silent.append("%s %s %s" % (seed[0], want, got))
            else:
                ctrl_bad.append("%s wanted %s got %s" % (seed[0], want, got))
        for x in real:
            print("REAL-FIND %s :: %s" % (x["check"], x["code"]))
        print("control fixture (fixed wiring) faults=%d (must be 0) %s"
              % (len(ctrl), ["%s:%s" % (x["check"], x["code"]) for x in ctrl]))
        print("claim-parser unit rows=%d faults=%d (must be 0)" % (len(UNIT_ROWS), len(units)))
        print("seeds: %d fired, %d silent %s, %d control violations %s"
              % (len(fired), len(silent), silent, len(ctrl_bad), ctrl_bad))
        ok = (not silent and not ctrl_bad and not units and len(fired) == len(seeds()) and not real)
        print("VERDICT SELFTEST_CLEAN" if ok else "VERDICT SELFTEST_NOT_CLEAN")
        rc = rc or (0 if ok else 1)
    return rc


if __name__ == "__main__":
    sys.exit(main())
