#!/bin/bash

## USAGE: run_samplesheet.sh

## DESCRIPTION: This script will run the reportIT pipeline on all analyses in the samplesheet

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

samplesheet_file="samplesheet.tsv"

while read line; do
    if [ ! -z "$line" ]; then # skip blank lines
        analysis_1="$(echo "$line" | cut -f1)"
        analysis_2="$(echo "$line" | cut -f2)"
        echo "${analysis_1}, ${analysis_2}"
        (
        [ ! -z "$analysis_1" ] && [ ! -z "$analysis_2" ] && echo "There are two" && exit
        [ ! -z "$analysis_1" ] || [ ! -z "$analysis_2" ] && echo "There is one" && exit
        )
    fi
done < "$samplesheet_file"
