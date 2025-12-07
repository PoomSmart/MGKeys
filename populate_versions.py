#!/usr/bin/env python3
"""
Script to populate keys_versions.py with iOS version information.

This script reads:
- versions/version-*.txt: Cumulative snapshots of keys that exist in each iOS version
- mapping-gestalt.h: All known gestalt keys

The script determines when each key was first introduced and when it was removed
(if applicable) by comparing consecutive version snapshots.

Keys are annotated with:
- "8.4": First appeared in iOS 8.4 (earliest tracked version)
- "12.0": First appeared in iOS 12.0
- Removed keys are tracked separately with the version they were removed in
"""

from pathlib import Path
import re


def extract_hashes_from_mapping(mapping_file: Path) -> set[str]:
    """Extract all obfuscated key hashes from a mapping file."""
    hashes = set()

    with mapping_file.open('r') as f:
        for line in f:
            # Match lines like:     "hash", "key_name",
            # or:                   "hash", NULL,
            match = re.match(r'\s*"([^"]+)",\s*(?:"[^"]*"|NULL),?', line)
            if match:
                hashes.add(match.group(1))

    return hashes


def read_version_file(version_file: Path) -> set[str]:
    """Read hashes from a version-specific file (e.g., versions/version-26.0.txt)."""
    hashes = set()

    if not version_file.exists():
        print(f"Warning: {version_file} does not exist")
        return hashes

    with version_file.open('r') as f:
        for line in f:
            hash_str = line.strip()
            if hash_str:
                hashes.add(hash_str)

    return hashes


