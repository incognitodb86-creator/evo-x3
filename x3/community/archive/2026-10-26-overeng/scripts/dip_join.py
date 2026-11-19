r"""dip_join.py - ALI-147 arm 3 (DIP), CPU-only ffmpeg, no render. Called by ralph.ps1 job kind "dip" (Forge requests it).
Per plan: fade the outgoing 12 frames to black/white and the incoming 12 frames in at each segment restart (frames 481, 962),
afade on the same times, no overlap (stays 1443 frames). libx264 crf 14 yuv420p + aac; base_reenc.mp4 = same encode, no fade.
Source: BASE segment files p7_r2_c3_pmot_full_pool_seg1..3.mp4. Writes dip.log, ffmpeg_cmd.txt, dipblack.mp4, dipwhite.mp4, base_reenc.mp4,
and a stills contact sheet per output around 0:10..0:50. ffmpeg fade docs: https://ffmpeg.org/ffmpeg-filters.html#fade
Usage: python -u dip_join.py <arm_dir>"""
import os, sys, subprocess, datetime, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import run_graph_job as rg
B = r"C:\AI\community\runs\p7_r2_c3_pmot_full_pool"; SEGS = [os.path.join(B, f"p7_r2_c3_pmot_full_pool_seg{i}.mp4") for i in (1, 2, 3)]
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CT")
def main():
    D = sys.argv[1]; os.makedirs(D, exist_ok=True); L = os.path.join(D, "dip.log"); cmds = []
    def log(m): open(L, "a", encoding="utf-8").write(f"{now()} {m}\n"); print(m, flush=True)
    log("DIP start")
    fps = 24; n = 12; fr = [rg.probe(s)["frames"] for s in SEGS]; log(f"segment frames {fr}")
    def build(color, out):
        fc = []; parts = []
        for i, f in enumerate(fr):
            v = f"[{i}:v]"; a = f"[{i}:a]"; vf = []; af = []
            if color and i < 2: vf.append(f"fade=t=out:start_frame={f - n}:nb_frames={n}:color={color}"); af.append(f"afade=t=out:st={(f - n) / fps:.4f}:d={n / fps:.4f}")
            if color and i > 0: vf.append(f"fade=t=in:start_frame=0:nb_frames={n}:color={color}"); af.append(f"afade=t=in:st=0:d={n / fps:.4f}")
            fc.append(f"{v}{','.join(vf) or 'null'}[v{i}]"); fc.append(f"{a}{','.join(af) or 'anull'}[a{i}]"); parts.append(f"[v{i}][a{i}]")
        fc.append(f"{''.join(parts)}concat=n={len(fr)}:v=1:a=1[v][a]")
        cmd = ["ffmpeg", "-hide_banner", "-y"] + sum([["-i", s] for s in SEGS], []) + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-frames:v", str(sum(fr)), "-c:a", "aac", os.path.join(D, out)]
        cmds.append(" ".join(f'"{c}"' if " " in c or ";" in c else c for c in cmd)); r = subprocess.run(cmd, capture_output=True, text=True)
        p = rg.probe(os.path.join(D, out)) if r.returncode == 0 else {}
        log(f"DIP {out} ffmpeg_exit={r.returncode} frames={p.get('frames')} audio={p.get('audio')} dur={p.get('duration')} bytes={p.get('bytes')}")
        cs = rg.contact_sheet(os.path.join(D, out), os.path.join(D, out[:-4] + "_stills_contact.png"), p.get("duration", 0)) if p else None
        log(f"DIP contact {cs}"); return r.returncode == 0 and p.get("frames") == sum(fr) and p.get("audio")
    ok = all([build(None, "base_reenc.mp4"), build("black", "dipblack.mp4"), build("white", "dipwhite.mp4")])
    open(os.path.join(D, "ffmpeg_cmd.txt"), "w", encoding="utf-8").write("\n\n".join(cmds) + "\n")
    log(f"DIP end {'ok' if ok else 'FAIL'}"); return 0 if ok else 5
if __name__ == "__main__": sys.exit(main())
