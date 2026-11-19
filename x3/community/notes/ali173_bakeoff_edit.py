# Max 2026-10-23: Derrick 1:07 PM CT "Yes, add 120 GPU min and 10 jobs for the bakeoff and let Forge restart and call ComfyUI itself".
# Edits ralph.ps1, PROMPT.md, TASKS.md (ralph-community) and 5slock\AGENTS.md in place. Backups first (*.bak-20261023-bakeoff in C:\AI\community\notes).
import shutil, sys, os
K = r"C:\Users\derek\5slock\ralph-community"; B = r"C:\AI\community\notes"; A = r"C:\Users\derek\5slock\AGENTS.md"
FILES = {"ralph.ps1": rf"{K}\ralph.ps1", "PROMPT.md": rf"{K}\PROMPT.md", "TASKS.md": rf"{K}\TASKS.md", "AGENTS_5slock.md": A}
if len(sys.argv) > 1: K, B, A = sys.argv[1], sys.argv[2], sys.argv[3]; FILES = {"ralph.ps1": f"{K}/ralph.ps1", "PROMPT.md": f"{K}/PROMPT.md", "TASKS.md": f"{K}/TASKS.md", "AGENTS_5slock.md": A}
for n, p in FILES.items():
    bak = os.path.join(B, n + ".bak-20261023-bakeoff")
    if os.path.exists(bak): sys.exit("backup exists: " + bak)
    shutil.copy2(p, bak)
def load(p):
    b = open(p, "rb").read(); bom = b.startswith(b"\xef\xbb\xbf"); s = b.decode("utf-8-sig"); crlf = "\r\n" in s
    return s.replace("\r\n", "\n"), bom, crlf
def save(p, s, bom, crlf):
    if crlf: s = s.replace("\n", "\r\n")
    open(p, "wb").write((b"\xef\xbb\xbf" if bom else b"") + s.encode("utf-8"))
def rep(s, a, b):
    if s.count(a) != 1: sys.exit(f"anchor count {s.count(a)}: {a[:90]}")
    return s.replace(a, b)
APPROVAL = 'Derrick 2026-10-23 1:07 PM CT "Yes, add 120 GPU min and 10 jobs for the bakeoff and let Forge restart and call ComfyUI itself"'
# ralph.ps1
p = FILES["ralph.ps1"]; s, bom, crlf = load(p)
s = rep(s, "[int]$GpuCapMin=495,[int]$JobMax=35,", "[int]$GpuCapMin=615,[int]$JobMax=45,")
s = rep(s, "'^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\\d+)$'", "'^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\\d+|ali173_[a-z0-9]+(_[a-z0-9]+)?_s\\d+)$'")
s = rep(s, "if($id -notmatch '^ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\\d+$'){ JobResult $id @{ ok = $false; note = 'refused: graph/dip ids are ali147_pool_<arm>_s<seed>' }",
           "if($id -notmatch '^(ali147_pool|ali173)_[a-z0-9]+(_[a-z0-9]+)?_s\\d+$'){ JobResult $id @{ ok = $false; note = 'refused: graph/dip ids are ali147_pool_<arm>_s<seed> or ali173_<arm>_s<seed>' }")
s = rep(s, '$Prot=@("$C\\scripts\\tests\\test_p6_review.py","$C\\scripts\\comm.py",', '$Prot=@("$C\\scripts\\tests\\test_p6_review.py","$C\\scripts\\comm.py","$C\\scripts\\comfy_ctl.py",')
i = s.index("param([int]$Max=")
s = s[:i] + ("# bakeoff 2026-10-23 (ALI-173, " + APPROVAL + "; backup C:\\AI\\community\\notes\\ralph.ps1.bak-20261023-bakeoff):\n"
             "#  - default caps 495 -> 615 GPU min, 35 -> 45 jobs (+120 min / +10 jobs for the bakeoff B1-B8; R6-R9 stay inside 495/35 per TASKS.md).\n"
             "#  - graph/dip + generic job ids may be ali173_<arm>_s<seed>; scripts\\comfy_ctl.py (Forge's ComfyUI restart helper) is harness-owned ($Prot).\n") + s[i:]
