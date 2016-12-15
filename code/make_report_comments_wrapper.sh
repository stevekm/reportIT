#!/bin/bash
# set -x

## USAGE: make_report_comments_wrapper.sh analysis_ID

## Description: This script will find parse an annotated analysis dir, 


#~~~~~ CUSTOM FUNCTIONS ~~~~~~# 
source "$(dirname $0)/custom_bash_functions.sh"


#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 1 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

echo -e "Now running script:\n${0}"

# ~~~~~~ script args ~~~~~~ #
analysis_ID="$1"
# analysis_ID="${@:1}" # accept a space separated list of ID's
outdir="output"

analysis_outdir="${outdir}/${analysis_ID}"
# make sure the dir
check_dirfile_exists "$analysis_outdir" "d"

report_comments_script="$(dirname $0)/make_report_comments.py"



#~~~~~ FIND ANALYIS SAMPLES ~~~~~~# 
# find all samples in the analysis dir

echo -e "\n-----------------------------------\n"
echo -e "Finding samples in analysis dir..."
analysis_samples="$(find "$analysis_outdir" -type d -path "*variantCaller_out*" -name "*IonXpress_*")"
error_on_zerolength "$analysis_samples" "TRUE" "Checking to make sure samples were found..."

for i in $analysis_samples; do
    echo "$i"
    sample_barcode="$(basename "$i")"
    echo -e "\nSample barcode is:\n$sample_barcode"

    sample_comment_file="${i}/${sample_barcode}_comments.md"
    echo -e "\nSample Comment file is:\n$sample_comment_file"
    touch "$sample_comment_file"

    # FIND SUMMARY TABLE
    echo -e "\nFinding sample summary table file..."
    sample_summary_file="$(find_sample_file "$analysis_outdir" "variantCaller_out" "$sample_barcode" "_summary.tsv" | head -1)"
    error_on_zerolength "$sample_summary_file" "TRUE" "Checking to make sure sample file was found..."
    echo -e "\nSample summary table file is:\n$sample_summary_file\n"

    num_lines="$(cat "$sample_summary_file" | wc -l)"
    min_number_lines="1"

    if [ -f $sample_comment_file ] && [ -f $sample_summary_file ] && (( $num_lines > $min_number_lines )); then
        echo -e "Running report comment script script..."
        set -x
        $report_comments_script "$sample_summary_file" -o "$sample_comment_file"
        set +x
    fi


done



