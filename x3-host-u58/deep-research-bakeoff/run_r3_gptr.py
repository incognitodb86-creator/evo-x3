#!/usr/bin/env python3
"""Run U32 R3 arm: GPT-Researcher against local llama-swap flash-next + embed-small + localhost SearXNG."""
import argparse
import asyncio
import datetime
import json
import os
import re
import time
from zoneinfo import ZoneInfo

# Configure local OpenAI-compatible + SearXNG env before importing GPTResearcher
os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:8080/v1"
os.environ["FAST_LLM"] = "openai:flash-next"
os.environ["SMART_LLM"] = "openai:flash-next"
os.environ["STRATEGIC_LLM"] = "openai:flash-next"
os.environ["EMBEDDING"] = "custom:embed-small"
os.environ["RETRIEVER"] = "searx"
os.environ["SEARX_URL"] = "http://127.0.0.1:8888"
os.environ["MAX_ITERATIONS"] = "2"
os.environ["MAX_SUBTOPICS"] = "2"
os.environ["MAX_SEARCH_RESULTS_PER_QUERY"] = "5"
os.environ["LLM_KWARGS"] = '{"reasoning_effort": "low"}'

from gpt_researcher import GPTResearcher

CT = ZoneInfo("America/Chicago")


def now_ct():
    return datetime.datetime.now(CT).strftime("%Y-%m-%d %H:%M:%S %Z")


async def run_one(q):
    t0 = time.monotonic()
    err = None
    report = ""
    sources = []
    costs = 0.0
    try:
        researcher = GPTResearcher(query=q["question"], report_type="research_report", verbose=False)
        await researcher.conduct_research()
        report = await researcher.write_report()
        sources = list(researcher.get_source_urls() or [])
        costs = researcher.get_costs()
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    wall_s = round(time.monotonic() - t0, 2)
    report_urls = sorted(set(re.findall(r"https?://[^\s\"'\]\)<>]+", report or "")))
    all_urls = sorted(set(sources) | set(report_urls))
    return {
        "arm": "R3_gpt_researcher",
        "question_id": q["id"],
        "question": q["question"],
        "started_ct": now_ct(),
        "wall_s": wall_s,
        "error": err,
        "report": report,
        "source_urls_returned": sources,
        "sources_urls": all_urls,
        "costs": costs,
    }


async def main_async(args):
    os.makedirs(args.out_dir, exist_ok=True)
    questions = json.load(open(args.questions_json))
    for q in questions:
        out = await run_one(q)
        with open(os.path.join(args.out_dir, f"{q['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, default=str)
        print(f"[{now_ct()}] R3 {q['id']}: wall={out['wall_s']}s sources={len(out['sources_urls'])} report_chars={len(out['report'])} err={out['error']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions-json", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_KEY_BOX")):
        raise SystemExit("OPENAI_API_KEY / LLM_KEY_BOX not set")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
