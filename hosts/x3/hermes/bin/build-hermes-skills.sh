#!/usr/bin/env bash
# Install the slim native Hermes render skills (h3-render, h3-writer).
# These skills no longer splice render/OPERATOR.md or writer_prompt.md.
# Usage: build-hermes-skills.sh           install into $HERMES_HOME/skills/creative/
#        build-hermes-skills.sh --check   print OK, or DRIFT and exit 1
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills" && pwd)"
DST="${HERMES_HOME:-/home/evo/.hermes}/skills/creative"
for f in "$SRC/h3-render/SKILL.md" "$SRC/h3-writer/SKILL.md"; do
  [ -s "$f" ] || { echo "MISSING $f" >&2; exit 2; }
done

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/h3-render" "$tmp/h3-writer"
cp "$SRC/h3-render/SKILL.md" "$tmp/h3-render/SKILL.md"
cp "$SRC/h3-writer/SKILL.md" "$tmp/h3-writer/SKILL.md"

if [ "${1:-}" = "--check" ]; then
  if diff -rq "$tmp/h3-render" "$DST/h3-render" >/dev/null 2>&1 && diff -rq "$tmp/h3-writer" "$DST/h3-writer" >/dev/null 2>&1; then
    echo "OK h3-render h3-writer match slim skill sources"
  else
    echo "DRIFT: rerun build-hermes-skills.sh (slim skill sources changed)"
    exit 1
  fi
  exit 0
fi

for s in h3-render h3-writer; do
  rm -rf "${DST:?}/$s"
  mkdir -p "$DST/$s"
  cp -r "$tmp/$s/." "$DST/$s/"
done
find "$DST/h3-render" "$DST/h3-writer" -type f -exec chmod 0644 {} +
echo "installed $DST/h3-render $DST/h3-writer"
