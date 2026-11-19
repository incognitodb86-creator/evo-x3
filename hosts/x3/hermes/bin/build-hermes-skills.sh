#!/usr/bin/env bash
# Build the Hermes render skills (h3-render, h3-writer) from the live masters, so Hermes follows the same rules as
# Render on pi. Hermes plan H9 / U4 / U6. Run as evo. Rerun after render/OPERATOR.md or writer_prompt.md changes.
# Usage: build-hermes-skills.sh           install into $HERMES_HOME/skills/creative/
#        build-hermes-skills.sh --check   print OK, or DRIFT and exit 1 if the installed skills differ from a fresh build
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills" && pwd)"
DST="${HERMES_HOME:-/home/evo/.hermes}/skills/creative"
AI="${EVO_AI_ROOT:-/home/evo/AI}"
OP="$AI/render/OPERATOR.md"
WP="$AI/render/writer_pipeline/writer_prompt.md"
for f in "$OP" "$WP" "$SRC/h3-render/HEAD.md" "$SRC/h3-writer/SKILL.md"; do
  [ -s "$f" ] || { echo "MISSING $f" >&2; exit 2; }
done

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/h3-render" "$tmp/h3-writer/references"
{
  cat "$SRC/h3-render/HEAD.md"
  printf '\nSource: %s, sha256 %s\n\n' "$OP" "$(sha256sum "$OP" | cut -d' ' -f1)"
  # Replace pi's $PIXL_KEY env var in OPERATOR.md curl lines with Hermes's token-file command substitution
  sed 's|\$PIXL_KEY|$(cat /home/evo/.config/pixlstash/render-read.token)|g' "$OP"
} > "$tmp/h3-render/SKILL.md"
cp "$SRC/h3-writer/SKILL.md" "$tmp/h3-writer/SKILL.md"
cp "$WP" "$tmp/h3-writer/references/writer_prompt.md"

if [ "${1:-}" = "--check" ]; then
  if diff -rq "$tmp/h3-render" "$DST/h3-render" >/dev/null 2>&1 && diff -rq "$tmp/h3-writer" "$DST/h3-writer" >/dev/null 2>&1; then
    echo "OK h3-render h3-writer match OPERATOR.md and writer_prompt.md"
  else
    echo "DRIFT: rerun build-hermes-skills.sh (OPERATOR.md, writer_prompt.md or the skill sources changed)"
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
