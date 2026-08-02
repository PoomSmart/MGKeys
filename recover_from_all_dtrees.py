import json
import subprocess
import glob

# Import from local modules
try:
    from keys_desc import unknown_keys_desc, known_keys_desc
    from obfuscate import calculate_obfuscated_key
except ImportError as e:
    print(f"Error: Could not import necessary modules: {e}")
    exit(1)

def extract_properties(node, path='', results=None):
    if results is None:
        results = []
    
    if isinstance(node, dict):
        for k, v in node.items():
            if k == 'children':
                extract_properties(v, path, results)
            elif isinstance(v, (dict, list)):
                extract_properties(v, path + '/' + k, results)
            else:
                results.append((path, k, v))
    elif isinstance(node, list):
        for item in node:
            extract_properties(item, path, results)
            
    return results

def main():
    dt_files = glob.glob("**/*.im4p", recursive=True)
    print(f"Found DeviceTree im4p files: {dt_files}")
    
    all_properties = {} # property_name -> set of paths
    
    for dt_file in dt_files:
        print(f"Processing {dt_file}...")
        try:
            res = subprocess.run(['ipsw', 'dtree', '--json', dt_file], capture_output=True, text=True, check=True)
            dt = json.loads(res.stdout)
            
            # Extract
            props = []
            if isinstance(dt, dict) and "device-tree" in dt:
                props = extract_properties(dt["device-tree"])
            elif isinstance(dt, list):
                props = extract_properties(dt)
            
            for path, name, val in props:
                if name not in all_properties:
                    all_properties[name] = set()
                all_properties[name].add((dt_file, path, str(val)))
                
        except Exception as e:
            print(f"Failed to process {dt_file}: {e}")
            
    print(f"Extracted {len(all_properties)} unique property names across all DeviceTrees.")
    
    new_found = {}
    for name in sorted(all_properties.keys()):
        h = calculate_obfuscated_key(name)
        if h in unknown_keys_desc:
            new_found[h] = name
            print(f"FOUND: {h} -> {name}")
            print("  Found in:")
            for dt_file, path, val in all_properties[name]:
                print(f"    - {dt_file} at {path} (value: {val})")
                
    print(f"Done. Found {len(new_found)} matches.")

if __name__ == "__main__":
    main()
