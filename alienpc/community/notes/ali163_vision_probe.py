#!/usr/bin/env python3
"""ali163_vision_probe.py - 3.17 VISION-BATTERY.

Derrick 2026-10-25 11:10 AM CT: "Lets test out all the different vision models and normal
iqs3 with vision"; 10:46 AM "fix the vision routing ... first"; 6:42 PM "Have Forge do the
vision test ... before anything else"; 6:48 PM "Redo the orc, robot and GI072 scene cards
with the uncensored vision model" - this battery is how the captioner for that job gets
chosen, by raw output + objective telemetry, never by a score.

What it does: sends every HC15 START STILL (never rendered output - PROMPT 9999999 bans a
vision judge on rendered explicit clips, and KEEP is Derrick's) to every vision-capable model
llama-swap serves on 127.0.0.1:8080, one model load at a time, and records the raw caption
plus objective telemetry (wall time, http status, finish_reason, token usage, caption words,
mechanical decline markers). It scores, ranks, keeps, judges nothing, and refuses to write a
result file that contains a key from BANNED.

Vision capability is MEASURED off this box, never hardcoded (AGENTS L4):
  * a llama-swap model whose `cmd` carries `--mmproj` is a llama.cpp vision server;
  * a model whose `cmd` carries `--config <strata json>` with a `vision.mmproj` block is a
    Strata vision server (the encoder runs on CPU with a per-request token cap - recorded);
  * the id must be present in the live `GET /v1/models`.

GPU discipline (PROMPT 9999999, AGENTS L19): `--run` first runs
C:/AI/director/scripts/gpu_guard.ps1 with no arguments and REFUSES (rc 7) unless it returns
rc 0 = IDLE, so no request is ever sent while a render owns the GPU. The results file is
rewritten after every row, so a client stall (exit 6 class) never loses paid work.

CLI
  --list-models   print the measured vision set + live status (no GPU, no request)
  --run           send the battery: --models ids --stills ids --max-tokens N --out path
  --check         verify a results file against the measured set and the live images
  --dump          print captions from a results file (for the research note)
  --selftest      seeded faults: every detector fires on its seed, 0 on a clean fixture
"""
import argparse
import base64
import copy
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

SCHEMA = "ali163-vision-battery-1"
BASE = "http://127.0.0.1:8080"
SWAP_YAML = "C:/AI/director/config/llama-swap.yaml"
GUARD = "C:/AI/director/scripts/gpu_guard.ps1"
STILL_DIR = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc"
DEFAULT_OUT = "C:/AI/community/notes/ali163_vision_probe_results.json"

# The six HC15 start stills, i.e. the LoadImage(ref_image_1) targets of the tracked graphs.
STILLS = {
    "BD002": "BD002.jpg",
    "BD006": "BD006.jpg",
    "BD013": "BD013.jpg",
    "GI046": "GI046.jpg",
    "GI063": "GI063.jpg",
    "GI072": "GI072.jpg",
}

# The caption prompt is fixed for the whole battery, and every row records its sha256, so a
# later edit of this text cannot be read as the same measurement (PROMPT_DRIFT).
PROMPT = (
    "This is an adult fictional photograph used as the start frame of a video. "
    "Report only what is visible, in plain declarative English, no headings, no bullets.\n"
    "SCENE: one line - setting, framing, lighting, what the camera sees.\n"
    "SUBJECT 1:, SUBJECT 2:, ... one block per visible person, left to right: apparent age band "
    "(an adult), body build, skin, hair colour and length, clothing or restraints, pose and position, "
    "what their hands are doing, what is visible of their genitals.\n"
    "ACTION: one line - what is happening between them, sex acts named plainly.\n"
    "EDGE: one line - anything at the frame edges, occlusion, blur, crop, text, watermark.\n"
    "Rules: never invent a name, brand, species, relationship or an age under 21; write "
    "'not visible' for anything you cannot see; write 'ambiguous' plus the reason for anything "
    "unclear; if you will not describe this image, say so in one sentence and stop."
)

