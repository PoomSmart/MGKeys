#!/usr/bin/env bash

set -e

DYLIB="libMobileGestalt.dylib"
ARCH=$1
[[ -z "$ARCH" ]] && ARCH=arm64e

# Use strings with stdin redirect to handle malformed Mach-O files
if strings -arch $ARCH -n 22 $DYLIB 2>/dev/null | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > temp-hashes.txt 2>/dev/null && [ -s temp-hashes.txt ]; then
    echo "Extracted hashes using arch-specific strings"
else
    echo "Warning: arch-specific strings failed, using plain strings"
    /usr/bin/strings - < $DYLIB 2>/dev/null | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > temp-hashes.txt
fi

if [ ! -s temp-hashes.txt ]; then
    echo "Error: Failed to extract any hashes from $DYLIB"
    exit 1
fi

echo "Extracted $(wc -l < temp-hashes.txt | tr -d ' ') potential hashes"
grep -v -f false-positives.txt temp-hashes.txt | sort -f > hashes.txt
rm -f temp-hashes.txt
python3 gen_mapping.py
