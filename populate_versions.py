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
            match = re.match(r'\s*"([^"]+)",\s*"[^"]*",?', line)
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


def parse_version(version_str: str) -> tuple:
    """Parse version string like '12.0' or '26.2' into tuple (12, 0) or (26, 2)."""
    parts = version_str.split('.')
    return tuple(int(p) for p in parts)


def generate_keys_versions():
    """Generate keys_versions.py from existing data."""

    # File paths
    mapping_gestalt = Path('mapping-gestalt.h')
    output_file = Path('keys_versions.py')

    # Extract all hashes from mapping-gestalt.h
    print(f"Reading hashes from {mapping_gestalt}...")
    all_hashes = extract_hashes_from_mapping(mapping_gestalt)
    print(f"Found {len(all_hashes)} total hashes in mapping-gestalt.h\n")

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
        hashes = read_version_file(version_file)
        print(f"Reading {version_file}: {len(hashes)} hashes")
        version_data.append((version_str, parse_version(version_str), hashes))

    # Sort by version number
    version_data.sort(key=lambda x: x[1])

    print()

    # Build version mapping by finding when each key first appeared
    version_map: dict[str, str] = {}  # hash -> version introduced
    removed_map: dict[str, str] = {}  # hash -> version removed

    # Track all keys we've ever seen
    all_seen_keys: set[str] = set()

    # Process versions in order to find first introduction
    for i, (version_str, _, hashes) in enumerate(version_data):
        all_seen_keys.update(hashes)

        if i == 0:
            # First version - all keys here are marked with this version
            for hash_str in hashes:
                version_map[hash_str] = version_str
        else:
            # Find keys that are new in this version (not in any previous version)
            prev_all_keys = set()
            for j in range(i):
                prev_all_keys.update(version_data[j][2])

            new_keys = hashes - prev_all_keys
            for hash_str in new_keys:
                version_map[hash_str] = version_str

    # Find removed keys by checking if they disappear in later versions
    # A key is "removed" if it exists in version N but not in version N+1
    # and doesn't come back in any later version
    for i in range(len(version_data) - 1):
        curr_version_str, _, curr_hashes = version_data[i]
        next_version_str, _, next_hashes = version_data[i + 1]

        # Keys that were in current version but not in next
        potentially_removed = curr_hashes - next_hashes

        # Check if they come back in any later version
        for hash_str in potentially_removed:
            comes_back = False
            for j in range(i + 2, len(version_data)):
                if hash_str in version_data[j][2]:
                    comes_back = True
                    break

            if not comes_back:
                removed_map[hash_str] = next_version_str

    # Keys in mapping-gestalt.h but not in any version file
    latest_version_str = version_data[-1][0] if version_data else "unknown"
    unknown_keys = all_hashes - all_seen_keys

    if unknown_keys:
        print(f"Found {len(unknown_keys)} keys not in any version file (marking as post-{latest_version_str})")
        for hash_str in unknown_keys:
            version_map[hash_str] = f"post-{latest_version_str}"

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

    # Print statistics
    print(f"\n✓ Generated {output_file}")
    print(f"  - Total keys: {len(version_map)}")
    if removed_map:
        print(f"  - Removed keys tracked: {len(removed_map)}")

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
        f.write('\n')
        f.write('Keys per iOS Version:\n')
        f.write('-' * 60 + '\n')

        # Calculate cumulative count for each version
        cumulative_counts = {}
        for i, (version_str, _, hashes) in enumerate(version_data):
            cumulative_counts[version_str] = len(hashes)

        # Print version stats to file
        for version_str in sorted(version_stats.keys(), key=sort_key):
            new_count = version_stats[version_str]
            cumulative_count = cumulative_counts.get(version_str, 0)

            if cumulative_count > 0:
                f.write(f'iOS {version_str:8s}  {cumulative_count:4d} total keys  ({new_count:+4d} new)\n')
            else:
                f.write(f'iOS {version_str:8s}  {new_count:4d} new keys\n')

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

    print(f"  - Report saved to {report_file}")

    # Print to console
    for version_str in sorted(version_stats.keys(), key=sort_key):
        count = version_stats[version_str]
        print(f"  - iOS {version_str}: {count} keys")


if __name__ == '__main__':
    generate_keys_versions()
