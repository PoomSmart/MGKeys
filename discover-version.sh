#!/usr/bin/env bash

# One-command discovery script for a specific iOS version or build
# Usage: ./discover-version.sh <DEVICE> <VERSION_OR_BUILD> [ARCH] [--remote-extract]
# Example: ./discover-version.sh iPhone15,2 18.6 arm64e
#          ./discover-version.sh iPhone15,2 22G86 --remote-extract  # Using build number
#          ./discover-version.sh iPhone15,2 18.6 --remote-extract

set -e

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-ipsw-extract.sh"

# Parse arguments
parse_common_args "$@"

# Set defaults
DEVICE=${DEVICE:-"iPhone15,2"}
VERSION=${VERSION:-"18.7"}

# Check prerequisites
check_prerequisites || exit 1

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

log_info "Discovery complete!"
