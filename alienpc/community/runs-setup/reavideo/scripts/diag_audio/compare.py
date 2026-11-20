import wave, hashlib, json, sys
from pathlib import Path
import numpy as np

work = Path(r"C:\Users\derek\AppData\Local\Temp\rv30v2_diag_audio")
outp = work / "compare.json"

def read_wav(p):
    with wave.open(str(p), "rb") as w:
        ch, sw, sr, nframes = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(nframes)
    assert sw == 2
    samples = np.frombuffer(raw, dtype=np.int16)
    return {
        "path": str(p),
        "channels": ch,
        "rate": sr,
        "nframes": nframes,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "file_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "samples": samples,
        "nbytes": len(raw),
        "duration": nframes / sr,
        "rms": float(np.sqrt(np.mean(samples.astype(np.float64)**2))) if samples.size else 0.0,
        "peak": int(np.max(np.abs(samples))) if samples.size else 0,
        "zero_frac": float(np.mean(samples == 0)) if samples.size else 0.0,
    }

files = ["v2_p01.wav","v2_p02.wav","v1_p01.wav","v1_p02.wav","v2_concat_a.wav","v2_concat_b.wav","v2_concat_a15.wav","v2_concat_b15.wav"]
wavs = {n: read_wav(work/n) for n in files}

def mono(w):
    s = w["samples"].astype(np.float64)
    if w["channels"] == 2:
        return 0.5 * (s[0::2] + s[1::2])
    return s

def cmp(wa, wb, max_lag=4800):
    a = wa["samples"].astype(np.int32)
    b = wb["samples"].astype(np.int32)
    n = min(a.size, b.size)
    a0, b0 = a[:n], b[:n]
    exact = wa["raw_sha256"] == wb["raw_sha256"]
    neq = np.flatnonzero(a0 != b0)
    equal_prefix = int(neq[0]) if neq.size else int(n)
    mad = float(np.mean(np.abs(a0 - b0)))
    ident = float(np.mean(a0 == b0))
    af = a0.astype(np.float64); bf = b0.astype(np.float64)
    na = np.linalg.norm(af); nb = np.linalg.norm(bf)
    cos = float(np.dot(af, bf) / (na * nb)) if na and nb else 0.0
    ma, mb = mono(wa), mono(wb)
    nf = min(ma.size, mb.size)
    ma, mb = ma[:nf], mb[:nf]
    # FFT-based correlation over +/- max_lag via np.correlate on a cropped window is still heavy;
    # use correlate with mode valid after padding? For 720k samples, np.correlate full is ok in numpy (FFT).
    corr = np.correlate(ma, mb, mode="full")
    lags = np.arange(-nf + 1, nf)
    mask = np.abs(lags) <= max_lag
    corr_w, lags_w = corr[mask], lags[mask]
    # energy-normalized at each lag approximately using sliding energy is expensive;
    # normalize by full energies (standard NCC approximation at small lag)
    denom = np.sqrt(np.dot(ma, ma) * np.dot(mb, mb))
    ncc = corr_w / denom if denom else corr_w
    i = int(np.argmax(ncc))
    best_lag = int(lags_w[i])
    best_ncc = float(ncc[i])
    # tighter normalized value at best lag
    if best_lag >= 0:
        x, y = ma[:nf-best_lag], mb[best_lag:]
    else:
        x, y = ma[-best_lag:], mb[:nf+best_lag]
    d = np.sqrt(np.dot(x,x)*np.dot(y,y))
    exact_ncc = float(np.dot(x,y)/d) if d else 0.0
    return {
        "exact_pcm_sha_match": exact,
        "len_a": int(a.size), "len_b": int(b.size),
        "compared_samples": int(n),
        "identical_sample_frac": ident,
        "equal_prefix_samples": equal_prefix,
        "mean_abs_diff_s16": mad,
        "cosine_similarity_aligned0": cos,
        "max_ncc_mono": exact_ncc,
        "max_ncc_lag_samples": best_lag,
        "max_ncc_lag_ms": best_lag * 1000.0 / wa["rate"],
        "approx_ncc_fullenergy": best_ncc,
        "duration_a": wa["duration"],
        "duration_b": wb["duration"],
    }

pairs = [
    ("v2_p01.wav","v2_p02.wav"),
    ("v1_p01.wav","v1_p02.wav"),
    ("v2_p01.wav","v2_concat_a.wav"),
    ("v2_p02.wav","v2_concat_b.wav"),
    ("v2_p01.wav","v2_concat_a15.wav"),
    ("v2_p02.wav","v2_concat_b15.wav"),
    ("v2_concat_a15.wav","v2_concat_b15.wav"),
    ("v2_concat_a.wav","v2_concat_b.wav"),
    ("v2_p01.wav","v1_p01.wav"),
    ("v2_p02.wav","v1_p02.wav"),
]
results = {"meta": {n: {k:v for k,v in w.items() if k!="samples"} for n,w in wavs.items()}, "pairs": {}}
for a,b in pairs:
    results["pairs"][f"{a} vs {b}"] = cmp(wavs[a], wavs[b])
outp.write_text(json.dumps(results, indent=2), encoding="utf-8")
print("WROTE", outp)
print(json.dumps(results["pairs"], indent=2))
