#!/bin/bash
# set -x

## USAGE: .... analysis_ID

## Description: This script will set up the reports directories in an analysis dir


#~~~~~ CUSTOM FUNCTIONS ~~~~~~# 
source "$(dirname $0)/custom_bash_functions.sh"

#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 1 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi
