#!/usr/bin/env python3
"""
EVO-X3 U18 Playwright MCP Bearer Auth Proxy.
- Listens on 127.0.0.1:8930 (loopback only until TOOLS PORT gate card is approved)
- Validates caller against MCP_KEY_* environment variables ONLY (never accepts LLM_KEY_*)
- Forwards authorized requests to containerized Playwright MCP at 127.0.0.1:8931
- Logs ONLY time_ct, caller key_id, HTTP method/path, and status
"""

import hmac
import http.client
import json
import os
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

CT_TZ = ZoneInfo("America/Chicago")

LISTEN_HOST, LISTEN_PORT_STR = os.environ.get("MCP_PROXY_LISTEN", "127.0.0.1:8930").rsplit(":", 1)
LISTEN_PORT = int(LISTEN_PORT_STR)
UPSTREAM_URL = urlparse(os.environ.get("MCP_UPSTREAM", "http://127.0.0.1:8931"))
MAX_BODY_BYTES = int(os.environ.get("MCP_MAX_BODY_BYTES", str(16 * 1024 * 1024)))


def load_mcp_keys():
    keys = {}
    for env_name, val in os.environ.items():
        if env_name.startswith("MCP_KEY_") and val:
            keys[env_name] = val
    return keys


MCP_KEYS = load_mcp_keys()


def identify_mcp_key(auth_header: str):
    if not auth_header:
        return None
    parts = auth_header.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    presented = parts[1].strip()
    for key_id, secret in MCP_KEYS.items():
        if hmac.compare_digest(presented, secret):
            return key_id
    return None


class McpProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        return

    def _log(self, key_id, status):
        ts = datetime.now(CT_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
        sys.stdout.write(json.dumps({
            "time_ct": ts,
            "key_id": key_id or "unauthorized",
            "method": self.command,
            "path": self.path,
            "status": status,
        }) + "\n")
        sys.stdout.flush()

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
                chunk_len = int(line.split(b";", 1)[0].strip(), 16)
                if chunk_len == 0:
                    self.rfile.readline(65537)
                    break
                total += chunk_len
                if total > MAX_BODY_BYTES:
                    raise OverflowError("request body too large")
                chunks.append(self.rfile.read(chunk_len))
                self.rfile.read(2)
            return b"".join(chunks)
        raw_len = self.headers.get("Content-Length", "0") or "0"
        content_len = int(raw_len)
        if content_len < 0:
            raise ValueError("negative Content-Length")
        if content_len > MAX_BODY_BYTES:
            raise OverflowError("request body too large")
        return self.rfile.read(content_len) if content_len > 0 else b""

    def _handle(self):
        key_id = identify_mcp_key(self.headers.get("Authorization", ""))
        if not key_id:
            self._send_json(401, {"error": "MCP bearer token required (LLM keys rejected)"})
            self._log(None, 401)
            return

        conn = None
        try:
            try:
                req_body = self._read_request_body()
            except ValueError:
                self._send_json(400, {"error": "invalid request framing"})
                self._log(key_id, 400)
                return
            except OverflowError:
                self._send_json(413, {"error": "request body exceeds max limit"})
                self._log(key_id, 413)
                return

            fwd_headers = {
                k: v for k, v in self.headers.items()
                if k.lower() not in ("host", "connection", "authorization", "transfer-encoding", "content-length")
            }
            fwd_headers["Content-Length"] = str(len(req_body))

            try:
                conn = http.client.HTTPConnection(UPSTREAM_URL.hostname, UPSTREAM_URL.port, timeout=300)
                conn.request(self.command, self.path, body=req_body, headers=fwd_headers)
                resp = conn.getresponse()
            except (OSError, http.client.HTTPException):
                self._send_json(502, {"error": "upstream unavailable"})
                self._log(key_id, 502)
                return

            resp_ctype = (resp.getheader("Content-Type") or "").lower()
            resp_te = (resp.getheader("Transfer-Encoding") or "").lower()
            is_sse = "text/event-stream" in resp_ctype
            is_chunked = "chunked" in resp_te
            stream_as_chunked = is_chunked or (is_sse and resp.getheader("Content-Length") is None)

            self.send_response(resp.status)
            for r_k, r_v in resp.getheaders():
                lk = r_k.lower()
                if lk in ("connection", "keep-alive", "transfer-encoding"):
                    continue
                if stream_as_chunked and lk == "content-length":
                    continue
                self.send_header(r_k, r_v)
            if stream_as_chunked:
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                while True:
                    chunk = resp.read1(65536)
                    if not chunk:
                        self.wfile.write(b"0\r\n\r\n")
                        self.wfile.flush()
                        break
                    self.wfile.write(f"{len(chunk):x}\r\n".encode("ascii") + chunk + b"\r\n")
                    self.wfile.flush()
            else:
                resp_body = resp.read()
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
                self.wfile.flush()
            self._log(key_id, resp.status)
        except (BrokenPipeError, ConnectionResetError):
            self._log(key_id, 499)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_DELETE(self):
        self._handle()


if __name__ == "__main__":
    if not MCP_KEYS:
        sys.stderr.write("ERROR: No MCP_KEY_* variables loaded from /etc/evo-x3/mcp.env.\n")
        sys.exit(1)
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), McpProxyHandler)
    print(f"evo-mcp-proxy listening on {LISTEN_HOST}:{LISTEN_PORT} -> {UPSTREAM_URL.geturl()} ({len(MCP_KEYS)} keys loaded)")
    server.serve_forever()
