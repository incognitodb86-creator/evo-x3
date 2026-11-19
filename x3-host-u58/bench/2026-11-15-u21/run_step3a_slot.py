#!/usr/bin/env python3
"""Run B3 coherence gate, U12 cold TTFT, and llama-benchy served-path sweep for one llama-swap slot."""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
OUT_DIR = "/home/derekboone/evo-x3/bench/2026-11-15-u21"
U12_SCRIPT = "/home/derekboone/evo-x3/stage-src/fixtures/u12-cold-ttft-prompt.py"
BENCHY_WRAPPER = os.path.join(OUT_DIR, "run_llama_benchy.py")
BENCHY_PY = "/home/derekboone/evo-x3/.venv-bench/bin/python"
BASE = "http://127.0.0.1:8080"


def now_ct():
    return datetime.datetime.now(CT).strftime("%Y-%m-%d %H:%M:%S %Z")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def api_get(path, key):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def wait_unloaded(key):
    # Ensure nothing is in flight before unloading
    r0 = json.loads(api_get("/running", key))
    if r0.get("running"):
        api_get("/unload", key)
    for _ in range(60):
        r = json.loads(api_get("/running", key))
        ps = sh('sudo -n podman ps --format "{{.Names}}"').stdout.splitlines()
        model_ct = [n for n in ps if n.startswith("llama-swap-")]
        gtt = int(open("/sys/class/drm/card1/device/mem_info_gtt_used").read().strip())
        if not r.get("running") and not model_ct and gtt < 512 * 1024 * 1024:
            return {"gtt_used_bytes": gtt, "containers": ps}
        time.sleep(1)
    raise RuntimeError("Timed out waiting for llama-swap unload")


