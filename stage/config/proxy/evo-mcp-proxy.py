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

    def _handle(self):
        key_id = identify_mcp_key(self.headers.get("Authorization", ""))
        if not key_id:
            body = json.dumps({"error": "MCP bearer token required (LLM keys rejected)"}).encode("utf-8")
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self._log(None, 401)
            return

        content_len = int(self.headers.get("Content-Length", "0") or "0")
        req_body = self.rfile.read(content_len) if content_len > 0 else b""
        fwd_headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in ("host", "connection", "authorization", "transfer-encoding")
        }

        conn = http.client.HTTPConnection(UPSTREAM_URL.hostname, UPSTREAM_URL.port, timeout=120)
        conn.request(self.command, self.path, body=req_body, headers=fwd_headers)
        resp = conn.getresponse()

        self.send_response(resp.status)
        for r_k, r_v in resp.getheaders():
            if r_k.lower() not in ("connection", "keep-alive", "transfer-encoding"):
                self.send_header(r_k, r_v)
        resp_body = resp.read()
        self.send_header("Content-Length", str(len(resp_body)))
        self.end_headers()
        self.wfile.write(resp_body)
        self.wfile.flush()
        conn.close()
        self._log(key_id, resp.status)

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
