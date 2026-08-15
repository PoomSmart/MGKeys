# MGKeys Discovery Reference

## Option A — full IPSW once (dylib + dtree)

```bash
DEVICE=iPhone15,2
VERSION=26.6          # or use VERSION=27.0 with a beta BUILD
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

For an unindexed beta, provide the final version, build, and direct Apple URL:

```bash
./discover-version.sh iPhone16,1 27.0 arm64e \
  --build 24A5408d \
  --ipsw-url "https://updates.cdn-apple.com/path/to/restore.ipsw"
./dump-dtree.sh --url "https://updates.cdn-apple.com/path/to/restore.ipsw"
```

Beta builds are stored under the final version number, so beta 5 of iOS 27.0
uses `versions/version-27.0.txt`.

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

## IDA reverse engineering

For unresolved hashes, open the IDA database produced from the dyld shared
cache rather than only `libMobileGestalt.dylib`:

```text
dyld_shared_cache/<BUILD>__<DEVICE>/dyld_shared_cache_arm64e.i64
```

Search the hash, follow data xrefs into MobileGestalt tables, and decompile
the associated lookup functions. Record evidence-based hints in
`keys_desc.py`; retain `NULL` mappings when no semantic name is established.

## Simulator-only hashes

```bash
./extract-sim-hashes.sh
./extract-sim-hashes.sh libMobileGestalt_sim.dylib arm64
./extract-sim-hashes.sh --no-post-process
./extract-sim-hashes.sh --no-discover
```

Discovery uses `DYLIB=... SKIP_MAYBE_NON_GESTALT=1 ./discover.sh --arch arm64` then `python3 sync_discovered_keys.py --legacy-only`. Do not run `discover-version.sh`, `deobfuscate.sh`, or `extract-hashes.sh` against the simulator dylib.

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
