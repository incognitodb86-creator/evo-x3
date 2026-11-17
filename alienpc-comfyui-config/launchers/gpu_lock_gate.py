#!/usr/bin/env python3
"""
GPU Lock Gate: Reverse proxy holding LLM requests during active GPU renders.

Forwards all HTTP methods and paths to an upstream server (e.g. llama-swap on
http://127.0.0.1:8080), streaming responses through (including SSE chunks).
On POST /v1/chat/completions and POST /v1/completions, checks a lock file
(default: C:\\AI\\locks\\gpu-render.lock). If the first integer is a live PID,
polls every 1 s for up to 1800 s. On timeout, returns 503 with Retry-After: 30.
A missing lock file, dead PID, or unparseable file forwards immediately.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import http.client
import http.server
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
from typing import Any
import urllib.parse

# Hop-by-hop headers per RFC 7230 / RFC 2616 that should not be proxied directly
HOP_BY_HOP_HEADERS: frozenset[str] = frozenset({
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "proxy-connection",
})


def is_pid_alive(pid: int, max_start_time: float | None = None) -> bool:
    """Check whether a process with the given PID is currently alive (and not a recycled PID started after max_start_time)."""
    if pid <= 0:
        return False
    if os.name == "nt":
        # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        exit_code = ctypes.c_ulong()
        success = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        if not success or exit_code.value != 259:  # STILL_ACTIVE = 259
            ctypes.windll.kernel32.CloseHandle(handle)
            return False
        if max_start_time is not None:
            ct = ctypes.c_ulonglong()
            et = ctypes.c_ulonglong()
            kt = ctypes.c_ulonglong()
            ut = ctypes.c_ulonglong()
            if ctypes.windll.kernel32.GetProcessTimes(
                handle, ctypes.byref(ct), ctypes.byref(et), ctypes.byref(kt), ctypes.byref(ut)
            ):
                proc_start = (ct.value - 116444736000000000) / 10_000_000.0
                if proc_start > max_start_time:
                    ctypes.windll.kernel32.CloseHandle(handle)
                    return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_lock_holder(lock_path: Path) -> int | None:
    """
    Return the live PID holding the GPU lock, or None if missing, unparseable, or stale.

    If the lock file exists and the first integer found corresponds to a live PID
    whose creation time is not after the lock timestamp, returns that PID.
    Otherwise returns None so callers can forward immediately.
    """
    if not lock_path.is_file():
        return None
    try:
        raw = lock_path.read_text(encoding="utf-8", errors="replace")
        mtime = lock_path.stat().st_mtime
    except OSError:
        return None

    match = re.search(r"(\d+)", raw)
    if not match:
        return None

    try:
        pid = int(match.group(1))
    except ValueError:
        return None

    lock_time = mtime
    ts_match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?)", raw)
    if ts_match:
        try:
            iso_ts = datetime.datetime.fromisoformat(ts_match.group(1)).timestamp()
            if abs(mtime - iso_ts) <= 3600:
                lock_time = min(mtime, iso_ts)
        except ValueError:
            pass

    return pid if is_pid_alive(pid, max_start_time=lock_time + 5.0) else None


def check_lock(
    lock_path: Path,
    max_wait: float,
    poll_interval: float,
) -> tuple[bool, float, int | None, bool]:
    """
    Check if the GPU render lock is held by a live PID, polling until release or timeout.

    Returns:
        tuple: (was_held, duration_waited_sec, initial_pid, timed_out)
    """
    initial_holder = get_lock_holder(lock_path)
    if initial_holder is None:
        return (False, 0.0, None, False)

    start_time = time.monotonic()
    current_pid: int | None = initial_holder

    while True:
        elapsed = time.monotonic() - start_time
        if elapsed >= max_wait:
            return (True, elapsed, initial_holder, True)

        sleep_time = min(poll_interval, max_wait - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

        current_pid = get_lock_holder(lock_path)
        if current_pid is None:
            # Lock released or process exited
            total_waited = time.monotonic() - start_time
            return (True, total_waited, initial_holder, False)


def log_held_request(
    log_path: Path,
    path: str,
    pid: int | None,
    held_sec: float,
    status: str,
) -> None:
    """Log one line to the log file for each request held by the lock."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} path={path} pid={pid} held_sec={held_sec:.2f} status={status}\n"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as err:
        sys.stderr.write(f"Failed to write to log file {log_path}: {err}\n")


class GpuLockGateHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler reverse-proxying all methods to upstream with lock checks."""

    protocol_version = "HTTP/1.1"

    # Forward all standard HTTP verbs to handle_proxy
    def handle(self) -> None:
        """Handle multiple requests if necessary, catching client disconnects cleanly."""
        self.close_connection = True
        try:
            self.handle_one_request()
            while not self.close_connection:
                self.handle_one_request()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def do_GET(self) -> None:
        self.handle_proxy()

    def do_POST(self) -> None:
        self.handle_proxy()

    def do_PUT(self) -> None:
        self.handle_proxy()

    def do_DELETE(self) -> None:
        self.handle_proxy()

    def do_PATCH(self) -> None:
        self.handle_proxy()

    def do_HEAD(self) -> None:
        self.handle_proxy()

    def do_OPTIONS(self) -> None:
        self.handle_proxy()

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default stderr logging unless verbose is requested."""
        server: GpuLockGateServer = self.server  # type: ignore[assignment]
        if getattr(server, "verbose", False):
            super().log_message(format, *args)

    def handle_proxy(self) -> None:
        """Handle incoming request, wait on lock if applicable, and forward upstream."""
        server: GpuLockGateServer = self.server  # type: ignore[assignment]
        method = self.command.upper()
        parsed_url = urllib.parse.urlsplit(self.path)
        req_path = parsed_url.path.rstrip("/")

        # Read request body if present
        body: bytes | None = None
        content_length_header = self.headers.get("Content-Length")
        if content_length_header is not None:
            try:
                length = int(content_length_header)
                body = self.rfile.read(length) if length > 0 else b""
            except (ValueError, OSError) as err:
                self.send_error_response(400, f"Invalid Content-Length or read error: {err}")
                return
        elif self.headers.get("Transfer-Encoding", "").lower() == "chunked":
            # Handle chunked request body if sent by client
            try:
                chunks: list[bytes] = []
                while True:
                    line = self.rfile.readline()
                    chunk_size = int(line.split(b";")[0].strip(), 16)
                    if chunk_size == 0:
                        while True:
                            trailer = self.rfile.readline()
                            if trailer in (b"\r\n", b"\n", b""):
                                break
                        break
                    chunks.append(self.rfile.read(chunk_size))
                    self.rfile.read(2)  # consume CRLF
                body = b"".join(chunks)
            except (ValueError, OSError) as err:
                self.send_error_response(400, f"Invalid chunked body: {err}")
                return

        # Check lock only on POST /v1/chat/completions (and /v1/completions)
        if method == "POST" and req_path in ("/v1/chat/completions", "/v1/completions"):
            was_held, held_sec, initial_pid, timed_out = check_lock(
                lock_path=server.lock_path,
                max_wait=server.max_wait,
                poll_interval=server.poll_interval,
            )
            if was_held:
                status_str = "timed_out_503" if timed_out else "forwarded"
                log_held_request(
                    log_path=server.log_path,
                    path=req_path,
                    pid=initial_pid,
                    held_sec=held_sec,
                    status=status_str,
                )
                if timed_out:
                    self.send_503_timeout(initial_pid, held_sec)
                    return

        # Determine target path on upstream
        if server.upstream_path:
            target_path = server.upstream_path + self.path
        else:
            target_path = self.path

        # Prepare headers for upstream
        upstream_headers: dict[str, str] = {}
        for key, value in self.headers.items():
            k_lower = key.lower()
            if k_lower not in HOP_BY_HOP_HEADERS and k_lower != "host":
                upstream_headers[key] = value

        upstream_headers["Host"] = f"{server.upstream_host}:{server.upstream_port}"
        if body is not None:
            upstream_headers["Content-Length"] = str(len(body))

        # Forward request to upstream
        conn: http.client.HTTPConnection | None = None
        try:
            conn = http.client.HTTPConnection(
                server.upstream_host,
                server.upstream_port,
                timeout=server.upstream_timeout,
            )
            conn.request(method, target_path, body=body, headers=upstream_headers)
            resp = conn.getresponse()

            # Forward response status
            self.send_response_only(resp.status, resp.reason)

            # Determine response headers to forward
            upstream_content_length = resp.getheader("Content-Length")
            for k, v in resp.getheaders():
                k_lower = k.lower()
                if k_lower in HOP_BY_HOP_HEADERS:
                    continue
                self.send_header(k, v)

            has_body = (
                method != "HEAD"
                and resp.status not in (204, 304)
                and not (100 <= resp.status < 200)
            )

            if not has_body:
                self.end_headers()
                return

            if upstream_content_length is not None:
                # Content-Length is already in headers
                self.end_headers()
                content_len = int(upstream_content_length)
                remaining = content_len
                while remaining > 0:
                    read_chunk = resp.read(min(remaining, 65536))
                    if not read_chunk:
                        break
                    self.wfile.write(read_chunk)
                    remaining -= len(read_chunk)
                self.wfile.flush()
            else:
                # No Content-Length: stream using chunked transfer encoding (SSE / dynamic)
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()

                read_func = getattr(resp, "read1", resp.read)
                while True:
                    chunk = read_func(8192)
                    if not chunk:
                        break
                    chunk_header = f"{len(chunk):X}\r\n".encode("ascii")
                    self.wfile.write(chunk_header + chunk + b"\r\n")
                    self.wfile.flush()

                # Terminating chunk
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()

        except (BrokenPipeError, ConnectionResetError):
            # Downstream client disconnected prematurely
            pass
        except OSError as err:
            self.send_error_response(502, f"Bad Gateway: upstream connection error ({err})")
        finally:
            if conn is not None:
                conn.close()

    def send_503_timeout(self, pid: int | None, waited_sec: float) -> None:
        """Send 503 Service Unavailable with Retry-After: 30 when lock wait times out."""
        error_payload = {
            "error": {
                "message": (
                    f"GPU lock held by PID {pid}; request timed out after {waited_sec:.1f}s"
                ),
                "type": "gpu_busy_timeout",
                "code": 503,
            }
        }
        body = json.dumps(error_payload).encode("utf-8")
        self.send_response(503, "Service Unavailable")
        self.send_header("Content-Type", "application/json")
        self.send_header("Retry-After", "30")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(body)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_error_response(self, code: int, message: str) -> None:
        """Send a formatted JSON error response to client."""
        body = json.dumps({
            "error": {
                "message": message,
                "code": code,
            }
        }).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(body)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass


