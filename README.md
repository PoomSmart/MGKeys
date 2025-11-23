# MGKeys

Mapping of the obfuscated keys (or questions) used by iOS's MobileGestalt to the de-obfuscated, easier-to-understand ones. To obfuscate a key, Apple calculates the base64 of `MGCopyAnswer{theKey}`, truncates the last two characters and calculates the MD5 from the resulting string.

It is our job to de-obfuscate them all.

The keys are currently based on iOS 26.2b3.

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

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/PoomSmart/MGKeys.git
cd MGKeys

# Install dependencies (optional, for development)
pip3 install -r requirements.txt
```

### Typical Workflow

1. Extract `libMobileGestalt.dylib` from the `dyld_shared_cache` of an iOS device
2. Run `deobfuscate.sh` script to get the new unmapped obfuscated keys
3. Throw the dylib into Hopper or IDA to find the human-readable function that is referenced by each key
4. Update the key mapping in `deobfuscated.py`
5. Run `deobfuscate.sh` again to update the mapping and to also verify each function name converts to the obfuscated key it references to
6. Move all keys that fail to convert to `unknown_keys_desc` of `keys_desc.py`, if any

## Usage

All scripts support `--help` flags for detailed usage information. Run any script with `--help` to see available options and examples.

### Automated Discovery

Use `discover-version.sh` to automate downloading an IPSW, extracting `libMobileGestalt.dylib`, and running discovery:

```bash
./discover-version.sh <DEVICE> <VERSION_OR_BUILD> [ARCH] [--remote-extract]

# Examples
./discover-version.sh iPhone15,2 16.5
./discover-version.sh iPhone15,2 20F66 --remote-extract
```

### Manual Discovery

For manual key discovery from an extracted dylib:

```bash
# Run discovery with default architecture (arm64e)
./discover.sh

# Specify architecture
./discover.sh --arch arm64

# See all options
./discover.sh --help
```

### Advanced Recovery Methods

#### Guessing Keys from Hints

If you have hints about unknown keys (from `keys_desc.py`):

```bash
# Attempt to guess all unknown keys
python3 guess_keys.py

# Target a specific key with verbose output
python3 guess_keys.py --key <OBFUSCATED_KEY> --verbose

# See all options
python3 guess_keys.py --help
```

#### Recovering from DeviceTree

Extract keys from IODeviceTree properties:

```bash
# 1. Dump DeviceTree to JSON
./dump_dtree.sh <path/to/ipsw_or_dtree>
# Or from remote IPSW
./dump_dtree.sh -d <DEVICE> -v <VERSION>

# 2. Recover keys from the JSON
python3 recover_from_dtree.py

# See all options
./dump_dtree.sh --help
python3 recover_from_dtree.py --help
```

## Development

### Running Tests

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. test_*.py

# Run specific test file
pytest test_obfuscate.py -v
```

### Type Checking

The Python scripts include comprehensive type hints:

```bash
# Install mypy (included in requirements.txt)
pip3 install -r requirements.txt

# Run type checker
mypy *.py
```

### Script Reference

All scripts support `--help` for detailed usage. Features:

- **Python scripts** (`*.py`): Type hints, pathlib, argparse, comprehensive error handling
- **Shell scripts** (`*.sh`): Help messages, prerequisite checks, input validation
- **Tests** (`test_*.py`): Comprehensive unit tests for core logic

Run any script with `--help` to see available options and examples.

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
