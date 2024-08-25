#!/bin/bash

HASHES="hashes.txt"
HASHES_LEGACY="hashes_legacy.txt"
ALL_HASHES="all-hashes.txt"

cp $HASHES $ALL_HASHES
cat $HASHES_LEGACY >> $ALL_HASHES