def capture_sys_snapshot():
    return {
        "at_ct": now_ct(),
        "gtt_used_bytes": int(open("/sys/class/drm/card1/device/mem_info_gtt_used").read().strip()),
        "free_bytes": sh("free -b").stdout.strip(),
        "sensors": sh("sensors").stdout.strip(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--depths", nargs="+", type=int, default=[0, 32768, 131072])
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--skip-u12", action="store_true")
    ap.add_argument("--skip-benchy", action="store_true")
    args = ap.parse_args()

    key = os.environ.get("LLM_KEY_BOX") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("LLM_KEY_BOX / OPENAI_API_KEY not set in env")

    slot = args.slot
    running_now = [m.get("model") for m in json.loads(api_get("/running", key)).get("running", [])]
    if args.skip_u12 and running_now == [slot]:
        pre_snap = capture_sys_snapshot()
        print(f"[{now_ct()}] === SLOT {slot}: already loaded & skip-u12 set (GTT={pre_snap['gtt_used_bytes']} bytes) ===")
    else:
        print(f"[{now_ct()}] === SLOT {slot}: unloading all models ===")
        unload_info = wait_unloaded(key)
        pre_snap = capture_sys_snapshot()
        print(f"[{now_ct()}] Unloaded cleanly. GTT={unload_info['gtt_used_bytes']} bytes")

    # 1. U12 Cold TTFT (no warmup, first request after load)
    if not args.skip_u12:
        t_before_u12 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(1)
        print(f"[{now_ct()}] Running U12 cold TTFT fixture on {slot}...")
        p_u12 = subprocess.run(
            ["python3", U12_SCRIPT, "--url", f"{BASE}/v1/chat/completions", "--model", slot, "--api-key-env", "LLM_KEY_BOX"],
            capture_output=True, text=True, timeout=900,
        )
        time.sleep(2)
        journal_u12 = sh(f'journalctl -u llama-swap --since "{t_before_u12}" --no-pager -o short-iso').stdout
        ct_name = f"llama-swap-{slot}"
        ct_logs_u12 = sh(f"sudo -n podman logs --tail 60 {ct_name} 2>&1").stdout
        u12_parsed = None
        try:
            u12_parsed = json.loads(p_u12.stdout)
        except Exception:
            pass
        u12_record = {
            "slot": slot,
            "started_ct": now_ct(),
            "rc": p_u12.returncode,
            "pre_snapshot": pre_snap,
            "post_snapshot": capture_sys_snapshot(),
            "fixture_stdout": u12_parsed if u12_parsed is not None else p_u12.stdout,
            "fixture_stderr": p_u12.stderr,
            "llama_swap_journal": journal_u12.splitlines()[-80:],
            "container_logs_tail": ct_logs_u12.splitlines()[-60:],
        }
        u12_path = os.path.join(OUT_DIR, f"u12_cold_ttft_{slot}.json")
        with open(u12_path, "w") as f:
            json.dump(u12_record, f, indent=2)
        print(f"[{now_ct()}] U12 cold TTFT saved to {u12_path}: wall={u12_parsed.get('client_wall_seconds') if u12_parsed else 'ERR'}s")
        if p_u12.returncode != 0:
            raise SystemExit(f"U12 failed on {slot}: {p_u12.stderr}")

    # 2. B3 Coherence Check
    print(f"[{now_ct()}] Running B3 coherence check on {slot}...")
    t_before_coh = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    coh_payload = {
        "model": slot,
        "messages": [
            {"role": "user", "content": "Explain in three clear sentences why unified memory allocation limits matter on AMD Strix Halo APUs."}
        ],
        "max_tokens": 1500,
        "temperature": 0.2,
        "reasoning_effort": "low",
        "stream": False,
    }
    if slot == "gemma4-heretic":
        coh_payload["chat_template_kwargs"] = {"enable_thinking": False}
    req = urllib.request.Request(
        f"{BASE}/v1/chat/completions",
        data=json.dumps(coh_payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=600) as resp:
        coh_raw = json.loads(resp.read().decode("utf-8"))
        coh_status = resp.status
    coh_wall = round(time.monotonic() - t0, 3)
    msg = (coh_raw.get("choices") or [{}])[0].get("message", {})
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
    coherent = (coh_status == 200) and (len(content.strip()) >= 40) and ("memory" in (content + reasoning).lower())
    journal_coh = sh(f'journalctl -u llama-swap --since "{t_before_coh}" --no-pager -o short-iso').stdout
    coh_rec = {
        "slot": slot,
        "at_ct": now_ct(),
        "http_status": coh_status,
        "wall_s": coh_wall,
        "coherent_pass": coherent,
        "content": content,
        "reasoning_chars": len(reasoning),
        "usage": coh_raw.get("usage"),
        "timings": coh_raw.get("timings"),
        "finish_reason": (coh_raw.get("choices") or [{}])[0].get("finish_reason"),
        "journal_tail": journal_coh.splitlines()[-30:],
    }
    coh_path = os.path.join(OUT_DIR, f"coherence_{slot}.json")
    with open(coh_path, "w") as f:
        json.dump(coh_rec, f, indent=2)
    print(f"[{now_ct()}] Coherence {slot}: pass={coherent}, wall={coh_wall}s, content_head={content[:100]!r}")
    if not coherent:
        raise SystemExit(f"Coherence check FAILED on {slot}!")

    # 3. B2 Served Path (llama-benchy)
    if not args.skip_benchy:
        benchy_json = os.path.join(OUT_DIR, f"llama_benchy_{slot}.json")
        benchy_log = os.path.join(OUT_DIR, f"llama_benchy_{slot}.log")
        cmd = [
            BENCHY_PY, BENCHY_WRAPPER,
            "--base-url", f"{BASE}/v1",
            "--model", slot,
            "--tokenizer", args.tokenizer,
            "--pp", "512",
            "--tg", "128",
            "--depth", *[str(d) for d in args.depths],
            "--runs", str(args.runs),
            "--no-cache",
            "--no-warmup",
            "--exit-on-first-fail",
            "--format", "json",
            "--save-result", benchy_json,
        ]
        print(f"[{now_ct()}] Running llama-benchy on {slot}: depths={args.depths}, runs={args.runs}...")
        t0 = time.monotonic()
        p_b = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        wall_b = round(time.monotonic() - t0, 2)
        with open(benchy_log, "w") as f:
            f.write(p_b.stdout + "\n--- STDERR ---\n" + p_b.stderr)
        print(f"[{now_ct()}] llama-benchy {slot} finished rc={p_b.returncode} in {wall_b}s")
        if p_b.returncode != 0:
            print(p_b.stdout[-1500:])
            print(p_b.stderr[-1500:])
            raise SystemExit(f"llama-benchy failed on {slot}")
        md_path = benchy_json[:-5] + ".md"
        if os.path.exists(md_path):
            print(open(md_path).read())

    post_snap = capture_sys_snapshot()
    print(f"[{now_ct()}] === SLOT {slot} DONE === GTT={post_snap['gtt_used_bytes']} bytes")


if __name__ == "__main__":
    main()
