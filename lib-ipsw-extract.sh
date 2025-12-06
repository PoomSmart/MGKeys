#!/usr/bin/env bash

# Shared library for IPSW extraction functionality
# Used by discover-version.sh and extract-version-hashes.sh

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if ipsw tool is installed
check_prerequisites() {
    if ! command -v ipsw &> /dev/null; then
        log_error "ipsw tool not installed. Install with: brew install blacktop/tap/ipsw"
        return 1
    fi
    return 0
}

# Parse common arguments
# Sets: DEVICE, VERSION, ARCH, REMOTE_EXTRACT
parse_common_args() {
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
}

# Determine if VERSION is a build number or version number
# Sets: BUILD, VERSION_NUM
detect_version_type() {
    local version="$1"
    local device="$2"

    BUILD=""
    VERSION_NUM=""

    if [[ "$version" =~ ^[0-9]+[A-Z][0-9]+$ ]]; then
        log_info "Detected build number: $version"
        BUILD="$version"

        # Try to get version from build using ipsw
        VERSION_INFO=$(ipsw download ipsw --device "$device" --build "$BUILD" --info 2>/dev/null || echo "")
        if [[ -n "$VERSION_INFO" ]]; then
            VERSION_NUM=$(echo "$VERSION_INFO" | grep -oE 'Version: [0-9.]+' | cut -d' ' -f2 || echo "")
        fi
    else
        log_info "Detected version number: $version"
        VERSION_NUM="$version"
    fi
}

# Extract libMobileGestalt.dylib using remote extraction
# Parameters: $1=DEVICE, $2=VERSION/BUILD, $3=ARCH, $4=CACHE_BASE_DIR
# Returns: Sets DYLIB_PATH and EXTRACTED_BUILD on success, returns 0
#          Returns 1 on failure
remote_extract_dylib() {
    local device="$1"
    local version="$2"
    local arch="$3"
    local cache_base_dir="${4:-dyld_shared_cache}"

    log_info "Attempting IPSW remote extraction..."
    mkdir -p "$cache_base_dir"

    detect_version_type "$version" "$device"

    # Use appropriate flag for version or build
    local ipsw_cmd
    if [[ -n "$BUILD" ]]; then
        ipsw_cmd="ipsw download ipsw --device \"$device\" --build \"$BUILD\" --dyld --dyld-arch \"$arch\" --output \"$cache_base_dir\" --confirm"
    else
        ipsw_cmd="ipsw download ipsw --device \"$device\" --version \"$VERSION_NUM\" --dyld --dyld-arch \"$arch\" --output \"$cache_base_dir\" --confirm"
    fi

    if ! eval "$ipsw_cmd" 2>&1; then
        log_error "IPSW remote extraction command failed"
        return 1
    fi

    log_info "Successfully extracted dyld_shared_cache from IPSW"

    # Find the extracted cache directory (format: BUILD__DEVICE)
    local cache_dir=$(find "$cache_base_dir" -maxdepth 1 -type d -name "*__${device}" | sort -r | head -1)

    if [[ -z "$cache_dir" ]]; then
        log_error "Could not find cache directory for $device"
        return 1
    fi

    log_info "Found cache directory: $cache_dir"

    # Extract build number from directory name
    EXTRACTED_BUILD=$(basename "$cache_dir" | cut -d'_' -f1)

    # Find the cache file
    local cache_file=$(find "$cache_dir" -name "dyld_shared_cache_${arch}" -type f | head -1)

    if [[ -z "$cache_file" ]]; then
        log_error "Could not find dyld_shared_cache_${arch} in $cache_dir"
        return 1
    fi

    log_info "Extracting libMobileGestalt.dylib from cache..."

    if ! ipsw dyld extract "$cache_file" libMobileGestalt.dylib --output "$cache_dir" 2>/dev/null; then
        log_error "Failed to extract libMobileGestalt.dylib from cache"
        return 1
    fi

    DYLIB_PATH=$(find "$cache_dir" -name "*libMobileGestalt*.dylib" -type f | head -1)

    if [[ -z "$DYLIB_PATH" ]]; then
        log_error "Could not find extracted libMobileGestalt.dylib"
        return 1
    fi

    log_info "Successfully extracted: $DYLIB_PATH"
    return 0
}

