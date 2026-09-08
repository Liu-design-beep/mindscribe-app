#!/usr/bin/env bash
set -euo pipefail

SOURCE="app/web/frontend"
MIRROR="app/frontend"
OUTPUT="dist"

if [[ ! -d "$SOURCE" ]]; then
  echo "Missing front-end source: $SOURCE" >&2
  exit 1
fi

rm -rf "$MIRROR" "$OUTPUT"
mkdir -p "$MIRROR" "$OUTPUT"
cp -a "$SOURCE"/. "$MIRROR"/
cp -a "$SOURCE"/. "$OUTPUT"/

echo "MindScribe portfolio front-end prepared in $MIRROR and $OUTPUT"
find "$OUTPUT" -maxdepth 2 -type f -printf '%p\n' | sort
