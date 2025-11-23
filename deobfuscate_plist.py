#!/usr/bin/env python3
"""
Transform obfuscated keys in com.apple.MobileGestalt.plist to deobfuscated ones.
Uses the mapping from deobfuscated.py to replace obfuscated keys with their readable names.
"""

import plistlib
import sys
from pathlib import Path

# Import the mapping
from deobfuscated import keys as obfuscated_to_deobfuscated_map
from typing import Optional


def deobfuscate_plist(input_path: str, output_path: Optional[str] = None):
    """
    Transform obfuscated keys in a plist file to their deobfuscated versions.
    
    Args:
        input_path: Path to the input plist file
        output_path: Path to save the deobfuscated plist (defaults to input_path with _deobfuscated suffix)
    
    Returns:
        Tuple of (transformed_count, total_keys)
    """
    # Read the plist
    with open(input_path, 'rb') as f:
        plist_data = plistlib.load(f)
    
    transformed_count = 0
    total_keys = 0
    
    # Process CacheExtra dictionary
    if 'CacheExtra' in plist_data and isinstance(plist_data['CacheExtra'], dict):
        cache_extra = plist_data['CacheExtra']
        keys_to_transform = {}
        
        for obfuscated_key in list(cache_extra.keys()):
            total_keys += 1
            if obfuscated_key in obfuscated_to_deobfuscated_map:
                deobfuscated_key = obfuscated_to_deobfuscated_map[obfuscated_key]
                keys_to_transform[obfuscated_key] = deobfuscated_key
                transformed_count += 1
        
        # Transform the keys
        for obfuscated_key, deobfuscated_key in keys_to_transform.items():
            cache_extra[deobfuscated_key] = cache_extra.pop(obfuscated_key)
            print(f"Transformed: {obfuscated_key} -> {deobfuscated_key}")
    
    # Determine output path
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_deobfuscated{input_file.suffix}")
    
    # Write the transformed plist
    with open(output_path, 'wb') as f:
        plistlib.dump(plist_data, f)
    
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
        sys.exit(1)


if __name__ == "__main__":
    main()
