r"""ALI-173 B2: offline clone of run_graph_job.static_check (the harness gate).

run_graph_job.static_check(g) is the gate the harness runs on every graph job, but it GETs
http://127.0.0.1:10004/object_info, so it only works while ComfyUI is awake. This file serves the
FULL object_info dump captured from :10004 on 2026-10-23 18:12 CT
(C:/AI/community/notes/ali173_b2_object_info_full.json, 2605 classes) in place of the socket, so the
REAL gate code runs with ComfyUI asleep - the AGENTS.md "offline clone of run_graph_job.static_check"
rule, done by monkeypatching urlopen instead of re-implementing the checks.

A fake urlopen that answered EVERY url with the schema would let the gate pass anything, so the stub
refuses any url that is not /object_info. main() then runs the gate over five deliberately broken
clones and prints the expected verdict for each: the schema faults must be REJECTED; the semantic
fault (chunk_seconds 5.5, which breaks Continuum's own assembly math) is the harness gate's BLIND
SPOT - only the builder gate in notes/ali173_b2_cont_build.py sees it. The real graph must come back
OK. Any surprise flips VERDICT to FAIL and the exit code to 1.

The gate returns a list of problem strings (empty = pass); main() reads it that way.

Usage: python C:/AI/community/notes/ali173_b2_static_offline.py [path/to/request.api.json]
"""
import copy, io, json, os, sys, urllib.request

W = r"C:\AI\community"
SCHEMA = json.load(open(os.path.join(W, "notes", "ali173_b2_object_info_full.json"), encoding="utf-8"))
# the harness runs graphs out of the COMMUNITY repo (ralph.ps1:284 = runs/<id>/request.api.json)
GRAPH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(W, "runs", "ali173_cont_hc1_s51140001", "request.api.json")


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
        return False


def fake_urlopen(url, timeout=None):
    u = str(url)
    if not u.endswith("/object_info"):
        raise AssertionError("offline static_check refused a non-schema request: " + u)
    return _Resp(json.dumps(SCHEMA).encode())


urllib.request.urlopen = fake_urlopen
sys.path.insert(0, os.path.join(W, "scripts"))
import run_graph_job  # noqa: E402  (imported after the patch, so its urlopen calls hit the schema dump)

KEY = "chunk_seconds 5.5 (the gate is blind; the builder gate catches it)"


def faults(g):
    a = copy.deepcopy(g); a["312"]["inputs"]["chunk_seconds"] = 5.5        # semantic only, invisible to this gate
    b = copy.deepcopy(g); b["312"]["inputs"]["negative_prompt"] = "no"      # not an input of this node
    c = copy.deepcopy(g); del c["312"]["inputs"]["sampler"]                 # missing required input
    d = copy.deepcopy(g); d["312"]["class_type"] = "H3ContinuumSamplerV40"  # unknown class
    e = copy.deepcopy(g); del e["136"]                                      # dangling audio_vae links
    # True = this gate must REJECT, False = this gate is blind here
    exp = {"none (the real graph)": False, KEY: False, "negative_prompt key added": True,
           "required sampler deleted": True, "class renamed to V40": True, "audio_vae node deleted": True}
    return exp, {"none (the real graph)": g, KEY: a, "negative_prompt key added": b,
                 "required sampler deleted": c, "class renamed to V40": d, "audio_vae node deleted": e}


def main():
    g = json.load(open(GRAPH, encoding="utf-8"))
    print("graph " + GRAPH + f"  nodes={len(g)}")
    probs = run_graph_job.static_check(g)
    ok = not probs
    print("REAL GRAPH  static_check:", "OK" if ok else "STATIC_FAIL", "|", "; ".join(probs) or "no problems")
    exp, cases = faults(g)
    bad = []
    for name, clone in cases.items():
        plist = run_graph_job.static_check(clone)
        passed = not plist
        want_reject = exp[name]
        tag = "PASSED" if passed else "REJECTED"
        if want_reject == passed:                     # want_reject True + passed -> gate missed a fault
            bad.append(name)
            tag += "  <== UNEXPECTED"
        print(f"PROBE {name:58s}: {tag} | {'; '.join(plist[:2]) or 'no problems'}")
    verdict = ok and not bad
    print("VERDICT:", "PASS - the harness gate passes the real graph, rejects every schema fault, and its blind "
          "spot (Continuum frame math) is named" if verdict else f"FAIL - unexpected gate result: {bad}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