save(p, s, bom, crlf)
# PROMPT.md
p = FILES["PROMPT.md"]; s, bom, crlf = load(p)
s = rep(s, "- Never call ComfyUI, llama-swap (/upstream/*, /comfyui/, /api/*, /unload) or Strata.", "- Outside the BAKEOFF EXCEPTION below, never call ComfyUI, llama-swap (/upstream/*, /comfyui/, /api/*, /unload) or Strata.")
L = s.split("\n"); gi = [i for i, l in enumerate(L) if l.startswith("- Outside the BAKEOFF EXCEPTION below")][0]
L.insert(gi + 1, "- BAKEOFF EXCEPTION (ALI-173, " + APPROVAL + "), for the TASKS.md BAKEOFF lines only: you may call ComfyUI's HTTP API yourself (read + queue: /prompt, /queue, /history, /view, /upload/image, /system_stats, /object_info/<Node>) on 127.0.0.1:10004 (its own port under llama-swap), :8188 or :8189, and llama-swap's OpenAI-style /v1 endpoints the way pi does (model coding_swift15_iq3s only; never a vision/judge model). "
         "You start, stop and restart ComfyUI yourself, including after installing custom nodes, ONLY with: python C:\\AI\\community\\scripts\\comfy_ctl.py start|stop|restart|status. "
         "GPU LOCK RULE: never stop or restart ComfyUI while a render job is running (check comfy_ctl.py status first; comfy_ctl and the guard both refuse while gpu_guard says BUSY). "
         "COMFY_OK CHECK: after EVERY start/restart run comfy_ctl.py status and continue only if it shows comfy_ok=True; otherwise mark the line [!] COMFY_DOWN + STOP_RALPH. "
         "ComfyUI and your own model share the GPU (llama-swap exclusive group), so do wake + queue + wait + fetch in ONE script call; your next model turn swaps ComfyUI out (after its queue drains). "
         "Still blocked: /upstream/*, /unload, /api/* on :8080, /interrupt, /free, Strata's port, raw Stop-Process/taskkill/Start-Process. Log every direct render in C:\\AI\\community\\notes\\bakeoff_gpu_ledger.md (id or prompt_id, start/end CT, minutes).")
s = "\n".join(L)
s = rep(s, "keep TASKS.md caps (35 jobs / 495 min)", "keep TASKS.md caps (harness 615 GPU min / 45 jobs since Derrick 1:07 PM CT; R6-R9 stay inside the original 495 min / 35 jobs; the extra 120 min / 10 jobs are the ALI-173 bakeoff's)")
save(p, s, bom, crlf)
# TASKS.md
p = FILES["TASKS.md"]; s, bom, crlf = load(p)
s = rep(s, "The harness caps are -GpuCapMin 495 -JobMax 35 (Derrick 10:29 AM CT)", "The harness caps are -GpuCapMin 615 -JobMax 45 (Derrick 1:07 PM CT; were 495/35 from 10:29 AM CT). This batch (R-lines R6-R9) still stops at the ORIGINAL 495 min / 35 jobs below; the extra 120 min / 10 jobs are only for the ALI-173 BAKEOFF (B1-B8)")
s = rep(s, "the live harness caps are -JobMax 35 and -GpuCapMin 495 min, so the job cap is 35 (the lines above now say 35); the 475-min request gate is unchanged.",
           "the R-line caps are 35 jobs / 495 min (the gates above; the 475-min request gate is unchanged). Since Derrick 1:07 PM CT the harness runs -GpuCapMin 615 -JobMax 45: the extra 120 min / 10 jobs belong to the ALI-173 BAKEOFF only.")
s = rep(s, "GPU rule unchanged: you never call ComfyUI/llama-swap yourself; every render goes through C:\\AI\\community\\p7\\JOB_REQUEST.json, and anything that must drive ComfyUI or llama-swap directly is a [!] Max line with the exact command (Max runs it under the GPU lock and budget). A ComfyUI restart to load a new node is a [!] Max line too.",
           "GPU (" + APPROVAL + "): you run all of it yourself under PROMPT.md's BAKEOFF EXCEPTION - ComfyUI API on :10004/:8188/:8189 (read + queue), llama-swap /v1, and python C:\\AI\\community\\scripts\\comfy_ctl.py start|stop|restart|status (never while a render runs; comfy_ok after every restart). Harness renders may also go through C:\\AI\\community\\p7\\JOB_REQUEST.json (ids ali173_<arm>_s<seed> are allowed). "
           "BAKEOFF BUDGET: +120 GPU min / +10 jobs, harness caps 615 min / 45 jobs. Record the logs\\p7_budget.json used_min/jobs when FINAL is ticked as the bakeoff start; log every direct ComfyUI render in C:\\AI\\community\\notes\\bakeoff_gpu_ledger.md (id or prompt_id, start/end CT, minutes). Before every bakeoff render: (p7 used_min - start used_min) + ledger minutes < 120 and (p7 jobs - start jobs) + ledger renders < 10, else [!] \"BLOCKED: bakeoff budget\" + STOP_RALPH.")
