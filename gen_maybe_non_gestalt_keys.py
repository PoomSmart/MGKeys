from pathlib import Path
from typing import Dict, Optional
from deobfuscated import keys
from deobfuscated_legacy import keys_legacy
from keys_desc import NON_KEY_DESC, known_keys_desc, unknown_keys_desc

MAYBE_NON_GESTALT_KEYS = Path('maybe-non-gestalt-keys.txt')
TEMP_INPUT = Path(f'temp-{MAYBE_NON_GESTALT_KEYS.name}')


def process_maybe_non_gestalt_keys() -> None:
    """Process and filter maybe-non-gestalt keys."""
    if not TEMP_INPUT.exists():
        print(f"Error: {TEMP_INPUT} not found")
        return

    total_processed = 0
    output_count = 0

    with TEMP_INPUT.open('r') as hashes:
        with MAYBE_NON_GESTALT_KEYS.open('w') as out:
            for raw_hash in hashes:
                obfuscated_hash = raw_hash.strip()
                total_processed += 1

                if not obfuscated_hash:
                    continue

                # Skip if already marked as non-gestalt key
                if NON_KEY_DESC in known_keys_desc.get(obfuscated_hash, ''):
                    continue
                if NON_KEY_DESC in unknown_keys_desc.get(obfuscated_hash, ''):
                    continue

                # Try to find deobfuscated key
                deobfuscated_key: Optional[str] = keys.get(obfuscated_hash)
                if deobfuscated_key is None:
                    deobfuscated_key = keys_legacy.get(obfuscated_hash)

                # Skip if deobfuscated and has uppercase (likely a real gestalt key)
                if deobfuscated_key is not None and any(c.isupper() for c in deobfuscated_key):
                    continue

                out.write(f'{obfuscated_hash}: {deobfuscated_key}\n')
                output_count += 1

    print(f"Processed {total_processed} hashes")
    print(f"Found {output_count} maybe-non-gestalt keys")
    print(f"Output written to {MAYBE_NON_GESTALT_KEYS}")


if __name__ == "__main__":
    process_maybe_non_gestalt_keys()
