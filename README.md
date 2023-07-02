# MGKeys

Mapping of the obfuscated keys (or questions) used by iOS's MobileGestalt to the de-obfuscated, easier-to-understand ones. To obfuscate a key, Apple calculates the base64 of `MGCopyAnswer{theKey}`, truncates the last two characters and calculates the MD5 from the resulting string.

It is our job to de-obfuscate them all.

## Patterns

There are a few certain patterns of the key names, which can be useful for de-obfuscation.

- Kebab case `some-key-name`
- Pascal case of `DeviceSupportsXXX` (common)
- Pascal case of `XXXCapability` (common)
    - `FrontFacing(Camera)XXXCapability`
    - `RearFacing(Camera)XXXCapability`
- Pascal case of `SupportsXXX`
- Pascal case of `HasXXX`
- Pascal case of `IsXXX`
- Pascal case of `XXXData` (usually come alongside another key without `Data` suffix in it)

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
