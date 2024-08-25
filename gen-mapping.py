from deobfuscated import keys
from deobfuscated_legacy import keys_legacy
from obfuscate import calculate_obfuscated_key, md5_string_for_obfuscated_key
from keys_desc import unknown_keys_desc

'''
This script generates a mapping file (mapping.h) for all keys in hashes.txt and hashes_legacy.txt. The mapped values are the deobfuscated keys.
This script also generates a potfile (potfile) for hashcat.
'''

HASHES = 'hashes.txt'
HASHES_LEGACY = 'hashes_legacy.txt'
MAPPING = 'mapping.h'
MAPPING_LEGACY = 'mapping-legacy.h'
POTFILE = 'potfile'

POTFILE_CONTENT = ''

def map(hashes_file, mapping_file, keys):
    global POTFILE_CONTENT
    mapping = {}
    deobfuscated = 0
    with open(hashes_file, 'r') as hashes:
        with open(mapping_file, 'w') as out:
            for raw_hash in hashes:
                hash = raw_hash.strip()
                if hash in keys:
                    if calculate_obfuscated_key(keys[hash]) != hash:
                        print(f'Error: {hash} does not match {keys[hash]}')
                        exit(1)
                    md5 = md5_string_for_obfuscated_key(hash)
                    POTFILE_CONTENT += f'{md5}:MGCopyAnswer{keys[hash]}\n'
                    keys[hash] = keys[hash].replace('"', '\\"')
                    mapping[hash] = f'"{keys[hash]}",'
                    deobfuscated += 1
                elif hash in unknown_keys_desc:
                    mapping[hash] = f'NULL, // {unknown_keys_desc[hash]}'
                else:
                    mapping[hash] = 'NULL,'
            for hash in keys:
                if hash not in mapping:
                    print(f'Warning: {hash} not found in {hashes_file}')
            if hashes_file == HASHES:
                for hash in unknown_keys_desc:
                    if hash not in mapping:
                        mapping[hash] = f'NULL, // {unknown_keys_desc[hash]}'
                        print(f'Warning: {hash} not found in {hashes_file}')
            mapping = dict(sorted(mapping.items(), key=lambda x: x[0].lower()))
            total = len(mapping)
            out.write('#include "struct.h"\n\n')
            out.write(f'// Total: {total} keys\n')
            out.write(f'// Deobfuscated: {deobfuscated} keys ({round((deobfuscated / total) * 100, 2)}%)\n\n')
            out.write('static const struct tKeyMapping keyMappingTable[] = {\n')
            for hash in mapping:
                out.write(f'    "{hash}", {mapping[hash]}\n')
            out.write('    NULL, NULL\n};\n')

map(HASHES, MAPPING, keys)
map(HASHES_LEGACY, MAPPING_LEGACY, keys_legacy)

with open(POTFILE, 'w') as out:
    out.write(POTFILE_CONTENT)
