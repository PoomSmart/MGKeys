#!/usr/bin/env bash

# One-command discovery script for a specific iOS version or build
# Usage: ./discover-version.sh <DEVICE> <VERSION_OR_BUILD> [ARCH] [--remote-extract]
# Example: ./discover-version.sh iPhone15,2 18.6 arm64e
#          ./discover-version.sh iPhone15,2 22G86 --remote-extract  # Using build number
#          ./discover-version.sh iPhone15,2 18.6 --remote-extract

set -e

# Parse arguments
DEVICE=""
VERSION=""
ARCH="arm64e"
REMOTE_EXTRACT=false

for arg in "$@"; do
    if [[ "$arg" == "--remote-extract" ]]; then
        REMOTE_EXTRACT=true
    elif [[ -z "$DEVICE" ]]; then
        DEVICE="$arg"
    elif [[ -z "$VERSION" ]]; then
        VERSION="$arg"
    else
        ARCH="$arg"
    fi
done

# Set defaults
DEVICE=${DEVICE:-"iPhone15,2"}
VERSION=${VERSION:-"18.7"}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
if ! command -v ipsw &> /dev/null; then
    log_error "ipsw tool not installed. Install with: brew install blacktop/tap/ipsw"
    exit 1
fi

log_info "Discovering Mobile Gestalt keys for $VERSION on $DEVICE ($ARCH)"
if [[ "$REMOTE_EXTRACT" == true ]]; then
    log_info "Remote extraction mode enabled (--remote-extract flag)"
fi
echo ""

# Determine if VERSION is a build number (e.g., 22G86) or version (e.g., 18.6)
BUILD=""
if [[ "$VERSION" =~ ^[0-9]+[A-Z][0-9]+$ ]]; then
    log_info "Detected build number: $VERSION"
    BUILD="$VERSION"
    VERSION=""  # Clear version to use build instead
else
    log_info "Detected version number: $VERSION"
fi

# Use full OTA download by default (better speed), unless --remote-extract is specified
if [[ "$REMOTE_EXTRACT" == true ]]; then
    log_info "Attempting IPSW remote extraction..."

    # Use appropriate flag for version or build
    if [[ -n "$BUILD" ]]; then
        IPSW_CMD="ipsw download ipsw --device \"$DEVICE\" --build \"$BUILD\" --dyld --dyld-arch \"$ARCH\" --confirm"
    else
        IPSW_CMD="ipsw download ipsw --device \"$DEVICE\" --version \"$VERSION\" --dyld --dyld-arch \"$ARCH\" --confirm"
    fi

    if eval "$IPSW_CMD" 2>/dev/null; then
        log_info "Successfully extracted dyld_shared_cache from IPSW"

        # Find the extracted dylib
        DYLIB=$(find . -name "libMobileGestalt*.dylib" -type f | head -1)

        if [[ -n "$DYLIB" ]]; then
            # Copy to standard location (ignore error if files are identical)
            cp "$DYLIB" libMobileGestalt.dylib 2>/dev/null || true
            log_info "Using dylib: libMobileGestalt.dylib"

            # Run discovery
            log_info "Running key discovery..."
            bash discover.sh
            bash deobfuscate.sh "$ARCH"

            log_info "Discovery complete!"
            exit 0
        fi
    fi
fi

log_info "IPSW remote extraction failed or not available"
echo ""
log_info "Falling back to full IPSW download method..."
echo ""

# Full IPSW download (default method - better download speeds than OTA)
log_info "Using full IPSW download method (~7-8GB)..."

# Use appropriate flag for version or build
if [[ -n "$BUILD" ]]; then
    log_info "Downloading IPSW for build $BUILD..."
    ipsw download ipsw --device "$DEVICE" --build "$BUILD" --confirm
    IPSW_FILE=$(find . -maxdepth 1 -name "*.ipsw" -type f | head -1)
else
    log_info "Downloading IPSW for version $VERSION..."
    ipsw download ipsw --device "$DEVICE" --version "$VERSION" --confirm
    IPSW_FILE=$(find . -maxdepth 1 -name "*.ipsw" -type f | head -1)
fi

if [[ -z "$IPSW_FILE" ]]; then
    log_error "IPSW download failed or file not found"
    exit 1
fi

log_info "IPSW downloaded: $IPSW_FILE"
log_info "Extracting dyld_shared_cache from IPSW..."

# Extract dyld_shared_cache locally
CACHE_DIR="dyld_shared_cache"
mkdir -p "$CACHE_DIR"

ipsw extract --dyld "$IPSW_FILE" --output "$CACHE_DIR" || {
    log_error "Failed to extract dyld_shared_cache from IPSW"
    exit 1
}

log_info "Successfully extracted dyld_shared_cache"

# Find and extract libMobileGestalt.dylib
CACHE_FILE=$(find "$CACHE_DIR" -name "dyld_shared_cache_${ARCH}" -type f | head -n 1)

if [[ -z "$CACHE_FILE" ]]; then
    log_error "Could not find dyld_shared_cache_${ARCH}"
    log_info "Available cache files:"
    find "$CACHE_DIR" -name "dyld_shared_cache*" -type f | head -5
    exit 1
fi

log_info "Extracting libMobileGestalt.dylib from cache..."
DYLIB_DIR="extracted_dylibs"
mkdir -p "$DYLIB_DIR"

if ipsw dyld extract "$CACHE_FILE" libMobileGestalt.dylib --output "$DYLIB_DIR" 2>/dev/null; then
    log_info "Extracted using 'libMobileGestalt.dylib' pattern"
else
    log_error "Failed to extract libMobileGestalt.dylib"
    exit 1
fi

# Find the extracted dylib
DYLIB=$(find "$DYLIB_DIR" -name "*libMobileGestalt*.dylib" -type f | head -1)

if [[ -z "$DYLIB" ]]; then
    log_error "Could not find extracted libMobileGestalt.dylib"
    exit 1
fi

# Copy to working directory
cp "$DYLIB" libMobileGestalt.dylib 2>/dev/null || true
log_info "Using dylib: libMobileGestalt.dylib"

# Clean up downloaded IPSW to save space
# rm -f "$IPSW_FILE"
# log_info "Cleaned up IPSW file"

# Run discovery
log_info "Running key discovery..."
if [[ -f "discover.sh" ]]; then
    bash discover.sh
fi

if [[ -f "deobfuscate.sh" ]]; then
    bash deobfuscate.sh "$ARCH"
fi

log_info "Discovery complete!"
