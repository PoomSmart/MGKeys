import argparse
from typing import Set, Optional
from obfuscate import calculate_obfuscated_key
from keys_desc import unknown_keys_desc


def generate_guesses(hint: str, start_char: Optional[str] = None) -> Set[str]:
    """
    Generate possible key name guesses from a hint.
    
    Args:
        hint: The hint/base name for the key
        start_char: Optional character the key must start with
        
    Returns:
        Set of possible key name guesses
    """
    if not hint:
        return {hint}
    
    guesses: Set[str] = set()
    
    # Basic guess: just the hint itself (if it looks like a key)
    guesses.add(hint)
    
    # If hint is CamelCase, try variations
    if hint and hint[0].isupper():
        # Try lowercase first letter
        guesses.add(hint[0].lower() + hint[1:])
        
        # Try adding "Device" prefix if not present
        if not hint.startswith("Device"):
            guesses.add("Device" + hint)
            
        # Try adding "Supports" if it looks like a capability
        if "Supports" not in hint:
            guesses.add("DeviceSupports" + hint)
            guesses.add("Supports" + hint)
        
        # Try other common prefixes
        if not hint.startswith("Has"):
            guesses.add("Has" + hint)
        if not hint.startswith("Is"):
            guesses.add("Is" + hint)
    
    # Try kebab-case to CamelCase conversion
    if "-" in hint:
        # Convert kebab-case to CamelCase
        parts = hint.split("-")
        camel = "".join(p.capitalize() for p in parts)
        guesses.add(camel)
        guesses.add("Device" + camel)
        guesses.add("DeviceSupports" + camel)
    
    # Filter by start character if provided
    if start_char:
        filtered_guesses: Set[str] = set()
        for g in guesses:
            if g.startswith(start_char):
                filtered_guesses.add(g)
        
        # If we filtered everything out, try common prefixes matching start_char
        if not filtered_guesses:
            # Common prefixes
            prefixes = ["Device", "Supports", "Has", "Is", "Allow", "Enable", "Disable"]
            for prefix in prefixes:
                if prefix.startswith(start_char):
                    candidate = prefix + hint
                    filtered_guesses.add(candidate)
        
        return filtered_guesses
    
    return guesses


def main(target_key: Optional[str] = None, verbose: bool = False) -> None:
    """
    Main function to guess unknown keys.
    
    Args:
        target_key: Optional specific obfuscated key to target
        verbose: Whether to show verbose output
    """
    keys_to_process = unknown_keys_desc
    
    if target_key:
        if target_key in unknown_keys_desc:
            keys_to_process = {target_key: unknown_keys_desc[target_key]}
        else:
            print(f"Error: Key {target_key} not found in unknown_keys_desc")
            return
    
    print(f"Attempting to guess {len(keys_to_process)} unknown keys...")
    
    found_count = 0
    total_keys = len(keys_to_process)
    
    for idx, (obfuscated_key, desc) in enumerate(keys_to_process.items(), 1):
        if verbose and idx % 10 == 0:
            print(f"Progress: {idx}/{total_keys} ({idx*100//total_keys}%)")
        
        # Parse desc for hints
        # Format: "non-gestalt-key, IODeviceTree:/path, starts with x, HintName"
        parts = [p.strip() for p in desc.split(",")]
        
        start_char: Optional[str] = None
        hint_name: Optional[str] = None
        
        for part in parts:
            if part.startswith("starts with "):
                start_char = part.replace("starts with ", "").strip()
            elif " " not in part and "/" not in part and part != "non-gestalt-key":
                hint_name = part
                
        if hint_name:
            guesses = generate_guesses(hint_name, start_char)
            
            if verbose:
                print(f"  Trying {len(guesses)} guesses for {obfuscated_key}...")
            
            for guess in guesses:
                calculated_hash = calculate_obfuscated_key(guess)
                if calculated_hash == obfuscated_key:
                    print(f"FOUND: {obfuscated_key} -> {guess}")
                    found_count += 1
                    break
                    
    print(f"Finished. Found {found_count} keys.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Guess unknown MobileGestalt keys based on hints",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-k", "--key",
        help="Target a specific obfuscated key"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output including progress"
    )
    
    args = parser.parse_args()
    
    main(target_key=args.key, verbose=args.verbose)
