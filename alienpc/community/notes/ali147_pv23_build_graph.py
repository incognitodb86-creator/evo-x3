r"""PV2-3 SETTINGS_DENSE seg1 graph build (CPU only; no GPU/ComfyUI/llama-swap call, no render).

TASKS line: "Copy CTRL request.api.json to runs\ali147_pool_dense_s51080000\. Only change:
m_shift.inputs.model = ["m_attn", 0] and delete node m_vsa (VSA off = full dense attention);
prompts = CTRL; new filename_prefix."

CTRL has NO request.api.json (PV2-1 finding, AGENTS.md 2026-10-22): the driver-rendered control's
graph IS runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json, whose node bodies are
byte-identical to the rendered ali147_pool_ctrl_s51080000.api.json (verified below). So that file
is the copy source, exactly as for PV2-1. Method: RAW line-targeted edit of the CTRL bytes, so
every other byte is untouched (CRLF kept, no trailing newline - the arm request.api.json shape).

Three changes only:
  1. m_shift.inputs.model  ["m_vsa", 0]  ->  ["m_attn", 0]      (1 line)
  2. node "m_vsa" (BlockSparseAttention) deleted                  (17 lines)
  3. save.filename_prefix  -> community/ali147_pool_dense_s51080000/ali147_pool_dense_s51080000

Writes only runs/ali147_pool_dense_s51080000/request.api.json.
Run: python C:/AI/community/notes/ali147_pv23_build_graph.py
"""
import hashlib
import json
import os
import sys

C = "C:/AI/community"
SRC = C + "/runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json"
RENDERED = C + "/runs/ali147_pool_ctrl_s51080000/ali147_pool_ctrl_s51080000.api.json"
NAME = "ali147_pool_dense_s51080000"
ARM = C + "/runs/" + NAME
DST = ARM + "/request.api.json"
RPT = C + "/notes/ali147-pv23-build-20261023.txt"

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


def canon(node):
    return json.dumps(node, sort_keys=True)


def gget(g, n, *path):
    """defensive lookup: never raises, so one missing key cannot hide the rest of the report"""
    v = g.get(n, {})
    for k in path:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return v


raw_src = open(SRC, "rb").read()
text_src = raw_src.decode("utf-8")
src = json.loads(text_src)
p("PV2-3 SETTINGS_DENSE build - copy source " + SRC)
p("  source bytes %d sha256 %s CRLF-count %d tail %r"
  % (len(raw_src), sha(raw_src), raw_src.count(b"\r\n"), raw_src[-4:]))
chk(raw_src.count(b"\n") == raw_src.count(b"\r\n") and not raw_src.endswith(b"\n"),
    "source is pure CRLF with no trailing newline (the arm request.api.json shape)")

# the control the harness really rendered: node-body compare (top-level key order may differ)
rendered = json.loads(open(RENDERED, "rb").read().decode("utf-8"))
chk(sorted(rendered) == sorted(src),
    "copy source node set == the rendered CTRL .api.json node set (%d nodes)" % len(src))
bodydiff = [n for n in sorted(src) if canon(src[n]) != canon(rendered[n])]
chk(bodydiff == [], "copy source node bodies are identical to the RENDERED control graph: %s" % json.dumps(bodydiff))
p("control node order: %s" % json.dumps(list(src)))
p("control classes: %s" % json.dumps(sorted(set(src[n]["class_type"] for n in src))))

tail = "\r\n}"
chk(text_src.endswith(tail), "source tail is CRLF + '}' with no trailing newline: " + repr(text_src[-6:]))
lines = text_src[: -len(tail)].split("\r\n")

# --- locate the three targets by brace depth (robust), never by hard-coded line numbers ---
node_at = []
for i, line in enumerate(lines):
    if line.startswith(' "') and line.endswith('": {'):
        node_at.append((i, line.strip()[1:].split('"', 1)[0]))
