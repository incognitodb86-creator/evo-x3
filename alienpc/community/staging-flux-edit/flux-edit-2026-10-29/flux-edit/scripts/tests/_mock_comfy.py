"""In-process mock of llama-swap + ComfyUI (/comfyui proxy) for driver tests. Outputs are copies of synthetic inputs."""
import json
import os
import shutil
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from PIL import Image


class State:
    def __init__(self, cin, cout):
        self.cin, self.cout = cin, cout
        self.running = [{"model": "llm_a", "state": "ready"}]
        self.running_seq = []          # responses returned first, one per GET /running
        self.stats_fail_n = 0
        self.version = "0.38.0"
        self.lora_opts = ["bfs_head_v1_flux-klein_9b_step3750_rank64.safetensors", "TripleView.safetensors"]
        self.evict, self.error, self.wrong_wh = set(), set(), set()
        self.prompts, self.history = {}, {}
        self.log = []                  # (method, path)
        self.lock = threading.Lock()

    def tag_of(self, g):
        return [n for n in g.values() if n["class_type"] == "SaveImage"][0]["inputs"]["filename_prefix"].split("/")[-1]

    def execute(self, pid):
        g = self.prompts[pid]
        tag = self.tag_of(g)
        base = tag[:-3] if tag.endswith("_r1") else tag
        if tag in self.evict:
            self.evict.discard(tag)
            del self.prompts[pid]
            return None
        if base in self.error and not tag.endswith("_r1"):
            return {"status": {"status_str": "error", "messages": [["execution_error", {"node_type": "VAEDecode"}]]},
                    "outputs": {}}
        body = [n for n in g.values() if n["_meta"]["title"] == "picture1_body"][0]["inputs"]["image"]
        src = os.path.join(self.cin, *body.split("/"))
        os.makedirs(os.path.join(self.cout, "flux_edit"), exist_ok=True)
        fn = f"{tag}_00001_.png"
        dst = os.path.join(self.cout, "flux_edit", fn)
        if base in self.wrong_wh:
            with Image.open(src) as im:
                im.resize((im.width // 2, im.height // 2)).save(dst)
        else:
            shutil.copyfile(src, dst)
        return {"status": {"status_str": "success"},
                "outputs": {"24": {"images": [{"filename": fn, "subfolder": "flux_edit", "type": "output"}]}}}


def make_handler(S):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, obj):
            raw = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            with S.lock:
                S.log.append(("GET", self.path))
                p = self.path
                if p == "/running":
                    r = S.running_seq.pop(0) if S.running_seq else {"running": S.running}
                    return self._send(200, r)
                if p == "/comfyui/system_stats":
                    if S.stats_fail_n > 0:
                        S.stats_fail_n -= 1
                        return self._send(503, {"error": "starting"})
                    return self._send(200, {"system": {"comfyui_version": S.version}, "devices": [{}]})
                if p == "/comfyui/object_info/LoraLoaderModelOnly":
                    return self._send(200, {"LoraLoaderModelOnly": {"input": {"required": {"lora_name": [S.lora_opts]}}}})
                if p.startswith("/comfyui/history/"):
                    pid = p.rsplit("/", 1)[1]
                    if pid in S.history:
                        return self._send(200, {pid: S.history[pid]})
                    if pid in S.prompts:
                        h = S.execute(pid)
                        if h is not None:
                            S.history[pid] = h
                            return self._send(200, {pid: h})
                    return self._send(200, {})
                if p == "/comfyui/queue":
                    return self._send(200, {"queue_running": [], "queue_pending": []})
                return self._send(404, {})

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            with S.lock:
                S.log.append(("POST", self.path))
                if self.path == "/comfyui/prompt":
                    pid = uuid.uuid4().hex
                    S.prompts[pid] = body["prompt"]
                    return self._send(200, {"prompt_id": pid, "number": len(S.prompts)})
                if self.path.startswith("/api/models/unload/"):
                    m = self.path.rsplit("/", 1)[1]
                    S.running = [e for e in S.running if e["model"] != m]
                    return self._send(200, {"msg": "ok"})
                return self._send(404, {})
    return H


class Mock:
    def __init__(self, cin, cout):
        self.S = State(cin, cout)
        self.srv = ThreadingHTTPServer(("localhost", 0), make_handler(self.S))
        self.url = f"http://localhost:{self.srv.server_address[1]}"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()

    def posts(self, path="/comfyui/prompt"):
        return sum(1 for m, p in self.S.log if m == "POST" and p == path)
