from __future__ import annotations
import shutil, zipfile, hashlib
from pathlib import Path

ZIP = Path(r"C:\Users\derek\AppData\Local\Temp\h3max_bridge_0.2.0.zip")
DEST = Path(r"C:\AI\community\scripts\h3max_bridge")
PARODY = Path(r"C:\AI\community\scripts\parody")
B7_SRC = Path(r"C:\Users\derek\AppData\Local\Temp\rv30v2\beta7_convert.py")

DEST.mkdir(parents=True, exist_ok=True)
# clear previous package files but not unrelated
if DEST.exists():
    for p in DEST.iterdir():
        if p.name.startswith("."):
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
with zipfile.ZipFile(ZIP) as z:
    z.extractall(DEST)
b7_dest = PARODY / "beta7_convert.py"
b7_copied = False
if not b7_dest.is_file() and B7_SRC.is_file():
    shutil.copy2(B7_SRC, b7_dest)
    b7_copied = True

def sha(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()

files = {
    "h3max_bridge.py": DEST / "src" / "h3max_bridge" / "h3max_bridge.py",
    "gates.py": DEST / "src" / "h3max_bridge" / "gates.py",
    "__init__.py": DEST / "src" / "h3max_bridge" / "__init__.py",
}
print("DEST", str(DEST))
print("files", {k: (v.is_file(), v.stat().st_size if v.is_file() else 0) for k,v in files.items()})
print("beta7_convert_present", b7_dest.is_file(), "copied_missing", b7_copied)
if b7_dest.is_file():
    print("beta7_convert_sha256", sha(b7_dest))
