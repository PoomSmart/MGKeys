#!/usr/bin/env python3
"""
Script to populate keys_versions.py with iOS version information.

This script reads:
- versions/version-*.txt: Keys that exist in each iOS version (cumulative snapshots)
- versions/version-*-exact.txt: Keys introduced exactly in that version (overrides)
- mapping-gestalt.h: All known gestalt keys

The version files are cumulative - version-X.Y.txt contains all keys that existed
up to and including iOS X.Y. The script computes differences to determine when
each key was introduced.

For precise version tracking, you can add version-X.Y-exact.txt files that specify
exactly which keys were introduced in that version, overriding the computed differences.

Example version files:
- versions/version-12.0.txt (all keys up to iOS 12)
- versions/version-26.0.txt (all keys up to iOS 26)
- versions/version-26.0-exact.txt (keys introduced exactly in iOS 26.0)
- versions/version-26.2.txt (all keys up to iOS 26.2)
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
    
    # Separate cumulative snapshots from exact version files
    cumulative_files = sorted(versions_dir.glob('version-*.txt')) if versions_dir.exists() else []
    # Filter out -exact.txt files from cumulative list
    cumulative_files = [f for f in cumulative_files if '-exact' not in f.stem]
    
    # Find exact version files
    exact_files = sorted(versions_dir.glob('version-*-exact.txt')) if versions_dir.exists() else []

    if not cumulative_files:
        print("Warning: No cumulative version files found in versions/ directory")
        print("Expected format: versions/version-26.0.txt, versions/version-26.2.txt, etc.")

    # Read all cumulative version files and sort by version number
    version_data = []
    for version_file in cumulative_files:
        version_str = version_file.stem.replace('version-', '')
        hashes = read_version_file(version_file)
        print(f"Reading hashes from {version_file}...")
        print(f"Found {len(hashes)} hashes for iOS {version_str}")
        version_data.append((version_str, parse_version(version_str), hashes))

    # Sort by version number
    version_data.sort(key=lambda x: x[1])

    print()

    # Build version mapping by computing differences from cumulative snapshots
    version_map = {}
    version_stats = {}

    # Keys in the earliest version are marked as "pre-X.Y"
    if version_data:
        earliest_version_str, _, earliest_hashes = version_data[0]
        pre_label = f"pre-{earliest_version_str}"

        for hash_str in earliest_hashes:
            version_map[hash_str] = pre_label

        version_stats[pre_label] = len(earliest_hashes)
        print(f"Marked {len(earliest_hashes)} keys as {pre_label} (existed in iOS {earliest_version_str})")

        # For each subsequent version, find new keys
        for i in range(1, len(version_data)):
            curr_version_str, _, curr_hashes = version_data[i]
            prev_version_str, _, prev_hashes = version_data[i - 1]

            # Keys in current but not in previous were introduced somewhere between prev and curr
            # Mark them as "X.Y-" (uncertain, needs exact file to be precise)
            new_keys = curr_hashes - prev_hashes

            for hash_str in new_keys:
                version_map[hash_str] = f"{curr_version_str}-"

            version_stats[f"{curr_version_str}-"] = len(new_keys)
            print(f"Found {len(new_keys)} new keys by iOS {curr_version_str} (marked as {curr_version_str}-)")

        # Keys not in any version file are marked as "unknown" or newer than latest
        latest_version_str, _, latest_hashes = version_data[-1]
        unknown_keys = all_hashes - latest_hashes

        if unknown_keys:
            unknown_label = f"post-{latest_version_str}"
            for hash_str in unknown_keys:
                version_map[hash_str] = unknown_label
            version_stats[unknown_label] = len(unknown_keys)
            print(f"Found {len(unknown_keys)} keys not in any version file (marked as {unknown_label})")
    else:
        # No version files, mark everything as unknown
        for hash_str in all_hashes:
            version_map[hash_str] = "unknown"
        version_stats["unknown"] = len(all_hashes)

    # Override with exact version files (higher priority)
    # This removes the "-" suffix for keys we know exactly when they were introduced
    if exact_files:
        print()
        for exact_file in exact_files:
            # Extract version from filename (e.g., "version-26.0-exact.txt" -> "26.0")
            version_str = exact_file.stem.replace('version-', '').replace('-exact', '')
            exact_hashes = read_version_file(exact_file)
            
            print(f"Reading exact version file {exact_file}...")
            print(f"Found {len(exact_hashes)} keys exactly introduced in iOS {version_str}")
            
            # Override the version for these keys (remove the "-" suffix)
            overridden_count = 0
            for hash_str in exact_hashes:
                if hash_str in version_map:
                    old_version = version_map[hash_str]
                    version_map[hash_str] = version_str
                    
                    # Update statistics
                    if old_version in version_stats:
                        version_stats[old_version] -= 1
                    if version_str not in version_stats:
                        version_stats[version_str] = 0
                    version_stats[version_str] += 1
                    overridden_count += 1
                else:
                    # Key not in mapping, just add it
                    version_map[hash_str] = version_str
                    if version_str not in version_stats:
                        version_stats[version_str] = 0
                    version_stats[version_str] += 1
            
            print(f"Marked {overridden_count} keys with exact version iOS {version_str}")

    # Sort for consistent output
    sorted_hashes = sorted(version_map.keys())

    # Generate the Python file
    print(f"\nGenerating {output_file}...")
    with output_file.open('w') as f:
        f.write('"""iOS version information for MobileGestalt keys.\n\n')
        f.write('This file is auto-generated by populate_versions.py.\n')
        f.write('Do not edit manually.\n\n')
        f.write('Version files:\n')
        f.write('- version-X.Y.txt: Cumulative snapshots (all keys up to iOS X.Y)\n')
        f.write('- version-X.Y-exact.txt: Keys introduced exactly in iOS X.Y (overrides)\n\n')
        f.write('Keys are annotated with:\n')
        f.write('- "pre-X.Y": Existed in the earliest tracked version (iOS X.Y)\n')
        f.write('- "X.Y": Exactly introduced in iOS X.Y (from -exact.txt file)\n')
        f.write('- "X.Y-": Introduced between previous version and X.Y (exact version unknown)\n')
        f.write('- "post-X.Y": Not in any tracked version (newer or undiscovered)\n')
        f.write('"""\n\n')
        f.write('# Dictionary mapping obfuscated key hash -> iOS version introduced\n')
        f.write('KEY_IOS_VERSIONS = {\n')

        for hash_str in sorted_hashes:
            version = version_map[hash_str]
            f.write(f'    "{hash_str}": "{version}",\n')

        f.write('}\n')

    # Print statistics
    print(f"\n✓ Generated {output_file}")
    print(f"  - Total keys: {len(version_map)}")

    # Sort stats for better readability
    # First show pre-*, then numeric versions, then post-*
    pre_stats = [(k, v) for k, v in version_stats.items() if k.startswith('pre-')]
    version_stats_numeric = [(k, v) for k, v in version_stats.items() if not k.startswith('pre-') and not k.startswith('post-') and k != 'unknown']
    post_stats = [(k, v) for k, v in version_stats.items() if k.startswith('post-') or k == 'unknown']

    for version_str, count in pre_stats:
        print(f"  - {version_str}: {count}")

    # Sort numeric versions properly
    try:
        version_stats_numeric.sort(key=lambda x: parse_version(x[0]))
    except:
        version_stats_numeric.sort()

    for version_str, count in version_stats_numeric:
        print(f"  - iOS {version_str}: {count}")

    for version_str, count in post_stats:
        print(f"  - {version_str}: {count}")


if __name__ == '__main__':
    generate_keys_versions()
