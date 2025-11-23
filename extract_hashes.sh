#!/usr/bin/env bash

set -e

# Optional env overrides:
#   DYLIB   - path to libMobileGestalt.dylib (default: libMobileGestalt.dylib in CWD)
#   OUT     - output file for hashes (default: hashes.txt)
#   ARCH    - architecture passed as first arg or defaults to arm64e

DYLIB=${DYLIB:-"libMobileGestalt.dylib"}
ARCH=$1
[[ -z "$ARCH" ]] && ARCH=arm64e
OUT=${OUT:-"hashes.txt"}
TEMP_FILE="temp-hashes.txt"

if [ ! -f "$DYLIB" ]; then
  echo "Error: DYLIB '$DYLIB' not found"
  exit 1
fi

# Use strings with stdin redirect to handle malformed Mach-O files
if strings -arch "$ARCH" -n 22 "$DYLIB" 2>/dev/null | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > "$TEMP_FILE" 2>/dev/null && [ -s "$TEMP_FILE" ]; then
    echo "Extracted hashes using arch-specific strings ($ARCH)"
else
    echo "Warning: arch-specific strings failed, using plain strings"
    /usr/bin/strings - < "$DYLIB" 2>/dev/null | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > "$TEMP_FILE"
fi

if [ ! -s "$TEMP_FILE" ]; then
    echo "Error: Failed to extract any hashes from $DYLIB"
    rm -f "$TEMP_FILE"
    exit 1
fi

echo "Extracted $(wc -l < "$TEMP_FILE" | tr -d ' ') potential hashes"
# Filter false positives and sort case-insensitively
if [ -f false-positives.txt ]; then
  grep -v -f false-positives.txt "$TEMP_FILE" | sort -f > "$OUT"
else
  echo "Note: false-positives.txt not found; skipping filter"
  sort -f "$TEMP_FILE" > "$OUT"
fi

rm -f "$TEMP_FILE"

if [ ! -s "$OUT" ]; then
  echo "Error: Output file '$OUT' is empty after processing"
  exit 1
fi

echo "Wrote $(wc -l < "$OUT" | tr -d ' ') hashes to $OUT"