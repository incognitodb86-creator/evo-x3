r"""PV2-3 SETTINGS_DENSE seg1 - graph_diff parse + pre-request read-only check (no GPU, no render).

Part 1 - the TASKS gate "graph_diff shows only m_shift.model, m_vsa removed, filename_prefix":
parse runs/ali147_pool_dense_s51080000/graph_diff.txt (written by
  git -C C:/AI/community/runs diff --no-index --output=... ali147_pool_ctrl_s51080000/submitted_graph.pretty.json ali147_pool_dense_s51080000/request.api.json)
and require: 2 hunks, 20 removed lines (the "m_vsa", link line + the 18-line m_vsa node block + the
control filename_prefix line) and 2 added lines ("m_attn", and the new prefix). Anything else = FAIL.

Part 2 - fairness: node-by-node compare of the arm graph against the RENDERED control graph
(runs/ali147_pool_ctrl_s51080000/ali147_pool_ctrl_s51080000.api.json, the graph that produced the
809.7 s control output), using json.dumps(node, sort_keys=True). The differing key set must be
exactly ['m_shift','save'] among the 24 shared nodes, m_vsa must be the only node present in the
control and not in the arm, and the c0/c1 prompts must be byte-identical to the control (this arm is
a SETTINGS arm, not a prompt arm).

Part 3 - the live gates the harness will apply: the p7 id/kind regexes PARSED out of ralph.ps1 (a
hardcoded copy of a regex proves nothing), the kind=graph gates (request.api.json present, no mp4),
the id-free gates (no result.json/.out/.err.out/status.log/objective.json/mp4/.api.json), the live
budget file, and the render-seconds baseline quoted from the control's own status.log.

Writes only C:/AI/community/p7/JOB_REQUEST.json (Part 4, at the end, only if all checks pass).
Run: python C:/AI/community/notes/ali147_pv23_precheck.py
"""
import hashlib
import json
import os
import re
import sys

C = "C:/AI/community"
RC = "C:/Users/derek/5slock/ralph-community"
CTRL = C + "/runs/ali147_pool_ctrl_s51080000"
SRC = CTRL + "/submitted_graph.pretty.json"
RENDERED = CTRL + "/ali147_pool_ctrl_s51080000.api.json"
NAME = "ali147_pool_dense_s51080000"
ARM = C + "/runs/" + NAME
DST = ARM + "/request.api.json"
DIFF = ARM + "/graph_diff.txt"
REQ = C + "/p7/JOB_REQUEST.json"
MODEL = C + "/p7/jobs/request_iter10.json"      # the last accepted 481-frame graph request (ran ok)
RPT = C + "/notes/ali147-pv23-precheck-20261023.txt"
MINUTES = 120

L = []
fails = []


def p(s):
    s = str(s)
    L.append(s)
    print(s)