def sort_version_file(version_file: Path) -> None:
    """Sort a version file alphabetically (case-insensitive) and remove duplicates."""
    if not version_file.exists():
        return

    # Read all lines
    with version_file.open('r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Sort uniquely (case-insensitive like sort -u)
    sorted_lines = sorted(set(lines), key=str.lower)

    # Write back
    with version_file.open('w') as f:
        for line in sorted_lines:
            f.write(f'{line}\n')


def parse_version(version_str: str) -> tuple:
    """Parse version string like '12.0' or '26.2' into tuple (12, 0) or (26, 2)."""
    parts = version_str.split('.')
    return tuple(int(p) for p in parts)


def generate_keys_versions():
    """Generate keys_versions.py from existing data."""

    # File paths
    mapping_file = Path('mapping.h')  # Contains ALL keys including non-gestalt
    mapping_legacy = Path('mapping-legacy.h')
    output_file = Path('keys_versions.py')

    # Extract all hashes from mapping files
    print(f"Reading hashes from {mapping_file}...")
    main_hashes = extract_hashes_from_mapping(mapping_file)
    print(f"Found {len(main_hashes)} hashes in mapping.h")

    legacy_hashes = set()
    if mapping_legacy.exists():
        print(f"Reading hashes from {mapping_legacy}...")
        legacy_hashes = extract_hashes_from_mapping(mapping_legacy)
        print(f"Found {len(legacy_hashes)} hashes in mapping-legacy.h")

    all_hashes = main_hashes | legacy_hashes
    print(f"Total mapped keys: {len(all_hashes)}\n")

    # Auto-discover all version files in versions/ directory
    versions_dir = Path('versions')
    if versions_dir.exists():
        # Exclude version-stats.txt from the glob results
        version_files = sorted([f for f in versions_dir.glob('version-*.txt') if f.name != 'version-stats.txt'])
    else:
        version_files = []

    if not version_files:
        print("Warning: No version files found in versions/ directory")
        print("Expected format: versions/version-26.0.txt, versions/version-26.2.txt, etc.")

    # Read all version files and sort by version number
    version_data = []
    for version_file in version_files:
        version_str = version_file.stem.replace('version-', '')

        # Auto-sort the version file
        sort_version_file(version_file)

        hashes = read_version_file(version_file)
        print(f"Reading {version_file}: {len(hashes)} hashes (sorted)")
        version_data.append((version_str, parse_version(version_str), hashes))

    # Sort by version number
    version_data.sort(key=lambda x: x[1])

    print()

    # Build version mapping by finding when each key first appeared
    version_map: dict[str, str] = {}  # hash -> version introduced
    removed_map: dict[str, str] = {}  # hash -> version removed
    reintroduced_map: dict[str, list[str]] = {}  # hash -> list of versions where it was reintroduced

    # Track all keys we've ever seen
    all_seen_keys: set[str] = set()

    # Track first and last appearance of each key
    first_appearance: dict[str, int] = {}  # hash -> index of first appearance
    last_appearance: dict[str, int] = {}  # hash -> index of last appearance

    # First pass: find all appearances
    for i, (version_str, _, hashes) in enumerate(version_data):
        all_seen_keys.update(hashes)
        for hash_str in hashes:
            if hash_str not in first_appearance:
                first_appearance[hash_str] = i
            last_appearance[hash_str] = i

    # Second pass: build version map and detect gaps (removed/reintroduced)
    for hash_str in all_seen_keys:
        first_idx = first_appearance[hash_str]
        last_idx = last_appearance[hash_str]

        # Mark with first appearance version
        version_map[hash_str] = version_data[first_idx][0]

        # Check for gaps between first and last appearance
        reintroductions = []
        was_present = True

        for i in range(first_idx + 1, last_idx + 1):
            is_present = hash_str in version_data[i][2]

            if not was_present and is_present:
                # Key reappeared - this is a reintroduction
                reintroductions.append(version_data[i][0])

            was_present = is_present

        if reintroductions:
            reintroduced_map[hash_str] = reintroductions

    # Third pass: find permanently removed keys
    # A key is "removed" if it doesn't appear in the last version but appeared earlier
    last_version_hashes = version_data[-1][2] if version_data else set()

    for hash_str in all_seen_keys:
        if hash_str not in last_version_hashes:
            # Find the last version it appeared in
            last_idx = last_appearance[hash_str]
            # Mark it as removed in the next version (if there is one)
            if last_idx < len(version_data) - 1:
                removed_map[hash_str] = version_data[last_idx + 1][0]

    # Keys in mapping files but not in any version file
    unmapped_keys = all_hashes - all_seen_keys

    if unmapped_keys:
        print(f"Found {len(unmapped_keys)} mapped keys not in any version file (marking as unknown)")
        for hash_str in unmapped_keys:
            version_map[hash_str] = "unknown"

    # Keys in version files but not mapped yet
    unknown_keys = all_seen_keys - all_hashes

    # Always write the unmapped keys file (even if empty)
    unmapped_file = Path('unmapped-keys-from-versions.txt')
    with unmapped_file.open('w') as f:
        f.write(f'# Keys found in version files but not in mapping.h or mapping-legacy.h\n')
        f.write(f'# Total: {len(unknown_keys)} unmapped keys\n')
        f.write(f'# These keys need to be deobfuscated and added to an appropriate mapping file\n\n')
        for h in sorted(unknown_keys):
            f.write(f'{h}\n')

    if unknown_keys:
        print(f"Warning: Found {len(unknown_keys)} keys in version files but not in mapping files")
        print(f"These unmapped keys are saved in unmapped-keys-from-versions.txt")

    # Print statistics
    version_stats: dict[str, int] = {}
    for version in version_map.values():
        version_stats[version] = version_stats.get(version, 0) + 1

    # Sort for consistent output
    sorted_hashes = sorted(version_map.keys())

    # Generate the Python file
    print(f"\nGenerating {output_file}...")
    with output_file.open('w') as f:
        f.write('"""iOS version information for MobileGestalt keys.\n\n')
        f.write('This file is auto-generated by populate_versions.py.\n')
        f.write('Do not edit manually.\n\n')
        f.write('Keys are annotated with the iOS version they first appeared in.\n')
        f.write('Removed keys are tracked in KEY_IOS_REMOVED with the version they were removed.\n')
        f.write('"""\n\n')
        f.write('# Dictionary mapping obfuscated key hash -> iOS version introduced\n')
        f.write('KEY_IOS_VERSIONS = {\n')

        for hash_str in sorted_hashes:
            version = version_map[hash_str]
            f.write(f'    "{hash_str}": "{version}",\n')

        f.write('}\n')

        # Write removed keys dictionary
        f.write('\n# Dictionary mapping obfuscated key hash -> iOS version removed\n')
        f.write('# Only includes keys that were present in an earlier version but removed later\n')
        f.write('KEY_IOS_REMOVED = {\n')

        for hash_str in sorted(removed_map.keys()):
            removed_version = removed_map[hash_str]
            f.write(f'    "{hash_str}": "{removed_version}",\n')

        f.write('}\n')

        # Write reintroduced keys dictionary
        f.write('\n# Dictionary mapping obfuscated key hash -> list of iOS versions where it was reintroduced\n')
        f.write('# These keys disappeared in some versions but came back later\n')
        f.write('KEY_IOS_REINTRODUCED = {\n')

        for hash_str in sorted(reintroduced_map.keys()):
            versions_list = reintroduced_map[hash_str]
            versions_str = ', '.join(f'"{v}"' for v in versions_list)
            f.write(f'    "{hash_str}": [{versions_str}],\n')

        f.write('}\n')

    # Print statistics
    print(f"\n✓ Generated {output_file}")
    print(f"  - Total keys: {len(version_map)}")
    if removed_map:
        print(f"  - Removed keys tracked: {len(removed_map)}")
    if reintroduced_map:
        print(f"  - Reintroduced keys tracked: {len(reintroduced_map)}")

    # Sort and print version stats
    def sort_key(v):
        if v.startswith('post-'):
            return (999, 999)
        try:
            return parse_version(v)
        except:
            return (998, 998)

    # Generate version statistics report
    report_file = Path('versions/version-stats.txt')
    print(f"\n✓ Generating {report_file}")

    with report_file.open('w') as f:
        f.write('MobileGestalt Keys - iOS Version Statistics\n')
        f.write('=' * 60 + '\n')
        f.write('Generated by populate_versions.py\n\n')
        f.write(f'Total unique keys tracked: {len(version_map)}\n')
        if removed_map:
            f.write(f'Total removed keys: {len(removed_map)}\n')
        if reintroduced_map:
            f.write(f'Total reintroduced keys: {len(reintroduced_map)}\n')
        f.write('\n')
        f.write('Keys per iOS Version:\n')
        f.write('-' * 60 + '\n')

        # Calculate cumulative count for each version
        cumulative_counts = {}
        for i, (version_str, _, hashes) in enumerate(version_data):
            cumulative_counts[version_str] = len(hashes)

        # Print version stats to file - iterate over ALL versions, not just those with new keys
        for version_str in sorted(cumulative_counts.keys(), key=sort_key):
            cumulative_count = cumulative_counts[version_str]
            new_count = version_stats.get(version_str, 0)

            if new_count > 0:
                f.write(f'iOS {version_str:8s}  {cumulative_count:4d} total keys  ({new_count:+4d} new)\n')
            else:
                f.write(f'iOS {version_str:8s}  {cumulative_count:4d} total keys\n')

        # Print removed keys summary if any
        if removed_map:
            f.write('\n')
            f.write('Removed Keys by Version:\n')
            f.write('-' * 60 + '\n')

            removed_stats: dict[str, int] = {}
            for removed_version in removed_map.values():
                removed_stats[removed_version] = removed_stats.get(removed_version, 0) + 1

            for version_str in sorted(removed_stats.keys(), key=sort_key):
                count = removed_stats[version_str]
                f.write(f'iOS {version_str:8s}  {count:4d} keys removed\n')

        # Print reintroduced keys summary if any
        if reintroduced_map:
            f.write('\n')
            f.write('Reintroduced Keys by Version:\n')
            f.write('-' * 60 + '\n')

            reintro_stats: dict[str, int] = {}
            for versions_list in reintroduced_map.values():
                for version_str in versions_list:
                    reintro_stats[version_str] = reintro_stats.get(version_str, 0) + 1

            for version_str in sorted(reintro_stats.keys(), key=sort_key):
                count = reintro_stats[version_str]
                f.write(f'iOS {version_str:8s}  {count:4d} keys reintroduced\n')

    print(f"  - Report saved to {report_file}")

    # Print to console
    for version_str in sorted(version_stats.keys(), key=sort_key):
        count = version_stats[version_str]
        print(f"  - iOS {version_str}: {count} keys")


if __name__ == '__main__':
    generate_keys_versions()
