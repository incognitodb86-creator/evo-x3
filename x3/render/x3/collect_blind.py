import json, random, sys, os, subprocess, secrets
from pathlib import Path
SRC = Path(sys.argv[1]); OUT = Path("/workspace/maxops/prompts/heretic-q8-vs-q4-blind-20261115"); OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(secrets.randbits(64))
timing = {l.split("\t")[0] + "_" + l.split("\t")[1]: l.strip().split("\t") for l in (SRC / "timing_raw.tsv").read_text().splitlines() if l.strip()}
asks = {1: "she has sex with him / missionary / POOL_F034", 2: "she has sex with him / doggy / POOL_F053", 3: "she gives him a blowjob / blowjob / POOL_F058"}
key = ["# KEY (do not open before scoring). Max Architect 2026-11-15, randomized per ask.", ""]
rows = []
def pi_usage(p):
    i = o = c = 0; n = 0
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try: e = json.loads(line)
        except Exception: continue
        if e.get("type") == "message_end" and isinstance(e.get("message"), dict) and e["message"].get("role") == "assistant":
            u = e["message"].get("usage") or {}; i += u.get("input", 0); o += u.get("output", 0); c += u.get("cacheRead", 0); n += 1
    return i, o, c, n
for a in (1, 2, 3):
    arms = ["q8", "q4km"]; rng.shuffle(arms)
    for label, arm in zip("AB", arms):
        rd = SRC / "runs" / f"{arm}_ask{a}"
        pick = json.loads((rd / "pick.json").read_text())
        status = pick.get("status")
        prompt = rd / "prompt.txt"
        body = prompt.read_text(encoding="utf-8") if prompt.exists() else f"(no prompt.txt: {status})\n"
        (OUT / f"ask{a}_{label}.txt").write_text(body, encoding="utf-8")
        key.append(f"ask{a}_{label}.txt = {arm} ({'Q8_0' if arm == 'q8' else 'Q4_K_M'})  status={status} pick={pick.get('pick')} score={pick.get('pick_score')}")
        calls = pick.get("llm_calls") or []
        pt = sum(c.get("prompt_tokens") or 0 for c in calls); ct = sum(c.get("completion_tokens") or 0 for c in calls)
        pi_i, pi_o, pi_c, pi_n = pi_usage(rd / "_pi.jsonl")
        t = timing.get(f"{arm}_ask{a}", ["", "", "?", "?"])
        rows.append((a, label, t[3], t[2], status, pick.get("seconds"), pick.get("llm_seconds"), len(calls), pt, ct, pi_n, pi_i + pi_c, pi_o))
(OUT / "KEY.txt").write_text("\n".join(key) + "\n", encoding="utf-8")
md = ["# Heretic Q8_0 vs Q4_K_M blind Render test: timing (EVO-X3, 2026-11-15)", "",
      "Render pi chat on the X3 (`~/AI/render/x3/render-pi.sh`, production Render argv) + writer pipeline on the same model; identical arm A sampling "
      "(temp 1.0, top_p 0.95, top_k 64, min_p 0.10; beat card temp 0.7; judge greedy), identical pristine pipeline state per arm, dry run only, nothing queued. "
      "Seeds are the pipeline's own random seeds (not fixed across arms). Rows are labelled by blinded file; the model for each file is only in KEY.txt. Models warmed before each arm, so wall time excludes the model load.", "",
      "Asks: " + "; ".join(f"ask{k}: {v}" for k, v in asks.items()), "",
      "| ask | file | wall s (pi chat end to end) | pi rc | status | pipeline s | pipeline LLM s | LLM calls | pipeline prompt tok | pipeline completion tok | pi turns | pi input tok (incl. cache) | pi output tok |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append("| " + " | ".join(str(x) for x in (f"ask{r[0]}", f"ask{r[0]}_{r[1]}.txt") + r[2:]) + " |")
(OUT / "timing.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md)); print(); print("\n".join(key))
