# MGKeys

Mapping of the obfuscated keys (or questions) used by iOS's MobileGestalt to the de-obfuscated, easier-to-understand ones. To obfuscate a key, Apple calculates the base64 of `MGCopyAnswer{theKey}`, truncates the last two characters and calculates the MD5 from the resulting string.

It is our job to de-obfuscate them all.

The keys are currently based on iOS 26.1.

## Patterns

There are a few certain patterns of the key names, which can be useful for de-obfuscation.

- Kebab case `some-key-name`
    - `has-xxx`
    - `supports-xxx`
- Pascal case of `DeviceSupportsXXX` (common)
- Pascal case of `XXXCapability` (common)
    - `FrontFacing(Camera)XXXCapability`
    - `RearFacing(Camera)XXXCapability`
- Pascal case of `SupportsXXX`
- Pascal case of `HasXXX`
- Pascal case of `IsXXX`
- Pascal case of `XXXData` (usually come alongside another key without `Data` suffix in it)

## Non-Gestalt Keys

There are also keys which are obfuscated the same way but are not considered as MobileGestalt keys. That is, you can't use `MGCopyAnswer` to get the value of the key. Instead, they are used for retrieving the value from the `IODeviceTree`, in an obfuscated manner. These keys are mostly in the kebab case, having their pascal case equivalent which is actually used by `MGCopyAnswer`. In the mapping files, these keys are marked with a comment `// non-gestalt-key`.

## Typical Workflow

1. Extract `libMobileGestalt.dylib` from the `dyld_shared_cache` of an iOS device
2. Run `deobfuscate.sh` script to get the new unmapped obfuscated keys
3. Throw the dylib into Hopper or IDA to find the human-readable function that is referenced by each key
4. Update the key mapping in `deobfuscated.py`
5. Run `deobfuscate.sh` again to update the mapping and to also verify each function name converts to the obfuscated key it references to
6. Move all keys that fail to convert to `unknown_keys_desc` of `keys_desc.py`, if any

## Automated Discovery

You can use `discover-version.sh` to automate the process of downloading an IPSW (or extracting remotely), extracting `libMobileGestalt.dylib`, and running the discovery scripts.

Usage:
```bash
./discover-version.sh <DEVICE> <VERSION_OR_BUILD> [ARCH] [--remote-extract]
```

Examples:
```bash
# Download IPSW for iPhone 14 Pro, iOS 16.5
./discover-version.sh iPhone15,2 16.5

# Use remote extraction (faster, no full download) for a specific build
./discover-version.sh iPhone15,2 20F66 --remote-extract
```

## Advanced Recovery Workflows

### Guessing Keys
If you have hints about the key (e.g., from `keys_desc.py`), you can use `guess_keys.py` to generate and verify potential key names:
```bash
python3 guess_keys.py
```

### Recovering from DeviceTree
Some keys are properties in the IODeviceTree. You can extract them from an IPSW or a DeviceTree file:

1. **Dump DeviceTree to JSON:**
   Use `dump_dtree.sh` with an IPSW file, a raw DeviceTree file, or specify a device and version for remote extraction:
   
   **Local File:**
   ```bash
   ./dump_dtree.sh <path/to/ipsw_or_dtree>
   ```

   **Remote Extraction:**
   ```bash
   ./dump_dtree.sh -d <DEVICE> -v <VERSION> [-b <BUILD>]
   # Example:
   ./dump_dtree.sh -d iPhone15,2 -v 16.5
   ```
   
   This will generate `devicetree.json`.

2. **Recover Keys:**
   Run `recover_from_dtree.py` to parse the JSON and check for matching keys:
   ```bash
   python3 recover_from_dtree.py
   ```

## Credits (Keys De-obfuscation)
- Jonathan Levin
- [Timac](https://twitter.com/timacfr)
- [Siguza](https://twitter.com/s1guza)
- [Elias Limneos](https://twitter.com/limneos)
- [PoomSmart](https://twitter.com/PoomSmart)
- [JackoPlane](https://twitter.com/JackoPlane)

## Further Readings
- http://newosxbook.com/articles/guesstalt.html by Jonathan Levin
- https://blog.timac.org/2017/0124-deobfuscating-libmobilegestalt-keys/ by Timac
- https://blog.timac.org/2018/1126-deobfuscated-libmobilegestalt-keys-ios-12/ by Timac
