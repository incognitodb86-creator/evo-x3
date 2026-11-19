#!/usr/bin/env python3
"""Import every image in /home/evo/AI/pixl-inbox into PixlStash (Max, Nov 16 2026, Derrick t2002s7376).
Imported files move to _imported/, failures to _failed/. Prints counts only. Token read from file, never printed.
Usage: sudo -u evo python3 /home/evo/AI/pixlstash-tagging/import_inbox.py"""
import json, os, shutil, time, urllib.request, uuid, mimetypes
INBOX = "/home/evo/AI/pixl-inbox"; API = "http://127.0.0.1:9537/api/v1/pictures/import"
TOK = open("/home/evo/.config/pixlstash/tagger-write.token").read().strip()
H = {"Authorization": "Bearer " + TOK}
EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".mov")
files = sorted(f for f in os.listdir(INBOX) if f.lower().endswith(EXT) and os.path.isfile(os.path.join(INBOX, f)))
tot = {"files": len(files), "imported": 0, "duplicate": 0, "failed": 0}
for i in range(0, len(files), 50):
    batch = files[i:i+50]; b = uuid.uuid4().hex; body = b""
    for f in batch:
        ct = mimetypes.guess_type(f)[0] or "application/octet-stream"
        body += f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{f}"\r\nContent-Type: {ct}\r\n\r\n'.encode()
        body += open(os.path.join(INBOX, f), "rb").read() + b"\r\n"
    body += f"--{b}--\r\n".encode()
    tid = json.load(urllib.request.urlopen(urllib.request.Request(API, data=body, method="POST",
          headers={**H, "Content-Type": "multipart/form-data; boundary=" + b}), timeout=600))["task_id"]
    while True:
        s = json.load(urllib.request.urlopen(urllib.request.Request(API + "/status?task_id=" + tid, headers=H), timeout=60))
        if s.get("status") in ("completed", "failed", "error", "cancelled"): break
        time.sleep(3)
    tot["imported"] += s.get("imported_count") or 0; tot["duplicate"] += s.get("duplicate_count") or 0
    ok = s.get("status") == "completed"
    if not ok: tot["failed"] += len(batch)
    for f in batch:
        shutil.move(os.path.join(INBOX, f), os.path.join(INBOX, "_imported" if ok else "_failed", f))
print(json.dumps(tot))
