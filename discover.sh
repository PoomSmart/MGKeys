#!/usr/bin/env bash

set -e

DYLIB="libMobileGestalt.dylib"
HASHES="hashes.txt"
READABLE="readable.txt"
OBFUSCATED="discover-obfuscated.txt"
OBFUSCATED_MAPPED="discover-obfuscated-mapped.txt"
MAYBE_NON_GESTALT_KEYS="maybe-non-gestalt-keys.txt"

nm -g --defined-only $DYLIB | awk '{print $3}' | grep "^_MobileGestalt_" | grep -v "_obj$" | sed -e 's/^_MobileGestalt_get_//' -e 's/^_MobileGestalt_copy_//' | awk '{print toupper(substr($0,1,1))substr($0,2)}' > $READABLE
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
