from deobfuscated import keys
from deobfuscated_legacy import keys_legacy
from keys_desc import NON_KEY_DESC, known_keys_desc, unknown_keys_desc

MAYBE_NON_GESTALT_KEYS = 'maybe-non-gestalt-keys.txt'

with open(f'temp-{MAYBE_NON_GESTALT_KEYS}', 'r') as hashes:
    with open(f'{MAYBE_NON_GESTALT_KEYS}', 'w') as out:
        for raw_hash in hashes:
            hash = raw_hash.strip()
            if NON_KEY_DESC in known_keys_desc.get(hash, ''):
                continue
            if NON_KEY_DESC in unknown_keys_desc.get(hash, ''):
                continue
            deobfuscated_key = keys.get(hash)
            if deobfuscated_key is None:
                deobfuscated_key = keys_legacy.get(hash)
            if deobfuscated_key is not None and any(c.isupper() for c in deobfuscated_key):
                continue
            out.write(f'{hash}: {deobfuscated_key}\n')
