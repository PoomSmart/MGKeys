#!/usr/bin/env bash

# Extract libMobileGestalt.dylib for a specific iOS version and generate version hashes
# This script ONLY extracts the dylib and creates version-XX.txt without running discovery or updating mappings
# Usage: ./extract-version-hashes.sh <DEVICE> <VERSION_OR_BUILD> [ARCH] [--remote-extract]
# Example: ./extract-version-hashes.sh iPhone15,2 18.0
#          ./extract-version-hashes.sh iPhone15,2 22A3354 --remote-extract  # Using build number
#          ./extract-version-hashes.sh iPhone15,2 18.0 arm64e --remote-extract

set -e

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-ipsw-extract.sh"

# Parse arguments
DEVICE=""
VERSION=""
ARCH="arm64e"
REMOTE_EXTRACT=false

show_help() {
    cat << EOF
Extract libMobileGestalt.dylib and generate version-specific hashes file

Usage: $0 <DEVICE> <VERSION_OR_BUILD> [ARCH] [--remote-extract]

Arguments:
    DEVICE              Device identifier (e.g., iPhone15,2)
    VERSION_OR_BUILD    iOS version (e.g., 18.0) or build number (e.g., 22A3354)
    ARCH               Architecture (default: arm64e)
    --remote-extract   Use remote extraction instead of full IPSW download

Examples:
    $0 iPhone15,2 18.0
    $0 iPhone15,2 22A3354 --remote-extract
    $0 iPhone15,2 18.0 arm64e
    $0 iPhone13,1 17.4 arm64e --remote-extract

Output:
    - Extracts libMobileGestalt.dylib to dyld_shared_cache/<BUILD>__<DEVICE>/
    - Generates versions/version-<VERSION>.txt with extracted hashes
    - Does NOT run discovery or update mapping files

EOF
    exit 0
}

# Parse arguments
for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        show_help
    fi
done

parse_common_args "$@"

# Validate required arguments
if [[ -z "$DEVICE" || -z "$VERSION" ]]; then
    echo "Error: DEVICE and VERSION_OR_BUILD are required"
    echo "Run with --help for usage information"
    exit 1
fi

# Check prerequisites
check_prerequisites || exit 1

log_info "Extracting version hashes for $VERSION on $DEVICE ($ARCH)"
if [[ "$REMOTE_EXTRACT" == true ]]; then
    log_info "Remote extraction mode enabled"
fi
echo ""

# Extract dylib
if ! extract_dylib "$DEVICE" "$VERSION" "$ARCH" "$REMOTE_EXTRACT"; then
    log_error "Failed to extract dylib"
    exit 1
fi

# DYLIB_PATH and EXTRACTED_BUILD are now set by extract_dylib
detect_version_type "$VERSION" "$DEVICE"

# Determine output filename
mkdir -p versions
if [[ -n "$VERSION_NUM" ]]; then
    OUTPUT_FILE="versions/version-${VERSION_NUM}.txt"
elif [[ -n "$EXTRACTED_BUILD" ]]; then
    OUTPUT_FILE="versions/version-${EXTRACTED_BUILD}.txt"
else
    OUTPUT_FILE="versions/version-${VERSION}.txt"
fi

# Extract hashes from the dylib
if ! extract_hashes_from_dylib "$DYLIB_PATH" "$ARCH" "$OUTPUT_FILE"; then
    log_error "Failed to extract hashes"
    exit 1
fi

HASH_COUNT=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')

echo ""
log_info "✓ Extraction complete!"
echo ""
log_info "Summary:"
log_info "  Device: $DEVICE"
log_info "  Version: ${VERSION_NUM:-$VERSION}"
if [[ -n "$EXTRACTED_BUILD" ]]; then
    log_info "  Build: $EXTRACTED_BUILD"
fi
log_info "  Architecture: $ARCH"
log_info "  Dylib: $DYLIB_PATH"
log_info "  Hashes: $OUTPUT_FILE ($HASH_COUNT keys)"
echo ""
log_info "Next steps:"
log_info "  - Review $OUTPUT_FILE"
log_info "  - Run populate_versions.py to update key version mappings"
log_info "  - No discovery or mapping updates were performed"