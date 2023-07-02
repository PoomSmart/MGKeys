#!/usr/bin/env bash

set -e

IN=$1
[[ -z "$IN" ]] && IN="hashes.txt"
OUT=$2
[[ -z "$OUT" ]] && OUT="md5hashes.txt"

clang -framework Foundation md5.m -o md5

rm -f $OUT
while IFS= read -r line
do
    ./md5 $line >> $OUT
done < $IN
