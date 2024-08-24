#!/usr/bin/env bash

set -e

IN=$1
[[ -z "$IN" ]] && IN="hashes.txt"
OUT=$2
[[ -z "$OUT" ]] && OUT="md5hashes.txt"
HASHES="temp-md5-hashes.txt"

cp $IN $HASHES
cat hashes_legacy.txt >> $HASHES

clang -framework Foundation util.m -o util

rm -f $OUT
while IFS= read -r line
do
    ./util md5 $line >> $OUT
done < $HASHES
