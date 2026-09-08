#!/usr/bin/env bash
set -euo pipefail

SOURCE="app/web/frontend"
OUTPUT="dist"

if [[ ! -d "$SOURCE" ]]; then
  echo "Missing front-end source: $SOURCE" >&2
  exit 1
fi

rm -rf "$OUTPUT"
mkdir -p "$OUTPUT"
cp -a "$SOURCE"/. "$OUTPUT"/

echo "MindScribe portfolio static build prepared in $OUTPUT"
find "$OUTPUT" -maxdepth 2 -type f -printf '%p\n' | sort
