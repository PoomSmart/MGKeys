from deobfuscated_keys import *
from unknown_keys_with_desc import *

mapping = {}

with open('hashes.txt', 'r') as hashes:
    with open('mapping.h', 'w') as out:
        deobfuscated = 0
        for raw_hash in hashes:
            hash = raw_hash.strip()
            if hash in deobfuscated_keys:
                mapping[hash] = f'"{deobfuscated_keys[hash]}",'
                deobfuscated += 1
            elif hash in unknown_with_desc:
                mapping[hash] = f'NULL, // {unknown_with_desc[hash]}'
            else:
                mapping[hash] = 'NULL,'
        for hash in deobfuscated_keys:
            if hash not in mapping:
                print(f'Warning: {hash} not found in hashes.txt')
        total = len(mapping)
        out.write('#include "struct.h"\n\n')
        out.write(f'// Total: {total} keys\n')
        out.write(f'// Deobfuscated: {deobfuscated} keys ({round((deobfuscated / total) * 100, 2)}%)\n\n')
        out.write('static const struct tKeyMapping keyMappingTable[] = {\n')
        for hash in mapping:
            out.write(f'    "{hash}", {mapping[hash]}\n')
        out.write('    NULL, NULL\n};\n')