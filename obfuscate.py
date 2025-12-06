import hashlib
import base64

def calculate_obfuscated_key(key: str):
    if "\"" in key:
        key = key.replace("\\\"", "\"")
    pre = "MGCopyAnswer" + key
    md5_hash = hashlib.md5(pre.encode()).digest()
    obfuscated_key = base64.b64encode(md5_hash).decode()
    return obfuscated_key[:22]

def md5_string_for_obfuscated_key(key: str):
    if not key:
        return None

    base64_key = key + "=="
    try:
        data = base64.b64decode(base64_key)
    except base64.binascii.Error:
        return None

    if len(data) != 16:
        return None

    return ''.join(f'{byte:02x}' for byte in data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <mode> <key1> [key2 ...]", file=sys.stderr)
        print("Modes: obfuscate, md5", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    keys = sys.argv[2:]

    if mode == "obfuscate":
        for key in keys:
            print(calculate_obfuscated_key(key))
    elif mode == "md5":
        for key in keys:
            result = md5_string_for_obfuscated_key(key)
            if result:
                print(result)
            else:
                sys.exit(1)
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)
