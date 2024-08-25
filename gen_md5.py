import os
from obfuscate import md5_string_for_obfuscated_key

'''
This script generates a file with MD5 hashes (md5hashes.txt) for each obfuscated key in all-hashes.txt.
'''

ALL_HASHES = "all-hashes.txt"
OUT = "md5hashes.txt"

try:
    os.remove(OUT)
except FileNotFoundError:
    pass

with open(OUT, "w") as out_file:
    with open(ALL_HASHES, "r") as hashes_file:
        for line in hashes_file:
            key = line.strip()
            md5 = md5_string_for_obfuscated_key(key)
            out_file.write(f"{md5}\n")
