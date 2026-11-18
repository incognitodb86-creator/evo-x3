#!/usr/bin/env python3
"""PLAN-v3.2 Phase 0 harness for C2 (Parallel), C3 (Refusals), C4 (Tools + tool_choice=none), and C6 (Vision).

Never prints or accepts API keys on the CLI. Pass the llama-swap key via --key-stdin or LLM_KEY_BOX env var.
"""

import argparse
import concurrent.futures as cf
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.request

REFUSAL_SCRIPT = "/home/derekboone/evo-x3/bakeoff/u26/refusal_key.py"
VISION_SCRIPT = "/home/derekboone/evo-x3/bakeoff/bench/vision_bench.py"
VISION_IMAGE = "/home/derekboone/evo-x3/bakeoff/bench/vision-test.png"


def post_chat(base: str, key: str | None, body: dict, timeout: int = 1800) -> dict:
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        base.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def run_c2(base: str, direct_base: str, key: str | None, model: str, jobs: list[int]) -> dict:
    words = "the quick brown fox jumps over a lazy dog while seven clocks ring in the old harbour town at dusk".split()

    def make_prompt(tokens: int, needle: str) -> str:
        rng = random.Random(tokens + len(needle))
        n = int(tokens * 0.75)
        body = [rng.choice(words) for _ in range(n)]
        body.insert(n // 2, f" The secret code is {needle}. ")
        return " ".join(body) + "\n\nWhat is the secret code? Reply with the code only."

    def one(idx: int, tokens: int) -> dict:
        needle = str(100000 + idx * 7919)
        body = {
            "model": model,
            "messages": [{"role": "user", "content": make_prompt(tokens, needle)}],
            "max_tokens": 256,
            "temperature": 0.0,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        t0 = time.time()
        try:
            res = post_chat(base, key, body, timeout=1800)
            ans = (res["choices"][0]["message"].get("content") or "").strip()
            return {
                "i": idx,
                "target_tokens": tokens,
                "prompt_tokens": (res.get("usage") or {}).get("prompt_tokens"),
                "wall_s": round(time.time() - t0, 2),
                "pass": needle in ans,
                "answer": ans[:80],
            }
        except Exception as exc:
            return {
                "i": idx,
                "target_tokens": tokens,
                "wall_s": round(time.time() - t0, 2),
                "pass": False,
                "error": str(exc)[:200],
            }

    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        results = list(ex.map(lambda pair: one(*pair), enumerate(jobs)))
    return {
        "jobs": jobs,
        "total_wall_s": round(time.time() - t0, 2),
        "all_pass": all(r["pass"] for r in results),
        "results": results,
    }


def run_c3(base: str, key: str | None, model: str, out_path: str) -> dict:
    cmd = [
        sys.executable,
        REFUSAL_SCRIPT,
        "--base",
        base,
        "--model",
        model,
        "--arm",
        model,
        "--out",
        out_path,
    ]
    stdin_data = None
    if key:
        cmd.append("--key-stdin")
        stdin_data = key + "\n"
    proc = subprocess.run(cmd, input=stdin_data, text=True, capture_output=True, check=False)
    data = json.load(open(out_path, "r", encoding="utf-8")) if os.path.exists(out_path) else {}
    tasks = data.get("tasks") or {}
    expected = ("benign_sysadmin", "adult_fiction", "explicit_adult")
    all_comply = all((tasks.get(k) or {}).get("verdict") == "comply" for k in expected)
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "all_comply": all_comply,
        "verdicts": {k: (tasks.get(k) or {}).get("verdict") for k in expected},
        "out_file": out_path,
    }


def run_c4(base: str, key: str | None, model: str, trials: int = 3) -> dict:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "lookup_user",
                "description": "Find a customer by email. Returns the user id.",
                "parameters": {
                    "type": "object",
                    "properties": {"email": {"type": "string"}},
                    "required": ["email"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_orders",
                "description": "List orders for a user id.",
                "parameters": {
                    "type": "object",
                    "properties": {"user_id": {"type": "string"}},
                    "required": ["user_id"],
                },
            },
        },
    ]

    chain_runs = []
    for trial in range(1, trials + 1):
        msgs = [
            {"role": "system", "content": "You are an agent. Use the tools; do not guess ids."},
            {"role": "user", "content": "How many orders does dana@example.com have? Look it up with the tools."},
        ]
        ok1 = ok2 = ok3 = False
        ids_intact = False
        err = None
        try:
            r1 = post_chat(
                base,
                key,
                {"model": model, "messages": msgs, "tools": tools, "max_tokens": 1200, "temperature": 0.2, "reasoning_effort": "low"},
            )
            m1 = (r1.get("choices") or [{}])[0].get("message") or {}
            tc1 = (m1.get("tool_calls") or [None])[0]
            if tc1:
                cid1 = tc1.get("id") or ""
                fn1 = tc1.get("function") or {}
                args1 = json.loads(fn1.get("arguments") or "{}")
                ok1 = bool(cid1) and fn1.get("name") == "lookup_user" and args1.get("email") == "dana@example.com"
                if ok1:
                    msgs.append({"role": "assistant", "content": None, "tool_calls": [tc1]})
                    msgs.append({"role": "tool", "tool_call_id": cid1, "content": json.dumps({"user_id": "u-4821", "name": "Dana"})})
                    r2 = post_chat(
                        base,
                        key,
                        {"model": model, "messages": msgs, "tools": tools, "max_tokens": 1200, "temperature": 0.2, "reasoning_effort": "low"},
                    )
                    m2 = (r2.get("choices") or [{}])[0].get("message") or {}
                    tc2 = (m2.get("tool_calls") or [None])[0]
                    if tc2:
                        cid2 = tc2.get("id") or ""
                        fn2 = tc2.get("function") or {}
                        args2 = json.loads(fn2.get("arguments") or "{}")
                        ok2 = bool(cid2) and fn2.get("name") == "get_orders" and args2.get("user_id") == "u-4821"
                        ids_intact = bool(cid1) and bool(cid2) and cid1 != cid2
                        if ok2:
                            msgs.append({"role": "assistant", "content": None, "tool_calls": [tc2]})
                            msgs.append(
                                {"role": "tool", "tool_call_id": cid2, "content": json.dumps({"orders": [{"id": "A1"}, {"id": "A2"}, {"id": "A3"}]})}
                            )
                            r3 = post_chat(
                                base,
                                key,
                                {"model": model, "messages": msgs, "tools": tools, "max_tokens": 1200, "temperature": 0.2, "reasoning_effort": "low"},
                            )
                            m3 = (r3.get("choices") or [{}])[0].get("message") or {}
                            c3 = m3.get("content") or ""
                            ok3 = bool(re.search(r"\b(3|three)\b", c3, re.I))
        except Exception as exc:
            err = str(exc)[:200]
        chain_runs.append(
            {
                "trial": trial,
                "step_pass": [ok1, ok2, ok3],
                "ids_intact": ids_intact,
                "pass": ok1 and ok2 and ok3 and ids_intact,
                "error": err,
            }
        )

    none_runs = []
    leak_re = re.compile(r"(<tool_call>|<function=|<parameter=|\{\s*\"name\"\s*:)", re.I)
    for idx in range(1, 3):
        try:
            r = post_chat(
                base,
                key,
                {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Answer directly in plain text without invoking tools."},
                        {"role": "user", "content": "Explain briefly why you cannot check Dana's order count right now."},
                    ],
                    "tools": tools,
                    "tool_choice": "none",
                    "max_tokens": 400,
                    "temperature": 0.2,
                    "reasoning_effort": "low",
                },
            )
            ch = (r.get("choices") or [{}])[0]
            msg = ch.get("message") or {}
            content = msg.get("content") or ""
            tcalls = msg.get("tool_calls") or []
            leaked = bool(leak_re.search(content))
            ok = (ch.get("finish_reason") == "stop") and (not tcalls) and (not leaked) and bool(content.strip())
            none_runs.append(
                {
                    "trial": idx,
                    "finish_reason": ch.get("finish_reason"),
                    "tool_calls_len": len(tcalls),
                    "leaked_call_text": leaked,
                    "content_preview": content[:160],
                    "pass": ok,
                }
            )
        except Exception as exc:
            none_runs.append({"trial": idx, "pass": False, "error": str(exc)[:200]})

    return {
        "chain_pass": sum(1 for x in chain_runs if x["pass"]),
        "chain_total": trials,
        "chain_runs": chain_runs,
        "tool_choice_none_pass": sum(1 for x in none_runs if x["pass"]),
        "tool_choice_none_total": 2,
        "tool_choice_none_runs": none_runs,
        "all_pass": all(x["pass"] for x in chain_runs) and all(x["pass"] for x in none_runs),
    }