def chk(cond, label):
    p(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(x):
    return json.dumps(x, sort_keys=True)


def gget(g, n, *path):
    v = g.get(n, {}) if isinstance(g, dict) else {}
    for k in path:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return v


g = json.loads(open(DST, "rb").read().decode("utf-8"))
src = json.loads(open(SRC, "rb").read().decode("utf-8"))
rendered = json.loads(open(RENDERED, "rb").read().decode("utf-8"))
raw = open(DST, "rb").read()
p("PV2-3 PRE-REQUEST READ-ONLY CHECK for " + NAME)
p("arm graph " + DST)
p("  bytes %d sha256 %s" % (len(raw), sha(raw)))
p("copy source " + SRC + " bytes %d sha256 %s" % (len(open(SRC, "rb").read()), sha(open(SRC, "rb").read())))
p("")

# ---------------- Part 1: the graph_diff gate ----------------
p("== Part 1: graph_diff.txt (the TASKS gate 'shows only m_shift.model, m_vsa removed, filename_prefix')")
dl = open(DIFF, encoding="utf-8").read().splitlines()
hunks = [x for x in dl if x.startswith("@@")]
minus = [x[1:] for x in dl if x.startswith("-") and not x.startswith("---")]
plus = [x[1:] for x in dl if x.startswith("+") and not x.startswith("+++")]
p("diff file lines %d, hunk headers %d" % (len(dl), len(hunks)))
for h in hunks:
    p("  hunk " + h)
p("removed %d / added %d" % (len(minus), len(plus)))
for x in plus:
    p("  + %r" % x)
chk(len(hunks) == 2, "exactly 2 hunks (the m_shift+m_vsa hunk is adjacent = one hunk, the prefix hunk is the 2nd)")
chk(len(minus) == 20 and len(plus) == 2, "20 removed lines + 2 added lines, nothing else")
chk([x.strip() for x in plus] == ['"m_attn",',
                                  '"filename_prefix": "community/%s/%s",' % (NAME, NAME)],
    "the 2 added lines are exactly the m_attn link and the new filename_prefix")
chk([x.strip() for x in minus if x.strip() == '"m_vsa",'] == ['"m_vsa",'],
    "one removed line is the m_shift -> m_vsa link (replaced by m_attn)")
chk([x.strip() for x in minus if x.strip().startswith('"filename_prefix"')] ==
    ['"filename_prefix": "community/ali147_pool_ctrl_s51080000/ali147_pool_ctrl_s51080000",'],
    "one removed line is the control's filename_prefix")
vsa_lines = [x.strip() for x in minus if x.strip().startswith('"m_vsa": {')]
p("removed m_vsa block header lines: %s" % json.dumps(vsa_lines))
chk(vsa_lines == ['"m_vsa": {'], "exactly one removed node block: m_vsa")
cls = [x.strip() for x in minus if x.strip().startswith('"class_type"')]
chk(cls == ['"class_type": "BlockSparseAttention",'], "the removed node's class is BlockSparseAttention (VSA off)")
for key in ('"selection": "vsa",', '"selection.keep_percent": 10,', '"start_percent": 0.2,',
            '"end_percent": 1.0,', '"min_tokens": 12288,', '"extra_tokens": 256,',
            '"sink_conditioning": "exact_kv_and_rows",', '"dense_blocks": "",', '"verbose": false'):
    chk(key in [x.strip() for x in minus], "removed VSA setting line: " + key)
chk(not [x for x in plus if "prompt" in x or "seed" in x or "steps" in x or "length" in x
          or "width" in x or "height" in x or "attention" in x],
    "no prompt / seed / steps / length / resolution / attention line is touched (one variable: VSA off)")
p("")

# ---------------- Part 2: fairness vs the rendered control ----------------
p("== Part 2: node-by-node fairness vs the RENDERED control graph (json.dumps(node, sort_keys=True))")
p("control nodes %d, arm nodes %d" % (len(rendered), len(g)))
chk(set(g) == set(rendered) - {"m_vsa"}, "arm node set == the rendered control's set minus m_vsa")
shared = sorted(set(g) & set(rendered))
diff_nodes = [n for n in shared if canon(g[n]) != canon(rendered[n])]
p("shared nodes %d; differing: %s" % (len(shared), json.dumps(sorted(diff_nodes))))
chk(sorted(diff_nodes) == ["m_shift", "save"], "differing nodes are exactly ['m_shift','save'] (%d/%d byte-identical)"
  % (len(shared) - len(diff_nodes), len(shared)))
chk(gget(g, "m_shift", "inputs", "model") == ["m_attn", 0], 'arm m_shift.inputs.model == ["m_attn", 0]')
chk(gget(rendered, "m_shift", "inputs", "model") == ["m_vsa", 0],
    "control m_shift.inputs.model == ['m_vsa', 0] (the VSA node the arm deletes)")
chk(canon(gget(g, "m_attn")) == canon(gget(rendered, "m_attn")),
    "m_attn byte-identical to the control, so the model chain becomes unet -> m_attn -> m_shift (dense)")
chk(canon(gget(g, "c0")) == canon(gget(rendered, "c0")) and canon(gget(g, "c1")) == canon(gget(rendered, "c1")),
    "c0/c1 byte-identical to the control: prompts are the CONTROL's (this is a settings arm, not a prompt arm)")
chk(sha(gget(g, "c0", "inputs", "prompt").encode("utf-8"))
    == "7b4b22bb170fbcb85dce706ef746a862d49fa14142c1a704a672d4819b77f889",
    "c0 prompt sha256 == the control/RS-series value 7b4b22bb170f... (unchanged)")
chk(sha(gget(g, "c1", "inputs", "prompt").encode("utf-8"))
    == "6686d7057ead8ac945bff9263858afee0d3881b119502d7d13ab63f69d86f013",
    "c1 prompt sha256 == the control value 6686d7057ead... (unchanged)")
chk(gget(g, "noise", "inputs", "noise_seed") == gget(rendered, "noise", "inputs", "noise_seed") == 51080000,
    "seed 51080000 == the control's")
chk(gget(g, "c0", "inputs", "length") + gget(g, "win1", "inputs", "extension_frames") == 481,
    "length 243 + extension 238 = 481 frames")
chk(gget(g, "c0", "inputs", "width") == 768 and gget(g, "c0", "inputs", "height") == 1344
    and gget(g, "mkvid", "inputs", "fps") == 24, "768x1344 @ 24 fps (the ffprobe gate of the check)")
chk(gget(g, "save", "inputs", "filename_prefix") == "community/%s/%s" % (NAME, NAME),
    "filename_prefix routes output to community/" + NAME)
sys.path.insert(0, C + "/scripts")
from comm import guard_ok
for n in sorted(g):
    pv = gget(g, n, "inputs", "prompt")
    if isinstance(pv, str):
        chk(guard_ok(pv), "comm.guard_ok passes on %s.prompt (adults-only guard, the harness's own call)" % n)
classes = sorted(set(g[n]["class_type"] for n in g))
rclasses = sorted(set(rendered[n]["class_type"] for n in rendered))
chk(set(classes) <= set(rclasses), "every class in the arm also appears in the OK-RENDERED control graph"
    " (the strongest non-GPU evidence of listability: the harness static node-list check at 127.0.0.1:10004")
p("       is a GPU call and is off-limits to Forge). arm classes: %s" % json.dumps(classes))
p("       control-only class removed: %s" % json.dumps(sorted(set(rclasses) - set(classes))))
p("")

# ---------------- Part 3: the live harness gates ----------------
p("== Part 3: the live gates, parsed out of ralph.ps1 (a hardcoded copy of a regex proves nothing)")
ps1 = open(RC + "/ralph.ps1", "rb").read().decode("utf-8", "replace")
plines = ps1.splitlines()
idpats = []
for ln in plines:
    if "-notmatch" in ln:
        for m in re.finditer(r"-notmatch\s+'([^']*)'", ln):
            pt = m.group(1)
            if "ali147" in pt:
                idpats.append(pt)
chk(len(idpats) >= 2, "found the two live p7 id gates in ralph.ps1: %d" % len(idpats))
for pt in idpats:
    chk(bool(re.search(pt, NAME)), "id %s passes %s" % (NAME, pt))
kindpat = [pt for pt in re.findall(r"-notmatch\s+'([^']*)'", ps1) if "graph" in pt and "dip" in pt]
for pt in kindpat:
    line = json.dumps({"id": NAME, "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": MINUTES})
    chk(bool(re.search(pt, line)), "kind=graph gate accepts this job line: " + pt)
p("id/kind gates found: %s" % json.dumps(idpats + kindpat))
p("ralph.ps1 graph-branch gates (live lines):")
for ln in plines:
    if "request.api.json" in ln or "already exists (arm already rendered)" in ln or "id already used" in ln:
        p("  " + ln.strip())
chk(os.path.exists(DST), "graph gate (ralph.ps1:268) passes: %s exists" % DST)
chk(not os.path.exists(ARM + "/" + NAME + ".mp4"), "graph gate (ralph.ps1:269) passes: no %s.mp4 (not already rendered)" % NAME)
for f in (C + "/p7/jobs/" + NAME + ".result.json", C + "/p7/jobs/" + NAME + ".out",
          C + "/p7/jobs/" + NAME + ".err.out", ARM + "/status.log", ARM + "/objective.json",
          ARM + "/" + NAME + ".api.json", ARM + "/" + NAME + ".mp4.json",
          ARM + "/PROOF.md", C + "/p7/jobs/" + NAME + ".result.json.failed-20261022"):
    chk(not os.path.exists(f), "absent, so the id is free (ralph.ps1:185 'id already used' gate clear): " + f)
p("arm dir contents:")
for n in sorted(os.listdir(ARM)):
    p("  %10d  %s" % (os.path.getsize(os.path.join(ARM, n)), n))
chk(sorted(os.listdir(ARM)) == ["graph_diff.txt", "request.api.json"],
    "arm dir holds only the two Forge-writable names this task allows")
p("p7/JOB_REQUEST.json present before writing: %s (a Request file is CONSUMED at exit -> p7/jobs/request_iter<NN>.json)"
  % os.path.exists(REQ))
p("")
p("== budget (live ralph-community/logs/p7_budget.json; ralph.ps1:187-188)")
bj = json.loads(open(RC + "/logs/p7_budget.json", "rb").read().decode("utf-8"))
p("p7_budget.json " + json.dumps(bj))
chk(isinstance(bj.get("used_min"), (int, float)) and isinstance(bj.get("cap_min"), (int, float))
    and bj["used_min"] < bj["cap_min"], "used_min %s < cap_min %s" % (bj.get("used_min"), bj.get("cap_min")))
chk(isinstance(bj.get("jobs"), int) and isinstance(bj.get("job_cap"), int) and bj["jobs"] < bj["job_cap"],
    "jobs %s < job_cap %s" % (bj.get("jobs"), bj.get("job_cap")))
p("NOTE: the live gates (ralph.ps1:187-188) test used_min >= cap_min and jobs >= job_cap only; the job's")
p("own 'minutes' is NOT part of the budget gate. ralph.ps1:270-271 clamps minutes to 30..180 and passes")
p("--timeout minutes*20 (per attempt) --max-redo 2. This arm requests minutes=%d = a %d s per-attempt cap:"
  % (MINUTES, MINUTES * 20))
p("the control (VSA ON) rendered 481 frames in 809.7 s, and the whole point of this arm is VSA OFF, i.e.")
p("full dense attention, so a slowdown is expected; 60 min (a 1200 s cap, exactly the control's time + 47%)")
p("would risk a per-attempt timeout, so %d min is requested for headroom. A longer render is not a failure" % MINUTES)
p("(the FIX4 arm's minutes:180 request rendered 50.1 min); it is reported as the measured slowdown.")
p("")
p("== render-seconds baseline, quoted live from the control's own status.log")
sl = open(CTRL + "/status.log", encoding="utf-8", errors="replace").read().splitlines()
for ln in sl:
    if ln.startswith("JOB start") or ln.startswith("JOB end") or "secs=" in ln:
        p("  control status.log: " + ln)
p("the compare table (this arm's render seconds vs 809.7 s) is produced in the NEXT iteration from")
p("runs/%s/status.log + objective.json, once the harness has run the job." % NAME)
p("")
p("== sbs / fixed-frame stills are Max's (the TASKS sbs rule)")
sbs = []
for root, _d, fn in os.walk(C + "/runs"):
    for f in fn:
        if f.startswith("sbs_"):
            sbs.append(os.path.relpath(os.path.join(root, f), C + "/runs").replace(os.sep, "/"))
p("find runs -name 'sbs_*' = %d file(s): %s" % (len(sbs), json.dumps(sorted(sbs))))
p("expected at verify: sbs_ctrl_dense.mp4 (hstack CTRL|SETTINGS_DENSE) and the fixed-frame stills are")
p("Max/harness files: run_graph_job.py has NO hstack path and its contact sheet samples only the")
p("+-1.5 s windows around 0:10-0:50 (frames 204-276, 444/456/468/480), never frame 0. Per the TASKS")
p("sbs rule: write 'sbs/stills pending Max' and tick on the objective checks, never block on it.")
p("")
p("== If ComfyUI OOMs (the TASKS escape hatch 'If ComfyUI OOMs: [!] PV2-3 dense OOM, no redo with other settings')")
p("OOM would show up as result.json ok=false / status.log 'CUDA out of memory' / err.out. That is a")
p("[!] + BLOCKED + STOP_RALPH at verify time, and no re-request with other settings. Not predictable")
p("without the GPU, so nothing to check here; the dense chain removes work (no BlockSparseAttention node),")
p("but it makes the attention itself dense over the full token count, which is the memory/driver risk.")
p("")

# ---------------- Part 4: write the request ----------------
p("== Part 4: writing p7/JOB_REQUEST.json (one job; the accepted byte shape)")
chk(not os.path.exists(REQ), "JOB_REQUEST.json is absent before writing")
model = open(MODEL, encoding="utf-8").read()
old_id = json.loads(model)["jobs"][0]["id"]
chk(model.count(old_id) == 1, "the accepted 481-frame request (request_iter10.json, ran ok) names its id once: " + old_id)
job = {"id": NAME, "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": MINUTES}
text = json.dumps({"jobs": [job]}) + "\n"
chk(text == model.replace(old_id, NAME).replace('"minutes": 60', '"minutes": %d' % MINUTES),
    "the bytes are the accepted request with only the id and minutes changed")
chk(text.endswith("}\n") and "\r" not in text and text.count("\n") == 1, "one line, LF, exactly one trailing newline")
with open(REQ, "wb") as f:
    f.write(text.encode("utf-8"))
rb = open(REQ, "rb").read()
p("wrote " + REQ + " bytes %d sha256 %s" % (len(rb), sha(rb)))
p("bytes " + repr(rb))
chk(rb == text.encode("utf-8"), "file bytes == the intended bytes (the write tool drops the trailing newline, so this is a script write)")
j = json.loads(rb.decode("utf-8"))
chk(list(j) == ["jobs"] and len(j["jobs"]) == 1, "exactly one job, top key 'jobs' only")
chk(list(j["jobs"][0]) == ["id", "kind", "frames", "frames_tol", "minutes"],
    "job key order matches the accepted request (id, kind, frames, frames_tol, minutes)")
chk(j["jobs"][0]["id"] == NAME and j["jobs"][0]["kind"] == "graph" and j["jobs"][0]["frames"] == 481
    and j["jobs"][0]["frames_tol"] == 0, "job = id %s, kind=graph, frames=481/0 (the c0+win1 sum), minutes=%d" % (NAME, MINUTES))
chk(gget(j, "jobs") is not None and len(j["jobs"]) == 1, "one job per request (PROMPT.md)")
p("")
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
p("")
p("NEXT ITERATION (verify): result.json ok + status.log 'JOB end ... ok secs=' + greps of")
p("'JOB error|CLIP_SKIP|clip_skip|error|SKIP|redo|STUCK|STATIC_FAIL|COMFY_DOWN|out of memory' = none,")
p("plain cmp request.api.json %s.api.json (no output = the graph that rendered is mine), ffprobe" % NAME)
p("-count_packets 481 + 768x1344 + 24/1 + audio stream, certutil sha256 of the mp4 and contact sheet,")
p("render seconds vs the control's 809.7 s (the slowdown report), sbs/stills pending Max.")
p("The PV2-3 line keeps '- [ ]' through this request iteration (PROMPT.md: Forge may only REQUEST).")
open(RPT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("REPORT " + RPT)
