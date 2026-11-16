#!/home/derekboone/evo-x3/.venv-bench/bin/python
"""B5 RULER-style multi-task long-context benchmark (32K & 128K) for flash-next and qwen27b.
Reproducible from tokenizer, length, and seed=42."""
import datetime
import hashlib
import json
import os
import random
import re
import subprocess
import time
import urllib.request
from zoneinfo import ZoneInfo
from tokenizers import Tokenizer

CT = ZoneInfo("America/Chicago")
OUT_DIR = "/home/derekboone/evo-x3/bench/2026-11-15-u21"
TOK_PATH = "/srv/models/flash-next-halogen/tokenizer/tokenizer.json"
CORPUS_PATH = os.path.expanduser("~/.cache/llama-benchy/cc6a0b5782734ee3b9069aa3b64cc62c.txt")
BASE = "http://127.0.0.1:8080"
SEED = 42
LENGTHS = [32768, 131072]
MODELS = ["flash-next", "qwen27b"]


def now_ct():
    return datetime.datetime.now(CT).strftime("%Y-%m-%d %H:%M:%S %Z")


def api_get(path, key):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def wait_unloaded(key):
    r0 = json.loads(api_get("/running", key))
    if r0.get("running"):
        api_get("/unload", key)
    for _ in range(60):
        r = json.loads(api_get("/running", key))
        ps = subprocess.run('sudo -n podman ps --format "{{.Names}}"', shell=True, capture_output=True, text=True).stdout.splitlines()
        if not r.get("running") and not [n for n in ps if n.startswith("llama-swap-")]:
            return
        time.sleep(1)


def build_haystack_sentences(corpus_text):
    # Clean prose chunks to fill arbitrary token lengths
    paras = [p.strip().replace("\n", " ") for p in corpus_text.split("\n\n") if len(p.strip()) > 120]
    return paras


def pack_to_exact_tokens(tok, paragraphs, insertions, question, target_len, rng):
    """Build prompt with insertions at fractional depths and exact token length == target_len."""
    q_ids = tok.encode("\n\nQUESTION:\n" + question, add_special_tokens=False).ids
    # Build filler pool larger than target_len
    filler_chunks = []
    cur_tokens = 0
    budget = target_len - len(q_ids) - 32
    idx = 0
    while cur_tokens < budget + 2048:
        p = paragraphs[(idx * 7 + 3) % len(paragraphs)]
        filler_chunks.append(p)
        cur_tokens += len(tok.encode(p + "\n\n", add_special_tokens=False).ids)
        idx += 1

    # Place insertions at their target fractions of filler_chunks
    for frac, text in sorted(insertions, key=lambda x: x[0], reverse=True):
        pos = max(1, min(len(filler_chunks) - 1, int(len(filler_chunks) * frac)))
        filler_chunks.insert(pos, text)

    # Encode and trim filler to exact token count so total == target_len
    body = "\n\n".join(filler_chunks)
    body_ids = tok.encode(body, add_special_tokens=False).ids
    # Keep all insertions intact: trim only from the tail if needed? Wait: if insertions go up to 0.90 of filler_chunks,
    # let's compute cumulative tokens to guarantee 100% of insertions sit inside budget!
    packed_parts = []
    used = 0
    # First measure total tokens of insertions
    ins_tokens = sum(len(tok.encode("\n\n" + t + "\n\n", add_special_tokens=False).ids) for _, t in insertions)
    filler_budget = target_len - len(q_ids) - ins_tokens
    # Group filler into segments between insertion fractions
    sorted_ins = sorted(insertions, key=lambda x: x[0])
    prev_f = 0.0
    para_cursor = 0
    for frac, text in sorted_ins:
        seg_budget = max(50, int(filler_budget * (frac - prev_f)))
        seg_ids = []
        while len(seg_ids) < seg_budget:
            p = paragraphs[para_cursor % len(paragraphs)] + "\n\n"
            para_cursor += 1
            seg_ids.extend(tok.encode(p, add_special_tokens=False).ids)
        packed_parts.append(tok.decode(seg_ids[:seg_budget], skip_special_tokens=True))
        packed_parts.append("\n\n" + text + "\n\n")
        used += seg_budget + len(tok.encode("\n\n" + text + "\n\n", add_special_tokens=False).ids)
        prev_f = frac

    # Tail segment up to exact target_len - len(q_ids)
    rem = max(0, (target_len - len(q_ids)) - len(tok.encode("".join(packed_parts), add_special_tokens=False).ids))
    tail_ids = []
    while len(tail_ids) < rem:
        p = paragraphs[para_cursor % len(paragraphs)] + "\n\n"
        para_cursor += 1
        tail_ids.extend(tok.encode(p, add_special_tokens=False).ids)
    packed_parts.append(tok.decode(tail_ids[:rem], skip_special_tokens=True))

    prompt_text = "".join(packed_parts) + "\n\nQUESTION:\n" + question
    # Final 1-token adjustment if BPE merge boundary shifted count by 1-3 tokens
    final_ids = tok.encode(prompt_text, add_special_tokens=False).ids
    if len(final_ids) > target_len:
        # Trim from very start (before 10% insertion) or tail before QUESTION
        head_trim = len(final_ids) - target_len
        p0_ids = tok.encode(packed_parts[0], add_special_tokens=False).ids
        if len(p0_ids) > head_trim + 20:
            packed_parts[0] = tok.decode(p0_ids[head_trim:], skip_special_tokens=True)
            prompt_text = "".join(packed_parts) + "\n\nQUESTION:\n" + question
    return prompt_text, len(tok.encode(prompt_text, add_special_tokens=False).ids)


