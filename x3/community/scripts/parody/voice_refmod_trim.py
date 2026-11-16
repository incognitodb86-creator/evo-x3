r"""Make a shorter copy of a MiniMax-H3 voice RefMod so it fits a cond-audio row cap.

Why this exists (voice-cap-shot-lufs 2026-11-16, prompt-maker brief): a continuation beat reserves
2 * latent_t cond-audio rows for its voice RefMod plus 2 * overlap_audio_t rows for the latent-tail guide's
keyframe audio, and the rows the voice reference can carry are 2 * latent_t of the reference the clip opens
with - 2000 for the 25.0 s / 1000-token FCSydny voice RefMod. Beat 2 of the 192 + 187 + 187 pack reserved
2 * 1000 + 2 * 65 = 2130 rows and died at c2_samp: "value tensor of shape [2000, 32] cannot be broadcast to
indexing result of shape [2130, 32]". The legal fix is a voice reference short enough that the tail fits under
the cap: latent_t <= (2000 - 2 * 65) / 2 = 935, and 920 tokens (23.0 s at the 40 Hz audio latent rate) leaves
30 rows of headroom on the tightest beat and 86 on the next.

What kind of artifact this is, and why a length cut is legal on it: a voice RefMod is a pre-encoded audio VAE
latent [1, 32, 2, latent_t] - ComfyUI-MiniMaxH3Mod/audio.py: make_audio_mod -> encode_audio -> the H3 audio
VAE's encode, stored by core.py: save_mods, and read back as core.py: H3RefMod.as_block() ->
{"kind": "audio", "ref_audio_t": latent_t, "audio_latent": latent}. It is not a trained LoRA/RefLoRA (those are
baked at a fixed token length) and not a raw source wav. The official pack shortens one of these itself:
audio.py: make_audio_mod(..., max_tokens=..., budget_policy="truncate") -> latent[..., :max_tokens // 2], and
core.py: H3RefMod.__post_init__ re-derives latent_t from the tensor, so a trimmed copy reports its own length
to the loader, to the row math and to the sampler. A contiguous slice is what the pack's own documented
shortening method is.

This tool never touches the original file: it writes a NEW .safetensors next to it - same tensor key, same
dtype, header metadata copied with the length fields updated and the description recording what was cut, why,
and the source's sha256. The cut is one contiguous window and its boundaries are chosen where the decoded audio
is silent, so no phoneme is cut mid-word. The boundary evidence is the waveform, not the latent: an audio VAE
codes silence as a dense small-magnitude latent, so a per-token scan of the latent has no dynamic range (the
poolclub file scored 998 of 1000 tokens as "speech" and no gap). Decode the source once (--decode-source), and
the cut is chosen from that (--from-wav).

CPU only: no GPU render, no ComfyUI run, no network, no queue. `--decode-source` / `--decode` are the two
optional steps that need the installed audio VAE, so run this file with the ComfyUI venv python.

Usage:
  python voice_refmod_trim.py --scan
  python voice_refmod_trim.py --decode-source /home/derekboone/AI/community/runs/<run>/dry-voice-cap/source_25s.wav
  python voice_refmod_trim.py --tokens 920 --dry-run --list-candidates \
      --from-wav /home/derekboone/AI/community/runs/<run>/dry-voice-cap/source_25s.wav
  python voice_refmod_trim.py --tokens 920 --from-wav ...\source_25s.wav \
      --decode /home/derekboone/AI/community/runs/<run>/dry-voice-cap/trimmed_23s.wav
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import torch
from safetensors import safe_open
from safetensors.torch import save_file

TOKENS_PER_SECOND = 40.0          # the 40 Hz audio-latent rate (build_request.AUDIO_LATENT_FPS)
TOKEN_MS = 25.0                   # one latent token = 25 ms
SAMPLES_PER_TOKEN = 800           # 32 kHz / 40 Hz
SAMPLE_RATE = 32000               # the sample rate the H3 audio VAE encodes at (audio.py: encode_audio)
REFMOD_DIR = Path(__file__).resolve().parents[3] / "comfy-alienpc" / "models" / "refmods"
AUDIO_VAE = REFMOD_DIR.parent / "audio_vae" / "minimax_h3_audio_vae_fp32.safetensors"
DEFAULT_SOURCE = REFMOD_DIR / "minimaxh3_oc_poolclub_v1_refmod_audio.safetensors"
COND_AUDIO_ROW_CAP = 2000         # build_request.AUDIO_REFMOD_ROW_CAP = 2 * latent_t of the base reference
MAX_LATENT_T: Dict[str, int] = {"beat_2": 935, "beat_3": 963}   # (cap - 2*overlap_audio_t) / 2, 65 / 37 rows
BEAT_TAIL_AUDIO_T = {"beat_2": 65, "beat_3": 37}                # the beats that need the trim


def _ms(tokens: float) -> str:
    return f"{tokens * TOKEN_MS / 1000.0:.3f}s"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_refmod(path: Path) -> Tuple[torch.Tensor, Dict[str, str]]:
    with safe_open(str(path), framework="pt") as f:
        latent = f.get_tensor("latent")
        meta = dict(f.metadata() or {})
    if latent.ndim != 4 or latent.shape[0] != 1 or tuple(latent.shape[1:3]) != (32, 2):
        raise SystemExit(f"{path.name}: not an H3 audio RefMod ([1, 32, 2, T]): {tuple(latent.shape)}")
    return latent, meta


def _scan_from_envelope(db: torch.Tensor) -> Dict[str, Any]:
    """A speech gate between the noise floor and the median of the loud blocks, then the speech mask and the gaps.

    The gate is deliberately blunt: 20 dB above the recorded floor separates speech from room tone. This is not a
    speech detector, it is the evidence for "this cut does not land on a word", which is all the trim needs.
    """
    floor = float(db.min())
    loud = db > floor + 20.0
    med = float(db[loud].median().item()) if bool(loud.any()) else floor + 20.0
    gate = floor + 0.25 * (med - floor)
    speech = db > gate
    voiced = [t for t in range(int(db.shape[0])) if bool(speech[t])]
    return {"latent_t": int(db.shape[0]), "db": db, "gate": gate, "floor_db": floor, "speech": speech,
            "gaps": gaps_from_speech(speech),
            "first_speech_t": voiced[0] if voiced else 0,
            "last_speech_t": (voiced[-1] + 1) if voiced else int(db.shape[0]),
            "speech_tokens": len(voiced)}


def gaps_from_speech(speech: torch.Tensor, min_gap_tokens: int = 10) -> List[Tuple[int, int]]:
    """Runs of >= `min_gap_tokens` (default 0.25 s) with no speech, as [start, end) token ranges."""
    T = int(speech.shape[0])
    gaps: List[Tuple[int, int]] = []
    run = None
    for t in range(T):
        if not bool(speech[t]) and run is None:
            run = t
        if (bool(speech[t]) or t == T - 1) and run is not None:
            end = t + 1 if t == T - 1 else t
            if end - run >= min_gap_tokens:
                gaps.append((run, end))
            run = None
    return gaps


def scan(latent: torch.Tensor) -> Dict[str, Any]:
    """Per-token energy of the latent itself, as a cheap first look. Not the boundary evidence - see wave_scan."""
    x = latent[0].to(torch.float32)
    db = 20 * torch.log10(x.pow(2).mean(dim=(0, 1)).sqrt().clamp_min(1e-9))
    out = _scan_from_envelope(db)
    out["source_t"] = int(db.shape[0])
    return out


def wave_scan(wav_path: Path, source_tokens: int) -> Dict[str, Any]:
    """Speech/gap scan of a DECODED waveform in 25 ms blocks - one block per latent token, on audible audio."""
    import torchaudio  # noqa: PLC0415

    wave, sr = torchaudio.load(str(wav_path))
    wave = wave.to(torch.float32)
    wave = wave.mean(dim=0) if wave.ndim == 2 else wave.reshape(-1)
    hop = max(1, int(round(float(sr) / TOKENS_PER_SECOND)))
    n = int(wave.shape[-1] // hop)
    if abs(n - source_tokens) > max(4, 0.02 * source_tokens):
        raise SystemExit(f"{wav_path.name}: {n} 25 ms blocks does not match the source's {source_tokens} tokens "
                         f"(sample rate {sr} -> {hop} samples per token; decode the source latent, not a clip)")
    blocks = wave[: n * hop].reshape(n, hop)
    db = 20 * torch.log10(blocks.pow(2).mean(dim=1).sqrt().clamp_min(1e-9))
    out = _scan_from_envelope(db)
    out["source_t"] = int(source_tokens)
    out["wav"] = {"path": str(wav_path), "sample_rate": int(sr), "hop_samples": hop,
                  "seconds": round(wave.shape[-1] / float(sr), 3)}
    return out


def choose_window(T: int, keep: int, scan_result: Dict[str, Any]) -> Dict[str, Any]:
    """The gap-bounded contiguous window of `keep` tokens that keeps the most speech (earliest start on a tie).

    A contiguous window can only drop material at its two ends, so the choice is where to cut: every gap's end is a
    legal window start (the first speech token after a gap) and every gap's start is a legal window end. Scoring
    every legal start by the speech it keeps is the shortest answer; ties go to the earliest start, which keeps the
    head of the reference - the opening of a single-speaker voice reference is its cleanest material, and the base
    beat keeps the full-length file, so this copy only has to carry the tail beats. The silence measured on each
    side of the chosen cut is reported: that is the evidence the cut does not land on a word.
    """
    if not (0 < keep <= T):
        raise SystemExit(f"keep {keep} tokens is not inside the source's {T}")
    speech = scan_result["speech"]
    voiced = [t for t in range(T) if bool(speech[t])]
    starts = {0} | {end for (_a, end) in scan_result["gaps"] if end <= T - keep}
    scored: List[Tuple[int, int, Dict[str, Any]]] = []
    for s in sorted(starts):
        e = s + keep
        if e > T:
            continue
        kept = int(speech[s:e].sum().item())
        before = [t for t in voiced if t < s]
        after = [t for t in voiced if t >= e]
        scored.append((-kept, s, {"start": s, "end": e, "speech_kept": kept,
                                  "speech_dropped": scan_result["speech_tokens"] - kept,
                                  "head_silence_tokens": (s - before[-1] - 1) if before else s,
                                  "tail_silence_tokens": (after[0] - e) if after else T - e}))
    if not scored:
        raise SystemExit(f"no gap-bounded window of {keep} tokens in {T} tokens")
    scored.sort(key=lambda c: (c[0], c[1]))
    win = dict(scored[0][2])
    win["keep_tokens"] = keep
    win["candidates"] = [{"start": c[2]["start"], "start_s": _ms(c[2]["start"]), "end": c[2]["end"],
                          "end_s": _ms(c[2]["end"]), "speech_kept": c[2]["speech_kept"],
                          "head_silence_ms": c[2]["head_silence_tokens"] * TOKEN_MS,
                          "tail_silence_ms": c[2]["tail_silence_tokens"] * TOKEN_MS} for c in scored[:3]]
    return win


def trimmed_meta(meta: Dict[str, str], win: Dict[str, Any]) -> Dict[str, str]:
    """Header metadata for the trimmed copy: same fields, length fields updated, and the cut recorded."""
    T, out = int(win["end"]) - int(win["start"]), dict(meta)
    seconds = T / TOKENS_PER_SECOND
    note = (f"trimmed from {_ms(int(win['source_t']))} to {_ms(T)} for the cond-audio row cap "
            f"(voice-cap-shot-lufs 2026-11-16): kept {_ms(win['start'])}-{_ms(win['end'])} of the source, cut in "
            f"silence ({win['head_silence_tokens'] * TOKEN_MS:.0f} ms of measured silence before the cut, "
            f"{win['tail_silence_tokens'] * TOKEN_MS:.0f} ms after it), dropped {int(win['speech_dropped'])} "
            f"speech tokens; 2*{T} + 2*overlap_audio_t rows fit the {COND_AUDIO_ROW_CAP}-row cap")
    for key in ("description", "summary"):
        if out.get(key):
            out[key] = f"{out[key]} | {note}"
    out.setdefault("description", note)
    out["latent_t"] = str(T)
    out["audio_seconds"] = f"{seconds:.3f}"
    if out.get("name"):
        out["name"] = f"{out['name']} [trimmed {_ms(T)}]"
    blob = out.get("refmod_meta")
    if isinstance(blob, str) and blob.strip().startswith("{"):
        try:
            inner = json.loads(blob)
            inner["latent_t"] = T
            inner["audio_seconds"] = round(seconds, 3)
            inner["source_latent_t"] = int(win["source_t"])
            inner["trim_note"] = note
            out["refmod_meta"] = json.dumps(inner, separators=(",", ":"))
        except ValueError:
            pass
    return out


def row_math(keep: int, beats: Dict[str, int] = BEAT_TAIL_AUDIO_T) -> Dict[str, Any]:
    """Packed value rows vs reserved rows for every tail beat, with the cap, the headroom and the max length."""
    packed = 2 * keep
    per_beat = {beat: {"overlap_audio_t": tail, "max_latent_t": MAX_LATENT_T[beat],
                       "packed_cond_audio_rows": packed, "layout_cond_audio_rows": packed + 2 * tail,
                       "row_cap": COND_AUDIO_ROW_CAP, "headroom_rows": COND_AUDIO_ROW_CAP - (packed + 2 * tail),
                       "fits": packed + 2 * tail <= COND_AUDIO_ROW_CAP}
                for beat, tail in beats.items()}
    return {"trimmed_latent_t": keep, "trimmed_seconds": keep / TOKENS_PER_SECOND,
            "per_beat": per_beat, "all_fit": all(v["fits"] for v in per_beat.values())}


def vae():
    """The installed H3 audio VAE, on CPU (needs the ComfyUI venv python; loads no video model)."""
    comfy_root = AUDIO_VAE.parents[2]
    if str(comfy_root) not in sys.path:
        sys.path.insert(0, str(comfy_root))
    import comfy.sd as sd  # noqa: PLC0415  (the installed runtime's VAE wrapper)
    from comfy.utils import load_torch_file  # noqa: PLC0415

    model = sd.VAE(sd=load_torch_file(str(AUDIO_VAE)), device=torch.device("cpu"))
    model.disable_offload = True
    return model


def decode_wav(latent: torch.Tensor, out_path: Path) -> Dict[str, Any]:
    """Decode a latent to a wav with the installed H3 audio VAE, so the cut can be heard and measured."""
    import torchaudio  # noqa: PLC0415

    wave = vae().decode(latent.to(torch.float32))
    wave = wave.as_subpixel() if hasattr(wave, "as_subpixel") else wave
    wave = torch.as_tensor(wave).to(torch.float32).squeeze()
    if wave.ndim == 1:
        wave = wave.unsqueeze(0)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(str(out_path), wave, SAMPLE_RATE)
    return {"path": str(out_path), "sample_rate": SAMPLE_RATE, "channels": int(wave.shape[0]),
            "samples": int(wave.shape[-1]), "seconds": round(wave.shape[-1] / float(SAMPLE_RATE), 3)}


def energy_profile(wav: Path, block_s: float = 0.5) -> Dict[str, Any]:
    """RMS of a wav in `block_s` blocks: the listen check in numbers - length, where speech starts and ends."""
    import torchaudio  # noqa: PLC0415

    wave, sr = torchaudio.load(str(wav))
    wave = wave.to(torch.float32)
    win = max(1, int(round(block_s * sr)))
    blocks = [[round(s / float(sr), 2), round(float(20 * torch.log10(
        wave[..., s:s + win].pow(2).mean().sqrt().clamp_min(1e-9))), 1)]
        for s in range(0, wave.shape[-1], win)]
    loud = [b for b in blocks if b[1] > -60.0]
    return {"path": str(wav), "seconds": round(wave.shape[-1] / float(sr), 3), "sample_rate": int(sr),
            "peak_rms_db": max(b[1] for b in blocks), "first_loud_block_s": loud[0][0] if loud else None,
            "last_loud_block_s": loud[-1][0] if loud else None, "rms_db_blocks": blocks}


def print_profile(scan_result: Dict[str, Any], step_tokens: int = 20) -> None:
    db, gate = scan_result["db"], scan_result["gate"]
    T = int(db.shape[0])
    for s in range(0, T, step_tokens):
        blk = db[s:s + step_tokens]
        print(f"  {_ms(s):>8}-{_ms(min(s + step_tokens, T) - 1):>8}  max {float(blk.max()):6.1f} "
              f"med {float(blk.median()):6.1f}  {'#' if float(blk.max()) > gate else '.'}")


def main(argv: Sequence[str] = ()) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--out", type=Path, default=None,
                    help="default: <source stem>_<seconds>s.safetensors next to the source")
    ap.add_argument("--tokens", type=int, default=920, help="latent tokens to keep (25 ms each)")
    ap.add_argument("--from-wav", type=Path, default=None,
                    help="choose the cut from this decoded source wav (the boundary evidence)")
    ap.add_argument("--decode-source", type=Path, default=None, help="decode the source latent to this wav")
    ap.add_argument("--decode", type=Path, default=None, help="decode the trimmed latent to this wav")
    ap.add_argument("--scan", action="store_true", help="print the 25 ms profile and the gaps, write nothing")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--list-candidates", action="store_true", help="print the best few windows")
    args = ap.parse_args(list(argv))

    src_sha = sha256(args.source)
    latent, meta = read_refmod(args.source)
    T = int(latent.shape[-1])
    if args.decode_source:
        print(f"decoded source -> {json.dumps(decode_wav(latent, args.decode_source))}")
        print(f"source level -> {json.dumps(energy_profile(args.decode_source))}")
    source_scan = scan(latent)
    scan_result = wave_scan(args.from_wav, T) if args.from_wav else source_scan
    where = "decoded waveform" if args.from_wav else "latent energy (a proxy: no dynamic range on this artifact)"
    print(f"source {args.source}")
    print(f"  latent {tuple(latent.shape)} dtype {latent.dtype} latent_t={T} duration={_ms(T)} sha256={src_sha[:16]}")
    print(f"  boundary evidence: {where}")
    print(f"  floor {scan_result['floor_db']:.1f} dB, speech gate {scan_result['gate']:.1f} dB, speech tokens "
          f"{scan_result['speech_tokens']} of {T}, speech spans {_ms(scan_result['first_speech_t'])}-"
          f"{_ms(scan_result['last_speech_t'])}")
    print(f"  gaps >= 0.25 s: " + (", ".join(f"{_ms(a)}-{_ms(b)}" for a, b in scan_result["gaps"]) or "none"))
    if args.scan:
        print_profile(scan_result)
        return 0

    win = choose_window(T, args.tokens, scan_result)
    win["source_t"] = T
    math = row_math(args.tokens)
    print(f"max latent_t under the {COND_AUDIO_ROW_CAP}-row cap: " +
          ", ".join(f"{b} (overlap_audio_t {t}) {MAX_LATENT_T[b]}" for b, t in BEAT_TAIL_AUDIO_T.items()))
    print(f"window kept {_ms(win['start'])}-{_ms(win['end'])} ({win['end'] - win['start']} tokens = "
          f"{(win['end'] - win['start']) * TOKEN_MS / 1000.0:.3f} s)")
    print(f"  speech kept {win['speech_kept']} of {scan_result['speech_tokens']}, dropped {win['speech_dropped']}; "
          f"measured silence at the cut: {win['head_silence_tokens'] * TOKEN_MS:.0f} ms before, "
          f"{win['tail_silence_tokens'] * TOKEN_MS:.0f} ms after")
    if args.list_candidates:
        for c in win["candidates"]:
            print(f"  candidate {c['start_s']}-{c['end_s']} speech_kept {c['speech_kept']} "
                  f"head_silence {c['head_silence_ms']:.0f} ms tail_silence {c['tail_silence_ms']:.0f} ms")
    for beat, v in math["per_beat"].items():
        print(f"  {beat}: packed {v['packed_cond_audio_rows']} + tail {2 * v['overlap_audio_t']} = "
              f"{v['layout_cond_audio_rows']} rows vs cap {v['row_cap']} -> headroom {v['headroom_rows']}, "
              f"fits={v['fits']}")
    if args.dry_run:
        print("DRY_RUN: nothing written")
        return 0
    if not math["all_fit"]:
        raise SystemExit(f"keeping {args.tokens} tokens does not fit the cap: choose latent_t <= "
                         f"{min(MAX_LATENT_T.values())}")

    out = args.out or args.source.with_name(
        f"{args.source.stem}_{int(round(args.tokens / TOKENS_PER_SECOND))}s.safetensors")
    if out.resolve() == args.source.resolve():
        raise SystemExit("the trimmed copy is a NEW file: --out must not be the source")
    if out.exists():
        raise SystemExit(f"{out} already exists - nothing is overwritten")
    kept = latent[..., win["start"]:win["end"]].contiguous()
    meta_out = trimmed_meta(meta, win)
    meta_out["source_refmod"] = str(args.source)
    meta_out["source_sha256"] = src_sha
    meta_out["trim_start_token"] = str(win["start"])
    meta_out["trim_end_token"] = str(win["end"])
    out.parent.mkdir(parents=True, exist_ok=True)
    save_file({"latent": kept}, str(out), metadata=meta_out)
    back, back_meta = read_refmod(out)
    ok = tuple(back.shape) == tuple(kept.shape) and torch.equal(back, kept)
    print(f"TRIM OK {out}")
    print(f"  latent {tuple(back.shape)} dtype {back.dtype} latent_t={back.shape[-1]} duration="
          f"{_ms(back.shape[-1])} round_trip={ok}")
    print(f"  new header: latent_t={back_meta.get('latent_t')} audio_seconds={back_meta.get('audio_seconds')} "
          f"subject_name={back_meta.get('subject_name')} keys={sorted(back_meta)}")
    print(f"  source untouched: {sha256(args.source) == src_sha} (sha256 {src_sha[:16]})")
    if args.decode:
        print(f"  decoded trimmed -> {json.dumps(decode_wav(back, args.decode))}")
        print(f"  trimmed level -> {json.dumps(energy_profile(args.decode))}")
    report = {"source": str(args.source), "source_sha256": src_sha, "out": str(out),
              "boundary_evidence": where, "window": {k: v for k, v in win.items()},
              "row_math": math, "round_trip": ok, "source_untouched": sha256(args.source) == src_sha,
              "new_metadata_keys": sorted(back_meta)}
    print("REPORT " + json.dumps(report, separators=(",", ":"), default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
