#!/bin/bash

## USAGE: get_run_IDs.sh <analysis_ID>

## DESCRIPTION: This script will read in the run.xls file and output just the sample IDs

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#" # "less_than", "greater_than", "equal"
echo_script_name


run_dir="$1"

echo -e "Analysis directory is:\n$run_dir"

# get first match to run XLS
run_xls="$(find "$run_dir" -type f -path "*variantCaller_out*" -name "*.xls" | head -1)"

outdir="$(dirname $run_xls)"
outfile="${outdir}/sample_barcode_IDs.tsv"

printf "Writing the sample barcode IDs to output file:\n%s\n" "$outfile"
# get the header
cat "$run_xls" | cut -f46-48 | head -1 > "$outfile"
# add the rest of the items
cat "$run_xls" | cut -f46-48 | tail -n +2 | sort -u >> "$outfile"
check_dirfile_exists "$outfile" "f" "Checking to make sure the file was written to..."
# check_num_file_lines "$outfile" 1
