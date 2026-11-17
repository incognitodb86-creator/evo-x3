#!/usr/bin/env python3
"""B4 Writer Quality benchmark runner: runs pinned prompts across 3 seeded rounds
for gemma4-heretic and flash-next-uncensored, producing a blinded A/B packet
(with A/B order swapped between rounds) and a separate key file."""
import datetime
import hashlib
import json
import os
import random
import statistics
import subprocess
import time
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
OUT_DIR = "/home/derekboone/evo-x3/bench/2026-11-15-u21"
PROMPT_FILE = "/home/derekboone/AI/community/benchmarks/u21-writer-prompts-20261115.json"
BASE = "http://127.0.0.1:8080"


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


def generate_one(key, model, prompt_text, samplers, seed):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": samplers["temperature"],
        "top_p": samplers["top_p"],
        "top_k": samplers["top_k"],
        "max_tokens": max(samplers["max_tokens"], 800),
        "seed": seed,
        "stream": False,
    }
    if model == "gemma4-heretic":
        body["min_p"] = samplers["min_p"]
        body["chat_template_kwargs"] = {"enable_thinking": samplers["enable_thinking"]}
    else:
        # Halogen closes thinking at 1 token when reasoning_effort="low"
        body["reasoning_effort"] = "low"
    req = urllib.request.Request(
        BASE + "/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=600) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    wall_s = time.monotonic() - t0
    choice = (raw.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
    usage = raw.get("usage") or {}
    timings = raw.get("timings") or {}
    return {
        "wall_s": round(wall_s, 3),
        "finish_reason": choice.get("finish_reason"),
        "content": content,
        "word_count": len(content.split()),
        "char_count": len(content),
        "reasoning_chars": len(reasoning),
        "usage": usage,
        "timings": timings,
    }


def main():
    key = os.environ.get("LLM_KEY_BOX") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("LLM_KEY_BOX not set")

    prompt_bytes = open(PROMPT_FILE, "rb").read()
    prompt_sha = hashlib.sha256(prompt_bytes).hexdigest()
    spec = json.loads(prompt_bytes.decode("utf-8"))
    git_hash = subprocess.run(
        ["git", "-C", "/home/derekboone/AI/community", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True
    ).stdout.strip()

    samplers = spec["samplers"]
    seeds = spec["seeds"]
    prompts = spec["prompts"]
    arms = ["gemma4-heretic", "flash-next-uncensored"]

    raw_runs = {}
    started_ct = now_ct()

    for arm in arms:
        print(f"[{now_ct()}] === B4 Arm: {arm} ===")
        wait_unloaded(key)
        # Warm load with a tiny 1-token ping so generation latencies exclude container boot
        ping_req = urllib.request.Request(
            BASE + "/v1/chat/completions",
            data=json.dumps({"model": arm, "messages": [{"role": "user", "content": "ok"}], "max_tokens": 1, "stream": False}).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            method="POST",
        )
        t_load0 = time.monotonic()
        with urllib.request.urlopen(ping_req, timeout=600) as resp:
            resp.read()
        print(f"[{now_ct()}] {arm} loaded in {time.monotonic() - t_load0:.2f}s")

        arm_res = {}
        for r_idx, seed in enumerate(seeds, start=1):
            round_key = f"round_{r_idx}"
            arm_res[round_key] = {"seed": seed, "items": {}}
            for p in prompts:
                out = generate_one(key, arm, p["prompt"], samplers, seed)
                arm_res[round_key]["items"][p["id"]] = out
                print(f"[{now_ct()}] {arm} r{r_idx}(seed={seed}) {p['id']}: {out['word_count']}w finish={out['finish_reason']} wall={out['wall_s']}s")
        raw_runs[arm] = arm_res

    finished_ct = now_ct()

    # Check Vulkan non-determinism on gemma4-heretic using a 3-sample fixed-seed check on W01
    print(f"[{now_ct()}] Checking Vulkan temperature=0 + fixed seed non-determinism (3 samples on gemma4-heretic)...")
    wait_unloaded(key)
    det_samples = []
    det_samplers = {**samplers, "temperature": 0.0, "top_k": 1, "top_p": 1.0, "min_p": 0.0}
    for i in range(3):
        out = generate_one(key, "gemma4-heretic", prompts[0]["prompt"], det_samplers, 4242)
        det_samples.append({
            "sample": i + 1,
            "sha256": hashlib.sha256(out["content"].encode()).hexdigest(),
            "word_count": out["word_count"],
            "head": out["content"][:180],
        })
    unique_hashes = len({s["sha256"] for s in det_samples})
    print(f"[{now_ct()}] Vulkan temp=0 seed=4242 unique hashes across 3 samples: {unique_hashes}/3")

    # Assemble blind A/B packet with A/B swapped between Round 1 and Round 2, and seeded permutation in Round 3
    rng = random.Random(20261115)
    blind_items = []
    key_map = []
    for p_idx, p in enumerate(prompts):
        # Round 1: odd index -> (heretic, uncensored), even -> (uncensored, heretic)
        r1_pair = ("gemma4-heretic", "flash-next-uncensored") if (p_idx % 2 == 0) else ("flash-next-uncensored", "gemma4-heretic")
        # Round 2: strict swap (B/A of Round 1) per EQ-Bench protocol
        r2_pair = (r1_pair[1], r1_pair[0])
        # Round 3: seeded random swap
        r3_pair = tuple(rng.sample(arms, 2))
        round_pairs = [(1, seeds[0], r1_pair), (2, seeds[1], r2_pair), (3, seeds[2], r3_pair)]

        for r_idx, seed, (arm_a, arm_b) in round_pairs:
            rkey = f"round_{r_idx}"
            out_a = raw_runs[arm_a][rkey]["items"][p["id"]]
            out_b = raw_runs[arm_b][rkey]["items"][p["id"]]
            blind_items.append({
                "round": r_idx,
                "seed": seed,
                "prompt_id": p["id"],
                "genre": p["genre"],
                "prompt": p["prompt"],
                "Label_A": out_a["content"],
                "Label_B": out_b["content"],
            })
            key_map.append({
                "round": r_idx,
                "seed": seed,
                "prompt_id": p["id"],
                "Label_A_arm": arm_a,
                "Label_B_arm": arm_b,
            })

    # Compute aggregate objective metrics per arm
    summary = {}
    for arm in arms:
        walls = []
        words = []
        tps_list = []
        completes = 0
        total = 0
        for rkey, rdata in raw_runs[arm].items():
            for pid, item in rdata["items"].items():
                total += 1
                if item["finish_reason"] in ("stop", "length") and item["char_count"] >= 200:
                    completes += 1
                walls.append(item["wall_s"])
                words.append(item["word_count"])
                ctok = (item.get("usage") or {}).get("completion_tokens")
                if ctok and item["wall_s"] > 0:
                    tps_list.append(ctok / item["wall_s"])
        summary[arm] = {
            "total_generations": total,
            "clean_completions": completes,
            "wall_s_mean": round(statistics.mean(walls), 2),
            "wall_s_sd": round(statistics.stdev(walls), 2) if len(walls) > 1 else 0.0,
            "word_count_mean": round(statistics.mean(words), 1),
            "word_count_sd": round(statistics.stdev(words), 1) if len(words) > 1 else 0.0,
            "client_tps_mean": round(statistics.mean(tps_list), 2) if tps_list else None,
            "client_tps_sd": round(statistics.stdev(tps_list), 2) if len(tps_list) > 1 else None,
        }

    blind_payload = {
        "benchmark": "U21-B4-Writer-Quality",
        "started_ct": started_ct,
        "finished_ct": finished_ct,
        "prompt_file": PROMPT_FILE,
        "prompt_file_git_hash": git_hash,
        "prompt_file_sha256": prompt_sha,
        "samplers": samplers,
        "seeds": seeds,
        "official_prompt_maker_scores": "PENDING (Prompt maker blind evaluation)",
        "blind_items": blind_items,
    }
    key_payload = {
        "prompt_file_git_hash": git_hash,
        "prompt_file_sha256": prompt_sha,
        "started_ct": started_ct,
        "finished_ct": finished_ct,
        "objective_summary": summary,
        "vulkan_temp0_determinism_check": {
            "model": "gemma4-heretic",
            "prompt_id": prompts[0]["id"],
            "temperature": 0.0,
            "seed": 4242,
            "unique_outputs": unique_hashes,
            "samples": det_samples,
        },
        "mapping": key_map,
        "raw_runs": raw_runs,
    }

    with open(os.path.join(OUT_DIR, "b4_writer_blind_outputs.json"), "w") as f:
        json.dump(blind_payload, f, indent=2)
    with open(os.path.join(OUT_DIR, "b4_writer_key.json"), "w") as f:
        json.dump(key_payload, f, indent=2)

    # Human-readable blind packet for Prompt maker
    lines = [
        "# U21 B4 Writer Quality — Blinded A/B Evaluation Packet",
        "",
        f"- **Prompt file:** `{PROMPT_FILE}`",
        f"- **Prompt file git commit:** `{git_hash}`",
        f"- **Prompt file SHA-256:** `{prompt_sha}`",
        f"- **Pinned samplers:** `temperature={samplers['temperature']}`, `top_p={samplers['top_p']}`, `top_k={samplers['top_k']}`, `min_p={samplers['min_p']}`, `max_tokens={samplers['max_tokens']}`, `enable_thinking={samplers['enable_thinking']}`",
        f"- **Fixed seeds (3 rounds):** `{seeds}`",
        "- **Order randomization:** Round 1 alternates A/B by prompt parity; Round 2 strictly inverts Round 1 (`A/B` -> `B/A`); Round 3 uses a seeded random order. Official mapping is stored separately in `b4_writer_key.json`.",
        "- **Status:** Official Prompt maker scores **PENDING**.",
        "",
    ]
    for item in blind_items:
        lines.extend([
            f"## Round {item['round']} (seed={item['seed']}) — {item['prompt_id']} ({item['genre']})",
            f"**Prompt:** {item['prompt']}",
            "",
            "### Sample A",
            item["Label_A"],
            "",
            "### Sample B",
            item["Label_B"],
            "",
            "---",
            "",
        ])
    with open(os.path.join(OUT_DIR, "b4_writer_blind_packet.md"), "w") as f:
        f.write("\n".join(lines))

    print(f"[{now_ct()}] B4 complete. Summary: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
