#!/usr/bin/env bash

# Update the simulator-only key list from a simulator libMobileGestalt.dylib.
# Does NOT replace hashes.txt or run device discovery.
#
# Usage: ./extract-sim-hashes.sh [DYLIB] [ARCH] [--no-post-process] [--no-discover]
# Example: ./extract-sim-hashes.sh
#          ./extract-sim-hashes.sh libMobileGestalt_sim.dylib arm64
#          ./extract-sim-hashes.sh --no-post-process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-ipsw-extract.sh"

DYLIB="libMobileGestalt_sim.dylib"
ARCH="arm64"
POST_PROCESS=true
DISCOVER=true
ALL_HASHES="sim-all-hashes.txt"
SIM_FILE="versions/version-sim.txt"
HASHES_FILE="hashes.txt"
LEGACY_FILE="hashes_legacy.txt"

show_help() {
    cat << EOF
Update simulator-only MobileGestalt hashes from a simulator dylib.

Usage: $0 [DYLIB] [ARCH] [--no-post-process] [--no-discover]

Arguments:
    DYLIB              Path to simulator libMobileGestalt (default: libMobileGestalt_sim.dylib)
    ARCH               Architecture (default: arm64; simulator dylibs are not arm64e)
    --no-post-process  Skip populate_versions.py and gen_mapping.py
    --no-discover      Skip symbol discovery / legacy name sync

This script:
    - Extracts hashes from the simulator dylib without touching hashes.txt
    - Writes versions/version-sim.txt with hashes that are not in any physical
      versions/version-X.Y.txt snapshot (or current hashes.txt)
    - Adds brand-new simulator-only hashes to hashes_legacy.txt
    - Removes current device hashes that were wrongly copied into hashes_legacy.txt
    - Discovers readable names from _MobileGestalt_* symbols and syncs them
      into deobfuscated_legacy.py (--legacy-only; does not move device keys)
    - Regenerates // Simulator annotations unless --no-post-process is set

Do NOT run discover-version.sh, deobfuscate.sh, or extract-hashes.sh against
the simulator dylib; those overwrite device hashes.txt.

Examples:
    $0
    $0 libMobileGestalt_sim.dylib arm64
    $0 --no-post-process

EOF
}

for arg in "$@"; do
    case "$arg" in
        -h|--help)
            show_help
            exit 0
            ;;
    esac
done

POSITIONAL=()
for arg in "$@"; do
    case "$arg" in
        --no-post-process)
            POST_PROCESS=false
            ;;
        --no-discover)
            DISCOVER=false
            ;;
        -h|--help)
            ;;
        *)
            POSITIONAL+=("$arg")
            ;;
    esac
done