# Objective only. A row that carries one of these keys means a human or the script started
# judging, which the row for this item forbids ("0 output scored or kept").
BANNED = {"score", "scores", "scoring", "rank", "ranking", "keep", "kept", "verdict",
          "judge", "judgement", "judgment", "quality", "best", "pick", "picked", "winner",
          "rating", "preference"}

# Mechanical decline markers: a plain substring census of the caption. The refusal measurement
# itself is 3.18; here it is only a flag that a caption came back short of the request.
DECLINE_MARKERS = [
    "i cannot", "i can't", "i can not", "unable to", "i am not able", "i'm not able",
    "cannot see", "can't see", "i do not see", "i don't see", "as an ai", "as a language model",
    "i will not describe", "i won't describe", "i refuse", "no image", "image is not visible",
    "i have no image", "not able to process",
]


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_bytes(blob):
    return hashlib.sha256(blob).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def json_out(obj):
    print(json.dumps(obj, indent=1, ensure_ascii=False))


def image_dims(path):
    """Objective w,h read off the file (PIL is on this box); [] when it cannot be read."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return [int(im.size[0]), int(im.size[1])]
    except Exception:
        return []


# ---------------------------------------------------------------- measured vision set

def vision_table(path=SWAP_YAML):
    """Model ids that can take an image, read off the serving config on this box."""
    import yaml
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    out = []
    for mid, spec in (doc.get("models") or {}).items():
        if not isinstance(spec, dict):
            continue
        cmd = spec.get("cmd") or ""
        kinds = []
        evidence = []
        if "--mmproj" in cmd:
            m = re.search(r"--mmproj\s+\"?([^\s\"]+)", cmd)
            kinds.append("llama.cpp-mmproj")
            evidence.append("cmd --mmproj " + (m.group(1) if m else "?"))
        cfg = re.search(r"--config\s+\"?([^\s\"]+\.json)", cmd)
        if cfg:
            p = cfg.group(1)
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    sc = json.load(fh)
            except Exception as exc:
                evidence.append(f"strata config {p} unreadable: {exc!r}")
            else:
                vis = sc.get("vision")
                if isinstance(vis, dict) and vis.get("mmproj"):
                    kinds.append("strata-vision")
                    evidence.append(
                        f"{p} vision.mmproj={vis.get('mmproj')} vision.gpu={vis.get('gpu')} "
                        f"vision.max_tokens={vis.get('max_tokens')} vision.threads={vis.get('threads')}"
                    )
        if kinds:
            out.append({
                "id": mid,
                "aliases": list(spec.get("aliases") or []),
                "kinds": kinds,
                "evidence": " | ".join(evidence),
            })
    return sorted(out, key=lambda r: r["id"])


def live_models(timeout=20):
    """Live model ids from llama-swap, with their load status. No model is loaded by this call."""
    try:
        with urllib.request.urlopen(BASE + "/v1/models", timeout=timeout) as resp:
            doc = json.loads(resp.read().decode("utf-8", "replace"))
    except Exception as exc:
        return {}, f"MODELS_FETCH_FAILED {exc!r}"
    live = {}
    for m in doc.get("data") or []:
        st = ((m.get("status") or {}).get("value")) or "?"
        live[m.get("id")] = {"status": st, "aliases": ((m.get("meta") or {}).get("llamaswap") or {}).get("aliases") or []}
    return live, None


def guard_rc():
    """gpu_guard.ps1 with NO arguments (AGENTS): 0 = IDLE. Run through PowerShell, not sh."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUARD],
            capture_output=True, text=True, timeout=120)
        return int(proc.returncode), (proc.stdout or "").strip()
    except Exception as exc:
        return 9, repr(exc)


# ---------------------------------------------------------------- one request

