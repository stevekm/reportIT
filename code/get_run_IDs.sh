#!/bin/bash

## USAGE: get_run_IDs.sh /path/to/run.xls

## DESCRIPTION: This script will read in the run.xls file and output just the sample IDs

#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 1 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

echo -e "Now running script:\n${0}"

run_dir="$1"

echo -e "Analysis directory is:\n$run_dir"

# get first match to run XLS
run_xls="$(find "$run_dir" -type f -path "*variantCaller_out*" -name "*.xls" | head -1)"

outdir="$(dirname $run_xls)"
outfile="${outdir}/sample_barcode_IDs.tsv"

cat "$run_xls" | cut -f46-48 | uniq > "$outfile" && echo -e "Output saved to:\n$outfile"



# run_xls="$1"
# outdir="$(dirname $run_xls)"
# outfile="${outdir}/sample_barcode_IDs.tsv"

# cat "$run_xls" | cut -f46-48 | uniq > "$outfile" && echo -e "Output saved to:\n$outfile"
