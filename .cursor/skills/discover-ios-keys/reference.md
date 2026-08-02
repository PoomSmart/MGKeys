# MGKeys Discovery Reference

## Option A — full IPSW once (dylib + dtree)

```bash
DEVICE=iPhone15,2
VERSION=26.6          # or BUILD=23G71
BUILD=23G71
CACHE=dyld_shared_cache/${BUILD}__${DEVICE}

# Download once (~10 GB); keep until dylib + dtree extracted
ipsw download ipsw --device "$DEVICE" --build "$BUILD" --confirm
IPSW=$(find . -maxdepth 1 -name "*_${BUILD}_*.ipsw" | head -1)

# Extract dyld + dylib
mkdir -p "$CACHE"
ipsw extract --dyld "$IPSW" --output "$CACHE"
# Cache may land in nested subdir:
INNER="$CACHE/${BUILD}__${DEVICE}"
ipsw dyld extract "$INNER/dyld_shared_cache_arm64e" libMobileGestalt.dylib --output "$INNER"
cp "$INNER"/libMobileGestalt*.dylib ./libMobileGestalt.dylib

# Extract DeviceTree from same IPSW
ipsw extract --dtree "$IPSW"
./dump-dtree.sh "$(find . -name 'DeviceTree*' -type f -not -name '*.json' | head -1)"

# Optional: rm -f "$IPSW"
```

## Option B — remote dyld once (gestalt-only)

```bash
./discover-version.sh iPhone15,2 26.6 --remote-extract
comm -13 <(sort versions/version-26.5.txt) <(sort versions/version-26.6.txt)
comm -23 <(sort versions/version-26.5.txt) <(sort versions/version-26.6.txt)
```

Add dtree later from a kept local IPSW: `./dump-dtree.sh <file.ipsw>` — not `-d -v` remote mode.

## Post-process only (after local extract)

```bash
./discover.sh && ./deobfuscate.sh arm64e
./discover-version.sh iPhone15,2 26.6 --post-process-only
```

## Secondary recovery

```bash
python3 recover_from_dtree.py
python3 recover_from_all_dtrees.py   # batch im4p files
python3 guess_keys.py
```

## Hashcat (last resort)

```bash
./combine-hashes.sh
python3 gen_md5.py
python3 gen_mapping.py
# run hashcat on md5hashes.txt, then update deobfuscated.py manually
```

## Obfuscation algorithm

```
MD5("MGCopyAnswer" + key) → base64 → truncate to 22 chars
```

Implemented in `obfuscate.py` as `calculate_obfuscated_key()`.

## Scripts to avoid combining (redundant fetches)

Do not run these in sequence for the same version:

1. `extract-version-hashes.sh --remote-extract`
2. `discover-version.sh --remote-extract`
3. `dump-dtree.sh -d <DEVICE> -v <VERSION>`

Use Option A or B instead.