def ask(model_id, still_id, image_path, max_tokens, timeout, prompt_sha, extra=None, arm=None):
    with open(image_path, "rb") as fh:
        blob = fh.read()
    mime = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    dataurl = f"data:{mime};base64," + base64.b64encode(blob).decode()
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": dataurl}},
        ]}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": False,
    }
    body.update(extra or {})
    req = urllib.request.Request(
        BASE + "/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST")
    start = now_iso()
    t0 = time.time()
    status = 0
    raw = ""
    err = ""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = int(resp.status)
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        try:
            raw = exc.read().decode("utf-8", "replace")
        except Exception:
            raw = ""
        err = f"HTTPError {exc.code}"
    except Exception as exc:
        err = repr(exc)
    wall = round(time.time() - t0, 2)
    caption = ""
    finish = ""
    usage = {}
    if raw:
        try:
            doc = json.loads(raw)
        except Exception as exc:
            err = (err + " " if err else "") + f"NON_JSON_BODY {exc!r}"
            doc = {}
        ch = (doc.get("choices") or [{}])[0]
        msg = ch.get("message") or {}
        content = msg.get("content")
        if isinstance(content, list):
            content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
        caption = content if isinstance(content, str) else ("" if content is None else str(content))
        rcontent = msg.get("reasoning_content")
        reasoning = rcontent if isinstance(rcontent, str) else ("" if rcontent is None else str(rcontent))
        finish = ch.get("finish_reason") or ""
        usage = doc.get("usage") if isinstance(doc.get("usage"), dict) else {}
        if status == 200 and (doc.get("error") or doc.get("error_code")):
            err = (err + " " if err else "") + json.dumps(doc.get("error") or doc.get("error_code"))[:400]
    low = caption.lower()
    hits = sorted({m for m in DECLINE_MARKERS if m in low})
    burned = int((usage or {}).get("completion_tokens") or 0)
    # Where the generated text landed: an empty `content` with completion_tokens > 0 means the
    # answer went to a reasoning field, which is a different fault from generating nothing.
    fields = sorted([str(k) for k in (msg or {}).keys()])
    empty = not caption.strip()
    return {
        "model_id": model_id,
        "still_id": still_id,
        "image_path": image_path.replace("\\", "/"),
        "image_bytes": len(blob),
        "image_sha256": sha256_bytes(blob),
        "image_dims": image_dims(image_path),
        "endpoint": BASE + "/v1/chat/completions",
        "prompt_sha": prompt_sha,
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "request_options": dict(extra or {}),
        "arm": arm or ("max_tokens=" + str(max_tokens) + ";opts=" + json.dumps(extra or {}, sort_keys=True)),
        "command": (
            f"python C:/AI/community/notes/ali163_vision_probe.py --run --models {model_id} "
            f"--stills {still_id} --max-tokens {max_tokens}"
            + (" --no-thinking" if (extra or {}).get("reasoning_effort") == "none" else "")
            + (" --arm " + arm if arm else "")
        ),
        "start_iso": start,
        "end_iso": now_iso(),
        "wall_s": wall,
        "http_status": status,
        "finish_reason": finish,
        "usage": usage,
        "caption": caption,
        "reasoning_text": reasoning,
        "reasoning_words": len(reasoning.split()),
        "caption_words": len(caption.split()),
        "caption_chars": len(caption),
        "decline_markers": hits,
        "message_fields": fields,
        "raw_body_excerpt": (raw[:4000] if (status != 200 or empty) else ""),
        "completion_tokens": burned,
        "error": (err + (" " + raw[:400] if status not in (200,) and raw else "")).strip(),
    }