class GpuLockGateServer(http.server.ThreadingHTTPServer):
    """Threading HTTP server carrying configuration for the lock gate proxy."""

    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[http.server.BaseHTTPRequestHandler],
        upstream: str,
        lock_path: Path,
        max_wait: float,
        poll_interval: float,
        log_path: Path,
        upstream_timeout: float = 1900.0,
        verbose: bool = False,
    ) -> None:
        super().__init__(server_address, handler_class)
        self.lock_path = lock_path
        self.max_wait = max_wait
        self.poll_interval = poll_interval
        self.log_path = log_path
        self.upstream_timeout = upstream_timeout
        self.verbose = verbose

        parsed = urllib.parse.urlsplit(upstream)
        self.upstream_host = parsed.hostname or "127.0.0.1"
        self.upstream_port = parsed.port or (443 if parsed.scheme == "https" else 80)
        self.upstream_path = parsed.path.rstrip("/")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="GPU Lock Gate reverse proxy for LLM completion requests",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("GPU_LOCK_GATE_PORT", "8085")),
        help="Port to bind (default: 8085)",
    )
    parser.add_argument(
        "--upstream",
        default=os.environ.get("GPU_LOCK_GATE_UPSTREAM", "http://127.0.0.1:8080"),
        help="Upstream URL to proxy requests to (default: http://127.0.0.1:8080)",
    )
    parser.add_argument(
        "--lock-path",
        type=Path,
        default=Path(os.environ.get("GPU_LOCK_FILE", r"C:\AI\locks\gpu-render.lock")),
        help=r"Path to the GPU lock file (default: C:\AI\locks\gpu-render.lock)",
    )
    parser.add_argument(
        "--max-wait",
        type=float,
        default=1800.0,
        help="Maximum wait time in seconds for lock to clear before 503 (default: 1800)",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Lock check poll interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path(r"C:\AI\director\logs\gpu_lock_gate.log"),
        help=r"Log file path for held requests (default: C:\AI\director\logs\gpu_lock_gate.log)",
    )
    parser.add_argument(
        "--upstream-timeout",
        type=float,
        default=1900.0,
        help="Timeout in seconds for upstream HTTP connections (default: 1900.0)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose access logging to stderr",
    )
    return parser.parse_args(argv)


def main() -> None:
    """Entry point to launch the GPU lock gate server."""
    args = parse_args()
    server = GpuLockGateServer(
        server_address=(args.host, args.port),
        handler_class=GpuLockGateHandler,
        upstream=args.upstream,
        lock_path=args.lock_path,
        max_wait=args.max_wait,
        poll_interval=args.poll_interval,
        log_path=args.log_path,
        upstream_timeout=args.upstream_timeout,
        verbose=args.verbose,
    )
    if args.verbose:
        sys.stderr.write(
            f"GPU Lock Gate listening on {args.host}:{args.port} -> {args.upstream}\n"
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
