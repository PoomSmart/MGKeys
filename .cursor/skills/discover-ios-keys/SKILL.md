---
name: discover-ios-keys
description: Discover and map new MobileGestalt keys for a new iOS version in MGKeys. Use when the user asks to discover keys for a new iOS version, update version snapshots, diff against the previous baseline, or run the MGKeys IPSW extraction and discovery pipeline.
---

# Discover iOS MobileGestalt Keys (MGKeys)

## Prerequisites

```bash
brew install blacktop/tap/ipsw
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Defaults: device `iPhone15,2`, arch `arm64e`, cache under `dyld_shared_cache/<BUILD>__<DEVICE>/`.

## Critical: single download

Do **not** run `extract-version-hashes.sh`, `discover-version.sh --remote-extract`, and `dump-dtree.sh -d -v` separately — each re-fetches from Apple's CDN. `lib-ipsw-extract.sh` has no cache-skip, and full IPSW fallback deletes the `.ipsw` after dyld extraction.

| Approach | When to use |
|----------|-------------|
| **Option A** (full IPSW once) | Need dylib + DeviceTree; preferred |
| **Option B** (remote dyld once) | Gestalt-only; skip separate hash snapshot |

See [reference.md](reference.md) for exact commands.

## Workflow checklist

```
- [ ] 1. Extract once (Option A or B)
- [ ] 2. Discover locally + post-process
- [ ] 3. Diff against previous version
- [ ] 4. Recover non-gestalt keys from DeviceTree
- [ ] 5. Reverse-engineer remaining unknowns in the dyld shared-cache IDA database
- [ ] 6. Guess remaining unknowns
- [ ] 7. Validate and update docs
```

### Step 1: Extract once

**Option A** — download IPSW once, extract dylib and dtree locally. Note: `ipsw extract --dyld` may nest cache at `dyld_shared_cache/<BUILD>__<DEVICE>/<BUILD>__<DEVICE>/`.

**Option B** — one shot:

```bash
./discover-version.sh iPhone15,2 <VERSION> --remote-extract
```

Skip `extract-version-hashes.sh`; `discover-version.sh` already writes `versions/version-<VERSION>.txt`.

### Step 2: Discover locally (Option A only)

```bash
./discover.sh
./deobfuscate.sh arm64e
./discover-version.sh iPhone15,2 <VERSION> --post-process-only
```

Post-processing writes `versions/version-<VERSION>.txt`, syncs `deobfuscated.py`, runs `populate_versions.py` and `gen_mapping.py`.

### Step 3: Diff against previous baseline

```bash
comm -13 <(sort versions/version-<PREV>.txt) <(sort versions/version-<VERSION>.txt)   # new
comm -23 <(sort versions/version-<PREV>.txt) <(sort versions/version-<VERSION>.txt)   # removed
```

Empty both diffs → metadata-only update (still add version file and bump README).

### Step 4: Non-gestalt recovery

Use `devicetree.json` from Step 1 — do not re-fetch remotely:

```bash
python3 recover_from_dtree.py
```

For multiple IPSWs: `python3 recover_from_all_dtrees.py` (scans `**/*.im4p`).

### Step 5: Reverse-engineer unknowns in IDA

Prefer the IDA database generated from the dyld shared cache over the
extracted dylib because it preserves shared-cache tables and cross-references:

```text
dyld_shared_cache/<BUILD>__<DEVICE>/dyld_shared_cache_arm64e.i64
```

Search unresolved hashes, follow data cross-references into MobileGestalt
registration tables, and decompile associated lookup functions. Record only
evidence-based paths or call-site findings in `keys_desc.py`; unresolved keys
should remain `NULL` rather than receive guessed names.

### Step 6: Remaining unknowns

```bash
python3 guess_keys.py
python3 guess_keys.py --key <HASH> --verbose
```

`./locate-usage.sh /path/to/iOS/source` only if an SDK/source tree is available.

Check triage artifacts:

| Category | Where to look |
|----------|---------------|
| Auto-mapped gestalt | `discover-obfuscated-mapped.txt`, `deobfuscated.py` |
| Non-gestalt | `maybe-non-gestalt-keys.txt`, `mapping.h` `NULL` entries |
| Unknown gestalt | `hashes.txt` minus `deobfuscated.py` |
| Removed | `comm -23` diff → `hashes_legacy.txt` |

### Step 7: Validate

```bash
.venv/bin/pytest
.venv/bin/mypy *.py
```

Update [README.md](../../../README.md) baseline line (`The keys are currently based on iOS …`). Confirm `versions/version-stats.txt` lists the new version.

## Expected outcomes

| Diff result | Action |
|-------------|--------|
| No change | Add `version-<VERSION>.txt`, bump README, extend mapping version comments |
| New gestalt hashes | Usually auto-mapped via `_MobileGestalt_*` symbols |
| New non-gestalt | `maybe-non-gestalt-keys.txt` → dtree recovery |
| Removed hashes | `sync_discovered_keys.py` moves to legacy; verify version-stats |

## Key files

- `versions/version-<VERSION>.txt` — hash snapshot (commit this)
- `versions/version-sim.txt` — simulator-only hashes (not in any physical snapshot)
- `deobfuscated.py` — key mappings
- `mapping.h`, `mapping-gestalt.h` — generated headers
- `keys_versions.py`, `versions/version-stats.txt` — version metadata
- `keys_desc.py` — unknown key hints

## Simulator-only list

Do **not** run device discovery against `libMobileGestalt_sim.dylib`. Use:

```bash
./extract-sim-hashes.sh
./extract-sim-hashes.sh libMobileGestalt_sim.dylib arm64 --no-post-process
```

That rewrites `versions/version-sim.txt`, appends new hashes to `hashes_legacy.txt`, discovers `_MobileGestalt_*` names into `deobfuscated_legacy.py` (`sync_discovered_keys.py --legacy-only`, no device-key moves), and regenerates `// Simulator` comments. Simulator dylibs are `arm64`, not `arm64e`.

## Additional resources

- Full Option A/B command blocks: [reference.md](reference.md)
- Project docs: [README.md](../../../README.md)
