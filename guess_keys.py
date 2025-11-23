import sys
from obfuscate import calculate_obfuscated_key
from keys_desc import unknown_keys_desc

def generate_guesses(hint, start_char):
    guesses = set()
    
    # Basic guess: just the hint itself (if it looks like a key)
    guesses.add(hint)
    
    # If hint is CamelCase, try variations
    if hint[0].isupper():
        # Try lowercase first letter
        guesses.add(hint[0].lower() + hint[1:])
        
        # Try adding "Device" prefix if not present
        if not hint.startswith("Device"):
            guesses.add("Device" + hint)
            
        # Try adding "Supports" if it looks like a capability
        if not "Supports" in hint:
            guesses.add("DeviceSupports" + hint)
            guesses.add("Supports" + hint)
            
    # Try to match start char if provided
    if start_char:
        filtered_guesses = set()
        for g in guesses:
            if g.startswith(start_char):
                filtered_guesses.add(g)
        
        # If we filtered everything out, maybe the hint was just a property name
        # and we need to construct the key from it matching the start char
        if not filtered_guesses:
            # Common prefixes
            prefixes = ["Device", "Supports", "Has", "Is", "Allow"]
            for p in prefixes:
                candidate = p + hint
                if candidate.startswith(start_char):
                    guesses.add(candidate)
                    
    return guesses

def main():
    print(f"Attempting to guess {len(unknown_keys_desc)} unknown keys...")
    
    found_count = 0
    
    for obfuscated_key, desc in unknown_keys_desc.items():
        # Parse desc for hints
        # Format: "non-gestalt-key, IODeviceTree:/path, starts with x, HintName"
        parts = [p.strip() for p in desc.split(",")]
        
        start_char = None
        hint_name = None
        
        for part in parts:
            if part.startswith("starts with "):
                start_char = part.replace("starts with ", "").strip()
            elif " " not in part and "/" not in part and part != "non-gestalt-key":
                hint_name = part
                
        if hint_name:
            guesses = generate_guesses(hint_name, start_char)
            
            for guess in guesses:
                calculated_hash = calculate_obfuscated_key(guess)
                if calculated_hash == obfuscated_key:
                    print(f"FOUND: {obfuscated_key} -> {guess}")
                    found_count += 1
                    break
                    
    print(f"Finished. Found {found_count} keys.")

if __name__ == "__main__":
    main()
