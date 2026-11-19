"""PV2-1 read-only probe: the exact byte shape of every archived p7 request (the format
the harness accepted) so JOB_REQUEST.json is written in the same form. Prints size,
trailing bytes and parsed jobs. Run: python notes/ali147_pv21_req_format_probe.py
"""
import glob
import json
import os

for f in sorted(glob.glob(r"C:/AI/community/p7/jobs/request_iter*.json")):
    raw = open(f, "rb").read()
    j = json.loads(raw.decode("utf-8"))
    print(os.path.basename(f), "bytes", len(raw), "trailing", repr(raw[-3:]),
          "crlf", raw.count(b"\r\n"), "jobs",
          [(x.get("id"), x.get("kind"), x.get("frames"), x.get("frames_tol"), x.get("minutes"))
           for x in j.get("jobs", [])],
          "top_keys", sorted(j))