def load_out(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return None


def new_doc(table):
    return {
        "schema": SCHEMA,
        "created_iso": now_iso(),
        "updated_iso": now_iso(),
        "endpoint": BASE + "/v1/chat/completions",
        "prompt_text": PROMPT,
        "prompt_sha": sha256_bytes(PROMPT.encode()),
        "decline_markers": DECLINE_MARKERS,
        "vision_table": table,
        "requested": {"models": [], "stills": []},
        "gates": [],
        "rows": [],
    }


def merge_row(doc, row):
    key = (row["model_id"], row["still_id"], row["prompt_sha"], row["arm"])
    doc["rows"] = [r for r in doc["rows"]
                   if (r.get("model_id"), r.get("still_id"), r.get("prompt_sha"), r.get("arm")) != key]
    doc["rows"].append(row)
    doc["rows"].sort(key=lambda r: (str(r.get("model_id")), str(r.get("still_id")), str(r.get("arm"))))


def save(doc, path):
    doc["updated_iso"] = now_iso()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def add_unique(seq, values):
    for v in values:
        if v not in seq:
            seq.append(v)
    seq.sort()


# ---------------------------------------------------------------- run

def do_run(args):
    table = vision_table()
    by_id = {m["id"]: m for m in table}
    live, live_err = live_models()
    prompt_sha = sha256_bytes(PROMPT.encode())
    rc, guard_text = guard_rc()
    print(f"gpu_guard rc={rc} {guard_text}")
    doc = load_out(args.out)
    if doc is None:
        doc = new_doc(table)
    doc["vision_table"] = table
    doc["gates"].append({"ts_iso": now_iso(), "gpu_guard_rc": rc, "gpu_guard_text": guard_text,
                         "argv": " ".join(sys.argv[1:]), "models_live_error": live_err})
    if rc != 0:
        save(doc, args.out)
        print(f"GPU_NOT_IDLE rc={rc} -> no request sent, no model loaded (PROMPT 9999999)")
        return 7
    models = args.models or sorted(by_id)
    stills = args.stills or sorted(STILLS)
    unknown = [m for m in models if m not in by_id]
    if unknown:
        print(f"NOT_VISION_MEASURED {unknown} - not in the vision set read off {SWAP_YAML}; skipped")
    offline = [m for m in models if m in by_id and m not in live]
    if offline:
        print(f"NOT_IN_LIVE_LIST {offline} - llama-swap does not list them; skipped")
    add_unique(doc["requested"]["models"], [m for m in models if m in by_id and m in live])
    add_unique(doc["requested"]["stills"], stills)
    save(doc, args.out)
    sent = 0
    for mid in models:
        if mid not in by_id or mid not in live:
            continue
        for sid in stills:
            path = os.path.join(STILL_DIR, STILLS[sid])
            if not os.path.exists(path):
                print(f"MISSING_IMAGE {sid} {path} - no request sent for it")
                continue
            row = ask(mid, sid, path, args.max_tokens, args.timeout, prompt_sha,
                      extra=cli_extra(args), arm=args.arm)
            merge_row(doc, row)
            save(doc, args.out)  # paid work lands on disk before the next request
            sent += 1
            head = " ".join(row["caption"].split())[:140]
            print(f"ROW model={mid} still={sid} arm={row['arm']} status={row['http_status']} wall_s={row['wall_s']} "
                  f"finish={row['finish_reason']} answer_words={row['caption_words']} "
                  f"reasoning_words={row['reasoning_words']} "
                  f"declines={len(row['decline_markers'])} err={row['error'][:120]}")
            print(f"  HEAD: {head}")
    ok = sum(1 for r in doc["rows"] if r["http_status"] == 200 and r["caption_words"] > 0)
    print(f"SENT {sent} rows this call; results file rows={len(doc['rows'])} ok={ok} -> {args.out}")
    return 0


# ---------------------------------------------------------------- check

def row_missing(row):
    out = []
    if not str(row.get("model_id") or "").strip():
        out.append("NO_MODEL")
    if not str(row.get("still_id") or "").strip():
        out.append("NO_IMAGE_ID")
    if not str(row.get("command") or "").strip():
        out.append("NO_COMMAND")
    if not str(row.get("endpoint") or "").strip():
        out.append("NO_ENDPOINT")
    if not str(row.get("start_iso") or "").strip() or not str(row.get("end_iso") or "").strip():
        out.append("NO_TIME")
    if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("image_sha256") or "")):
        out.append("NO_SHA")
    if not re.fullmatch(r"[0-9a-f]{16,}", str(row.get("prompt_sha") or "")):
        out.append("NO_PROMPT_SHA")
    if not isinstance(row.get("http_status"), int):
        out.append("NO_STATUS")
    return out


def check(doc, table_ids, prompt_sha, label, strict=False):
    """Two classes, deliberately.
      FAULT   = the file is not trustworthy (missing row/command/time/sha, drift, a judging
                key, a non-vision model id, a duplicate). This is what gates.
      OUTCOME = what a model actually did (non-200, empty caption, burned its whole token
                budget, decline markers). That IS the measurement: reported, never hidden,
                and blocking only under --strict. Nothing here scores/ranks/keeps/judges a
                caption - KEEP is Derrick's (PROMPT 9999999).
    """
    faults = []
    outcomes = []
    rows = doc.get("rows") or []
    if not rows:
        faults.append("NO_ROWS the results file carries no measurement row")
    seen = {}
    for i, row in enumerate(rows):
        code = f"row{i} {row.get('model_id')}/{row.get('still_id')}"
        for f in row_missing(row):
            faults.append(f"{f} {code}")
        for key in row.keys():
            if str(key).lower() in BANNED:
                faults.append(f"BANNED_TOKEN {code} key={key} (this item records 0 scored/kept output)")
        if row.get("http_status") != 200:
            outcomes.append(f"HTTP_ERROR {code} status={row.get('http_status')} "
                            f"wall_s={row.get('wall_s')} err={str(row.get('error'))[:160]}")
        if row.get("http_status") == 200 and not str(row.get("caption") or "").strip():
            burned = int(((row.get("usage") or {}).get("completion_tokens")) or row.get("completion_tokens") or 0)
            rwords = int(row.get("reasoning_words") or 0)
            if rwords > 0:
                outcomes.append(f"CAPTION_IN_REASONING_ONLY {code} arm={row.get('arm')} the answer field is empty while "
                                f"{rwords} words came back in reasoning_content "
                                f"(completion_tokens={burned}, finish={row.get('finish_reason')})")
            elif burned > 0:
                outcomes.append(f"CAPTION_BURNED_TOKENS {code} arm={row.get('arm')} status=200 completion_tokens={burned} "
                                f"finish={row.get('finish_reason')} fields={row.get('message_fields')} "
                                f"with an empty content and no reasoning_content")
            else:
                outcomes.append(f"EMPTY_CAPTION {code} arm={row.get('arm')} status=200, nothing generated, empty caption")
        if row.get("decline_markers"):
            outcomes.append(f"DECLINE_FLAGGED {code} markers={row.get('decline_markers')}")
        if str(row.get("prompt_sha") or "") != prompt_sha:
            faults.append(f"PROMPT_DRIFT {code} row prompt_sha={str(row.get('prompt_sha'))[:12]} != current")
        if str(row.get("model_id") or "") not in table_ids:
            faults.append(f"NOT_VISION {code} model id is not in the vision set measured off the configs")
        key = (row.get("model_id"), row.get("still_id"), row.get("arm"))
        if key in seen:
            faults.append(f"DUPLICATE_ROW {code} duplicates row{seen[key]}")
        seen[key] = i
        seen.setdefault(("pair", row.get("model_id"), row.get("still_id")), i)
        path = str(row.get("image_path") or "")
        if path:
            if not os.path.exists(path):
                faults.append(f"MISSING_IMAGE {code} {path}")
            elif sha256_file(path) != row.get("image_sha256"):
                faults.append(f"IMAGE_DRIFT {code} bytes on disk differ from the measured sha256")
    req = doc.get("requested") or {}
    have = {k[1:] for k in seen if k[0] == "pair"}
    for mid in req.get("models") or []:
        for sid in req.get("stills") or []:
            if (mid, sid) not in have:
                faults.append(f"MISSING_PAIR model={mid} still={sid} was requested and has no row")
    for key in doc.keys():
        if str(key).lower() in BANNED:
            faults.append(f"BANNED_TOKEN top-level key={key}")
    ok = [r for r in rows if r.get("http_status") == 200 and str(r.get("caption") or "").strip()]
    blocked = faults + outcomes if strict else faults
    print(f"vision battery {label}: rows={len(rows)} captioned={len(ok)} "
          f"models={len(set(r.get('model_id') for r in rows))} "
          f"stills={len(set(r.get('still_id') for r in rows))} "
          f"integrity_faults={len(faults)} model_outcomes={len(outcomes)} strict={int(strict)}")
    for f in faults[:40]:
        print("  FAULT " + f)
    for o in outcomes[:40]:
        print("  OUTCOME " + o)
    if blocked:
        print("PROBLEMS " + json.dumps({
            "faults": {k: sum(1 for f in faults if f.split()[0] == k) for k in sorted({f.split()[0] for f in faults})},
            "outcomes": {k: sum(1 for o in outcomes if o.split()[0] == k) for k in sorted({o.split()[0] for o in outcomes})}},
            sort_keys=True))
        print("VERDICT VISION_BATTERY RED")
    else:
        print("VERDICT VISION_BATTERY CLEAN")
    return len(blocked)


