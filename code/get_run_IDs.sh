#!/bin/bash

## USAGE: get_run_IDs.sh /path/to/run.xls

## DESCRIPTION: This script will read in the run.xls file and output just the sample IDs

run_xls="$1"

outdir="$(dirname $run_xls)"
outfile="${outdir}/sample_barcode_IDs.tsv"

cat "$run_xls" | cut -f46-48 | uniq > "$outfile" && echo -e "Output saved to:\n$outfile"