p("node key lines: %d" % len(node_at))


def block(name):
    start = [i for i, n in node_at if n == name]
    if not start:
        return None
    i0 = start[0]
    depth = 0
    for j in range(i0, len(lines)):
        depth += lines[j].count("{") - lines[j].count("}")
        if j > i0 and depth == 0:
            return (i0, j)
    return None


def inner(name, key):
    """index of the line `   "key": ...` inside node `name`"""
    blk = block(name)
    if blk is None:
        return None
    for i in range(blk[0] + 1, blk[1]):
        if lines[i].startswith('   "%s":' % key):
            return i
    return None


vsa = block("m_vsa")
shift_model = inner("m_shift", "model")
prefix_line = inner("save", "filename_prefix")
p("m_vsa block (body indices, inclusive): %s" % json.dumps(vsa))
p("m_shift.model line index: %s ; save.filename_prefix line index: %s" % (shift_model, prefix_line))
p("  lines: %r %r" % (lines[shift_model], lines[shift_model + 1]))
p("  line : %r" % lines[prefix_line])
chk(vsa is not None and lines[vsa[0]] == ' "m_vsa": {' and lines[vsa[1]].strip() == "},"
    and src["m_vsa"]["class_type"] == "BlockSparseAttention",
    "m_vsa node block located and brace-balanced (%d lines, class BlockSparseAttention)"
    % (vsa[1] - vsa[0] + 1))
nxt = [n for i, n in node_at if i == vsa[1] + 1]
expected_next = list(src)[list(src).index("m_vsa") + 1]
chk(nxt == [expected_next],
    "the line after the block is the next node key (%s), so the deletion is exactly the node block"
    % json.dumps(nxt))
chk(lines[shift_model].strip() == '"model": [' and lines[shift_model + 1].strip() == '"m_vsa",',
    "m_shift.inputs.model is the link to m_vsa: %r / %r" % (lines[shift_model], lines[shift_model + 1]))
chk(lines[prefix_line].strip().startswith('"filename_prefix": "community/ali147_pool_ctrl_s51080000/'),
    "the prefix line is the control's: " + repr(lines[prefix_line]))

# --- the raw edit: replace lines first (indices unchanged), delete last ---
out = list(lines)
out[shift_model + 1] = lines[shift_model + 1].replace('"m_vsa",', '"m_attn",')
prefix = "community/%s/%s" % (NAME, NAME)
indent = lines[prefix_line][: len(lines[prefix_line]) - len(lines[prefix_line].lstrip())]
comma = "," if lines[prefix_line].rstrip().endswith(",") else ""
out[prefix_line] = '%s"filename_prefix": %s%s' % (indent, json.dumps(prefix, ensure_ascii=True), comma)
del out[vsa[0]: vsa[1] + 1]

new_text = "\r\n".join(out) + tail
os.makedirs(ARM, exist_ok=True)
with open(DST, "wb") as f:
    f.write(new_text.encode("utf-8"))

# --- self-checks on the file just written ---
raw = open(DST, "rb").read()
g = json.loads(raw.decode("utf-8"))
p("")
p("WROTE " + DST)
p("  bytes %d sha256 %s (source %d, delta %+d)" % (len(raw), sha(raw), len(raw_src), len(raw) - len(raw_src)))
chk(raw == new_text.encode("utf-8"), "file bytes == the intended bytes (UTF-8)")
chk(raw.count(b"\n") == raw.count(b"\r\n") and not raw.endswith(b"\n"),
    "pure CRLF, no trailing newline (the shape of every arm request.api.json that rendered)")
chk(new_text.replace("\r\n", "\n") == json.dumps(g, indent=1, ensure_ascii=True),
    "text is canonical json.dumps(indent=1, ensure_ascii=True)")
chk(list(g) == [n for n in src if n != "m_vsa"],
    "node key ORDER == the control's order minus m_vsa (%d nodes)" % len(g))
