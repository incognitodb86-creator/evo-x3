# Offline verification: no network, no ComfyUI, no LLM. Mocks comm.http / subprocess.run.
import sys, json, types, subprocess
sys.path.insert(0, r"C:\AI\community\scripts")
import comm
calls = []
def fake_http(url, data=None, timeout=60, method=None):
    calls.append((method or ("POST" if data is not None else "GET"), url.replace(comm.LS, "")))
    if url.endswith("/running"): return {"running": [{"model": "strata"}, {"model": "comfyui_auto"}, {"model": "qwen9b"}]}
    if url.endswith("/system_stats"): return {"system": {"comfyui_version": "mock"}, "devices": [{"vram_free": 0}]}
    return "OK"
comm.http = fake_http; comm.log = lambda *a, **k: None
comm.ensure_comfy()
print("A2 calls:", calls)
assert ("POST", "/api/models/unload/strata") in calls and ("POST", "/api/models/unload/qwen9b") in calls
assert not any(u == "/unload" for _, u in calls) and not any("comfyui_auto" in u and "unload" in u for _, u in calls)
import batch_queue as bq
src = open(bq.__file__, encoding="utf-8").read()
loop = src[src.index("for sh in shots:                                                   # 3)"):src.index("files = [d[\"file\"]")]
assert "ensure_comfy(LF)" in loop and loop.index("ensure_comfy(LF)") < loop.index("r = run(")
print("A2 batch_queue: ensure_comfy inside the per-job loop before run()")
seen = {}
def fake_run(argv, **k):
    seen["argv"] = argv; return types.SimpleNamespace(returncode=0, stderr="")
bq.subprocess.run = fake_run; bq.log = lambda *a, **k: None
bq.upload(r"C:\x\fake.mp4", "fake_run", None)
i = seen["argv"].index("--retries"); print("A3 argv:", seen["argv"][2:]); assert seen["argv"][i+1] == "3"
P = ["prompt A", "prompt B"]
gk = comm.build("i2v", P, "x.png", 768, 1344, 243, 10, 123, "p", ext_frames=238)
gp = comm.build("i2v", P, "x.png", 768, 1344, 243, 10, 123, "p", ext_frames=238, attention="pytorch attention")
diff = [(k, kk) for k in gk for kk in gk[k]["inputs"] if gk[k]["inputs"][kk] != gp.get(k, {}).get("inputs", {}).get(kk)]
print("A5 graph diff (kitchen vs pytorch):", diff, "| node sets equal:", set(gk) == set(gp))
assert diff == [("m_attn", "attention")] and set(gk) == set(gp)
assert gk["m_attn"]["inputs"]["attention"] == "comfy kitchen attention"
print("ALL OK")
