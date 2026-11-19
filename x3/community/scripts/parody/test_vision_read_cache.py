"""RP1 tests: vision_read() sha256 JSON cache and <=1024px JPEG downscale."""
import base64
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_request as br
import render_writer_pipeline as rwp


def _make_png(path: Path, size=(64, 48), color=(120, 80, 200)) -> Path:
    im = Image.new("RGB", size, color)
    im.save(path, "PNG")
    return path


def _decode_data_url(messages):
    url = messages[0]["content"][1]["image_url"]["url"]
    header, b64 = url.split(",", 1)
    raw = base64.b64decode(b64)
    im = Image.open(io.BytesIO(raw))
    im.load()
    return header, im


def test_vision_read_cache_same_still_once_different_bytes_twice(tmp_path, monkeypatch):
    still = _make_png(tmp_path / "still_a.png", size=(320, 240), color=(10, 20, 30))
    cache_dir = tmp_path / "_still_read_cache"
    calls = []

    def fake_chat(messages):
        calls.append(messages)
        return json.dumps({"room": "bedroom", "surface": "bed", "people": "one woman"})

    # Default cache_dir=None: cache is off by default
    br.vision_read(still, fake_chat)
    br.vision_read(still, fake_chat)
    assert len(calls) == 2

    calls.clear()
    r1 = br.vision_read(still, fake_chat, cache_dir=cache_dir, model_alias="vision_v1")
    r2 = br.vision_read(still, fake_chat, cache_dir=cache_dir, model_alias="vision_v1")
    assert len(calls) == 1
    assert r1 == r2 == {"room": "bedroom", "surface": "bed", "people": "one woman"}

    digest = hashlib.sha256(still.read_bytes()).hexdigest()
    sig = br._still_cache_suffix("vision_v1")
    cache_file = cache_dir / f"{digest}_{sig}.json"
    assert cache_file.is_file()
    doc = json.loads(cache_file.read_text(encoding="utf-8"))
    assert doc["read"] == r1 and doc["sha256"] == digest and doc["prompt_sha8"] == sig and doc["model_alias"] == "vision_v1"

    # Different model alias -> cache miss
    br.vision_read(still, fake_chat, cache_dir=cache_dir, model_alias="vision_v2")
    assert len(calls) == 2

    # Changed VISION_READ_PROMPT -> cache miss
    monkeypatch.setattr(br, "VISION_READ_PROMPT", br.VISION_READ_PROMPT + "\n# extra")
    br.vision_read(still, fake_chat, cache_dir=cache_dir, model_alias="vision_v1")
    assert len(calls) == 3

    # Different bytes -> cache miss
    still_b = _make_png(tmp_path / "still_b.png", size=(320, 240), color=(200, 150, 50))
    r3 = br.vision_read(still_b, fake_chat, cache_dir=cache_dir, model_alias="vision_v1")
    assert len(calls) == 4
    assert r3["room"] == "bedroom"


def test_vision_read_sends_jpeg_resized_keeping_aspect_le_1024(tmp_path):
    big = _make_png(tmp_path / "big.png", size=(2000, 1000), color=(80, 160, 240))
    seen = []

    def fake_chat(messages):
        seen.append(_decode_data_url(messages))
        return json.dumps({"room": "living room", "surface": "sofa"})

    br.vision_read(big, fake_chat, cache_dir=tmp_path / "cache")
    assert len(seen) == 1
    header, im = seen[0]
    assert header == "data:image/jpeg;base64"
    assert im.format == "JPEG"
    assert max(im.size) <= 1024
    assert im.size == (1024, 512)

    # Small image is not upscaled and still sent as JPEG
    small = _make_png(tmp_path / "small.png", size=(400, 600), color=(240, 80, 160))
    br.vision_read(small, fake_chat, cache_dir=tmp_path / "cache")
    header2, im2 = seen[1]
    assert header2 == "data:image/jpeg;base64"
    assert im2.format == "JPEG"
    assert im2.size == (400, 600)


def test_pipeline_ensure_still_read_reuses_runs_root_cache(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    monkeypatch.setattr(rwp, "RUNS_ROOT", runs_root)
    still = _make_png(tmp_path / "shared.png", size=(1600, 800), color=(30, 90, 150))

    class StubClient:
        def __init__(self):
            self.n = 0

        def chat(self, messages, *args, **kwargs):
            self.n += 1
            return json.dumps({"room": "studio", "surface": "floor"})

    client = StubClient()
    cfg = {"model_alias": "test_vision"}
    rd1 = runs_root / "run_1"
    rd2 = runs_root / "run_2"
    rd1.mkdir(parents=True)
    rd2.mkdir(parents=True)

    d1 = rwp._ensure_still_read_raw(rd1, str(still), None, client, cfg, lambda *a: None)
    d2 = rwp._ensure_still_read_raw(rd2, str(still), None, client, cfg, lambda *a: None)
    assert client.n == 1
    assert d1["read"] == d2["read"] == {"room": "studio", "surface": "floor"}
    assert (rd1 / "still_read.json").is_file()
    assert (rd2 / "still_read.json").is_file()
