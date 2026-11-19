#!/usr/bin/env python3
"""Clean-room implementation of kyuz0's 3-tier deep-research agent architecture
(Orchestrator -> Searcher subagents saving markdown pages -> Page-Analyzer subagents
using grep/snippet + embed-small semantic ranking, with hard tool quotas).
Runs purely against local llama-swap (flash-next / flash-next-sub / embed-small)
and localhost SearXNG (http://127.0.0.1:8888)."""
import argparse
import datetime
import hashlib
import html
import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
LLM_BASE = "http://127.0.0.1:8080/v1"
SEARX_BASE = "http://127.0.0.1:8888"


def now_ct():
    return datetime.datetime.now(CT).strftime("%Y-%m-%d %H:%M:%S %Z")


class QuotaTracker:
    def __init__(self, limits):
        self.limits = dict(limits)
        self.used = {k: 0 for k in limits}

    def check_and_consume(self, tool_name):
        if self.used[tool_name] >= self.limits[tool_name]:
            return False, f"QUOTA_EXCEEDED: tool '{tool_name}' limit ({self.limits[tool_name]}) reached. Synthesize from gathered facts."
        self.used[tool_name] += 1
        return True, None

    def budget_banner(self):
        parts = [f"{k}: {self.limits[k] - self.used[k]}/{self.limits[k]} left" for k in self.limits]
        return "[TOOL QUOTA REMAINING: " + ", ".join(parts) + "]"


def llm_chat(key, model, messages, tools=None, max_tokens=2048, temperature=0.3, tracker=None):
    msgs = list(messages)
    if tracker is not None and msgs and msgs[0]["role"] == "system":
        msgs[0] = {"role": "system", "content": msgs[0]["content"] + "\n\n" + tracker.budget_banner()}
    body = {
        "model": model,
        "messages": msgs,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "reasoning_effort": "low",
        "stream": False,
    }
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        LLM_BASE + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def get_embeddings(key, texts):
    body = {"model": "embed-small", "input": texts}
    req = urllib.request.Request(
        LLM_BASE + "/embeddings",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    return [d["embedding"] for d in data["data"]]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-9
    nb = math.sqrt(sum(x * x for x in b)) or 1e-9
    return dot / (na * nb)


def html_to_markdown(raw_html):
    # Clean-room lightweight HTML->Markdown extractor (no external code copied)
    text = re.sub(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw_html, flags=re.S | re.I)
    title_m = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.S | re.I)
    title = html.unescape(re.sub(r"\s+", " ", title_m.group(1))).strip() if title_m else ""
    text = re.sub(r"<h([1-6])[^>]*>(.*?)</h\1>", lambda m: f"\n{'#' * int(m.group(1))} {m.group(2)}\n", text, flags=re.S | re.I)
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"\n- \1", text, flags=re.S | re.I)
    text = re.sub(r"<(p|div|br|tr|section|article)[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    cleaned = "\n".join(ln for ln in lines if ln)
    return title, cleaned


def searx_search(query, num_results=6):
    url = f"{SEARX_BASE}/search?q={urllib.parse.quote_plus(query)}&format=json"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode("utf-8"))
    results = []
    for item in (data.get("results") or [])[:num_results]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
        })
    return results


