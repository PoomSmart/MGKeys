from deobfuscated_keys import *

unknown_with_desc = {
    "/EVOCjM/Nmb2roP5ebtEFA": "supports-spatial-facetime",
    "0rbLl0hXmTehfEduXfeJYQ": "X7SF9XDG+CBhoPIXA1YlCg",
    "1qDdT/85SS7sxriK0wIbbg": "MGIOMFBSupport.c",
    "2oKaRZpltNseA9gTdIKTQQ": "eW5H/Gwg0uqbMqFot70pYg",
    "2tBx5IzZX4CpUVJ79LfsVg": "tribeca",
    "5Y72WwdS5NYHdc00gEZ/DQ": "8DHlxr5ECKhTSL3HmlZQGQ: aqc-a, extlom-mac-address",
    "6WdGcQGw4VLzrgxJo+bcrw": "TF31PAB6aO8KAbPyNKSxKA",
    "7ZipyD32hkjOUTl66Q8REw": "has /usr/libexec/lockdownd(.internal) or not",
    "8bCjks0zVuOcdivIhytNbQ": "QVwCp3Lu9RLnxw7LO9DBfQ",
    "8S7ydMJ4DlCUF38/hI/fJA": "PearlCameraCapability",
    "a1r7npIrhXsZ7SmKRKC1eA": "supports-meteor or noqTy5fUbyK03UHxWigBBQ",
    "AspYltP/iGWg0qxfg7c/3w": "twodbl",
    "bbtR9jQx50Fv5Af/affNtA": "+VIu65zA5EW4ztayJXvOUg if AppleTV, IODeviceTree:/product, product-name otherwise",
    "byGRtH44VNik9CzN/QKLCw": "SBe5o/DMF5Z94MS+ZzmBCA",
    "DoMjIR2qPkxXtP/kDu/gfQ": "mesa type",
    "eW5H/Gwg0uqbMqFot70pYg": "soc-generation related",
    "eXzS2kvF8nNOI/xIJKquHg": "scandium, /arm-io, InterfaceName",
    "fYsrGTmVTbneEs3HKetEdQ": "IODeviceTree:/product/camera > ItOvlwIhFj2aCXL4wk3ijg",
    "IMUksyctl4kC/BFI2K/Qyw": "IODeviceTree:/product/camera > bmYssgjtQNKMy3Zhf8N+2w",
    "iTvGxmtSOnHv548XON379A": "mesa type",
    "JWjvsupiqWYtIGwr8yGd8w": "eW5H/Gwg0uqbMqFot70pYg",
    "kT9JwUR2xPCTHTdgvG3UdA": "Af/UTHptqxLPG5sy0wQTiw",
    "Lg1EJX11Jb7EbveB6+YgVQ": "lwHRTZNO5Jq87pVlzdNGIA (DeviceSupports720p)",
    "lo3szoQ4sLy7o3+ZD0GcAQ": "primary usage (page)",
    "m7lDS+oP8q0pGg+CO7RvPg": "IODeviceTree:/chosen > 4JalTKSe5a9I+mb00ATvag",
    "Mi/ME+v1wZqkvXFU3xX3KA": "eW5H/Gwg0uqbMqFot70pYg",
    "NDnoY3adyyskgiIQBNtlyQ": "IODeviceTree:/, model-config NED=1",
    "njUcH4bm+JBmvASakDdObg": "IODeviceTree:/arm-io/isp > /4LCTfMhvzuiK6b557ir5Q",
    "PFnuFyqMMnGUQQnTqS5byg": "IODeviceTree:/product > MlDJggkQz38CLQh3AVv7VQ",
    "RNcdWbM8+dO5tx82A+YCcQ": "host UUID",
    "STBQ8gY0pl0CK8VmRcks4w": "IODeviceTree:/product/camera > IvdL59ITgJvhb5ptpLbqRg",
    "VuGdqp8UBpi9vPWHlPluVQ": "array",
    "W/xqvBX9L07XHb0BOtYycQ": "yF2IQrYS4yyREV4ZkbLysw",
    "WAfNjeiwOd/k6+VU6D6SIQ": "5Y72WwdS5NYHdc00gEZ/DQ",
    "XnXl4MhKZx3zRKvA7ZwIYQ": "iPad ? 10 : 20",
    "XYlJKKkj2hztRP1NWWnhlw": "IODeviceTree:/chosen > E3qwwdwgUSy6FV6VC+Uf3A",
    "yF2IQrYS4yyREV4ZkbLysw": "AppleFillmoreDevice, local-mac-address-64",
    "Z06ZMtQY6G3kKrC7fs/gOA": "hSjeLvzobsJCklk4+pzu3g",
    "ZYqko/XM5zD3XBfN5RmaXA": "PiPPinned or IODeviceTree:/product > h9v96tCehBWUil/aJ7UrcA"
}

mapping = {}

with open('hashes.txt', 'r') as hashes:
    with open('mapping.h', 'w') as out:
        for raw_hash in hashes:
            hash = raw_hash.strip()
            if hash in deobfuscated_keys:
                mapping[hash] = f'"{deobfuscated_keys[hash]}",'
            elif hash in unknown_with_desc:
                mapping[hash] = f'NULL, // {unknown_with_desc[hash]}'
            else:
                mapping[hash] = 'NULL,'
        total = len(mapping)
        deobfuscated = len(deobfuscated_keys)
        out.write('#include "struct.h"\n\n')
        out.write(f'// Total: {total} keys\n')
        out.write(f'// Deobfuscated: {deobfuscated} keys ({round((deobfuscated / total) * 100, 2)}%)\n\n')
        out.write('static const struct tKeyMapping keyMappingTable[] = {\n')
        for hash in mapping:
            out.write(f'    "{hash}", {mapping[hash]}\n')
        out.write('    NULL, NULL\n};\n')