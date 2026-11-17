import json, glob, os, collections, datetime
CUT = datetime.datetime(2026,10,29,19,40).timestamp()
kinds = collections.Counter(); names = collections.Counter()
def scan(d, tag):
    n = collections.Counter()
    for p in glob.glob(os.path.join(d, '*.jsonl')):
        if os.path.getmtime(p) < CUT: continue
        for l in open(p, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l); m = r.get('message') or {}; c = m.get('content')
            if isinstance(c, list):
                for it in c:
                    if isinstance(it, dict):
                        kinds[str(it.get('type'))] += 1
                        if str(it.get('type')) in ('toolCall', 'tool_call') and it.get('name'):
                            n[str(it['name'])] += 1
    print(tag, dict(n))
scan(r'C:\Users\derek\5slock\ralph-community\talk\sessions', 'LANE ')
for d in glob.glob(r'C:\Users\derek\.pi\agent\sessions\*forge*'):
    scan(d, 'MAIN ')
print('content item types:', dict(kinds))