def fetch_and_save_page(url, pages_dir):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) U32ResearchBot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        ctype = r.headers.get("Content-Type", "")
        raw = r.read(600_000).decode("utf-8", errors="replace")
    if "html" in ctype.lower() or "<html" in raw[:500].lower():
        title, md = html_to_markdown(raw)
    else:
        title, md = url, raw
    slug = hashlib.sha256(url.encode()).hexdigest()[:12]
    fname = f"{slug}.md"
    fpath = os.path.join(pages_dir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(f"---\nurl: {url}\ntitle: {title}\n---\n\n{md}\n")
    return {"file": fname, "path": fpath, "url": url, "title": title, "chars": len(md)}


def run_searcher_subagent(key, angle, pages_dir, tracker, metrics):
    """Tier 2: Searcher subagent searches SearXNG for an angle and saves top pages to disk as Markdown."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search SearXNG and return top titles, URLs, and snippets.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_page",
                "description": "Fetch a URL and save its content as a local Markdown file for page analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"],
                },
            },
        },
    ]
    msgs = [
        {
            "role": "system",
            "content": (
                "You are a Searcher subagent. Search the web for the assigned research angle, "
                "fetch the most authoritative primary URLs (docs, changelogs, benchmark writeups, GitHub raw files) "
                "to save them as Markdown files, and return a JSON list of saved page paths and URLs."
            ),
        },
        {"role": "user", "content": f"Research angle: {angle}"},
    ]
    saved_pages = []
    for _ in range(6):
        resp = llm_chat(key, "flash-next-sub", msgs, tools=tools, max_tokens=800, temperature=0.2, tracker=tracker)
        u = resp.get("usage") or {}
        metrics["prompt_tokens"] += u.get("prompt_tokens", 0)
        metrics["completion_tokens"] += u.get("completion_tokens", 0)
        msg = (resp.get("choices") or [{}])[0].get("message") or {}
        tcalls = msg.get("tool_calls") or []
        msgs.append(msg)
        if not tcalls:
            break
        for tc in tcalls:
            fn = (tc.get("function") or {}).get("name")
            try:
                args = json.loads((tc.get("function") or {}).get("arguments") or "{}")
            except Exception:
                args = {}
            if fn in ("search_web", "fetch_page"):
                ok, err = tracker.check_and_consume(fn)
                metrics["tool_calls"][fn] = metrics["tool_calls"].get(fn, 0) + 1
                if not ok:
                    res_obj = {"error": err}
                elif fn == "search_web":
                    try:
                        res_obj = {"results": searx_search(args.get("query", angle))}
                    except Exception as e:
                        res_obj = {"error": repr(e)}
                else:
                    try:
                        pinfo = fetch_and_save_page(args.get("url", ""), pages_dir)
                        saved_pages.append(pinfo)
                        res_obj = pinfo
                    except Exception as e:
                        res_obj = {"error": repr(e)}
            else:
                res_obj = {"error": f"unknown tool {fn}"}
            msgs.append({"role": "tool", "tool_call_id": tc.get("id", "call_1"), "content": json.dumps(res_obj)})
    return saved_pages


def run_page_analyzer_subagent(key, question, page_info, tracker, metrics):
    """Tier 3: Page-Analyzer subagent uses grep + embed-small semantic ranking on saved Markdown
    to extract only verified facts + exact URL, keeping raw HTML/pages out of orchestrator context."""
    ok, err = tracker.check_and_consume("analyze_page")
    metrics["tool_calls"]["analyze_page"] = metrics["tool_calls"].get("analyze_page", 0) + 1
    if not ok:
        return {"url": page_info["url"], "facts": err}

    raw_md = open(page_info["path"], encoding="utf-8", errors="replace").read()
    # Chunk into ~1200-char snippets with 200-char overlap
    chunks = []
    step = 1000
    for i in range(0, min(len(raw_md), 30000), step):
        chunks.append(raw_md[i:i + 1200])
    if not chunks:
        return {"url": page_info["url"], "facts": "Empty page."}

    # Rank chunks using embed-small semantic similarity + keyword overlap
    top_chunks = chunks[:4]
    try:
        q_emb = get_embeddings(key, ["search_query: " + question])[0]
        c_embs = get_embeddings(key, ["search_document: " + c for c in chunks[:16]])
        scored = sorted(
            [(cosine(q_emb, ce), idx, chunks[idx]) for idx, ce in enumerate(c_embs)],
            key=lambda x: x[0],
            reverse=True,
        )
        top_chunks = [item[2] for item in scored[:4]]
    except Exception:
        pass

    snippet_text = "\n\n---\n\n".join(top_chunks)
    msgs = [
        {
            "role": "system",
            "content": (
                "You are a Page-Analyzer subagent. Extract ONLY concrete, verifiable facts from the provided "
                "Markdown excerpts that help answer the research question. Include exact numbers, dates, flags, "
                "versions, licenses, and quote short exact phrases when helpful. If the excerpts do not support "
                "an answer, state 'NO_RELEVANT_FACTS'. Always cite the exact source URL."
            ),
        },
        {
            "role": "user",
            "content": f"Question: {question}\nSource URL: {page_info['url']}\nTitle: {page_info['title']}\n\nExcerpts:\n{snippet_text}",
        },
    ]
    resp = llm_chat(key, "flash-next-sub", msgs, max_tokens=600, temperature=0.1, tracker=tracker)
    u = resp.get("usage") or {}
    metrics["prompt_tokens"] += u.get("prompt_tokens", 0)
    metrics["completion_tokens"] += u.get("completion_tokens", 0)
    msg = (resp.get("choices") or [{}])[0].get("message") or {}
    return {"url": page_info["url"], "title": page_info["title"], "facts": msg.get("content", "")}


def run_question(key, q_id, question, run_dir):
    pages_dir = os.path.join(run_dir, q_id, "pages")
    os.makedirs(pages_dir, exist_ok=True)
    tracker = QuotaTracker({"search_web": 4, "fetch_page": 6, "analyze_page": 6})
    metrics = {"prompt_tokens": 0, "completion_tokens": 0, "tool_calls": {"search_web": 0, "fetch_page": 0, "analyze_page": 0}}
    t0 = time.monotonic()

    # Tier 1a: Orchestrator decomposes query into 2 focused search angles
    plan_resp = llm_chat(
        key,
        "flash-next",
        [
            {"role": "system", "content": "You are the Orchestrator of a 3-tier deep-research agent. Decompose the user's question into exactly 2 concise web search queries (one per line, no numbering or commentary)."},
            {"role": "user", "content": question},
        ],
        max_tokens=160,
        temperature=0.2,
        tracker=tracker,
    )
    u0 = plan_resp.get("usage") or {}
    metrics["prompt_tokens"] += u0.get("prompt_tokens", 0)
    metrics["completion_tokens"] += u0.get("completion_tokens", 0)
    raw_angles = ((plan_resp.get("choices") or [{}])[0].get("message") or {}).get("content", "")
    angles = [ln.strip("-* 0123456789.") for ln in raw_angles.splitlines() if ln.strip()][:2]
    if not angles:
        angles = [question]

    # Tier 2: Searcher subagents save fetched pages as markdown
    all_pages = []
    seen_urls = set()
    for ang in angles:
        for p in run_searcher_subagent(key, ang, pages_dir, tracker, metrics):
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                all_pages.append(p)

    # Tier 3: Page-Analyzer subagents extract distilled facts using grep/embed-small
    analyses = []
    for p in all_pages[:6]:
        analyses.append(run_page_analyzer_subagent(key, question, p, tracker, metrics))

    # Tier 1b: Orchestrator writes final cited report strictly from distilled facts
    distilled_block = "\n\n".join(
        f"Source: {a['url']} ({a.get('title', '')})\nFacts:\n{a['facts']}" for a in analyses
    )
    final_resp = llm_chat(
        key,
        "flash-next",
        [
            {
                "role": "system",
                "content": (
                    "You are the Orchestrator writing the final deep-research report. "
                    "Synthesize a precise, well-structured, directly cited answer using ONLY the verified "
                    "source facts returned by your Page-Analyzer subagents. Include explicit inline markdown "
                    "links [label](url) for every factual claim and a Sources section at the bottom."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nVerified Page-Analyzer Findings:\n{distilled_block}",
            },
        ],
        max_tokens=1500,
        temperature=0.2,
        tracker=tracker,
    )
    uf = final_resp.get("usage") or {}
    metrics["prompt_tokens"] += uf.get("prompt_tokens", 0)
    metrics["completion_tokens"] += uf.get("completion_tokens", 0)
    report = ((final_resp.get("choices") or [{}])[0].get("message") or {}).get("content", "")
    wall_s = round(time.monotonic() - t0, 2)

    out = {
        "arm": "R1_kyuz0_3tier_cleanroom",
        "question_id": q_id,
        "question": question,
        "started_ct": now_ct(),
        "wall_s": wall_s,
        "angles": angles,
        "pages_saved": [{"url": p["url"], "title": p["title"], "file": p["file"], "chars": p["chars"]} for p in all_pages],
        "sources_urls": [p["url"] for p in all_pages],
        "analyses": analyses,
        "report": report,
        "metrics": metrics,
        "quotas": tracker.limits,
    }
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, f"{q_id}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions-json", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    key = os.environ.get("LLM_KEY_BOX") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("LLM_KEY_BOX / OPENAI_API_KEY not set")
    questions = json.load(open(args.questions_json))
    for q in questions:
        res = run_question(key, q["id"], q["question"], args.out_dir)
        print(f"[{now_ct()}] R1 {q['id']}: wall={res['wall_s']}s sources={len(res['sources_urls'])} tokens={res['metrics']['prompt_tokens']+res['metrics']['completion_tokens']}")


if __name__ == "__main__":
    main()
