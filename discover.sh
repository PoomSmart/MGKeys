#!/usr/bin/env bash

set -e

DYLIB=$1
[[ -z "$DYLIB" ]] && DYLIB=libMobileGestalt.dylib
HASHES="hashes.txt"
READABLE="readable.txt"
OBFUSCATED="obfuscated.txt"

nm -g --defined-only $DYLIB | awk '{print $3}' | grep "^_MobileGestalt_" | grep -v "_obj$" | sed -e 's/^_MobileGestalt_get_//' -e 's/^_MobileGestalt_copy_//' | awk '{print toupper(substr($0,1,1))substr($0,2)}' > $READABLE
clang -framework Foundation util.m -o util

rm -f $OBFUSCATED
while IFS= read -r line
do
    value=`./util obfuscate $line`
    echo "$value: $line" >> $OBFUSCATED
done < $READABLE

sort -f $OBFUSCATED -o $OBFUSCATED
