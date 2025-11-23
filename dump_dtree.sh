#!/bin/bash

# Check if ipsw is installed
if ! command -v ipsw &> /dev/null; then
    echo "Error: ipsw is not installed"
    exit 1
fi

INPUT=$1

if [ -z "$INPUT" ]; then
    # Try to find a DeviceTree file in current directory
    DT_FILE=$(find . -name "DeviceTree*" -type f | head -n 1)
    if [ -z "$DT_FILE" ]; then
        # Try to find an IPSW file
        IPSW_FILE=$(find . -name "*.ipsw" -type f | head -n 1)
        if [ -z "$IPSW_FILE" ]; then
            echo "Usage: $0 <IPSW file or DeviceTree file>"
            exit 1
        else
            echo "Found IPSW: $IPSW_FILE"
            INPUT=$IPSW_FILE
        fi
    else
        echo "Found DeviceTree: $DT_FILE"
        INPUT=$DT_FILE
    fi
fi

# If input is an IPSW, extract DeviceTree
if [[ "$INPUT" == *.ipsw ]]; then
    echo "Extracting DeviceTree from $INPUT..."
    ipsw extract --dtree "$INPUT"
    
    # Find the extracted DeviceTree (it might be in a subdirectory)
    DT_FILE=$(find . -name "DeviceTree*" -type f -not -name "*.json" | head -n 1)
    if [ -z "$DT_FILE" ]; then
        echo "Error: Failed to extract DeviceTree"
        exit 1
    fi
else
    DT_FILE=$INPUT
fi

echo "Dumping DeviceTree to devicetree.json..."
ipsw dtree --json "$DT_FILE" > devicetree.json

if [ $? -eq 0 ]; then
    echo "Success! Saved to devicetree.json"
else
    echo "Error: Failed to dump DeviceTree"
    exit 1
fi
