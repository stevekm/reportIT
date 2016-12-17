#!/bin/bash
# set -x

## USAGE: make_report_comments_wrapper.sh <analysis_ID> <analysis_ID> ...
## Description: This script will find parse an annotated analysis dir, 

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~# 
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~# 
num_args_should_be "greater_than" "0" "$#" # "less_than", "greater_than", "equal"
echo_script_name


# ~~~~~~ script args ~~~~~~ #
analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg

for i in $analysis_ID_list; do
    analysis_ID="$i"
    echo -e "\nAnalysis ID is:\n$analysis_ID\n"


    analysis_outdir="${outdir}/${analysis_ID}"
    # make sure the dir
    check_dirfile_exists "$analysis_outdir" "d"

    report_comments_script="${codedir}/make_report_comments.py"



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
done