def run_c6(direct_base: str, model: str, out_path: str) -> dict:
    cmd = [
        sys.executable,
        VISION_SCRIPT,
        "--base",
        direct_base,
        "--model",
        model,
        "--arm",
        model,
        "--image",
        VISION_IMAGE,
        "--out",
        out_path,
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    data = json.load(open(out_path, "r", encoding="utf-8")) if os.path.exists(out_path) else {}
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "vision_works": bool(data.get("vision_works")),
        "checks": data.get("checks"),
        "out_file": out_path,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8080")
    ap.add_argument("--direct-base", default="http://127.0.0.1:8081")
    ap.add_argument("--model", default="flash-next-uncensored-v2")
    ap.add_argument("--c2-jobs", default="100000,100000,100000,100000")
    ap.add_argument("--checks", default="c2,c3,c4,c6")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--key-stdin", action="store_true")
    args = ap.parse_args()

    key = sys.stdin.readline().strip() if args.key_stdin else os.environ.get("LLM_KEY_BOX")
    os.makedirs(args.out_dir, exist_ok=True)
    checks = {c.strip().lower() for c in args.checks.split(",") if c.strip()}
    jobs = [int(x.strip()) for x in args.c2_jobs.split(",") if x.strip()]

    summary = {"model": args.model, "started": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "checks": {}}
    if "c3" in checks:
        summary["checks"]["c3"] = run_c3(args.base, key, args.model, os.path.join(args.out_dir, "c3_refusal.json"))
    if "c4" in checks:
        summary["checks"]["c4"] = run_c4(args.base, key, args.model, trials=3)
    if "c6" in checks:
        summary["checks"]["c6"] = run_c6(args.direct_base, args.model, os.path.join(args.out_dir, "c6_vision.json"))
    if "c2" in checks:
        summary["checks"]["c2"] = run_c2(args.base, args.direct_base, key, args.model, jobs)

    out_json = os.path.join(args.out_dir, "summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
