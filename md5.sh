#!/usr/bin/env bash

set -e

IN=$1
[[ -z "$IN" ]] && IN="hashes.txt"
OUT=$2
[[ -z "$OUT" ]] && OUT="md5hashes.txt"

clang -framework Foundation util.m -o util

rm -f $OUT
while IFS= read -r line
do
    ./util md5 $line >> $OUT
done < $IN
