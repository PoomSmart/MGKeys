#!/bin/bash

if [ -z $1 ]
then
    echo "must provide search location"
    return 1
fi

LOCATION=$1

grep "\", NULL" mapping.h | sed -e $'s/[\t",]//g' | sed -e $'s/NULL.*$//g' | while read -r line; do echo "$line"; grep -nri "$line" $LOCATION; echo ""; done