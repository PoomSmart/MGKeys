from pathlib import Path
from typing import Dict, List, Tuple

from deobfuscated import keys
from deobfuscated_legacy import keys_legacy
from obfuscate import calculate_obfuscated_key, md5_string_for_obfuscated_key
from keys_desc import NON_KEY_DESC, known_keys_desc, unknown_keys_desc
from keys_versions import KEY_IOS_VERSIONS, KEY_IOS_REMOVED, KEY_IOS_REINTRODUCED

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

# Load all version files to compute ranges
def load_version_data() -> Dict[str, List[str]]:
    """Load all version files and return a dict mapping hash -> list of versions where it appears."""
    from pathlib import Path

    key_versions: Dict[str, List[str]] = {}
    versions_dir = Path('versions')

    if not versions_dir.exists():
        return key_versions

    version_files = sorted([f for f in versions_dir.glob('version-*.txt') if f.name != 'version-stats.txt'])

    for version_file in version_files:
        version_str = version_file.stem.replace('version-', '')
        with version_file.open('r') as f:
            for line in f:
                hash_str = line.strip()
                if hash_str:
                    if hash_str not in key_versions:
                        key_versions[hash_str] = []
                    key_versions[hash_str].append(version_str)

    return key_versions

def parse_version(version_str: str) -> Tuple:
    """Parse version string like '12.0' into tuple (12, 0)."""
    try:
        parts = version_str.split('.')
        return tuple(int(p) for p in parts)
    except:
        return (999, 999)

def format_version_ranges(obfuscated_key: str, key_versions_data: Dict[str, List[str]]) -> str:
    """Format version ranges for a key, showing gaps clearly."""
    if obfuscated_key not in KEY_IOS_VERSIONS:
        return ''

    intro_version = KEY_IOS_VERSIONS[obfuscated_key]
    removed_suffix = ''

    # Check if key was removed
    if obfuscated_key in KEY_IOS_REMOVED:
        removed_version = KEY_IOS_REMOVED[obfuscated_key]
        removed_suffix = f' (removed in {removed_version})'

    # If key is not reintroduced, use simple format
    if obfuscated_key not in KEY_IOS_REINTRODUCED:
        if intro_version == 'sim':
            return ' // Simulator'
        elif intro_version == 'unknown':
            return ' // iOS unknown'
        elif removed_suffix:
            return f' // iOS {intro_version}+{removed_suffix}'
        else:
            return f' // iOS {intro_version}+'

    # Key was reintroduced - compute ranges
    if obfuscated_key not in key_versions_data:
        # Fallback to simple format if we don't have version data
        reintro_versions = KEY_IOS_REINTRODUCED[obfuscated_key]
        reintro_str = ', '.join(f'{v}+' for v in reintro_versions)
        return f' // iOS {intro_version}, {reintro_str}{removed_suffix}'

    # Get all versions where key appears, sorted
    versions = sorted(key_versions_data[obfuscated_key], key=parse_version)

    if not versions:
        return f' // iOS {intro_version}+{removed_suffix}'

    # Group consecutive versions into ranges
    ranges = []
    range_start = versions[0]
    range_end = versions[0]

    for i in range(1, len(versions)):
        curr_version = versions[i]
        prev_version = versions[i-1]

        curr_parts = parse_version(curr_version)
        prev_parts = parse_version(prev_version)

        # Check if versions are consecutive (allow minor version increments)
        is_consecutive = (
            (curr_parts[0] == prev_parts[0] and curr_parts[1] == prev_parts[1] + 1) or  # Minor bump
            (curr_parts[0] == prev_parts[0] + 1 and curr_parts[1] == 0)  # Major bump to .0
        )

        if is_consecutive:
            range_end = curr_version
        else:
            # End current range, start new one
            if range_start == range_end:
                ranges.append(range_start)
            else:
                ranges.append(f'{range_start}-{range_end}')
            range_start = curr_version
            range_end = curr_version

    # Add final range
    if range_start == range_end:
        # Only add + if key wasn't removed
        if removed_suffix:
            ranges.append(f'{range_start}')
        else:
            ranges.append(f'{range_start}+')
    else:
        # Only add + if key wasn't removed
        if removed_suffix:
            ranges.append(f'{range_start}-{range_end}')
        else:
            ranges.append(f'{range_start}-{range_end}+')

    return f' // iOS {", ".join(ranges)}{removed_suffix}'# Cache version data
VERSION_DATA = load_version_data()

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
    if add_version:
        version_comment = format_version_ranges(obfuscated_key, VERSION_DATA)

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
                desc = unknown_keys_desc[obfuscated_key]
                if only_gestalt or not GEN_NON_GESTALT_KEY:
                    continue
                stats['non_gestalt_keys'] += 1
                # Get version info for unmapped keys
                version_comment = ''
                if add_version:
                    version_comment = format_version_ranges(obfuscated_key, VERSION_DATA)
                    if version_comment:
                        version_comment = ', ' + version_comment[4:]  # Remove ' // ' and add ', '
                mapping[obfuscated_key] = f'NULL, // {NON_KEY_DESC}, {desc}{version_comment}'
            else:
                stats['unexplored_keys'] += 1
                # Get version info for unexplored keys
                version_comment = ''
                if add_version:
                    version_comment = format_version_ranges(obfuscated_key, VERSION_DATA)
                mapping[obfuscated_key] = f'NULL,{version_comment}'

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
    generate_mapping(HASHES_FILE, MAPPING_FILE, TABLE_NAME, False, keys, add_version=True)
    generate_mapping(HASHES_FILE, MAPPING_GESTALT_FILE, TABLE_NAME, True, keys, add_version=True)
    generate_mapping(HASHES_LEGACY_FILE, MAPPING_LEGACY_FILE, TABLE_LEGACY_NAME, False, keys_legacy, add_version=True)
    generate_mapping(HASHES_LEGACY_FILE, MAPPING_GESTALT_LEGACY_FILE, TABLE_LEGACY_NAME, True, keys_legacy, add_version=True)

    with POTFILE.open('w') as out:
        out.write(potfile_content)
