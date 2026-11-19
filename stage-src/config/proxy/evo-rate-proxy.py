#!/usr/bin/env python3
"""
EVO-X3 U14 Loopback Per-Key Rate Limiter & Metadata Logger.
- Listens on 127.0.0.1:8080 (forwarded by Tailscale Serve on 443)
- Forwards authenticated requests to llama-swap on 127.0.0.1:8082
- Rejects missing/invalid bearer keys with HTTP 401
- Blocks /slots unless explicitly authorized (defense in depth alongside --no-slots)
- Enforces per-key concurrency + token-bucket RPM so one caller (e.g. Hermes) cannot starve Forge/pi
- Logs ONLY: time_ct, key_id (name, never secret/prefix), status, model, usage tokens, tok/s
  Never logs request prompts, response content, or key material.
"""

import collections
import hmac
import http.client
import json
import os
import posixpath
import re
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

CT_TZ = ZoneInfo("America/Chicago")

LISTEN_HOST, LISTEN_PORT_STR = os.environ.get("EVO_PROXY_LISTEN", "127.0.0.1:8080").rsplit(":", 1)
LISTEN_PORT = int(LISTEN_PORT_STR)
UPSTREAM_URL = urlparse(os.environ.get("EVO_LLAMASWAP_UPSTREAM", "http://127.0.0.1:8082"))
MAX_CONCURRENT_PER_KEY = int(os.environ.get("EVO_MAX_CONCURRENT_PER_KEY", "4"))
RPM_PER_KEY = int(os.environ.get("EVO_RPM_PER_KEY", "120"))
MAX_BODY_BYTES = int(os.environ.get("EVO_MAX_BODY_BYTES", str(64 * 1024 * 1024)))
# Blocks /slots, //slots, /v1/../slots and llama-swap passthrough /upstream/<model>/slots.
SLOTS_PATH_RE = re.compile(r"^/+(?:upstream/+[^/]+/+)?slots(?:/|$)", re.IGNORECASE)


def load_key_map():
    keys = {}
    for env_name, val in os.environ.items():
        if env_name.startswith("LLM_KEY_") and val:
            keys[env_name] = val
    return keys


KEY_MAP = load_key_map()
KEY_SEMAPHORES = collections.defaultdict(lambda: threading.Semaphore(MAX_CONCURRENT_PER_KEY))
KEY_TIMESTAMPS = collections.defaultdict(collections.deque)
RATE_LOCK = threading.Lock()
LOG_LOCK = threading.Lock()


def identify_key(auth_header: str):
    if not auth_header:
        return None
    parts = auth_header.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    presented = parts[1].strip()
    for key_id, secret in KEY_MAP.items():
        if hmac.compare_digest(presented, secret):
            return key_id
    return None


