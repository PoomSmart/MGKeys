#!/usr/bin/env bash

if [ -z $1 ]
then
    echo "Must provide the search location"
    return 1
fi

LOCATION=$1

grep "\", NULL" mapping.h | sed -e $'s/[\t",]//g' | sed -e $'s/NULL.*$//g' | while read -r line; do echo "$line"; grep -nris --exclude=\*.{png,jpg,h,plist,strings,car,xpc,ttc,ttf,otf,bin} "$line" $LOCATION; echo ""; done