def make_tasks(tok, paragraphs, length):
    rng = random.Random(SEED + length)
    tasks = []

    # 1. niah_multikey_2
    k1 = f"{rng.randint(100000, 999999)}"
    k2 = f"{rng.randint(100000, 999999)}"
    ins1 = []
    for i in range(20):
        frac = 0.04 + (i * 0.045)
        dkey = f"DIST_{rng.randint(1000,9999)}"
        dval = f"{rng.randint(100000,999999)}"
        ins1.append((frac, f"[RECORD] The magic calibration code for {dkey} is {dval}."))
    ins1.append((0.25, f"[RECORD] The magic calibration code for TARGET_ALPHA is {k1}."))
    ins1.append((0.75, f"[RECORD] The magic calibration code for TARGET_BRAVO is {k2}."))
    q1 = "What are the magic calibration codes for TARGET_ALPHA and TARGET_BRAVO? Reply with both numbers clearly."
    p1, n1 = pack_to_exact_tokens(tok, paragraphs, ins1, q1, length, rng)
    tasks.append({
        "task_id": "niah_multikey_2",
        "prompt": p1,
        "local_tokens": n1,
        "expected": [k1, k2],
        "grade": lambda ans, a=k1, b=k2: (a in ans) and (b in ans),
    })

    # 2. vt_multihop (5-hop variable tracking)
    v0 = str(rng.randint(10000, 99999))
    dv = str(rng.randint(10000, 99999))
    ins2 = [
        (0.15, f"[ASSIGNMENT] VAR_ORION = {v0}"),
        (0.28, f"[ASSIGNMENT] VAR_DECOY_1 = {dv}"),
        (0.35, "[ASSIGNMENT] VAR_LYRA = VAR_ORION"),
        (0.55, "[ASSIGNMENT] VAR_CYGNUS = VAR_LYRA"),
        (0.66, "[ASSIGNMENT] VAR_DECOY_2 = VAR_DECOY_1"),
        (0.75, "[ASSIGNMENT] VAR_DRACO = VAR_CYGNUS"),
        (0.90, "[ASSIGNMENT] VAR_VEGA = VAR_DRACO"),
    ]
    q2 = f"Find all variables in the document that are assigned (directly or transitively) the value {v0}. List every matching variable name."
    p2, n2 = pack_to_exact_tokens(tok, paragraphs, ins2, q2, length, rng)
    expected_vars = ["VAR_ORION", "VAR_LYRA", "VAR_CYGNUS", "VAR_DRACO", "VAR_VEGA"]
    tasks.append({
        "task_id": "vt_multihop",
        "prompt": p2,
        "local_tokens": n2,
        "expected": expected_vars,
        "grade": lambda ans, ev=expected_vars: all(v in ans.upper() for v in ev) and ("VAR_DECOY" not in ans.upper().split("NOT")[0]),
    })

    # 3. fwe_aggregation (frequency tracking across document)
    words = [("KESTREL7", 9), ("FALCON3", 5), ("MERLIN9", 2)]
    ins3 = []
    all_tags = []
    for w, cnt in words:
        all_tags.extend([w] * cnt)
    rng.shuffle(all_tags)
    for idx, tag in enumerate(all_tags):
        frac = 0.05 + (idx / len(all_tags)) * 0.88
        ins3.append((frac, f"[BEACON TAG: {tag}]"))
    q3 = "Count all [BEACON TAG: ...] markers in the document (among KESTREL7, FALCON3, MERLIN9). Which beacon tag appears MOST frequently, and how many times does it appear?"
    p3, n3 = pack_to_exact_tokens(tok, paragraphs, ins3, q3, length, rng)
    tasks.append({
        "task_id": "fwe_aggregation",
        "prompt": p3,
        "local_tokens": n3,
        "expected": ["KESTREL7", "9"],
        "grade": lambda ans: ("KESTREL7" in ans.upper()) and bool(re.search(r"\b(9|nine)\b", ans, re.I)),
    })

    # 4. qa_multifact (3 distributed facts)
    f1 = "Maren Lindqvist"
    f2 = "7814-COBALT"
    f3 = "19:40 UTC"
    ins4 = [
        (0.10, f"[DISPATCH NOTE] The lead hydrologist assigned to Station Borealis is {f1}."),
        (0.50, f"[DISPATCH NOTE] The emergency bulkhead override code for Borealis is {f2}."),
        (0.90, f"[DISPATCH NOTE] The supply icebreaker departs Pier 4 at {f3}."),
    ]
    q4 = "Answer three questions from the DISPATCH NOTE entries: 1) Who is the lead hydrologist for Station Borealis? 2) What is the emergency bulkhead override code? 3) When does the supply icebreaker depart Pier 4?"
    p4, n4 = pack_to_exact_tokens(tok, paragraphs, ins4, q4, length, rng)
    tasks.append({
        "task_id": "qa_multifact",
        "prompt": p4,
        "local_tokens": n4,
        "expected": [f1, f2, f3],
        "grade": lambda ans, a=f1, b=f2, c=f3: (a.lower() in ans.lower()) and (b.lower() in ans.lower()) and ("19:40" in ans),
    })

    return tasks


