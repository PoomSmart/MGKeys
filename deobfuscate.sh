#!/usr/bin/env bash

set -e

# Wrapper script: generate hashes (via extract_hashes.sh) then build mapping.
# Usage: ./deobfuscate.sh [arch]

ARCH=$1
[[ -z "$ARCH" ]] && ARCH=arm64e

./extract_hashes.sh "$ARCH"
python3 gen_mapping.py
