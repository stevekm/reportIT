#!/bin/bash
# set -x

## USAGE: make_report_comments_wrapper.sh /path/to/analysis_dir

## Description: This script will find parse an annotated analysis dir, 


#~~~~~ CUSTOM FUNCTIONS ~~~~~~# 
function check_dirfile_exists {
    local dirfile="$1"
    local dirfile_type="$2" # d or f

    # check if dir exists
    if [ $dirfile_type == "d" ]; then
        [ ! -d $dirfile ] && echo -e "ERROR: Item is not a dir:\n$dirfile\nDoes it exist?\nExiting..." && exit
    fi

        # check if dir exists
    if [ $dirfile_type == "f" ]; then
        [ ! -f $dirfile ] && echo -e "ERROR: Item is not a file:\n$dirfile\nDoes it exist?\nExiting..." && exit
    fi
}

function error_on_zerolength {
    local test_string="$1"
    local test_type="$2" # TRUE or FALSE
    local test_message="$3"

    echo -e "$test_message"

    # check if zero length string
    if [ $test_type == "TRUE" ]; then
        [ -z "$test_string" ] && echo -e "ERROR: String is length zero\nExiting..." && exit
    fi

    # check if non-zero length string
    if [ $test_type == "FALSE" ]; then
        [ ! -z "$test_string" ] && echo -e "ERROR: String is not length zero\nExiting..." && exit
    fi

}

function find_sample_file {
    # find a file from the sample's analysis directory; return first result!
    local analysis_dir="$1"
    local path_pattern="$2" # coverageAnalysis_out OR variantCaller_out
    local barcode_ID="$3"
    local file_extension="$4"

    # find output/Auto_user_SN2-213-IT16-049-2_269_302 -type f -path "*coverageAnalysis_out*" -path "*IonXpress_011*" -name "*.bam"
    find "$analysis_dir" -type f -path "*$path_pattern*" -path "*$barcode_ID*" -name "*$file_extension"

}


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