if [[ ${#POSITIONAL[@]} -ge 1 ]]; then
    DYLIB="${POSITIONAL[0]}"
fi
if [[ ${#POSITIONAL[@]} -ge 2 ]]; then
    ARCH="${POSITIONAL[1]}"
fi

if [[ ! -f "$DYLIB" ]]; then
    log_error "Simulator dylib not found: $DYLIB"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    log_error "python3 not found"
    exit 1
fi

mkdir -p versions

log_info "Extracting simulator hashes from $DYLIB ($ARCH)"
DYLIB="$DYLIB" OUT="$ALL_HASHES" "$SCRIPT_DIR/extract-hashes.sh" "$ARCH"

# comm(1) requires C-locale byte order. sort -f is case-insensitive and
# produces a different order, so mixed-case hashes (e.g. current device keys)
# were incorrectly treated as simulator-only.
c_sort() {
    LC_ALL=C sort -u "$@"
}

PHYSICAL_FILE="$(mktemp)"
KNOWN_FILE="$(mktemp)"
NEW_LEGACY="$(mktemp)"
PRUNED_LEGACY="$(mktemp)"
ALL_SORTED="$(mktemp)"
SIM_SORTED="$(mktemp)"
trap 'rm -f "$PHYSICAL_FILE" "$KNOWN_FILE" "$NEW_LEGACY" "$PRUNED_LEGACY" "$ALL_SORTED" "$SIM_SORTED"' EXIT

{
    if compgen -G "versions/version-[0-9]*.txt" > /dev/null; then
        cat versions/version-[0-9]*.txt
    fi
    if [[ -f "$HASHES_FILE" ]]; then
        cat "$HASHES_FILE"
    fi
} | c_sort > "$PHYSICAL_FILE"

c_sort "$ALL_HASHES" -o "$ALL_SORTED"
LC_ALL=C comm -23 "$ALL_SORTED" "$PHYSICAL_FILE" | c_sort > "$SIM_SORTED"
ALL_COUNT=$(wc -l < "$ALL_HASHES" | tr -d ' ')
log_info "Found $(wc -l < "$SIM_SORTED" | tr -d ' ') simulator-only hashes in this dylib"

touch "$LEGACY_FILE"
c_sort "$LEGACY_FILE" -o "$KNOWN_FILE"
PRUNED_COUNT=0
if [[ -f "$HASHES_FILE" ]]; then
    CURRENT_SORTED="$(mktemp)"
    trap 'rm -f "$PHYSICAL_FILE" "$KNOWN_FILE" "$NEW_LEGACY" "$PRUNED_LEGACY" "$ALL_SORTED" "$SIM_SORTED" "$CURRENT_SORTED"' EXIT
    c_sort "$HASHES_FILE" -o "$CURRENT_SORTED"
    LC_ALL=C comm -23 "$KNOWN_FILE" "$CURRENT_SORTED" > "$PRUNED_LEGACY"
    PRUNED_COUNT=$(LC_ALL=C comm -12 "$KNOWN_FILE" "$CURRENT_SORTED" | wc -l | tr -d ' ')
    if [[ "$PRUNED_COUNT" -gt 0 ]]; then
        sort -f "$PRUNED_LEGACY" > "$LEGACY_FILE"
        log_info "Removed $PRUNED_COUNT current device hashes from $LEGACY_FILE"
    fi
    c_sort "$LEGACY_FILE" -o "$KNOWN_FILE"
fi

known_inputs=("$LEGACY_FILE")
if [[ -f "$HASHES_FILE" ]]; then
    known_inputs+=("$HASHES_FILE")
fi
c_sort "${known_inputs[@]}" > "$KNOWN_FILE"

LC_ALL=C comm -23 "$SIM_SORTED" "$KNOWN_FILE" > "$NEW_LEGACY"
NEW_COUNT=$(wc -l < "$NEW_LEGACY" | tr -d ' ')

if [[ "$NEW_COUNT" -gt 0 ]]; then
    cat "$NEW_LEGACY" >> "$LEGACY_FILE"
    sort -fu "$LEGACY_FILE" -o "$LEGACY_FILE"
    log_info "Added $NEW_COUNT new simulator-only hashes to $LEGACY_FILE"
else
    log_info "No new hashes to add to $LEGACY_FILE"
fi

# Keep historical simulator-only hashes that never appeared on a physical
# device, even if this particular sim dylib no longer contains them.
LEGACY_SIM="$(mktemp)"
trap 'rm -f "$PHYSICAL_FILE" "$KNOWN_FILE" "$NEW_LEGACY" "$PRUNED_LEGACY" "$ALL_SORTED" "$SIM_SORTED" "$CURRENT_SORTED" "$LEGACY_SIM"' EXIT
c_sort "$LEGACY_FILE" -o "$KNOWN_FILE"
LC_ALL=C comm -23 "$KNOWN_FILE" "$PHYSICAL_FILE" | c_sort > "$LEGACY_SIM"
c_sort "$SIM_SORTED" "$LEGACY_SIM" | sort -f > "$SIM_FILE"

SIM_COUNT=$(wc -l < "$SIM_FILE" | tr -d ' ')
log_info "Wrote $SIM_FILE ($SIM_COUNT simulator-only, including historical)"

DISCOVERED_COUNT=0
if [[ "$DISCOVER" == true ]]; then
    log_info "Discovering readable names from $DYLIB"
    DYLIB="$DYLIB" SKIP_MAYBE_NON_GESTALT=1 "$SCRIPT_DIR/discover.sh" --arch "$ARCH"
    discover_output=$(python3 "$SCRIPT_DIR/sync_discovered_keys.py" --legacy-only)
    while IFS= read -r line; do
        case "$line" in
            ADDED=*) DISCOVERED_COUNT=${line#ADDED=} ;;
            ERROR*) log_error "$line" ; exit 1 ;;
        esac
    done <<< "$discover_output"
    log_info "Synced $DISCOVERED_COUNT discovered names into deobfuscated_legacy.py"
else
    log_info "Skipped symbol discovery (--no-discover)"
fi

if [[ "$POST_PROCESS" == true ]]; then
    python3 "$SCRIPT_DIR/gen_mapping.py"
    python3 "$SCRIPT_DIR/populate_versions.py"
    python3 "$SCRIPT_DIR/gen_mapping.py"
    log_info "Regenerated keys_versions.py and mapping headers"
else
    log_info "Skipped post-processing (--no-post-process)"
    log_info "Run: python3 populate_versions.py && python3 gen_mapping.py"
fi

log_info "Simulator key list update complete"
log_info "  Dylib: $DYLIB"
log_info "  All simulator hashes: $ALL_HASHES ($ALL_COUNT)"
log_info "  Simulator-only: $SIM_FILE ($SIM_COUNT)"
log_info "  New legacy hashes: $NEW_COUNT"
log_info "  Discovered legacy names: $DISCOVERED_COUNT"