# Extract libMobileGestalt.dylib using full IPSW download
# Parameters: $1=DEVICE, $2=VERSION/BUILD, $3=ARCH, $4=CACHE_BASE_DIR
# Returns: Sets DYLIB_PATH and EXTRACTED_BUILD on success, returns 0
#          Returns 1 on failure
full_ipsw_extract_dylib() {
    local device="$1"
    local version="$2"
    local arch="$3"
    local cache_base_dir="${4:-dyld_shared_cache}"

    log_info "Using full IPSW download method (~7-8GB)..."

    detect_version_type "$version" "$device"

    # Use appropriate flag for version or build
    local ipsw_file
    if [[ -n "$BUILD" ]]; then
        log_info "Downloading IPSW for build $BUILD..."
        ipsw download ipsw --device "$device" --build "$BUILD" --confirm
        # Try multiple patterns to find the downloaded IPSW
        ipsw_file=$(find . -maxdepth 1 -name "*_${BUILD}_*.ipsw" -type f | head -1)
        EXTRACTED_BUILD="$BUILD"
    else
        log_info "Downloading IPSW for version $VERSION_NUM..."
        ipsw download ipsw --device "$device" --version "$VERSION_NUM" --confirm
        # Try multiple patterns: device_version, or just version in filename
        ipsw_file=$(find . -maxdepth 1 -name "*_${VERSION_NUM}_*.ipsw" -o -name "*${VERSION_NUM//./_}*.ipsw" -type f | head -1)
        # If still not found, try any recent IPSW
        if [[ -z "$ipsw_file" ]]; then
            ipsw_file=$(find . -maxdepth 1 -name "*.ipsw" -type f -newer . 2>/dev/null | head -1)
        fi
        # Extract build from filename if possible
        if [[ "$ipsw_file" =~ _([0-9]+[A-Z][0-9]+)_ ]]; then
            EXTRACTED_BUILD="${BASH_REMATCH[1]}"
        fi
    fi

    if [[ -z "$ipsw_file" ]]; then
        log_error "IPSW download failed or file not found"
        return 1
    fi

    log_info "IPSW downloaded: $ipsw_file"
    log_info "Extracting dyld_shared_cache from IPSW..."

    # Create cache directory with build info
    local cache_dir
    if [[ -n "$EXTRACTED_BUILD" ]]; then
        cache_dir="$cache_base_dir/${EXTRACTED_BUILD}__${device}"
    else
        cache_dir="$cache_base_dir/${device}"
    fi
    mkdir -p "$cache_dir"

    if ! ipsw extract --dyld "$ipsw_file" --output "$cache_dir"; then
        log_error "Failed to extract dyld_shared_cache from IPSW"
        return 1
    fi

    log_info "Successfully extracted dyld_shared_cache"

    # Find and extract libMobileGestalt.dylib
    local cache_file=$(find "$cache_dir" -name "dyld_shared_cache_${arch}" -type f | head -n 1)

    if [[ -z "$cache_file" ]]; then
        log_error "Could not find dyld_shared_cache_${arch}"
        log_info "Available cache files:"
        find "$cache_dir" -name "dyld_shared_cache*" -type f | head -5
        return 1
    fi

    log_info "Extracting libMobileGestalt.dylib from cache..."

    if ! ipsw dyld extract "$cache_file" libMobileGestalt.dylib --output "$cache_dir" 2>/dev/null; then
        log_error "Failed to extract libMobileGestalt.dylib"
        return 1
    fi

    DYLIB_PATH=$(find "$cache_dir" -name "*libMobileGestalt*.dylib" -type f | head -1)

    if [[ -z "$DYLIB_PATH" ]]; then
        log_error "Could not find extracted libMobileGestalt.dylib"
        return 1
    fi

    log_info "Successfully extracted: $DYLIB_PATH"

    # Clean up downloaded IPSW to save space
    log_info "Cleaning up IPSW file to save space..."
    rm -f "$ipsw_file"

    return 0
}

# Extract libMobileGestalt.dylib (tries remote first if requested, falls back to full download)
# Parameters: $1=DEVICE, $2=VERSION/BUILD, $3=ARCH, $4=USE_REMOTE
# Returns: Sets DYLIB_PATH and EXTRACTED_BUILD on success, returns 0
#          Returns 1 on failure
extract_dylib() {
    local device="$1"
    local version="$2"
    local arch="$3"
    local use_remote="${4:-false}"
    local cache_base_dir="dyld_shared_cache"

    if [[ "$use_remote" == "true" ]]; then
        if remote_extract_dylib "$device" "$version" "$arch" "$cache_base_dir"; then
            return 0
        fi
        log_warn "Remote extraction failed, falling back to full IPSW download..."
    fi

    full_ipsw_extract_dylib "$device" "$version" "$arch" "$cache_base_dir"
    return $?
}

# Extract hashes from a dylib file
# Parameters: $1=DYLIB_PATH, $2=ARCH, $3=OUTPUT_FILE
# Returns: 0 on success, 1 on failure
extract_hashes_from_dylib() {
    local dylib_path="$1"
    local arch="$2"
    local output_file="$3"

    log_info "Extracting hashes from dylib..."
    local temp_hashes="temp-hashes-$$.txt"
    local filtered_hashes="filtered-hashes-$$.txt"

    # Use strings to extract hashes
    if strings -arch "$arch" -n 22 "$dylib_path" 2>/dev/null | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > "$temp_hashes" 2>/dev/null && [ -s "$temp_hashes" ]; then
        log_info "Extracted hashes using arch-specific strings ($arch)"
    else
        log_warn "Arch-specific strings failed, using plain strings"
        /usr/bin/strings - < "$dylib_path" 2>/dev/null | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > "$temp_hashes"
    fi

    if [ ! -s "$temp_hashes" ]; then
        log_error "Failed to extract any hashes from $dylib_path"
        rm -f "$temp_hashes"
        return 1
    fi

    log_info "Extracted $(wc -l < "$temp_hashes" | tr -d ' ') potential hashes"

    # Filter false positives and sort
    if [ -f false-positives.txt ]; then
        grep -v -f false-positives.txt "$temp_hashes" | sort -f > "$filtered_hashes"
        log_info "Filtered false positives"
    else
        log_warn "false-positives.txt not found; skipping filter"
        sort -f "$temp_hashes" > "$filtered_hashes"
    fi

    # Copy to output file
    cp "$filtered_hashes" "$output_file"
    rm -f "$temp_hashes" "$filtered_hashes"

    local hash_count=$(wc -l < "$output_file" | tr -d ' ')
    log_info "Wrote $hash_count hashes to $output_file"

    return 0
}