def main():
    key = os.environ.get("LLM_KEY_BOX") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("LLM_KEY_BOX not set")

    tok_sha = hashlib.sha256(open(TOK_PATH, "rb").read()).hexdigest()
    tok = Tokenizer.from_file(TOK_PATH)
    paragraphs = build_haystack_sentences(open(CORPUS_PATH, encoding="utf-8").read())

    results = {
        "benchmark": "U21-B5-RULER-Subset",
        "started_ct": now_ct(),
        "seed": SEED,
        "tokenizer_path": TOK_PATH,
        "tokenizer_sha256": tok_sha,
        "lengths": LENGTHS,
        "models": {},
    }

    for model in MODELS:
        print(f"[{now_ct()}] === B5 RULER Model: {model} ===")
        wait_unloaded(key)
        model_res = {"by_length": {}}
        for length in LENGTHS:
            tasks = make_tasks(tok, paragraphs, length)
            length_res = {"tasks": [], "passed": 0, "total": len(tasks)}
            for t in tasks:
                body = {
                    "model": model,
                    "messages": [{"role": "user", "content": t["prompt"]}],
                    "temperature": 0.0,
                    "seed": SEED,
                    "max_tokens": 1500,
                    "reasoning_effort": "low",
                    "cache_prompt": False,
                    "stream": False,
                }
                req = urllib.request.Request(
                    f"{BASE}/v1/chat/completions",
                    data=json.dumps(body).encode(),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                    method="POST",
                )
                t0 = time.monotonic()
                with urllib.request.urlopen(req, timeout=1200) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                wall = round(time.monotonic() - t0, 2)
                choice = (raw.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                content = msg.get("content") or ""
                reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
                ans_text = content if content.strip() else reasoning
                passed = bool(t["grade"](ans_text))
                if passed:
                    length_res["passed"] += 1
                row = {
                    "task_id": t["task_id"],
                    "local_tokens": t["local_tokens"],
                    "server_prompt_tokens": (raw.get("usage") or {}).get("prompt_tokens"),
                    "completion_tokens": (raw.get("usage") or {}).get("completion_tokens"),
                    "wall_s": wall,
                    "finish_reason": choice.get("finish_reason"),
                    "timings": raw.get("timings"),
                    "expected": t["expected"],
                    "passed": passed,
                    "answer_excerpt": ans_text[:400],
                }
                length_res["tasks"].append(row)
                print(f"[{now_ct()}] {model} L={length} {t['task_id']}: pass={passed} ptok={row['server_prompt_tokens']} wall={wall}s")
            length_res["accuracy"] = round(length_res["passed"] / length_res["total"], 4)
            model_res["by_length"][str(length)] = length_res
        results["models"][model] = model_res

    results["finished_ct"] = now_ct()
    out_path = os.path.join(OUT_DIR, "b5_ruler_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[{now_ct()}] B5 complete -> {out_path}")


if __name__ == "__main__":
    main()
