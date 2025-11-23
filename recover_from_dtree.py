import json
import sys
import os

# Add current directory to sys.path to import keys_desc and obfuscate
sys.path.append(os.getcwd())

try:
    from keys_desc import unknown_keys_desc, known_keys_desc
    from obfuscate import calculate_obfuscated_key
except ImportError:
    print("Error: Could not import necessary modules")
    sys.exit(1)

def extract_properties(node_list, candidates):
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

def main():
    try:
        with open("devicetree.json", "r") as f:
            dt = json.load(f)
    except FileNotFoundError:
        print("Error: devicetree.json not found")
        return

    candidates = set()
    
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
    
    # Check against all keys
    all_hashes = {**unknown_keys_desc, **known_keys_desc}
    
    for candidate in candidates:
        h = calculate_obfuscated_key(candidate)
        
        if h in unknown_keys_desc:
            print(f"FOUND NEW: {h} -> {candidate}")
            new_found_count += 1
            found_count += 1
        elif h in known_keys_desc:
            # print(f"FOUND KNOWN: {h} -> {candidate}")
            found_count += 1
            
    print(f"Total matches found: {found_count}")
    print(f"New keys recovered: {new_found_count}")

if __name__ == "__main__":
    main()