chk(set(g) == set(src) - {"m_vsa"}, "node set == control set minus m_vsa")
chk("m_vsa" not in raw.decode("utf-8"), "the string 'm_vsa' appears nowhere in the new graph")
chk(sorted(set(g[n]["class_type"] for n in g)) == sorted(set(src[n]["class_type"] for n in src) - {"BlockSparseAttention"}),
    "classes == the control's classes minus BlockSparseAttention (NO new node class is introduced)")
p("       the harness static node-list check at render time can only get safer: every remaining class")
p("       appears in the already-rendered control graph runs/ali147_pool_ctrl_s51080000/"
  + "ali147_pool_ctrl_s51080000.api.json (its result.json is ok=true).")
p("new classes: %s" % json.dumps(sorted(set(g[n]["class_type"] for n in g))))

diff = [n for n in g if canon(g[n]) != canon(src[n])]
p("differing_nodes vs the control: %s" % json.dumps(sorted(diff)))
chk(sorted(diff) == ["m_shift", "save"], "differing nodes are exactly ['m_shift','save']")
ident = [n for n in g if canon(g[n]) == canon(src[n])]
chk(len(ident) == len(g) - 2, "%d/%d nodes byte-identical to the control (all of them but m_shift and save)"
  % (len(ident), len(g)))
mkeys = [k for k in g["m_shift"]["inputs"] if canon(g["m_shift"]["inputs"][k]) != canon(src["m_shift"]["inputs"][k])]
chk(mkeys == ["model"], "m_shift: only inputs.model differs (%s)" % json.dumps(mkeys))
chk(gget(g, "m_shift", "inputs", "model") == ["m_attn", 0], 'm_shift.inputs.model == ["m_attn", 0]')
chk(gget(g, "m_shift", "class_type") == "MiniMaxH3SigmaShift"
    and gget(g, "m_shift", "inputs", "shift_video") == gget(src, "m_shift", "inputs", "shift_video") == 10.0
    and gget(g, "m_shift", "inputs", "shift_audio") == gget(src, "m_shift", "inputs", "shift_audio") == 3.0,
    "m_shift class and shift_video 10.0 / shift_audio 3.0 unchanged")
chk(canon(gget(g, "m_attn")) == canon(gget(src, "m_attn")), "m_attn node untouched (the new direct source of m_shift)")
chk(gget(g, "m_attn", "class_type") == "ModelAttentionBackend"
    and gget(g, "m_attn", "inputs", "attention") == "comfy kitchen attention"
    and gget(g, "m_attn", "inputs", "model") == ["unet", 0],
    "m_attn stays ModelAttentionBackend attention='comfy kitchen attention' model=['unet',0] (live values, not a guess)")
chk(gget(g, "unet") == gget(src, "unet") and gget(g, "vvae") == gget(src, "vvae")
    and gget(g, "avae") == gget(src, "avae") and gget(g, "clip") == gget(src, "clip"),
    "model-chain loaders (unet/vvae/avae/clip) byte-identical to the control - the ONLY change is VSA off")
chk(gget(g, "save", "class_type") == gget(src, "save", "class_type"), "save class unchanged (SaveVideo)")
chk(gget(g, "save", "inputs", "filename_prefix") == prefix, "save.filename_prefix == " + prefix)
skeys = [k for k in g["save"]["inputs"] if canon(g["save"]["inputs"][k]) != canon(src["save"]["inputs"][k])]
chk(skeys == ["filename_prefix"], "save: only inputs.filename_prefix differs (%s)" % json.dumps(skeys))
chk(gget(g, "save", "inputs", "codec") == gget(src, "save", "inputs", "codec")
    and gget(g, "save", "inputs", "format") == gget(src, "save", "inputs", "format")
    and gget(g, "save", "inputs", "video") == gget(src, "save", "inputs", "video"),
    "save codec/format/video unchanged")

