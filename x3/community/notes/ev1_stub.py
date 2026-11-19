"""EV1 stub webhook listener (ALI-179 test only, CPU, loopback).

Listens on 127.0.0.1:<port> and records every POST to notes/ev1_stub_capture.jsonl:
the path, the header NAMES, the length of every header that carried the shared key (never the value),
and the parsed JSON body. Nothing secret is stored: the dummy key value is only compared by length.

Usage:  python ev1_stub.py <port> [capture.jsonl]
A POST answers {"ok": true}. Empty POST = the readiness probe (answered, not recorded).
"""
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8231
CAP = sys.argv[2] if len(sys.argv) > 2 else "C:/AI/community/notes/ev1_stub_capture.jsonl"
KEY_LEN = int(sys.argv[3]) if len(sys.argv) > 3 else 0   # dummy key length, for the "key arrived" assertion


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        b = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        self._send({"ok": True, "stub": "alive"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        if not raw.strip():
            self._send({"ok": True, "stub": "alive"})
            return
        key_hdrs = {k: len(v) for k, v in self.headers.items()
                    if "key" in k.lower() or "authorization" in k.lower() or "token" in k.lower()}
        try:
            body = json.loads(raw)
        except Exception as e:  # noqa: BLE001
            body = {"_unparsed": raw, "_err": str(e)}
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "path": self.path,
            "content_type": self.headers.get("Content-Type"),
            "header_names": sorted(self.headers.keys()),
            "key_headers_len": key_hdrs,
            "key_arrived": any(v == KEY_LEN for v in key_hdrs.values()) if KEY_LEN else None,
            "body": body,
            "body_keys": sorted(body.keys()) if isinstance(body, dict) else None,
        }
        with open(CAP, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._send({"ok": True, "recorded": True})


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
