#!/bin/bash

## USAGE: convert_utf16_to_utf8.sh input.txt output.txt

## DESCRIPTION: This script will convert a UTF-16 formatted file to UTF-8



#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 2 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

input="$1"
output="$2"

iconv -f UTF-16 -t UTF-8 "$input" -o "$output"