def do_check(args):
    doc = load_out(args.out)
    if doc is None:
        print(f"NO_RESULTS_FILE {args.out} - the battery has not been run")
        print("VERDICT VISION_BATTERY RED")
        return 1
    prompt_sha = doc.get("prompt_sha") or sha256_bytes(PROMPT.encode())
    table_ids = {m["id"] for m in (doc.get("vision_table") or [])} or {m["id"] for m in vision_table()}
    n = check(doc, table_ids, prompt_sha, os.path.basename(args.out), strict=args.strict)
    return 1 if n else 0


def do_dump(args):
    doc = load_out(args.out)
    if doc is None:
        print(f"NO_RESULTS_FILE {args.out}")
        return 1
    print(f"# rows in {args.out} (schema {doc.get('schema')}, prompt_sha {str(doc.get('prompt_sha'))[:16]}, "
          f"created {doc.get('created_iso')}, updated {doc.get('updated_iso')})")
    for row in doc.get("rows") or []:
        print(f"\n== model={row.get('model_id')} still={row.get('still_id')} "
              f"status={row.get('http_status')} wall_s={row.get('wall_s')} finish={row.get('finish_reason')} "
              f"answer_words={row.get('caption_words')} reasoning_words={row.get('reasoning_words')} "
              f"declines={row.get('decline_markers')} arm={row.get('arm')}")
        print(f"   usage={json.dumps(row.get('usage') or {})}")
        print(f"   command={row.get('command')}")
        if row.get("error"):
            print(f"   ERROR {str(row['error'])[:300]}")
        print("   " + str(row.get("caption") or "").replace("\n", "\n   "))
    return 0


def do_list(args):
    table = vision_table()
    live, err = live_models()
    print(f"vision set measured off {SWAP_YAML}: {len(table)}")
    for m in table:
        print(f"  {m['id']} aliases={m['aliases']} kinds={m['kinds']}")
        print(f"    evidence: {m['evidence']}")
    print(f"live at {BASE}/v1/models: {json.dumps({k: v['status'] for k, v in live.items()}, ensure_ascii=False)}")
    if err:
        print("  " + err)
    print(f"start stills in {STILL_DIR}: " + ", ".join(f"{k}={STILLS[k]}" for k in sorted(STILLS)))
    return 0


# ---------------------------------------------------------------- selftest (L10)

