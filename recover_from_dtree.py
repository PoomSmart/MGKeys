import json
import argparse
from pathlib import Path
from typing import Dict, Set, Any, Optional

# Import from local modules
try:
    from keys_desc import unknown_keys_desc, known_keys_desc
    from obfuscate import calculate_obfuscated_key
except ImportError as e:
    print(f"Error: Could not import necessary modules: {e}")
    print("Make sure you're running this script from the MGKeys directory")
    exit(1)


def extract_properties(node_list: Any, candidates: Set[str]) -> None:
    """
    Recursively extract property names from DeviceTree nodes.
    
    Args:
        node_list: List of DeviceTree nodes
        candidates: Set to accumulate candidate property names
    """
    if not isinstance(node_list, list):
        return

    for item in node_list:
        if not isinstance(item, dict):
            continue
            
        for node_name, node_body in item.items():
            # Node name might be a candidate (unlikely but possible)
            candidates.add(node_name)
            
            if not isinstance(node_body, dict):
                continue
                
            for prop_name, prop_val in node_body.items():
                if prop_name == "children":
                    extract_properties(prop_val, candidates)
                else:
                    # Property name is a candidate
                    candidates.add(prop_name)


def load_devicetree(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load DeviceTree JSON file.
    
    Args:
        file_path: Path to devicetree.json
        
    Returns:
        Parsed JSON data or None if error
    """
    if not file_path.exists():
        print(f"Error: {file_path} not found")
        return None
    
    try:
        with file_path.open("r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON: {e}")
        return None


def main(devicetree_file: Path) -> None:
    """
    Main function to recover keys from DeviceTree.
    
    Args:
        devicetree_file: Path to devicetree.json file
    """
    dt = load_devicetree(devicetree_file)
    if dt is None:
        return

    candidates: Set[str] = set()
    
    # Root might be a dict with "device-tree"
    if isinstance(dt, dict) and "device-tree" in dt:
        # Add properties of device-tree itself
        root_body = dt["device-tree"]
        for k, v in root_body.items():
            if k == "children":
                extract_properties(v, candidates)
            else:
                candidates.add(k)
    elif isinstance(dt, list):
        extract_properties(dt, candidates)
    else:
        print("Unknown JSON structure root")
            
    print(f"Extracted {len(candidates)} unique properties from DeviceTree")

    found_count = 0
    new_found_count = 0
    
    for candidate in candidates:
        obfuscated_hash = calculate_obfuscated_key(candidate)
        
        if obfuscated_hash in unknown_keys_desc:
            print(f"FOUND NEW: {obfuscated_hash} -> {candidate}")
            new_found_count += 1
            found_count += 1
        elif obfuscated_hash in known_keys_desc:
            # Uncomment to see known matches
            # print(f"FOUND KNOWN: {obfuscated_hash} -> {candidate}")
            found_count += 1
            
    print(f"Total matches found: {found_count}")
    print(f"New keys recovered: {new_found_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recover MobileGestalt keys from DeviceTree JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 recover_from_dtree.py
  python3 recover_from_dtree.py path/to/devicetree.json
  python3 recover_from_dtree.py --file custom.json
        """
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="devicetree.json",
        help="Path to devicetree.json file (default: devicetree.json)"
    )
    parser.add_argument(
        "-f", "--file",
        dest="file_flag",
        help="Alternative way to specify file path"
    )
    
    args = parser.parse_args()
    
    # Use --file flag if provided, otherwise positional arg
    file_path = Path(args.file_flag if args.file_flag else args.file)
    
    main(file_path)
