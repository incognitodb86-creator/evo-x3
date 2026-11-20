import wave, json, hashlib
from pathlib import Path
import numpy as np

work = Path(r"C:\Users\derek\AppData\Local\Temp\rv30v2_diag_audio")

def load(name):
    p = work / name
    with wave.open(str(p), "rb") as w:
        ch, sw, sr, nf = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(nf)
    assert sw == 2
    s = np.frombuffer(raw, dtype=np.int16)
    return s, ch, sr, nf, hashlib.sha256(raw).hexdigest()

def mono(s, ch):
    x = s.astype(np.float64)
    return 0.5 * (x[0::2] + x[1::2]) if ch == 2 else x

def stats(a, ch):
    x = a.astype(np.float64)
    m = mono(a, ch)
    return {
        "pcm_sha256": None,  # filled by caller
        "n": int(a.size),
        "rms": float(np.sqrt(np.mean(x*x))),
        "peak": int(np.max(np.abs(a))),
        "zero_frac": float(np.mean(a == 0)),
        "mono_rms": float(np.sqrt(np.mean(m*m))),
    }

def cosine(a, b):
    n = min(a.size, b.size)
    af = a[:n].astype(np.float64); bf = b[:n].astype(np.float64)
    na = np.linalg.norm(af); nb = np.linalg.norm(bf)
    return float(np.dot(af, bf) / (na * nb)) if na and nb else 0.0

def ncc_lags(ma, mb, lags):
    out = []
    nf = min(ma.size, mb.size)
    ma, mb = ma[:nf], mb[:nf]
    for lag in lags:
        if lag >= 0:
            x, y = ma[:nf-lag], mb[lag:]
        else:
            x, y = ma[-lag:], mb[:nf+lag]
        d = np.sqrt(np.dot(x,x) * np.dot(y,y))
        v = float(np.dot(x,y)/d) if d else 0.0
        out.append({"lag_samples": int(lag), "lag_ms": lag * 1000.0 / 48000.0, "ncc": v})
    # best among these
    best = max(out, key=lambda r: r["ncc"])
    return best, out

# lag grid: every 10ms over +/- 200ms, plus 0, plus 1s and 5s and 15s-ish for "same stem different window" check is not needed between packs of same length
lags = list(range(-9600, 9601, 480))  # +/- 200ms every 10ms
# also a coarser +/- 2s every 50ms to catch delayed copy
lags += list(range(-96000, 96001, 2400))
lags = sorted(set(lags))

names = ["v2_p01.wav","v2_p02.wav","v1_p01.wav","v1_p02.wav","v2_concat_a15.wav","v2_concat_b15.wav"]
wavs = {}
meta = {}
for n in names:
    s, ch, sr, nf, sha = load(n)
    wavs[n] = (s, ch, sr)
    st = stats(s, ch)
    st["pcm_sha256"] = sha
    st["duration"] = nf / sr
    st["rate"] = sr
    st["channels"] = ch
    meta[n] = st

pairs = [
    ("v2_p01.wav","v2_p02.wav"),
    ("v1_p01.wav","v1_p02.wav"),
    ("v2_concat_a15.wav","v2_concat_b15.wav"),
    ("v2_p01.wav","v1_p01.wav"),
    ("v2_p02.wav","v1_p02.wav"),
    ("v2_p01.wav","v2_concat_a15.wav"),
    ("v2_p02.wav","v2_concat_b15.wav"),
]
results = {"meta": meta, "pairs": {}}
for a,b in pairs:
    sa, cha, sra = wavs[a]
    sb, chb, srb = wavs[b]
    ident = float(np.mean(sa[:min(sa.size,sb.size)] == sb[:min(sa.size,sb.size)]))
    mad = float(np.mean(np.abs(sa[:min(sa.size,sb.size)].astype(np.int32) - sb[:min(sa.size,sb.size)].astype(np.int32))))
    best, grid = ncc_lags(mono(sa, cha), mono(sb, chb), lags)
    results["pairs"][f"{a} vs {b}"] = {
        "exact_pcm_sha_match": meta[a]["pcm_sha256"] == meta[b]["pcm_sha256"],
        "identical_sample_frac": ident,
        "mean_abs_diff_s16": mad,
        "cosine_similarity_aligned0": cosine(sa, sb),
        "max_ncc_mono_on_grid": best,
        "ncc_at_0": next(x for x in grid if x["lag_samples"]==0),
    }

Path(r"C:\Users\derek\AppData\Local\Temp\rv30v2_diag_audio\compare_fast.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
