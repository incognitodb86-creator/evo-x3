# ALI-147 PV2-6 report probe 4 (READ-ONLY): repo commits for the model chain / VSA path. No GPU, no render.
import os, subprocess, datetime

NOTES = r"C:/AI/community/notes"
OUT = os.path.join(NOTES, "ali147-pv26-commits-20261023.txt")
REPOS = [
    ("ComfyUI core (comfy_extras/nodes_sparse_attention.py = BlockSparseAttention)", r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"),
    ("ComfyUI_MiniMax_H3_Extender (MiniMaxH3* built-ins)", r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes/ComfyUI_MiniMax_H3_Extender"),
]
VSAFILE = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/comfy_extras/nodes_sparse_attention.py"
L = []
L.append("ALI-147 PV2-6 commits probe - %s  READ-ONLY" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return (r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip())


for tag, repo in REPOS:
    L.append("\n== %s\n   dir %s exists=%s" % (tag, repo, os.path.isdir(repo)))
    if not os.path.isdir(repo):
        continue
    for args in (["git", "rev-parse", "HEAD"], ["git", "rev-parse", "--short", "HEAD"],
                 ["git", "status", "--porcelain"], ["git", "log", "-1", "--format=%H %ad %s", "--date=iso"]):
        rc, so, se = run(args, cwd=repo)
        L.append("   %s -> rc=%d %s %s" % (" ".join(args), rc, so.replace("\n", " | ")[:400], se.strip()[:120]))
L.append("\n== the VSA node file (ComfyUI core, not the Extender)")
L.append("   %s exists=%s size=%s" % (VSAFILE, os.path.exists(VSAFILE), os.path.getsize(VSAFILE) if os.path.exists(VSAFILE) else "-"))
if os.path.exists(VSAFILE):
    import hashlib
    L.append("   sha256 %s" % hashlib.sha256(open(VSAFILE, "rb").read()).hexdigest())
    L.append("   last-modified mtime %s" % datetime.datetime.fromtimestamp(os.path.getmtime(VSAFILE)).isoformat())
    txt = open(VSAFILE, encoding="utf-8", errors="replace").read().splitlines()
    for i, line in enumerate(txt, 1):
        if "class BlockSparseAttention" in line or "NODE_CLASS_MAPPINGS" in line and "BlockSparse" in line:
            L.append("   %s:%d| %s" % (os.path.basename(VSAFILE), i, line.strip()))
rc, so, se = run(["git", "-C", r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI", "log", "-1", "--format=%H", "--", "comfy_extras/nodes_sparse_attention.py"])
L.append("\n   last commit touching nodes_sparse_attention.py -> rc=%d %s %s" % (rc, so, se.strip()[:120]))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("wrote %s  %d B" % (OUT, os.path.getsize(OUT)))