# settings that must stay at the control's values (one variable: VSA off)
chk(gget(g, "noise", "inputs", "noise_seed") == gget(src, "noise", "inputs", "noise_seed") == 51080000,
    "seed stays 51080000 (RandomNoise, untouched)")
chk(gget(g, "c0", "inputs", "length") == 243 and gget(g, "c0", "inputs", "width") == 768
    and gget(g, "c0", "inputs", "height") == 1344,
    "c0 length 243 / 768x1344 unchanged (%s)" % gget(g, "c0", "class_type"))
chk(gget(g, "mkvid", "inputs", "fps") == 24, "mkvid fps stays 24 (CreateVideo)")
chk(gget(g, "c0", "inputs", "length") + gget(g, "win1", "inputs", "extension_frames") == 481,
    "c0.length 243 + win1.extension_frames %s = 481 frames (the frames=481 / frames_tol=0 request)"
    % gget(g, "win1", "inputs", "extension_frames"))
scheds = [n for n in g if g[n]["class_type"] == "BasicScheduler"]
chk(sorted([gget(g, n, "inputs", "steps") for n in scheds]) == sorted([gget(src, n, "inputs", "steps") for n in scheds])
    and len(scheds) == 2, "both BasicScheduler steps values unchanged from the control (%s)" % json.dumps(scheds))
chk(gget(g, "ksel") == gget(src, "ksel"), "sampler selection (ksel) unchanged")
prompts = [n for n in sorted(g) if isinstance(gget(g, n, "inputs", "prompt"), str)]
chk(prompts == [n for n in sorted(src) if isinstance(gget(src, n, "inputs", "prompt"), str)],
    "same prompt-bearing nodes as the control: %s" % json.dumps(prompts))
for n in prompts:
    pv = gget(g, n, "inputs", "prompt")
    chk(pv == gget(src, n, "inputs", "prompt"),
        "%s.prompt == the control prompt verbatim (%d chars, sha256 %s)" % (n, len(pv), sha(pv.encode("utf-8"))))
sys.path.insert(0, C + "/scripts")
from comm import guard_ok
for n in prompts:
    chk(guard_ok(gget(g, n, "inputs", "prompt")), "comm.guard_ok passes on %s.prompt (adults-only guard)" % n)
chk(gget(g, "img") == gget(src, "img"), "the LoadImage node is byte-identical to the control")
for n in sorted(g):
    if g[n]["class_type"] == "LoadImage":
        s = gget(g, n, "inputs", "image")
        cand = os.path.join("C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input", s.replace("/", os.sep))
        chk(os.path.isfile(cand), "%s image %r resolves inside ComfyUI\\input" % (n, s))
        if os.path.isfile(cand):
            b = open(cand, "rb").read()
            chk(len(sha(b)) == 64, "%s still sha256 is a full 64 chars: %s" % (n, sha(b)))
chk(all(gget(g, n) == gget(src, n) for n in ("c0", "c1", "tail1", "win1", "app1", "dec_v", "dec_v", "dec_a",
                                             "s0_guide", "s0_samp", "s0_sched", "s1_guide", "s1_samp", "s1_sched")),
    "every conditioning / sampling / decode node is byte-identical to the control")

p("")
p("NEXT: notes/ali147_pv23_diffcheck.py parses runs/%s/graph_diff.txt (git diff --no-index vs the copy" % NAME)
p("source) and requires the hunks to be exactly m_shift.model, the m_vsa removal, filename_prefix.")
p("The render (status.log JOB end ok, ffprobe 481/768x1344/24/audio, sha256, render seconds vs CTRL 809.7,")
p("sbs_ctrl_dense.mp4) is verified in the NEXT iteration - Forge may only REQUEST. sbs/fixed-frame stills")
p("are Max's files (run_graph_job.py has no hstack path). This line keeps '- [ ]'.")
open(RPT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
print("REPORT " + RPT)
