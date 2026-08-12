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
# Sets: DEVICE, VERSION, ARCH, BUILD, IPSW_URL, REMOTE_EXTRACT
parse_common_args() {
    DEVICE=""
    VERSION=""
    ARCH="arm64e"
    BUILD=""
    IPSW_URL=""
    REMOTE_EXTRACT=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --remote-extract)
                REMOTE_EXTRACT=true
                ;;
            --build)
                BUILD="$2"
                shift
                ;;
            --ipsw-url)
                IPSW_URL="$2"
                shift
                ;;
            --arch)
                ARCH="$2"
                shift
                ;;
            *)
                if [[ -z "$DEVICE" ]]; then
                    DEVICE="$1"
                elif [[ -z "$VERSION" ]]; then
                    VERSION="$1"
                else
                    ARCH="$1"
                fi
                ;;
        esac
        shift
    done
}

# Determine if VERSION is a build number or version number
# Sets: BUILD, VERSION_NUM
detect_version_type() {
    local version="$1"
    local device="$2"

    VERSION_NUM=""

    if [[ "$version" =~ ^[0-9]+[A-Z][0-9]+[A-Za-z]*$ ]]; then
        log_info "Detected build number: ${BUILD:-$version}"
        BUILD="${BUILD:-$version}"
    elif [[ "$version" =~ ^[0-9]+(\.[0-9]+)+([[:space:]]+[Bb]eta([[:space:]]+[0-9]+)?)?$ ]]; then
        VERSION_NUM="${version%%[[:space:]]*}"
        log_info "Detected iOS version: $VERSION_NUM"
    else
        log_error "Unrecognized version or build identifier: $version"
        return 1
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

    detect_version_type "$version" "$device" || return 1

    if [[ -n "$IPSW_URL" ]]; then
        if ! ipsw extract --dyld --dyld-arch "$arch" --remote \
            --output "$cache_base_dir" "$IPSW_URL"; then
            log_error "IPSW remote extraction command failed"
            return 1
        fi
    else
        local ipsw_args=(download ipsw --device "$device" --dyld
            --dyld-arch "$arch" --output "$cache_base_dir" --confirm)
        if [[ -n "$BUILD" ]]; then
            ipsw_args+=(--build "$BUILD")
        else
            ipsw_args+=(--version "$VERSION_NUM")
        fi
        if ! ipsw "${ipsw_args[@]}"; then
            log_error "IPSW remote extraction command failed"
            return 1
        fi
    fi

    log_info "Successfully extracted dyld_shared_cache from IPSW"

    # Find the extracted cache directory (format: BUILD__DEVICE).
    local cache_dir
    cache_dir=$(find "$cache_base_dir" -maxdepth 3 -type d \
        -name "*__${device}" | sort -r | head -1)

    if [[ -z "$cache_dir" ]]; then
        log_error "Could not find cache directory for $device"
        return 1
    fi

    log_info "Found cache directory: $cache_dir"

    # Extract build number from directory name.
    EXTRACTED_BUILD=$(basename "$cache_dir" | cut -d'_' -f1)

    # Find the cache file.
    local cache_file
    cache_file=$(find "$cache_dir" -name "dyld_shared_cache_${arch}" -type f | head -1)

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

# Download and extract libMobileGestalt.dylib from a complete IPSW.
# Parameters: $1=DEVICE, $2=VERSION/BUILD, $3=ARCH, $4=CACHE_BASE_DIR
# Returns: Sets DYLIB_PATH and EXTRACTED_BUILD on success, returns 0
#          Returns 1 on failure
full_ipsw_extract_dylib() {
    local device="$1"
    local version="$2"
    local arch="$3"
    local cache_base_dir="${4:-dyld_shared_cache}"

    log_info "Using full IPSW download method (~11GB for this beta)..."

    detect_version_type "$version" "$device" || return 1

    local ipsw_file
    if [[ -n "$IPSW_URL" ]]; then
        ipsw_file="${IPSW_URL##*/}"
        ipsw_file="${ipsw_file%%\?*}"
        log_info "Downloading IPSW from supplied URL..."
        if ! curl -fL --retry 3 --output "$ipsw_file" "$IPSW_URL"; then
            log_error "IPSW download failed"
            return 1
        fi
    else
        local download_args=(download ipsw --device "$device" --confirm)
        if [[ -n "$BUILD" ]]; then
            log_info "Downloading IPSW for build $BUILD..."
            download_args+=(--build "$BUILD")
        else
            log_info "Downloading IPSW for version $VERSION_NUM..."
            download_args+=(--version "$VERSION_NUM")
        fi
        if ! ipsw "${download_args[@]}"; then
            log_error "IPSW download failed"
            return 1
        fi
        if [[ -n "$BUILD" ]]; then
            ipsw_file=$(find . -maxdepth 1 -name "*_${BUILD}_*.ipsw" -type f | head -1)
            EXTRACTED_BUILD="$BUILD"
        else
            ipsw_file=$(find . -maxdepth 1 \( -name "*_${VERSION_NUM}_*.ipsw" \
                -o -name "*${VERSION_NUM//./_}*.ipsw" \) -type f | head -1)
        fi
    fi

    if [[ -z "$ipsw_file" || ! -f "$ipsw_file" ]]; then
        log_error "IPSW download failed or file not found"
        return 1
    fi

    if [[ -z "$EXTRACTED_BUILD" && "$ipsw_file" =~ _([0-9]+[A-Z][0-9]+[A-Za-z]*)_ ]]; then
        EXTRACTED_BUILD="${BASH_REMATCH[1]}"
    fi

    log_info "IPSW downloaded: $ipsw_file"
    log_info "Extracting dyld_shared_cache from IPSW..."

    local cache_dir
    cache_dir="$cache_base_dir/${EXTRACTED_BUILD:-$device}"
    mkdir -p "$cache_dir"

    if ! ipsw extract --dyld "$ipsw_file" --output "$cache_dir"; then
        log_error "Failed to extract dyld_shared_cache from IPSW"
        return 1
    fi

    log_info "Successfully extracted dyld_shared_cache"

    local cache_file
    cache_file=$(find "$cache_dir" -name "dyld_shared_cache_${arch}" -type f | head -n 1)
    if [[ -z "$cache_file" ]]; then
        log_error "Could not find dyld_shared_cache_${arch}"
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
    if [[ -z "$IPSW_URL" ]]; then
        log_info "Cleaning up downloaded IPSW file to save space..."
        rm -f "$ipsw_file"
    fi
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

    # Try llvm-nm first (most robust), fallback to nm, then strings
    if command -v llvm-nm &> /dev/null && llvm-nm -g --defined-only "$dylib_path" 2>/dev/null | awk '{print $3}' | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > "$temp_hashes" 2>/dev/null && [ -s "$temp_hashes" ]; then
        log_info "Extracted hashes using llvm-nm"
    elif nm -g --defined-only "$dylib_path" 2>/dev/null | awk '{print $3}' | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > "$temp_hashes" 2>/dev/null && [ -s "$temp_hashes" ]; then
        log_info "Extracted hashes using nm"
    elif strings -arch "$arch" -n 22 "$dylib_path" 2>/dev/null | grep -i '^[a-zA-Z0-9\+\/]\{22\}$' > "$temp_hashes" 2>/dev/null && [ -s "$temp_hashes" ]; then
        log_info "Extracted hashes using arch-specific strings ($arch)"
    else
        log_warn "nm tools and arch-specific strings failed, using plain strings"
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
