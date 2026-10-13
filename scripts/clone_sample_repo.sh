#!/usr/bin/env bash
# Clones sample_repo.bundle into a working checkout at sample_repo/, in the
# repo root, with its full (backdated) commit history intact.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUNDLE="$HERE/sample_repo.bundle"
OUT_DIR="$(cd "$HERE/.." && pwd)/sample_repo"

if [ ! -f "$BUNDLE" ]; then
  echo "error: $BUNDLE not found" >&2
  exit 1
fi

rm -rf "$OUT_DIR"
git clone -q "$BUNDLE" "$OUT_DIR"
echo "Cloned sample repo at: $OUT_DIR"
