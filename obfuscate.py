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
