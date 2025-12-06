from pathlib import Path
from typing import Dict

from deobfuscated import keys
from deobfuscated_legacy import keys_legacy
from obfuscate import calculate_obfuscated_key, md5_string_for_obfuscated_key
from keys_desc import NON_KEY_DESC, known_keys_desc, unknown_keys_desc
from keys_versions import KEY_IOS_VERSIONS, KEY_IOS_REMOVED

'''
This script generates a mapping file (mapping.h) for all keys in hashes.txt and hashes_legacy.txt. The mapped values are the deobfuscated keys.
This script also generates a potfile (potfile) for hashcat.
'''

HASHES_FILE = Path('hashes.txt')
HASHES_LEGACY_FILE = Path('hashes_legacy.txt')
MAPPING_FILE = Path('mapping.h')
MAPPING_GESTALT_FILE = Path('mapping-gestalt.h')
MAPPING_LEGACY_FILE = Path('mapping-legacy.h')
MAPPING_GESTALT_LEGACY_FILE = Path('mapping-gestalt-legacy.h')
TABLE_NAME = 'keyMappingTable'
TABLE_LEGACY_NAME = 'keyMappingTableLegacy'
POTFILE = Path('potfile')

GEN_NON_GESTALT_KEY = True
USE_MAPPING_AS_SOURCE = False

potfile_content = ''

def process_key(
    obfuscated_key: str,
    keys_map: Dict[str, str],
    mapping: Dict[str, str],
    only_gestalt: bool,
    stats: Dict[str, int],
    add_version: bool = False
) -> bool:
    global potfile_content

    if calculate_obfuscated_key(keys_map[obfuscated_key]) != obfuscated_key:
        print(f'Error: {obfuscated_key} is not deobfuscated to {keys_map[obfuscated_key]}')
        exit(1)

    md5 = md5_string_for_obfuscated_key(obfuscated_key)
    if not only_gestalt:
        potfile_content += f'{md5}:MGCopyAnswer{keys_map[obfuscated_key]}\n'

    # Escape quotes for C string
    escaped_key = keys_map[obfuscated_key].replace('"', '\\"')

    # Get version info if requested
    version_comment = ''
    if add_version and obfuscated_key in KEY_IOS_VERSIONS:
        intro_version = KEY_IOS_VERSIONS[obfuscated_key]
        if obfuscated_key in KEY_IOS_REMOVED:
            removed_version = KEY_IOS_REMOVED[obfuscated_key]
            version_comment = f' // iOS {intro_version}+ (removed in {removed_version})'
        elif intro_version == 'unknown':
            version_comment = f' // iOS {intro_version}'
        else:
            version_comment = f' // iOS {intro_version}+'

    if obfuscated_key in known_keys_desc:
        # known_keys_desc now contains non-gestalt keys
        if only_gestalt or not GEN_NON_GESTALT_KEY:
            return False
        stats['non_gestalt_keys'] += 1
        mapping[obfuscated_key] = f'"{escaped_key}", // {NON_KEY_DESC}{version_comment}'
    else:
        stats['deobfuscated_gestalt_keys'] += 1
        if version_comment:
            mapping[obfuscated_key] = f'"{escaped_key}",{version_comment}'
        else:
            mapping[obfuscated_key] = f'"{escaped_key}",'

    stats['deobfuscated_keys'] += 1
    return True

def generate_mapping(
    hashes_path: Path,
    mapping_path: Path,
    table_name: str,
    only_gestalt: bool,
    input_keys: Dict[str, str],
    add_version: bool = False
) -> None:
    # Create a copy to avoid modifying the original dictionary if it's used elsewhere
    keys_map = input_keys.copy()
    mapping: Dict[str, str] = {}

    stats = {
        'deobfuscated_keys': 0,
        'deobfuscated_gestalt_keys': 0,
        'non_gestalt_keys': 0,
        'unexplored_keys': 0
    }

    seen_keys = set()

    if not hashes_path.exists():
        print(f"Warning: {hashes_path} does not exist.")
        return

    with hashes_path.open('r') as hashes:
        for raw_hash in hashes:
            obfuscated_key = raw_hash.strip()
            if not obfuscated_key:
                continue

            if obfuscated_key in keys_map:
                seen_keys.add(obfuscated_key)
                if not process_key(obfuscated_key, keys_map, mapping, only_gestalt, stats, add_version):
                    continue
            elif obfuscated_key in unknown_keys_desc:
                # unknown_keys_desc now contains IODeviceTree paths only
                desc = unknown_keys_desc[obfuscated_key]
                if only_gestalt or not GEN_NON_GESTALT_KEY:
                    continue
                stats['non_gestalt_keys'] += 1
                mapping[obfuscated_key] = f'NULL, // {NON_KEY_DESC}, {desc}'
            else:
                stats['unexplored_keys'] += 1
                mapping[obfuscated_key] = 'NULL,'

    for obfuscated_key in keys_map:
        if obfuscated_key not in seen_keys:
            if USE_MAPPING_AS_SOURCE:
                if not process_key(obfuscated_key, keys_map, mapping, only_gestalt, stats, add_version):
                    continue
            else:
                print(f'Warning: {obfuscated_key} not found in {hashes_path}')

    # Sort mapping
    sorted_mapping = dict(sorted(mapping.items(), key=lambda x: x[0].lower()))
    total = len(sorted_mapping)

    with mapping_path.open('w') as out:
        out.write('#include "struct.h"\n\n')
        out.write(f'// Total: {total} keys\n')
        percentage = round((stats['deobfuscated_keys'] / total) * 100, 2) if total > 0 else 0
        out.write(f'// Deobfuscated: {stats["deobfuscated_keys"]} keys ({percentage}%)\n')

        if not only_gestalt:
            gestalt_total = total - stats['non_gestalt_keys']
            out.write(f'// Total gestalt keys: {gestalt_total} keys\n')
            gestalt_percentage = round((stats['deobfuscated_gestalt_keys'] / gestalt_total) * 100, 2) if gestalt_total > 0 else 0
            out.write(f'// Deobfuscated gestalt: {stats["deobfuscated_gestalt_keys"]} keys ({gestalt_percentage}%)\n')

        out.write(f'// Unexplored: {stats["unexplored_keys"]} keys\n')
        out.write('\n')
        out.write(f'static const struct tKeyMapping {table_name}[] = {{\n')
        for key, value in sorted_mapping.items():
            out.write(f'    "{key}", {value}\n')
        out.write('    NULL, NULL\n};\n')

if __name__ == '__main__':
    generate_mapping(HASHES_FILE, MAPPING_FILE, TABLE_NAME, False, keys)
    generate_mapping(HASHES_FILE, MAPPING_GESTALT_FILE, TABLE_NAME, True, keys, add_version=True)
    generate_mapping(HASHES_LEGACY_FILE, MAPPING_LEGACY_FILE, TABLE_LEGACY_NAME, False, keys_legacy)
    generate_mapping(HASHES_LEGACY_FILE, MAPPING_GESTALT_LEGACY_FILE, TABLE_LEGACY_NAME, True, keys_legacy, add_version=True)

    with POTFILE.open('w') as out:
        out.write(potfile_content)
