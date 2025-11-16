#!/usr/bin/env bash

set -e

DYLIB="libMobileGestalt.dylib"
HASHES="hashes.txt"
READABLE="readable.txt"
OBFUSCATED="discover-obfuscated.txt"
OBFUSCATED_MAPPED="discover-obfuscated-mapped.txt"
MAYBE_NON_GESTALT_KEYS="maybe-non-gestalt-keys.txt"

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
    exit 1
fi

echo "Extracted $(wc -l < $READABLE | tr -d ' ') symbols"
clang -framework Foundation util.m -o util -Wno-deprecated-declarations

rm -f $OBFUSCATED $OBFUSCATED_MAPPED
while IFS= read -r readable
do
    hash=`./util obfuscate $readable`
    echo "$hash: $readable" >> $OBFUSCATED_MAPPED
    echo $hash >> $OBFUSCATED
done < $READABLE

sort -f $OBFUSCATED_MAPPED -o $OBFUSCATED_MAPPED

grep -v -f $OBFUSCATED $HASHES | sort -f > temp-$MAYBE_NON_GESTALT_KEYS

python3 gen_maybe_non_gestalt_keys.py

rm -f temp-$MAYBE_NON_GESTALT_KEYS