s = rep(s, 'if the id is refused or the budget is short, [!] "Max: id gate / budget for <id>" + STOP_RALPH.', 'if the id is still refused or the budget is short, [!] "BLOCKED: id gate / budget for <id>" + STOP_RALPH.')
s = rep(s, "End with [!] Max: restart ComfyUI between jobs to load Continuum.", "Then restart ComfyUI yourself to load Continuum: python C:\\AI\\community\\scripts\\comfy_ctl.py restart (it refuses while a render runs: wait, then retry), then comfy_ctl.py status must show comfy_ok=True and GET http://127.0.0.1:10004/object_info/<a Continuum node class> must answer.")
s = rep(s, "It drives ComfyUI + llama-swap directly, so write the exact run command into notes and mark [!] Max: run infinite-creation scene (Max runs it under the GPU lock), then score it when the output exists.",
           "It drives ComfyUI (:10004) and llama-swap /v1 directly: run it yourself (comfy_ctl.py start + comfy_ok first; ledger the render), in one command call because a pass ends at 20 min (if it cannot finish inside one pass, write what it reached + [!] \"BLOCKED: infinite-creation run exceeds one pass\" + STOP_RALPH), then score it.")
R4H = ('- [ ] R4H SMALL PROMPT-LLM RESEARCH (Derrick 2026-10-23 1:14 PM CT "Didn\'t we also research a smaller model that goes on the GPU that\'s been fine tuned for this? Do research what does the community do"; research only, no downloads, no GPU, no vision judge). '
 'Find the community\'s small GPU-resident LLMs (about 4-14B, so they fit next to ComfyUI on 16 GB) that are fine-tuned or abliterated for writing NSFW video prompts for MiniMax-H3 Ref2VA, Wan or LTX; vision-capable models that read reference sheets are a plus. Compare against the 27B Heretic the Civitai H3 prompt writer uses (https://civitai.com/models/2967166). '
 'Sources with web GET (each with its URL): Hugging Face (model cards, /api/models?search=..., discussions), Civitai, r/StableDiffusion and r/LocalLLaMA. Also check what earlier research already found (C:\\AI\\community\\notes, the 2026-10-23 comfy auto-pipeline research summary in ALI-173). '
 'Write C:\\AI\\community\\notes\\small_prompt_llm_research_20261023.md: a table of 3-5 candidates (model, size + quant, VRAM, vision yes/no, what it was fine-tuned for, community evidence + URL) and ONE recommendation. Any download is a separate [!] line naming the file + size + URL (pause for Derrick\'s card); do not download. '
 'Check: the file exists with 3-5 rows, every row has a URL, and one recommendation line.')
L = s.split("\n")
if any(l.startswith("- [") and " R4H " in l[:12] for l in L): sys.exit("R4H already present")
g = [i for i, l in enumerate(L) if l.startswith("- [") and l[5:10] == " R4G "]
r6 = [i for i, l in enumerate(L) if l.startswith("- [") and l[5:].startswith(" R6 REDO clip 3")]
if len(g) == 1:
    at = g[0] + 1
    while at < len(L) and L[at].startswith((" ", "\t")) and not L[at].startswith("- ["): at += 1
elif len(r6) == 1: at = r6[0]
else: sys.exit("no R4G or R6 anchor")
L.insert(at, R4H); s = "\n".join(L)
save(p, s, bom, crlf)
# AGENTS.md
p = FILES["AGENTS_5slock.md"]; s, bom, crlf = load(p)
a = "- Never call llama-swap (127.0.0.1:8080), /upstream/*, /load, /unload, ComfyUI (:8188, :8189, :1000x) or Strata. One request unloads you and kills a running render."
s = rep(s, a, a + "\n- BAKEOFF exception (ALI-173, Derrick 1:07 PM CT): for BAKEOFF lines only, ComfyUI API on :10004/:8188/:8189 (read + queue), llama-swap /v1, and python C:/AI/community/scripts/comfy_ctl.py start|stop|restart|status (never during a render; comfy_ok after every restart). See PROMPT.md.")
save(p, s, bom, crlf)
print("ok")
