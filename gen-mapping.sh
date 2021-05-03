#!/bin/bash

sed 's/.*/    \"&\", NULL,/' hashes.txt > temp-mapping.h