---
name: discover-ios-keys
description: Discover and map new MobileGestalt keys for a new iOS version in MGKeys. Use when the user asks to discover keys for a new iOS version, update version snapshots, diff against the previous baseline, run the IPSW extraction pipeline, or check blacktop/ipsw-diffs for libMobileGestalt.dylib changes without downloading an IPSW.
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
| **Option A** (full IPSW once) | Need dylib + DeviceTree; preferred for first snapshot of a major version |
| **Option B** (remote dyld once) | Gestalt-only; skip separate hash snapshot |
| **Option C** (ipsw-diffs check) | [blacktop/ipsw-diffs](https://github.com/blacktop/ipsw-diffs) already has `libMobileGestalt.dylib.md` for the build pair; gestalt-only delta, no IPSW download |

See [reference.md](reference.md) for exact commands. Option C details: [reference.md § ipsw-diffs check mode](reference.md#ipsw-diffs-check-mode).

## Workflow checklist

Use **Option C** when the user points at an ipsw-diffs URL or only the RC→public (or adjacent beta) dylib diff matters. Skip Steps 1–2 and start at **Step 3C**, then 6–7; run Steps 4–5 only if non-gestalt or symbol/name mismatches remain.

```
- [ ] 1. Extract once (Option A or B) — skip for Option C
- [ ] 2. Discover locally + post-process — skip for Option C unless validating full snapshot
- [ ] 3. Diff against previous version (or 3C: parse ipsw-diffs)
- [ ] 4. Recover non-gestalt keys from DeviceTree — optional for Option C
- [ ] 5. Reverse-engineer remaining unknowns in the dyld shared-cache IDA database
- [ ] 6. Guess remaining unknowns
- [ ] 7. Validate and update docs
```

### Step 3C: ipsw-diffs check mode (Option C)

1. Open the dylib diff for the target build pair:
   `iOS/<major>_<minor>_<olderBuild>_vs_<major>_<minor>_<newerBuild>/DYLIBS/usr/lib/libMobileGestalt.dylib.md`
2. Collect **added** gestalt evidence:
   - New `_MobileGestalt_get_*` / `_MobileGestalt_copy_*` symbols
   - New 22-character obfuscated hash strings
   - New PascalCase or kebab-case strings tied to those symbols (MGCopyAnswer / DeviceTree plaintext on iOS 27+)
3. Derive the MGCopyAnswer name from each new symbol the same way `discover.sh` does: strip `_MobileGestalt_get_`, capitalize the first character only (`deviceSupportsFaceprint` → `DeviceSupportsFaceprint`).
4. **Verify every hash** with `calculate_obfuscated_key()` in `obfuscate.py`. Do not trust hash↔name pairing in the markdown; diff layout can swap adjacent strings.
5. If obfuscation does not match the hash in the diff, treat the symbol as a hint only: decompile the getter (Step 5) and search for `MGCopyAnswer` / `MGGetBoolAnswer` / literal question strings (example: symbol `arm64Ex1ExecutionCapability` vs question `arm64e.x1`).
6. Update mappings: add sorted entries to `deobfuscated.py` and `hashes.txt`. Build `versions/version-<VERSION>.txt` as **previous release snapshot + new hashes** (sorted like `hashes.txt`), or re-run Option A/B later to reconcile the full set.
7. Run `python3 populate_versions.py` then `python3 gen_mapping.py` (run `gen_mapping.py` again if version comments were missing). Confirm new keys show `// iOS <VERSION>+` in `mapping-gestalt.h`.

Ignore debug-only string churn (NVRAM labels, internal UUIDs) unless you establish a gestalt or non-gestalt mapping. Readable DeviceTree strings without a new obfuscated hash do not go into `hashes.txt`.

Full URL patterns, fetch tips, and a verification one-liner: [reference.md § ipsw-diffs check mode](reference.md#ipsw-diffs-check-mode).


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

Update [README.md](../../../README.md) **only** the baseline line (`The keys are currently based on iOS …`). Do not add release notes, new-key lists, or ipsw-diff links to the README. Confirm `versions/version-stats.txt` lists the new version.

## Expected outcomes

| Diff result | Action |
|-------------|--------|
| No change | Add `version-<VERSION>.txt`, bump README baseline only, extend mapping version comments |
| New gestalt hashes (Option C) | Map via symbols + `obfuscate.py`; extend snapshot; IDA if name≠hash |
| New gestalt hashes (A/B) | Usually auto-mapped via `_MobileGestalt_*` symbols |
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

- Full Option A/B/C command blocks: [reference.md](reference.md)
- ipsw-diffs gestalt-only workflow: [reference.md § ipsw-diffs check mode](reference.md#ipsw-diffs-check-mode)
- Project docs: [README.md](../../../README.md)
