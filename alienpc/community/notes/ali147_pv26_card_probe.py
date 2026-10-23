# ALI-147 PV2-6 report probe 2 (READ-ONLY): the PV2-4 (K1) and PV2-5 (KV31) gates. No GPU, no node list,
# no render, no job request, no download/install/delete, no image viewing. Writes ONLY C:/AI/community/notes/.
import os, sys, json, hashlib, subprocess, re, datetime

NOTES = r"C:/AI/community/notes"
OUT = os.path.join(NOTES, "ali147-pv26-card-probe-20261023.txt")
RUNS = r"C:/AI/community/runs"
SPEC = r"C:/Users/derek/5slock/ralph-community/specs/ali147.md"
TASKS = r"C:/Users/derek/5slock/ralph-community/TASKS.md"
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"

L = []
F = 0
P = 0


def p(s):
    L.append(s)


def ck(cond, label):
    global F, P
    if cond:
        P += 1
        p("PASS  " + label)
    else:
        F += 1
        p("FAIL  " + label)
    return bool(cond)


def raw(path):
    with open(path, "rb") as f:
        return f.read()


def sha(path):
    return hashlib.sha256(raw(path)).hexdigest()


def find(root, needle):
    hits = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "node_modules", "__pycache__", "cache", "custom_nodes")]
        for f in fn:
            if needle in (dp + "/" + f).lower():
                hits.append((os.path.join(dp, f), os.path.getsize(os.path.join(dp, f))))
        if len(hits) > 40:
            break
    return hits


p("ALI-147 PV2-6 report probe 2 (K1 / KV31 gates) - %s  READ-ONLY" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

p("\n== the K1 card (PV2-4 gate C)")
K1 = [os.path.join(COMFY, "models", "loras", "h3", "Vagina_minimax-h3_epoch20.safetensors"),
      os.path.join(COMFY, "models", "loras", "Vagina_minimax-h3_epoch20.safetensors")]
for kp in K1:
    p("  %s exists=%s" % (kp, os.path.exists(kp)))
ck(not any(os.path.exists(k) for k in K1), "no h3\\Vagina_minimax-h3_epoch20.safetensors in the runtime loras tree = PV2-4 gate C is not met")
p("  %s\\models\\loras listing: %s" % (COMFY, sorted(os.listdir(os.path.join(COMFY, "models", "loras")))))
p("  'vagina' name search under models\\loras: %s" % find(os.path.join(COMFY, "models", "loras"), "vagina"))
p("  'snofs' name search under models\\loras: %s" % find(os.path.join(COMFY, "models", "loras"), "snofs"))
p("  'snofs' name search under ComfyUI\\input: %s" % find(os.path.join(COMFY, "input"), "snofs"))

p("\n== the SNOFS reference image named by PV2-4/PV2-5 (looked for by NAME, no download)")
for root in [r"C:/Users/derek/5slock/approved_characters", r"C:/Users/derek/5slock/plans"]:
    p("  'sno' name search under %s: %s" % (root, find(root, "sno")))
p("  b3_p04 reference-image candidates in approved_characters\\REF_SHEETS_2026-10-19: %s" %
  sorted(os.listdir(r"C:/Users/derek/5slock/approved_characters/REF_SHEETS_2026-10-19")))
p("  approved_characters\\POOL: %s" % sorted(os.listdir(r"C:/Users/derek/5slock/approved_characters/POOL")))

p("\n== the KV31 card (PV2-5 gate C)")
KV = r"C:/Users/derek/cufy/gemma4-3b-export/cards/qwen-image-2-9b/kv31_inference_master.safetensors"
KVDIR = os.path.dirname(KV)
p("  path %s exists=%s" % (KV, os.path.exists(KV)))
if os.path.isdir(KVDIR):
    p("  directory listing: %s" % sorted(os.listdir(KVDIR)))
p("  'kv31' name search under C:/Users/derek/cufy: %s" % find(r"C:/Users/derek/cufy", "kv31"))
p("  'inference_master' search under cufy: %s" % find(r"C:/Users/derek/cufy", "inference_master"))

p("\n== PV2-5 prompt file (the Klein prompt named by the spec/TASKS)")
for nm in ["stillfix_A_anatomy_ref_klein", "stillfix_B_matte_skin_klein", "v2_rs016_c1_r2v", "v2_seg1_c1_r2v_fix1"]:
    fp = r"C:/AI/community/specs/prompt_v2/%s.txt" % nm
    p("  %s.txt exists=%s" % (nm, os.path.exists(fp)))
p("  specs\\prompt_v2 listing: %s" % sorted(os.listdir(r"C:/AI/community/specs/prompt_v2")))

p("\n== PV2-4 / PV2-5 spec text (specs\\ali147.md, the K1 and KV31 arms)")
spec = raw(SPEC).decode("utf-8", "replace")
for i, line in enumerate(spec.splitlines(), 1):
    if "PV2-4" in line or "PV2-5" in line or "K1" in line or "KV31" in line:
        p("  spec:%d| %s" % (i, line.strip()))

p("\n== budget gate for any further GPU job (ralph.ps1 reads this file)")
b = json.loads(raw(BUDGET).decode("utf-8"))
p("  p7_budget.json %s" % json.dumps(b, sort_keys=True))
p("  remaining minutes = %.1f of cap %d ; jobs %d of job_cap %d" % (b["cap_min"] - b["used_min"], b["cap_min"], b["jobs"], b["job_cap"]))
p("  PV2-4/PV2-5 estimated GPU cost = a Klein 9B bf16 image render (the spec/TASKS estimate 30-40 min wall, NOT a 60 min video)")
ck(b["cap_min"] - b["used_min"] < 30, "remaining budget minutes (%.1f) < the PV2-5 KV31 render estimate (30-40 min) = the budget gate would refuse it in this run" % (b["cap_min"] - b["used_min"]))
ck(b["jobs"] < b["job_cap"], "job_cap has %d slot(s) left (so the minutes, not the job count, is the binding gate)" % (b["job_cap"] - b["jobs"]))

p("\n== the PV2-4/PV2-5 lines as written in TASKS.md (the gate the line itself imposes)")
for i, line in enumerate(raw(TASKS).decode("utf-8", "replace").splitlines(), 1):
    if line.strip().startswith("- [ ] PV2-4") or line.strip().startswith("- [ ] PV2-5"):
        p("  TASKS:%d| %s" % (i, line.strip()[:400]))

p("\nTOTAL PASS=%d FAIL=%d" % (P, F))
p("ALL CHECKS PASS" if F == 0 else "FAILURES PRESENT: %d" % F)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("wrote %s  %d B  PASS=%d FAIL=%d" % (OUT, os.path.getsize(OUT), P, F))
