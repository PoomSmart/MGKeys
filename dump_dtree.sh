#!/bin/bash

# Check if ipsw is installed
if ! command -v ipsw &> /dev/null; then
    echo "Error: ipsw is not installed"
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
        exit 1
    fi
    
    echo "Getting IPSW URL for $DEVICE..."
    if [[ -n "$BUILD" ]]; then
        URL=$(ipsw download ipsw --device "$DEVICE" --build "$BUILD" --urls 2>/dev/null | head -n 1)
    else
        URL=$(ipsw download ipsw --device "$DEVICE" --version "$VERSION" --urls 2>/dev/null | head -n 1)
    fi
    
    if [[ -z "$URL" ]]; then
        echo "Error: Could not find IPSW URL"
        exit 1
    fi
    
    echo "Found URL: $URL"
    echo "Extracting DeviceTree from remote IPSW..."
    ipsw extract --remote --dtree "$URL"
    
    # Find the extracted DeviceTree
    DT_FILE=$(find . -name "DeviceTree*" -type f -not -name "*.json" | head -n 1)
    
elif [[ -n "$INPUT" ]]; then
    if [[ "$INPUT" == *.ipsw ]]; then
        echo "Extracting DeviceTree from $INPUT..."
        ipsw extract --dtree "$INPUT"
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
            ipsw extract --dtree "$IPSW_FILE"
            DT_FILE=$(find . -name "DeviceTree*" -type f -not -name "*.json" | head -n 1)
        fi
    else
        echo "Found DeviceTree: $DT_FILE"
    fi
fi

if [ -z "$DT_FILE" ]; then
    echo "Usage: $0 [IPSW file or DeviceTree file]"
    echo "       $0 -d <DEVICE> -v <VERSION> [-b <BUILD>]"
    exit 1
fi

echo "Processing DeviceTree: $DT_FILE"
echo "Dumping DeviceTree to devicetree.json..."
if command -v jq &> /dev/null; then
    ipsw dtree --json "$DT_FILE" | jq . > devicetree.json
else
    ipsw dtree --json "$DT_FILE" | python3 -m json.tool > devicetree.json
fi

if [ $? -eq 0 ]; then
    echo "Success! Saved to devicetree.json"
else
    echo "Error: Failed to dump DeviceTree"
    exit 1
fi
