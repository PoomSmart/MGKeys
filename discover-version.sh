#!/usr/bin/env bash

# One-command discovery script for a specific iOS version or build
# Usage: ./discover-version.sh <DEVICE> <VERSION> [ARCH] [OPTIONS]
# Example: ./discover-version.sh iPhone15,2 18.6 arm64e
#          ./discover-version.sh iPhone15,2 18.6 --build 22G86 --remote-extract
#          ./discover-version.sh iPhone16,1 27.0 --build 24A5408d --ipsw-url URL
#          ./discover-version.sh iPhone15,2 18.6 --remote-extract
#          ./discover-version.sh iPhone15,2 26.4 --post-process-only

set -e

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-ipsw-extract.sh"

POST_PROCESS_ONLY=false

show_help() {
    cat << EOF
Usage: $0 <DEVICE> <VERSION> [ARCH] [OPTIONS]

Options:
  --remote-extract     Use IPSW remote extraction
  --build BUILD        Explicit IPSW build identifier (including beta suffixes)
  --ipsw-url URL       Use a direct IPSW URL instead of ipsw.me lookup
  --post-process-only  Skip extraction/discovery and only run post-processing

Beta versions are recorded using their final version number (for example,
"27.0 beta 5" is written as version-27.0.txt).

Post-processing includes:
  - Write versions/version-<VERSION>.txt from hashes.txt
  - Update deobfuscated.py from discover-obfuscated-mapped.txt
  - Move mapped hashes missing from hashes.txt into hashes_legacy.txt (sorted)
  - Regenerate mapping headers
  - Run populate_versions.py
EOF
}

filter_args=()
for arg in "$@"; do
    case "$arg" in
        --post-process-only)
            POST_PROCESS_ONLY=true
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            filter_args+=("$arg")
            ;;
    esac
done

# Parse arguments
parse_common_args "${filter_args[@]}"

# Set defaults
DEVICE=${DEVICE:-"iPhone15,2"}
VERSION=${VERSION:-"18.7"}

# Check prerequisites
check_prerequisites || exit 1

if ! command -v python3 &> /dev/null; then
    log_error "python3 not found"
    exit 1
fi

run_post_processing() {
    local version_value

    detect_version_type "$VERSION" "$DEVICE"
    version_value="${VERSION_NUM:-$VERSION}"

    if [[ "$version_value" =~ ^[0-9]+(\.[0-9]+)+$ ]]; then
        mkdir -p versions
        if [[ -s "hashes.txt" ]]; then
            sort -fu hashes.txt > "versions/version-${version_value}.txt"
            log_info "Wrote version snapshot: versions/version-${version_value}.txt"
        else
            log_warn "hashes.txt is missing/empty; skipping versions/version-${version_value}.txt"
        fi
    else
        log_warn "Resolved version '$version_value' is not numeric; skipping version snapshot"
    fi

    if [[ ! -f "discover-obfuscated-mapped.txt" ]]; then
        log_warn "discover-obfuscated-mapped.txt not found; skipping deobfuscated and legacy sync"
    else
        local update_output
        update_output=$(python3 "$SCRIPT_DIR/sync_discovered_keys.py")

        while IFS= read -r line; do
            case "$line" in
                ADDED=*) added_count=${line#ADDED=} ;;
                MOVED=*) moved_count=${line#MOVED=} ;;
                DEOBF_CHANGED=*) deobf_changed=${line#DEOBF_CHANGED=} ;;
                LEGACY_CHANGED=*) legacy_changed=${line#LEGACY_CHANGED=} ;;
                ERROR*) log_error "$line" ; exit 1 ;;
            esac
        done <<< "$update_output"

        log_info "Auto-updated deobfuscated keys: ${added_count:-0} added"
        log_info "Moved hashes missing from hashes.txt to hashes_legacy.txt: ${moved_count:-0}"
        if [[ "${legacy_changed:-0}" == "1" ]]; then
            log_info "Sorted hashes_legacy.txt"
        fi
    fi

    local should_regen_mapping=false
    if [[ "${deobf_changed:-0}" == "1" || "${legacy_changed:-0}" == "1" ]]; then
        should_regen_mapping=true
    fi

    if [[ -d "versions" ]]; then
        python3 populate_versions.py
        log_info "Updated keys_versions.py and versions/version-stats.txt"
        should_regen_mapping=true
    else
        log_warn "versions directory not found; skipping populate_versions.py"
    fi

    if [[ "$should_regen_mapping" == true ]]; then
        python3 gen_mapping.py
        log_info "Regenerated mapping headers"
    else
        log_info "No mapping source changes detected; skipped gen_mapping.py"
    fi
}

if [[ "$POST_PROCESS_ONLY" == false ]]; then
    log_info "Discovering Mobile Gestalt keys for $VERSION on $DEVICE ($ARCH)"
    if [[ "$REMOTE_EXTRACT" == true ]]; then
        log_info "Remote extraction mode enabled (--remote-extract flag)"
    fi
    echo ""

    # Extract dylib
    if ! extract_dylib "$DEVICE" "$VERSION" "$ARCH" "$REMOTE_EXTRACT"; then
        log_error "Failed to extract dylib"
        exit 1
    fi

    # DYLIB_PATH is now set by extract_dylib
    # Copy to standard location for discovery scripts
    cp "$DYLIB_PATH" libMobileGestalt.dylib 2>/dev/null || true
    log_info "Using dylib: libMobileGestalt.dylib"

    # Run discovery
    log_info "Running key discovery..."
    if [[ -f "discover.sh" ]]; then
        bash discover.sh || true
    fi

    if [[ -f "deobfuscate.sh" ]]; then
        bash deobfuscate.sh "$ARCH"
    fi
else
    log_info "Post-process-only mode enabled; skipping extraction and discovery"
fi

run_post_processing

log_info "Discovery complete!"
