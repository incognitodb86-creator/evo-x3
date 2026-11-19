#!/usr/bin/env python
"""t4_bridge.py - tiny local file bridge for the browser-side workflow conversion.

Usage: python t4_bridge.py [--dir RUNDIR] [--port 10099] [--log BRIDGE.LOG]

  GET  /get?path=<file>        -> serves a file from the allowed roots (CORS on)
  POST /save?name=<file>       -> writes the request body into the run dir
  GET  /ping                   -> "pong"

Allowed roots: the run dir, C:\\AI\\community\\scripts, C:\\AI\\community\\input.
One request per connection, single-threaded, and it exits after --max-requests
(default 40) so it cannot outlive the task. Logs one line per request.
"""
import http.server
import os
import sys
import urllib.parse

ROOTS = [
    r"C:\AI\community\runs\terrace_dom_q5stockv2_20261028_s51083011",
    r"C:\AI\community\scripts",
    r"C:\AI\community\input",
]
RUN = ROOTS[0]
PORT = 10099
LOG = None
MAXR = 40
NREQ = [0]


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        if LOG:
            with open(LOG, "a", encoding="utf-8") as f:
                f.write("%s %s\n" % (self.log_date_time_string(), fmt % a))

    def send(self, code, body, ctype="application/octet-stream"):
        b = body if isinstance(body, bytes) else str(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self.send(204, b"")

    def resolve(self, rel):
        rel = rel.replace("\\", "/").lstrip("/")
        for root in ROOTS:
            p = os.path.normpath(os.path.join(root, rel))
            if p.startswith(os.path.normpath(root) + os.sep) and os.path.isfile(p):
                return p
        return None

    def do_GET(self):
        NREQ[0] += 1
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/ping":
            return self.send(200, "pong")
        if u.path == "/get":
            p = self.resolve((q.get("path") or [""])[0])
            if not p:
                return self.send(404, "not found or outside allowed roots")
            with open(p, "rb") as f:
                data = f.read()
            self.log_message("GET %s -> %d bytes", (q.get("path") or [""])[0], len(data))
            return self.send(200, data, "application/json" if p.endswith(".json") else "application/octet-stream")
        return self.send(404, "no route")

    def do_POST(self):
        NREQ[0] += 1
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path != "/save":
            return self.send(404, "no route")
        name = (q.get("name") or [""])[0]
        rel = os.path.normpath(os.path.join(RUN, name.replace("\\", "/").lstrip("/")))
        if not rel.startswith(RUN):
            return self.send(400, "bad name")
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        with open(rel, "wb") as f:
            f.write(data)
        self.log_message("POST %s -> %s (%d bytes)", name, rel, len(data))
        return self.send(200, "wrote %d bytes to %s" % (len(data), rel))


def main():
    global RUN, PORT, LOG, MAXR
    for i, a in enumerate(sys.argv):
        if a == "--dir":
            RUN = ROOTS[0] = os.path.abspath(sys.argv[i + 1])
            ROOTS[0] = RUN
        if a == "--port":
            PORT = int(sys.argv[i + 1])
        if a == "--log":
            LOG = sys.argv[i + 1]
        if a == "--max-requests":
            MAXR = int(sys.argv[i + 1])
    srv = http.server.HTTPServer(("127.0.0.1", PORT), H)
    print("bridge on http://127.0.0.1:%d roots=%s" % (PORT, ROOTS), flush=True)
    while NREQ[0] < MAXR:
        srv.handle_request()
    print("bridge done after %d requests" % NREQ[0], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
