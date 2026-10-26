"""Zip this repo into submission.zip, ready to upload.

Leaves out what a reviewer doesn't need: the Udacity workspace's Langfuse
database (.langfuse/, hundreds of MB), the unpacked sample repo, logs, caches
and virtual environments. Run it from anywhere:

    python3 scripts/make_submission.py
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "submission.zip"
SKIP_DIRS = {
    ".langfuse",
    ".git",
    ".venv",
    "venv",
    ".logs",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
# Rebuilt from starter_bundle/sample_repo.bundle, which the zip keeps.
SKIP_PATHS = {"starter_bundle/sample_repo"}


def main() -> None:
    count = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
            rel_dir = Path(dirpath).relative_to(REPO_ROOT)
            dirnames[:] = sorted(
                d
                for d in dirnames
                if d not in SKIP_DIRS
                and not d.endswith(".egg-info")
                and (rel_dir / d).as_posix() not in SKIP_PATHS
            )
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if path == OUT or name == ".DS_Store":
                    continue
                zf.write(path, (rel_dir / name).as_posix())
                count += 1
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT.relative_to(REPO_ROOT)}: {count} files, {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
