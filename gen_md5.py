from pathlib import Path
from typing import Optional
from obfuscate import md5_string_for_obfuscated_key

"""
This script generates a file with MD5 hashes (md5hashes.txt) for each obfuscated key in all-hashes.txt.
"""

ALL_HASHES = Path("all-hashes.txt")
OUT = Path("md5hashes.txt")


def generate_md5_hashes() -> None:
    """Generate MD5 hashes for all obfuscated keys."""
    # Remove output file if it exists
    OUT.unlink(missing_ok=True)

    # Check if input file exists
    if not ALL_HASHES.exists():
        print(f"Error: {ALL_HASHES} not found")
        return

    count = 0
    skipped = 0

    with OUT.open("w") as out_file:
        with ALL_HASHES.open("r") as hashes_file:
            for line in hashes_file:
                key = line.strip()
                if not key:
                    continue

                md5: Optional[str] = md5_string_for_obfuscated_key(key)
                if md5:
                    out_file.write(f"{md5}\n")
                    count += 1
                else:
                    skipped += 1

    print(f"Generated {count} MD5 hashes")
    if skipped > 0:
        print(f"Skipped {skipped} invalid keys")
    print(f"Output written to {OUT}")


if __name__ == "__main__":
    generate_md5_hashes()
