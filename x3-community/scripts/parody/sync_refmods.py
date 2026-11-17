"""RefMod library sync from HuggingFace malcolmrey/minimaxh3 (U4).

Downloads missing or incomplete *_refmod.safetensors by name list.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional
import urllib.request


HF_BASE_URL = "https://huggingface.co/malcolmrey/minimaxh3/resolve/main"
MIN_VALID_SIZE_BYTES = 500_000  # RefMods are ~1.1 MB; anything under 500 KB is truncated/incomplete


def name_to_refmod_filename(name: str) -> str:
    """Convert an identity name to its canonical RefMod filename on HuggingFace."""
    clean = re.sub(r"[^a-zA-Z0-9]", "", name).lower()
    return f"minimaxh3_{clean}_v1_refmod.safetensors"


def check_sync_status(
    names: List[str],
    target_dir: Path,
    expected_filenames: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Check which RefMod files are present, missing, or size-mismatched.

    Args:
        names: List of identity names.
        target_dir: Directory where RefMods are stored.
        expected_filenames: Optional explicit list of filenames to check.

    Returns:
        Dict with keys:
            - up_to_date: list of valid filenames present
            - missing: list of filenames not on disk
            - incomplete: list of filenames on disk but truncated (< MIN_VALID_SIZE_BYTES)
            - total_checked: count of files checked
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    filenames: List[str] = []
    if expected_filenames:
        filenames.extend(expected_filenames)
    else:
        for n in names:
            fn = name_to_refmod_filename(n)
            if fn not in filenames:
                filenames.append(fn)

    up_to_date: List[str] = []
    missing: List[str] = []
    incomplete: List[str] = []

    for fn in filenames:
        p = target_dir / fn
        if not p.is_file():
            missing.append(fn)
        elif p.stat().st_size < MIN_VALID_SIZE_BYTES:
            incomplete.append(fn)
        else:
            up_to_date.append(fn)

    return {
        "up_to_date": up_to_date,
        "missing": missing,
        "incomplete": incomplete,
        "to_download": missing + incomplete,
        "total_checked": len(filenames),
    }


def download_refmod(filename: str, target_dir: Path) -> Path:
    """Download a single RefMod from HuggingFace.

    Args:
        filename: Filename, e.g. minimaxh3_emiliaclarke_v1_refmod.safetensors.
        target_dir: Destination folder.

    Returns:
        Path to downloaded file.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    dest_path = target_dir / filename
    temp_path = target_dir / f"{filename}.part"

    url = f"{HF_BASE_URL}/{filename}?download=true"
    req = urllib.request.Request(url, headers={"User-Agent": "AlienPc-Forge-Parody/1.0"})

    with urllib.request.urlopen(req, timeout=60) as resp, open(temp_path, "wb") as f_out:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            f_out.write(chunk)

    if temp_path.stat().st_size < MIN_VALID_SIZE_BYTES:
        temp_path.unlink(missing_ok=True)
        raise IOError(f"Downloaded file {filename} is too small (< {MIN_VALID_SIZE_BYTES} bytes)")

    temp_path.replace(dest_path)
    return dest_path


def sync_refmods(
    names: List[str],
    target_dir: Path,
    dry_run: bool = True,
    expected_filenames: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Sync RefMod files for given names from HuggingFace.

    Args:
        names: List of identity names.
        target_dir: Target directory.
        dry_run: If True, only report files that need downloading (R6-a).
        expected_filenames: Optional explicit filename overrides.

    Returns:
        Dict with sync results and download counts.
    """
    status = check_sync_status(names, target_dir, expected_filenames)

    if dry_run:
        return {
            "dry_run": True,
            "to_download": status["to_download"],
            "missing": status["missing"],
            "incomplete": status["incomplete"],
            "up_to_date": status["up_to_date"],
            "downloaded": [],
            "errors": [],
        }

    downloaded: List[str] = []
    errors: List[Dict[str, str]] = []

    for fn in status["to_download"]:
        try:
            download_refmod(fn, target_dir)
            downloaded.append(fn)
        except Exception as e:
            errors.append({"filename": fn, "error": str(e)})

    return {
        "dry_run": False,
        "to_download": status["to_download"],
        "downloaded": downloaded,
        "errors": errors,
        "up_to_date": status["up_to_date"] + downloaded,
    }


def main() -> int:
    """CLI entrypoint for sync_refmods."""
    parser = argparse.ArgumentParser(description="Sync H3 RefMods from HuggingFace")
    parser.add_argument("names", nargs="+", help="Identity names to sync")
    parser.add_argument("--target-dir", default=str(Path(__file__).resolve().parents[3] / "comfy-alienpc" / "models" / "refmods"), help="Destination folder")
    parser.add_argument("--dry-run", action="store_true", help="Report missing without downloading")
    args = parser.parse_args()

    res = sync_refmods(args.names, Path(args.target_dir), dry_run=args.dry_run)
    print(f"Sync result (dry_run={res['dry_run']}):")
    print(f"  To download: {len(res['to_download'])}")
    print(f"  Up to date:  {len(res['up_to_date'])}")
    if res.get("downloaded"):
        print(f"  Downloaded:  {len(res['downloaded'])}")
    if res.get("errors"):
        print(f"  Errors:      {len(res['errors'])}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