def fixture(prompt_sha, table_ids):
    """A clean 2x2 fixture over two real start stills: 0 faults is the control."""
    stills = ["BD002", "GI046"]
    models = sorted(table_ids)[:2]
    doc = new_doc([{"id": m, "aliases": [], "kinds": ["fixture"], "evidence": "fixture"} for m in models])
    doc["prompt_sha"] = prompt_sha
    doc["requested"] = {"models": list(models), "stills": list(stills)}
    for mid in models:
        for sid in stills:
            path = os.path.join(STILL_DIR, STILLS[sid]).replace("\\", "/")
            blob = open(path, "rb").read()
            doc["rows"].append({
                "model_id": mid, "still_id": sid, "image_path": path,
                "image_bytes": len(blob), "image_sha256": sha256_bytes(blob), "image_dims": [8, 8],
                "endpoint": BASE + "/v1/chat/completions", "prompt_sha": prompt_sha,
                "max_tokens": 700, "temperature": 0.0, "request_options": {}, "arm": "fixture-arm",
                "command": f"python notes/ali163_vision_probe.py --run --models {mid} --stills {sid}",
                "start_iso": now_iso(), "end_iso": now_iso(), "wall_s": 1.0,
                "http_status": 200, "finish_reason": "stop", "usage": {"completion_tokens": 0},
                "caption": "SCENE: studio. SUBJECT 1: an adult. ACTION: nothing. EDGE: clean.",
                "reasoning_text": "", "reasoning_words": 0,
                "caption_words": 10, "caption_chars": 60, "decline_markers": [], "error": "",
            })
    doc["rows"].sort(key=lambda r: (r["model_id"], r["still_id"]))
    return doc


SEEDS = {
    "http_error": ("HTTP_ERROR", lambda d: d["rows"][0].__setitem__("http_status", 500)),
    "decline_flagged": ("DECLINE_FLAGGED", lambda d: d["rows"][0].__setitem__("decline_markers", ["i cannot"])),
    "no_rows": ("NO_ROWS", lambda d: d.__setitem__("rows", [])),
    "missing_pair": ("MISSING_PAIR", lambda d: d.__setitem__("rows", d["rows"][:-1])),
    "empty_caption": ("EMPTY_CAPTION", lambda d: (d["rows"][0].__setitem__("caption", "   "),
                                                  d["rows"][0].__setitem__("usage", {}))),
    "caption_burned_tokens": ("CAPTION_BURNED_TOKENS", lambda d: (d["rows"][0].__setitem__("caption", ""),
                                                                  d["rows"][0].__setitem__("usage", {"completion_tokens": 700}),
                                                                  d["rows"][0].__setitem__("reasoning_text", ""),
                                                                  d["rows"][0].__setitem__("reasoning_words", 0))),
    "caption_in_reasoning_only": ("CAPTION_IN_REASONING_ONLY", lambda d: (d["rows"][0].__setitem__("caption", ""),
                                                                         d["rows"][0].__setitem__("reasoning_text", "long chain of thought"),
                                                                         d["rows"][0].__setitem__("reasoning_words", 118))),
    "no_model": ("NO_MODEL", lambda d: d["rows"][0].__setitem__("model_id", "")),
    "no_command": ("NO_COMMAND", lambda d: d["rows"][0].__setitem__("command", "")),
    "no_time": ("NO_TIME", lambda d: d["rows"][0].__setitem__("start_iso", "")),
    "no_sha": ("NO_SHA", lambda d: d["rows"][0].__setitem__("image_sha256", "zz")),
    "image_drift": ("IMAGE_DRIFT", lambda d: d["rows"][0].__setitem__("image_sha256", "0" * 64)),
    "missing_image": ("MISSING_IMAGE", lambda d: d["rows"][0].__setitem__("image_path", "C:/no/such/still.jpg")),
    "no_prompt_sha": ("NO_PROMPT_SHA", lambda d: d["rows"][0].__setitem__("prompt_sha", "")),
    "prompt_drift": ("PROMPT_DRIFT", lambda d: d["rows"][0].__setitem__("prompt_sha", "deadbeef"*4)),
    "banned_row_token": ("BANNED_TOKEN", lambda d: d["rows"][0].__setitem__("keep", True)),
    "banned_top_token": ("BANNED_TOKEN", lambda d: d.__setitem__("best", "vl_judge")),
    "not_vision": ("NOT_VISION", lambda d: d["rows"][0].__setitem__("model_id", "a_text_only_model")),
    "duplicate_row": ("DUPLICATE_ROW", lambda d: d["rows"].append(dict(d["rows"][0]))),
}


