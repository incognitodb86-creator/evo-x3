# OPT4 close-out: medians of the final kept-config bench (encoding-sniffing reader, per the OPT4b lesson).
import json, os, statistics, io

d = r'C:\AI\community\notes\_opt4'
p = os.path.join(d, 'bench.jsonl')
raw = open(p, 'rb').read()
enc = 'utf-16' if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else ('utf-8-sig' if raw[:3] == b'\xef\xbb\xbf' else 'utf-8')
rows = []
for ln in raw.decode(enc, 'replace').splitlines():
    ln = ln.strip()
    if not ln:
        continue
    try:
        o = json.loads(ln)
    except Exception:
        continue
    if o.get('tag') == 'opt4-final':
        rows.append(o)

def med(k):
    v = [float(r[k]) for r in rows if r.get(k) is not None]
    return (round(statistics.median(v), 1), round(min(v), 1), round(max(v), 1), len(v))

out = {'tag': 'opt4-final', 'config_proved_live_at': 'strata.exe pid 26492 @21:16:59 (--pool-workers 13, no --pool-affinity, no --resident-budget-gib)',
       'rows': len(rows), 'encoding': enc,
       'pp_tps_median_min_max_n': med('pp_tps'), 'tg_tps_median_min_max_n': med('tg_tps'),
       'wall_s_median_min_max_n': med('wall_s'),
       'compare': {
           'pre_tuning_item_baseline_pp_tg_wall': [617, '83 (79.5-85.7)', '7.0-8.0'],
           'opt5_arena_medians': [1720.5, 125.0, 4.16],
           'opt4b_p_all_medians_same_config_2048': [1684.8, 117.6, 3.31]},
       'runs': [{k: r.get(k) for k in ('run', 'at', 'wall_s', 'pp_tps', 'tg_tps', 'prompt_tokens', 'completion_tokens')} for r in rows]}
txt = json.dumps(out, indent=1, ensure_ascii=False)
open(os.path.join(d, 'final.result.json'), 'w', encoding='utf-8').write(txt)
print(txt)
