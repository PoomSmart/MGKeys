from deobfuscated import keys
from deobfuscated_legacy import keys_legacy
from unknown_keys_with_desc import *

def map(hashes_file, mapping_file, keys):
    mapping = {}
    with open(hashes_file, 'r') as hashes:
        with open(mapping_file, 'w') as out:
            for raw_hash in hashes:
                hash = raw_hash.strip()
                if hash in keys:
                    keys[hash] = keys[hash].replace('"', '\\"')
                    mapping[hash] = f'"{keys[hash]}",'
                elif hash in unknown_with_desc:
                    mapping[hash] = f'NULL, // {unknown_with_desc[hash]}'
                else:
                    mapping[hash] = 'NULL,'
            for hash in keys:
                if hash not in mapping:
                    mapping[hash] = f'"{keys[hash]}",'
                    print(f'Warning: {hash} not found in {hashes_file}')
            if hashes_file == 'hashes.txt':
                for hash in unknown_with_desc:
                    if hash not in mapping:
                        mapping[hash] = f'NULL, // {unknown_with_desc[hash]}'
                        print(f'Warning: {hash} not found in {hashes_file}')
            mapping = dict(sorted(mapping.items(), key=lambda x: x[0].lower()))
            total = len(mapping)
            deobfuscated = len(keys)
            out.write('#include "struct.h"\n\n')
            out.write(f'// Total: {total} keys\n')
            out.write(f'// Deobfuscated: {deobfuscated} keys ({round((deobfuscated / total) * 100, 2)}%)\n\n')
            out.write('static const struct tKeyMapping keyMappingTable[] = {\n')
            for hash in mapping:
                out.write(f'    "{hash}", {mapping[hash]}\n')
            out.write('    NULL, NULL\n};\n')

map('hashes.txt', 'mapping.h', keys)
map('hashes_legacy.txt', 'mapping-legacy.h', keys_legacy)