def do_selftest(args):
    """Seeds run strict=True so a FAULT (file not trustworthy) and an OUTCOME (what a model
    did) both count as "the detector fired"; the real artifact is gated on FAULT only, and
    its OUTCOME counts are printed - the measurement is reported, never hidden."""
    prompt_sha = sha256_bytes(PROMPT.encode())
    table_ids = {"fixture_model_a", "fixture_model_b"}
    base = fixture(prompt_sha, table_ids)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        control = check(base, table_ids, prompt_sha, "fixture-control", strict=True)
    print(f"control fixture: blocked={control} (must be 0)")
    if control:
        for line in buf.getvalue().splitlines():
            if line.strip().startswith(("FAULT", "OUTCOME")):
                print("  CONTROL " + line.strip())
    fired = {}
    silent = []
    for name, (code, mutate) in sorted(SEEDS.items()):
        doc = copy.deepcopy(base)
        mutate(doc)
        buf = io.StringIO()
        with redirect_stdout(buf):
            check(doc, table_ids, prompt_sha, f"seed:{name}", strict=True)
        out = buf.getvalue()
        hits = sorted({re.sub(r"^(FAULT|OUTCOME) ", "", f).split()[0]
                       for f in re.findall(r"^\s+(?:FAULT|OUTCOME) (\S+)", out, re.M)})
        if code in hits:
            fired[name] = hits
        else:
            silent.append(name)
            print(f"  SILENT seed={name} wants {code} fires={hits}")
    real = load_out(args.out)
    real_blocked = "absent"
    real_outcomes = "-"
    if real is not None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            real_blocked = check(real, {m["id"] for m in (real.get("vision_table") or [])} or table_ids,
                                 real.get("prompt_sha") or prompt_sha, "real-artifact", strict=args.strict)
        m = re.search(r"model_outcomes=(\d+)", buf.getvalue())
        real_outcomes = m.group(1) if m else "?"
    print(f"seeds: {len(SEEDS)} fired: {len(fired)} silent: {len(silent)} {silent}")
    print(f"real artifact {args.out}: blocked={real_blocked} model_outcomes={real_outcomes} strict={int(args.strict)}")
    if control == 0 and not silent and real_blocked in (0, "absent"):
        print("VERDICT SELFTEST_CLEAN")
        return 0
    print("VERDICT SELFTEST_RED")
    return 1


def cli_extra(args):
    """Extra request-body keys for an arm. `reasoning_effort: none` and
    `chat_template_kwargs.enable_thinking=false` are the knobs llama.cpp and the Qwen3 chat
    template document for turning thinking off; both are recorded per row so the arm is
    reproducible, and each arm's rows carry their own label."""
    extra = dict(args.extra_json or {})
    if args.no_thinking:
        extra["reasoning_effort"] = "none"
        extra["chat_template_kwargs"] = {"enable_thinking": False}
    return extra


def main(argv=None):
    ap = argparse.ArgumentParser(description="3.17 VISION-BATTERY (see module docstring)")
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--stills", nargs="*", default=None)
    ap.add_argument("--max-tokens", type=int, default=700)
    ap.add_argument("--arm", default=None, help="label recorded on every row of this --run")
    ap.add_argument("--no-thinking", action="store_true",
                   help="send reasoning_effort=none + chat_template_kwargs.enable_thinking=false")
    ap.add_argument("--extra-json", default=None, type=json.loads,
                   help="extra JSON object merged into the request body (recorded per row)")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--strict", action="store_true",
                   help="--check/--selftest: block on model outcomes as well as file faults")
    args = ap.parse_args(argv)
    for sid in (args.stills or []):
        if sid not in STILLS:
            ap.error(f"--stills {sid} is not a known start still ({sorted(STILLS)})")
    if args.list_models:
        return do_list(args)
    if args.run:
        return do_run(args)
    if args.check:
        return do_check(args)
    if args.dump:
        return do_dump(args)
    if args.selftest:
        return do_selftest(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
