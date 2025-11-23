#!/bin/bash

# Show usage/help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS] [INPUT]

Dump Device Tree from IPSW or raw DeviceTree file to devicetree.json.

OPTIONS:
    -d, --device DEVICE     Device identifier (e.g., iPhone15,2)
    -v, --version VERSION   iOS version (e.g., 16.5)
    -b, --build BUILD       Build number (alternative to version)
    -h, --help              Show this help message

ARGUMENTS:
    INPUT                   Path to IPSW file or raw DeviceTree file

EXAMPLES:
    # Extract from local IPSW
    $0 iPhone.ipsw

    # Extract from remote IPSW
    $0 -d iPhone15,2 -v 16.5

    # Extract from specific build
    $0 -d iPhone15,2 -b 20F66

    # Extract from DeviceTree file
    $0 DeviceTree.file

EOF
}

# Check if ipsw is installed
if ! command -v ipsw &> /dev/null; then
    echo "Error: ipsw is not installed"
    echo "Install with: brew install blacktop/tap/ipsw"
    exit 1
fi

# Check for python3 or jq for JSON formatting
if ! command -v jq &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "Error: Neither jq nor python3 is available"
    echo "Install jq with: brew install jq"
    echo "Or ensure python3 is installed"
    exit 1
fi

DEVICE=""
VERSION=""
BUILD=""
INPUT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
        show_help
        exit 0
        ;;
        -d|--device)
        DEVICE="$2"
        shift
        shift
        ;;
        -v|--version)
        VERSION="$2"
        shift
        shift
        ;;
        -b|--build)
        BUILD="$2"
        shift
        shift
        ;;
        *)
        INPUT="$1"
        shift
        ;;
    esac
done

DT_FILE=""

if [[ -n "$DEVICE" ]]; then
    if [[ -z "$VERSION" && -z "$BUILD" ]]; then
        echo "Error: Must specify --version or --build with --device"
        show_help
        exit 1
    fi
    
    # Validate device identifier format (basic check)
    if ! [[ "$DEVICE" =~ ^[A-Za-z]+[0-9]+,[0-9]+ ]]; then
        echo "Warning: Device identifier '$DEVICE' may be invalid"
        echo "Expected format: ModelName##,# (e.g., iPhone15,2)"
    fi
    
    echo "Getting IPSW URL for $DEVICE..."
    if [[ -n "$BUILD" ]]; then
        URL=$(ipsw download ipsw --device "$DEVICE" --build "$BUILD" --urls 2>/dev/null | head -n 1)
    else
        URL=$(ipsw download ipsw --device "$DEVICE" --version "$VERSION" --urls 2>/dev/null | head -n 1)
    fi
    
    if [[ -z "$URL" ]]; then
        echo "Error: Could not find IPSW URL for device $DEVICE"
        [[ -n "$BUILD" ]] && echo "  Build: $BUILD" || echo "  Version: $VERSION"
        exit 1
    fi
    
    echo "Found URL: $URL"
    echo "Extracting DeviceTree from remote IPSW..."
    if ! ipsw extract --remote --dtree "$URL"; then
        echo "Error: Failed to extract DeviceTree from remote IPSW"
        exit 1
    fi
    
    # Find the extracted DeviceTree
    DT_FILE=$(find . -name "DeviceTree*" -type f -not -name "*.json" | head -n 1)
    
elif [[ -n "$INPUT" ]]; then
    if [[ ! -f "$INPUT" ]]; then
        echo "Error: Input file '$INPUT' does not exist"
        exit 1
    fi
    
    if [[ "$INPUT" == *.ipsw ]]; then
        echo "Extracting DeviceTree from $INPUT..."
        if ! ipsw extract --dtree "$INPUT"; then
            echo "Error: Failed to extract DeviceTree from IPSW"
            exit 1
        fi
        DT_FILE=$(find . -name "DeviceTree*" -type f -not -name "*.json" | head -n 1)
    else
        DT_FILE="$INPUT"
    fi
else
    # Try to find a DeviceTree file in current directory
    DT_FILE=$(find . -name "DeviceTree*" -type f -not -name "*.json" | head -n 1)
    if [ -z "$DT_FILE" ]; then
        # Try to find an IPSW file
        IPSW_FILE=$(find . -name "*.ipsw" -type f | head -n 1)
        if [ -n "$IPSW_FILE" ]; then
            echo "Found IPSW: $IPSW_FILE"
            echo "Extracting DeviceTree from $IPSW_FILE..."
            if ! ipsw extract --dtree "$IPSW_FILE"; then
                echo "Error: Failed to extract DeviceTree from IPSW"
                exit 1
            fi
            DT_FILE=$(find . -name "DeviceTree*" -type f -not -name "*.json" | head -n 1)
        fi
    else
        echo "Found DeviceTree: $DT_FILE"
    fi
fi

if [ -z "$DT_FILE" ]; then
    echo "Error: No DeviceTree file found or specified"
    echo ""
    show_help
    exit 1
fi

if [ ! -f "$DT_FILE" ]; then
    echo "Error: DeviceTree file '$DT_FILE' not found"
    exit 1
fi

echo "Processing DeviceTree: $DT_FILE"
echo "Dumping DeviceTree to devicetree.json..."

if command -v jq &> /dev/null; then
    if ! ipsw dtree --json "$DT_FILE" | jq . > devicetree.json; then
        echo "Error: Failed to dump DeviceTree with jq"
        exit 1
    fi
else
    echo "Note: jq not found, using python3 for JSON formatting"
    if ! ipsw dtree --json "$DT_FILE" | python3 -m json.tool > devicetree.json; then
        echo "Error: Failed to dump DeviceTree with python3"
        exit 1
    fi
fi

if [ $? -eq 0 ]; then
    echo "Success! Saved to devicetree.json"
else
    echo "Error: Failed to dump DeviceTree"
    exit 1
fi
