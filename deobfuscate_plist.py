#!/usr/bin/env python3
"""
Transform obfuscated keys in com.apple.MobileGestalt.plist to deobfuscated ones.
Uses the mapping from deobfuscated.py to replace obfuscated keys with their readable names.
Preserves the original order and formatting of the plist file.
"""

import sys
from pathlib import Path
from typing import Optional
import re

# Import the mapping
from deobfuscated import keys as obfuscated_to_deobfuscated_map


def deobfuscate_plist(input_path: str, output_path: Optional[str] = None):
    """
    Transform obfuscated keys in a plist file to their deobfuscated versions.

    Args:
        input_path: Path to the input plist file
        output_path: Path to save the deobfuscated plist (defaults to input_path with _deobfuscated suffix)

    Returns:
        Tuple of (transformed_count, total_keys)
    """
    # Read the original plist as text to preserve formatting and order
    with open(input_path, 'r', encoding='utf-8') as f:
        plist_text = f.read()

    transformed_count = 0
    total_keys = 0

    # Find the CacheExtra section
    cache_extra_start = plist_text.find('<key>CacheExtra</key>')
    if cache_extra_start == -1:
        print("Warning: CacheExtra section not found in plist")
        return 0, 0

    # Find the start of the CacheExtra dict
    cache_extra_dict_start = plist_text.find('<dict>', cache_extra_start)
    if cache_extra_dict_start == -1:
        print("Warning: CacheExtra dict not found")
        return 0, 0

    # Find the end of CacheExtra dict by counting depth
    depth = 0
    pos = cache_extra_dict_start
    cache_extra_dict_end = -1

    while pos < len(plist_text):
        dict_open = plist_text.find('<dict>', pos)
        dict_close = plist_text.find('</dict>', pos)

        if dict_close == -1:
            break

        if dict_open != -1 and dict_open < dict_close:
            depth += 1
            pos = dict_open + 6
        else:
            if depth == 0:
                cache_extra_dict_end = dict_close + 7
                break
            depth -= 1
            pos = dict_close + 7

    if cache_extra_dict_end == -1:
        print("Warning: Could not find end of CacheExtra dict")
        return 0, 0

    # Extract the CacheExtra section
    before_section = plist_text[:cache_extra_dict_start]
    cache_extra_section = plist_text[cache_extra_dict_start:cache_extra_dict_end]
    after_section = plist_text[cache_extra_dict_end:]

    # Pattern to match plist keys
    key_pattern = re.compile(r'<key>([^<]+)</key>')

    # Find all keys and replace obfuscated ones
    matches = list(key_pattern.finditer(cache_extra_section))

    # Skip the first match if it's just whitespace context
    for match in matches:
        key = match.group(1)
        if key in obfuscated_to_deobfuscated_map:
            total_keys += 1
            deobfuscated_key = obfuscated_to_deobfuscated_map[key]
            old_key_tag = f'<key>{key}</key>'
            new_key_tag = f'<key>{deobfuscated_key}</key>'
            # Only replace the first occurrence to handle duplicates properly
            cache_extra_section = cache_extra_section.replace(old_key_tag, new_key_tag, 1)
            print(f"Transformed: {key} -> {deobfuscated_key}")
            transformed_count += 1
        else:
            # Count keys that aren't in the mapping (but are actual keys, not nested dict keys)
            # We can identify CacheExtra keys as those that appear at the top level of the dict
            if key != 'CacheExtra':
                # Check if this is a top-level key by looking at indentation
                line_start = cache_extra_section.rfind('\n', 0, match.start()) + 1
                indent = match.start() - line_start
                # Top level keys in CacheExtra typically have 2 tabs (16 spaces or 2 tabs)
                if indent <= 20:  # Reasonable threshold for top-level keys
                    total_keys += 1

    # Reconstruct the plist
    plist_text = before_section + cache_extra_section + after_section

    # Determine output path
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_deobfuscated{input_file.suffix}")

    # Write the transformed plist
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(plist_text)

    print(f"\nTransformation complete!")
    print(f"Total keys: {total_keys}")
    print(f"Transformed: {transformed_count} ({transformed_count/total_keys*100:.2f}%)" if total_keys > 0 else "No keys found")
    print(f"Output saved to: {output_path}")

    return transformed_count, total_keys


def main():
    if len(sys.argv) < 2:
        print("Usage: python deobfuscate_plist.py <input_plist> [output_plist]")
        print("\nExample:")
        print("  python deobfuscate_plist.py com.apple.MobileGestalt.plist")
        print("  python deobfuscate_plist.py com.apple.MobileGestalt.plist output.plist")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(input_path).exists():
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)

    try:
        deobfuscate_plist(input_path, output_path)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
