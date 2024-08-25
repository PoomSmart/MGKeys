#!/usr/bin/env bash

set -e

DYLIB="libMobileGestalt.dylib"
ARCH=$1
[[ -z "$ARCH" ]] && ARCH=arm64e

strings -arch $ARCH -n 22 $DYLIB | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > temp-hashes.txt
grep -v -f false-positives.txt temp-hashes.txt | sort -f > hashes.txt
rm -f temp-hashes.txt
python3 gen-mapping.py
