#!/bin/bash

## USAGE: IGV_snapshot_parser.sh <analysis ID> <analysis ID> <analysis ID> ...  

## DESCRIPTION: This script will generate and run IGV snapshot batchscripts
## for all supplied analyses. First, the script will search for a 
## 'combined analysis' and 
## This script operates on all supplied analyses


#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 1 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

analysis_ID="${@:1}" # accept a space separated list of ID's
outdir="output"