def log_ct(key_id: str, method: str, path: str, status: int, model: str, tokens_out: int, tok_s: float):
    ts = datetime.now(CT_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    line = json.dumps({
        "time_ct": ts,
        "key_id": key_id or "anonymous",
        "method": method,
        "path": path,
        "status": status,
        "model": model or "-",
        "completion_tokens": tokens_out,
        "decode_tok_s": round(tok_s, 2) if tok_s is not None else None,
    })
    with LOG_LOCK:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


class RateProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Suppress default BaseHTTPRequestHandler stderr logging
        return

    def _send_json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_request_body(self):
        te = self.headers.get("Transfer-Encoding", "").lower()
        if "chunked" in te:
            chunks = []
            total = 0
            while True:
                line = self.rfile.readline(65537)
                if not line:
                    break
                size_str = line.split(b";", 1)[0].strip()
                chunk_len = int(size_str, 16)
                if chunk_len == 0:
                    self.rfile.readline(65537)
                    break
                total += chunk_len
                if total > MAX_BODY_BYTES:
                    raise OverflowError("request body too large")
                chunks.append(self.rfile.read(chunk_len))
                self.rfile.read(2)  # CRLF
            return b"".join(chunks)
        raw_len = self.headers.get("Content-Length", "0") or "0"
        content_len = int(raw_len)
        if content_len < 0:
            raise ValueError("negative Content-Length")
        if content_len > MAX_BODY_BYTES:
            raise OverflowError("request body too large")
        return self.rfile.read(content_len) if content_len > 0 else b""

    def _handle(self):
        parsed = urlparse(self.path)
        norm_path = posixpath.normpath(parsed.path or "/")
        if SLOTS_PATH_RE.match(parsed.path or "") or SLOTS_PATH_RE.match(norm_path):
            self._send_json(401, {"error": "slots endpoint disabled"})
            log_ct(None, self.command, parsed.path, 401, "-", 0, None)
            return

        key_id = identify_key(self.headers.get("Authorization", ""))
        if not key_id:
            self._send_json(401, {"error": "unauthorized"})
            log_ct(None, self.command, parsed.path, 401, "-", 0, None)
            return

        now = time.monotonic()
        with RATE_LOCK:
            dq = KEY_TIMESTAMPS[key_id]
            while dq and now - dq[0] > 60.0:
                dq.popleft()
            if len(dq) >= RPM_PER_KEY:
                self._send_json(429, {"error": "rate limit exceeded", "retry_after_s": 5})
                log_ct(key_id, self.command, parsed.path, 429, "-", 0, None)
                return
            dq.append(now)

        sem = KEY_SEMAPHORES[key_id]
        acquired = sem.acquire(timeout=15.0)
        if not acquired:
            self._send_json(429, {"error": "concurrency limit exceeded for caller"})
            log_ct(key_id, self.command, parsed.path, 429, "-", 0, None)
            return

        req_model = "-"
        conn = None
        try:
            try:
                req_body = self._read_request_body()
            except ValueError:
                self._send_json(400, {"error": "invalid request framing"})
                log_ct(key_id, self.command, parsed.path, 400, "-", 0, None)
                return
            except OverflowError:
                self._send_json(413, {"error": "request body exceeds max limit"})
                log_ct(key_id, self.command, parsed.path, 413, "-", 0, None)
                return

            if req_body and self.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    parsed_json = json.loads(req_body)
                    if isinstance(parsed_json, dict) and isinstance(parsed_json.get("model"), str):
                        req_model = parsed_json["model"]
                except Exception:
                    pass

            fwd_headers = {}
            for h_k, h_v in self.headers.items():
                if h_k.lower() not in ("host", "connection", "transfer-encoding", "content-length"):
                    fwd_headers[h_k] = h_v
            fwd_headers["Content-Length"] = str(len(req_body))

            t0 = time.monotonic()
            try:
                conn = http.client.HTTPConnection(UPSTREAM_URL.hostname, UPSTREAM_URL.port, timeout=600)
                conn.request(self.command, self.path, body=req_body, headers=fwd_headers)
                resp = conn.getresponse()
            except (OSError, http.client.HTTPException):
                self._send_json(502, {"error": "upstream unavailable"})
                log_ct(key_id, self.command, parsed.path, 502, req_model, 0, None)
                return

            resp_ctype = (resp.getheader("Content-Type") or "").lower()
            resp_te = (resp.getheader("Transfer-Encoding") or "").lower()
            is_sse = "text/event-stream" in resp_ctype
            is_chunked = "chunked" in resp_te
            stream_as_chunked = is_chunked or (is_sse and resp.getheader("Content-Length") is None)

            self.send_response(resp.status)
            for r_k, r_v in resp.getheaders():
                lk = r_k.lower()
                if lk in ("connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "upgrade", "transfer-encoding"):
                    continue
                if stream_as_chunked and lk == "content-length":
                    continue
                self.send_header(r_k, r_v)
            if stream_as_chunked:
                self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()

            if stream_as_chunked:
                while True:
                    # read1 returns as soon as any bytes arrive; read(n) would block until n bytes and stall SSE tokens.
                    chunk = resp.read1(65536)
                    if not chunk:
                        self.wfile.write(b"0\r\n\r\n")
                        self.wfile.flush()
                        break
                    self.wfile.write(f"{len(chunk):x}\r\n".encode("ascii") + chunk + b"\r\n")
                    self.wfile.flush()
                log_ct(key_id, self.command, parsed.path, resp.status, req_model, 0, None)
            else:
                resp_body = resp.read()
                self.wfile.write(resp_body)
                self.wfile.flush()
                dt = max(time.monotonic() - t0, 1e-6)
                out_toks = 0
                tok_s = None
                try:
                    rdata = json.loads(resp_body)
                    usage = rdata.get("usage") or {}
                    out_toks = int(usage.get("completion_tokens") or 0)
                    if out_toks > 0:
                        tok_s = out_toks / dt
                except Exception:
                    pass
                log_ct(key_id, self.command, parsed.path, resp.status, req_model, out_toks, tok_s)
        except (BrokenPipeError, ConnectionResetError):
            log_ct(key_id, self.command, parsed.path, 499, req_model, 0, None)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            sem.release()

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_DELETE(self):
        self._handle()


if __name__ == "__main__":
    if not KEY_MAP:
        sys.stderr.write("ERROR: No LLM_KEY_* variables loaded from EnvironmentFile.\n")
        sys.exit(1)
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), RateProxyHandler)
    print(f"evo-rate-proxy listening on {LISTEN_HOST}:{LISTEN_PORT} -> {UPSTREAM_URL.geturl()} ({len(KEY_MAP)} keys loaded)")
    server.serve_forever()
