#!/usr/bin/env bash

set -e

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Discover MobileGestalt keys from libMobileGestalt.dylib.

OPTIONS:
    -a, --arch ARCH         Architecture to extract (default: arm64e)
    -h, --help              Show this help message

PREREQUISITES:
    - libMobileGestalt.dylib in current directory
    - python3

EXAMPLES:
    # Use default architecture (arm64e)
    $0

    # Specify architecture
    $0 --arch arm64

EOF
}

DYLIB="libMobileGestalt.dylib"
HASHES="hashes.txt"
READABLE="readable.txt"
OBFUSCATED="discover-obfuscated.txt"
OBFUSCATED_MAPPED="discover-obfuscated-mapped.txt"
MAYBE_NON_GESTALT_KEYS="maybe-non-gestalt-keys.txt"
ARCH="arm64e"

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
        show_help
        exit 0
        ;;
        -a|--arch)
        ARCH="$2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
    esac
done

# Check prerequisites
if [ ! -f "$DYLIB" ]; then
    echo "Error: $DYLIB not found in current directory"
    echo "Please extract libMobileGestalt.dylib first"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    echo "Please install Python 3"
    exit 1
fi

if [ ! -f "obfuscate.py" ]; then
    echo "Error: obfuscate.py not found"
    exit 1
fi

echo "Using architecture: $ARCH"

# Try llvm-nm first (most robust), fallback to nm, then strings
if command -v llvm-nm &> /dev/null && llvm-nm -g --defined-only $DYLIB 2>/dev/null | awk '{print $3}' | grep "^_MobileGestalt_" | grep -v "_obj$" | sed -e 's/^_MobileGestalt_get_//' -e 's/^_MobileGestalt_copy_//' | awk '{print toupper(substr($0,1,1))substr($0,2)}' > $READABLE 2>/dev/null && [ -s $READABLE ]; then
    echo "Using llvm-nm for symbol extraction"
elif nm -g --defined-only $DYLIB 2>/dev/null | awk '{print $3}' | grep "^_MobileGestalt_" | grep -v "_obj$" | sed -e 's/^_MobileGestalt_get_//' -e 's/^_MobileGestalt_copy_//' | awk '{print toupper(substr($0,1,1))substr($0,2)}' > $READABLE 2>/dev/null && [ -s $READABLE ]; then
    echo "Using nm for symbol extraction"
else
    echo "Warning: nm tools failed, using strings extraction (may include false positives)"
    # Use strings with GNU strings if available, otherwise BSD strings
    if command -v gstrings &> /dev/null; then
        gstrings -a $DYLIB 2>/dev/null | grep "^_MobileGestalt_" | grep -v "_obj$" | sed -e 's/^_MobileGestalt_get_//' -e 's/^_MobileGestalt_copy_//' | awk '{print toupper(substr($0,1,1))substr($0,2)}' | sort -u > $READABLE
    else
        # Force strings to work even with malformed Mach-O
        /usr/bin/strings - < $DYLIB 2>/dev/null | grep "^_MobileGestalt_" | grep -v "_obj$" | sed -e 's/^_MobileGestalt_get_//' -e 's/^_MobileGestalt_copy_//' | awk '{print toupper(substr($0,1,1))substr($0,2)}' | sort -u > $READABLE
    fi
fi

if [ ! -s $READABLE ]; then
    echo "Error: Failed to extract any symbols from $DYLIB"
    echo "The dylib may be corrupted or encrypted"
    exit 1
fi

echo "Extracted $(wc -l <$READABLE | tr -d ' ') symbols"

rm -f $OBFUSCATED $OBFUSCATED_MAPPED

mapfile -t readables < $READABLE
if [ ${#readables[@]} -gt 0 ]; then
    mapfile -t hashes < <(python3 obfuscate.py obfuscate "${readables[@]}")
    for i in "${!readables[@]}"; do
        echo "${hashes[$i]}: ${readables[$i]}" >> $OBFUSCATED_MAPPED
        echo "${hashes[$i]}" >> $OBFUSCATED
    done
fi

sort -f $OBFUSCATED_MAPPED -o $OBFUSCATED_MAPPED

if [ ! -f "$HASHES" ]; then
    echo "Warning: $HASHES not found, skipping maybe-non-gestalt-keys generation"
else
    grep -v -f $OBFUSCATED $HASHES | sort -f > temp-$MAYBE_NON_GESTALT_KEYS

    if command -v python3 &> /dev/null; then
        python3 gen_maybe_non_gestalt_keys.py
    else
        echo "Warning: python3 not found, skipping maybe-non-gestalt-keys processing"
    fi

    rm -f temp-$MAYBE_NON_GESTALT_KEYS
fi

echo "Discovery complete!"
echo "Results:"
echo "  - Readable keys: $READABLE"
echo "  - Obfuscated mapped: $OBFUSCATED_MAPPED"
[[ -f "$MAYBE_NON_GESTALT_KEYS" ]] && echo "  - Maybe non-gestalt: $MAYBE_NON_GESTALT_KEYS"
