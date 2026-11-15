#!/usr/bin/env bash
set -euo pipefail

# Verify or generate SHA-256 manifest for staged/installed models in /srv/models
MODELS_DIR="${1:-/srv/models}"
MANIFEST="${MODELS_DIR}/SHA256SUMS"

if [[ ! -d "$MODELS_DIR" ]]; then
  echo "ERROR: Models directory not found: $MODELS_DIR" >&2
  exit 1
fi

if [[ "${2:-}" == "--write" ]]; then
  echo "Generating SHA-256 manifest at $MANIFEST ..."
  (cd "$MODELS_DIR" && find . -type f -name '*.gguf' -o -name '*.safetensors' | sort | xargs -r sha256sum > "$MANIFEST")
  echo "Done. Recorded $(wc -l < "$MANIFEST") files."
else
  if [[ ! -f "$MANIFEST" ]]; then
    echo "ERROR: $MANIFEST not found. Run with --write once files are downloaded and verified." >&2
    exit 1
  fi
  (cd "$MODELS_DIR" && sha256sum -c "$MANIFEST")
fi
