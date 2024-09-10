# MGKeys

Mapping of the obfuscated keys (or questions) used by iOS's MobileGestalt to the de-obfuscated, easier-to-understand ones. To obfuscate a key, Apple calculates the base64 of `MGCopyAnswer{theKey}`, truncates the last two characters and calculates the MD5 from the resulting string.

It is our job to de-obfuscate them all.

The keys are currently based on iOS 18.0 RC.

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
