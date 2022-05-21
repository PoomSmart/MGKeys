#!/bin/bash

# specify path to libMobileGestalt.dylib
strings -arch arm64 -n 22 $1 | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > temp-hashes.txt
grep -v -f false-positives.txt temp-hashes.txt | sort -f > hashes.txt
rm -f temp-hashes.txt
python3 gen-mapping.py
exit