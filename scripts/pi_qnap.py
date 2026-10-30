r"""pi_qnap.py - full QNAP access for Pi (Derek, 2026-10-28: "Give it full access"). Uses rclone remote 'qnap:'; credentials stay in rclone config, never printed.
  ls <path>            list a folder
  get <path>           copy NAS file/folder to C:\AI\community\qnap_in\
  put <local> <dest>   copy local file/folder to NAS path <dest> (overwrites)
  mkdir <path>         create folder
  mv <src> <dst>       move/rename on the NAS
  rm <path>            delete a file (rmdir <path> for an empty folder; purge <path> for a folder and contents)
Paths with '..' refused. Raw rclone stays blocked for Pi; only this helper is allowed."""
import subprocess, sys, os
IN = r"C:\AI\community\qnap_in"
def bad(p): return ".." in p.replace("\\", "/").split("/") or p.startswith("-")
def q(p): return "qnap:" + p.lstrip("/")
def run(a): r = subprocess.run(["rclone"] + a, capture_output=True, text=True, timeout=3600); print((r.stdout + r.stderr).strip()[-4000:]); return r.returncode
a = sys.argv[1:]
if len(a) < 2 or any(bad(x) for x in a[1:] if not os.path.exists(x)): print(__doc__); sys.exit(2)
c = a[0]
if c == "ls": sys.exit(run(["lsl", q(a[1]), "--max-depth", "1"]))
if c == "get": os.makedirs(IN, exist_ok=True); sys.exit(run(["copy", q(a[1]), IN, "-v"]))
if c == "put" and len(a) == 3:
    cmd = "copyto" if os.path.isfile(a[1]) else "copy"; sys.exit(run([cmd, a[1], q(a[2]), "-v"]))
if c == "mkdir": sys.exit(run(["mkdir", q(a[1])]))
if c == "mv" and len(a) == 3: sys.exit(run(["moveto", q(a[1]), q(a[2]), "-v"]))
if c == "rm": sys.exit(run(["deletefile", q(a[1]), "-v"]))
if c == "rmdir": sys.exit(run(["rmdir", q(a[1])]))
if c == "purge": sys.exit(run(["purge", q(a[1]), "-v"]))
print(__doc__); sys.exit(2)
