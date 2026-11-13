"""Writer calls through the existing llama-swap endpoint (GPU lock gate :8085 -> llama-swap :8080).

The key comes from the LLAMA_SWAP_KEY environment variable, else from pi's models.json provider entry. It is never
logged, printed or put on a command line (Max Architect 3, 2026-11-13).
"""
from __future__ import annotations

import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

PI_MODELS = Path(os.path.expanduser(r"~\.pi\agent\models.json"))


class WriterDown(RuntimeError):
    """The writer server was unreachable or timed out after every retry."""


def _api_key() -> Optional[str]:
    k = os.environ.get("LLAMA_SWAP_KEY")
    if k:
        return k
    try:  # Windows user-scope env (a process started before the variable was set does not see it)
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            v, _ = winreg.QueryValueEx(h, "LLAMA_SWAP_KEY")
            if v:
                return v
    except Exception:
        pass
    try:
        d = json.loads(PI_MODELS.read_text(encoding="utf-8"))
        v = d["providers"]["llama-swap"].get("apiKey")
        if isinstance(v, str) and v:
            return os.environ.get(v, v) if re.fullmatch(r"[A-Z_][A-Z0-9_]*", v) else v
    except Exception:
        pass
    return None


def strip_think(text: str) -> str:
    t = text or ""
    if "</think>" in t:
        t = t.split("</think>")[-1]
    t = re.sub(r"(?s)<\|channel\>thought.*?<channel\|>", "", t)
    return t.strip()


class Client:
    def __init__(self, cfg: Dict[str, Any], log=None):
        self.cfg = cfg
        self.base = cfg.get("endpoint", "http://127.0.0.1:8085/v1").rstrip("/")
        self.model = cfg["model_alias"]
        self.timeout = float(cfg.get("timeout_s", 600))
        self.backoff = list(cfg.get("retry_backoff_s", [10, 30, 90]))
        self.log = log or (lambda *a, **k: None)
        self.calls: List[Dict[str, Any]] = []
        self._fail_after = int(os.environ.get("WP_FAULT_WRITER_DOWN_AFTER", "-1"))  # fault drill only

    def chat(self, messages: List[Dict[str, Any]], sampler: Dict[str, Any], seed: int, max_tokens: int,
             response_format: Optional[Dict[str, Any]] = None, purpose: str = "") -> str:
        body: Dict[str, Any] = {"model": self.model, "messages": messages, "max_tokens": int(max_tokens), "stream": False,
                                "seed": int(seed), "cache_prompt": True}
        for k in ("temperature", "top_p", "top_k", "min_p", "presence_penalty", "frequency_penalty", "repetition_penalty",
                  "penalty_last_n"):
            if sampler.get(k) is not None:
                body[k] = sampler[k]
        if sampler.get("dry_multiplier"):  # passed through; servers without DRY ignore unknown keys
            for k in ("dry_multiplier", "dry_base", "dry_allowed_length", "dry_penalty_last_n", "dry_sequence_breakers"):
                if sampler.get(k) is not None:
                    body[k] = sampler[k]
        body["chat_template_kwargs"] = {"enable_thinking": bool(self.cfg.get("thinking", False))}
        if response_format:
            body["response_format"] = response_format
        data = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        key = _api_key()
        if key:
            headers["Authorization"] = "Bearer " + key
        attempts = [0.0] + [float(b) for b in self.backoff]
        last_err = None
        for n, wait in enumerate(attempts):
            if n:
                self.log("writer_retry", {"purpose": purpose, "attempt": n, "sleep_s": wait, "error": last_err})
                time.sleep(wait)
            t0 = time.time()
            try:
                if 0 <= self._fail_after <= len(self.calls):
                    raise urllib.error.URLError("fault drill: writer server killed")
                req = urllib.request.Request(self.base + "/chat/completions", data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    out = json.loads(r.read().decode("utf-8"))
                msg = out["choices"][0]["message"]
                text = strip_think(msg.get("content") or "")
                usage = out.get("usage") or {}
                self.calls.append({"purpose": purpose, "seconds": round(time.time() - t0, 2), "seed": seed,
                                   "completion_tokens": usage.get("completion_tokens"), "prompt_tokens": usage.get("prompt_tokens"),
                                   "finish": out["choices"][0].get("finish_reason")})
                return text
            except urllib.error.HTTPError as e:
                last_err = f"HTTP {e.code}"
                if e.code < 500 and e.code != 429:
                    raise WriterDown(f"writer HTTP {e.code} ({purpose})")
            except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError) as e:
                last_err = f"{type(e).__name__}: {str(e)[:120]}"
        raise WriterDown(f"writer unreachable after {len(attempts)} tries ({purpose}): {last_err}")
