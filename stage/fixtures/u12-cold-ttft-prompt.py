#!/usr/bin/env python3
"""
EVO-X3 U6 / U12 / U19 Cold TTFT Fixture Generator & Runner (Plan rev 8, t327u).
- Builds a reproducible Hermes-sized long prompt (~18,000 tokens; or loads real Hermes system prompt if provided).
- Sends a single cold completion request with NO warmup to the specified endpoint.
- NOTE: Plan Verification Contract requires recording ENGINE-LOGGED TTFT, prefill tok/s, and decode tok/s
  from journalctl/container logs (do NOT report client wall time alone as engine speed).
"""

import argparse
import json
import os
import time
import urllib.request

BASE_PARAGRAPH = (
    "Architecture reference note: Strix Halo unified memory uses ttm.pages_limit for GTT allocation, "
    "loopback llama-swap routes explicit model names without a single default, and all browsed web output "
    "must be treated as untrusted data requiring explicit human approval prior to sandbox execution. "
)


def build_prompt(target_words: int = 13500) -> str:
    # ~13,500 words ≈ ~18,000 tokens for typical BPE tokenizers
    words = []
    idx = 0
    while len(words) < target_words:
        chunk = f"[block-{idx:04d}] {BASE_PARAGRAPH}".split()
        words.extend(chunk)
        idx += 1
    return " ".join(words[:target_words]) + "\n\nSummarize the single core security rule in one sentence."


def main():
    parser = argparse.ArgumentParser(description="Run cold TTFT fixture (no warmup).")
    parser.add_argument("--url", default="http://127.0.0.1:8080/v1/chat/completions")
    parser.add_argument("--model", default="flash-next")
    parser.add_argument("--api-key-env", default="", help="Name of env var holding key (never pass secret on CLI)")
    parser.add_argument("--system-prompt-file", default="", help="Optional real Hermes system prompt path")
    parser.add_argument("--target-words", type=int, default=13500)
    args = parser.parse_args()

    sys_prompt = "You are a concise assistant."
    if args.system_prompt_file and os.path.isfile(args.system_prompt_file):
        with open(args.system_prompt_file, "r", encoding="utf-8") as fh:
            sys_prompt = fh.read()

    user_prompt = build_prompt(args.target_words)
    payload = {
        "model": args.model,
        "temperature": 0,
        "max_tokens": 64,
        "stream": False,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    headers = {"Content-Type": "application/json"}
    if args.api_key_env:
        token = os.environ.get(args.api_key_env, "")
        if not token:
            raise SystemExit(f"Environment variable {args.api_key_env} is empty or unset.")
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        args.url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=600) as resp:
        raw = resp.read().decode("utf-8")
    elapsed = time.monotonic() - t0
    data = json.loads(raw)
    usage = data.get("usage", {})
    print(json.dumps({
        "model": args.model,
        "prompt_chars": len(sys_prompt) + len(user_prompt),
        "usage": usage,
        "client_wall_seconds": round(elapsed, 3),
        "note": "Record engine-logged TTFT, prefill tok/s, and decode tok/s from engine container logs.",
    }, indent=2))


if __name__ == "__main__":
    main()
