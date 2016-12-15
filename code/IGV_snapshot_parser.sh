#!/bin/bash

## USAGE: IGV_snapshot_parser.sh <analysis ID> <analysis ID> <analysis ID> ...  

## DESCRIPTION: This script will generate and run IGV snapshot batchscripts
## for all supplied analyses. First, the script will search for a 
## 'combined_sample_barcode_IDs.tsv' file; if found, the NC control will be parsed out
## and used as the control BAM for the IGV screenshots
## Otherwise, the script will parse out the BAM files per sample and run the 
## IGV screenshot Python script on each one
## This script operates on all supplied analyses


#~~~~~ CUSTOM FUNCTIONS ~~~~~~#
source "$(dirname $0)/custom_bash_functions.sh"

#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 1 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

analysis_ID="$1"
# analysis_ID="${@:1}" # accept a space separated list of ID's
outdir="output"
control_sampleID_file="data/control_sampleIDs.txt" # file with extended regex NC sample ID's
# make sure the control sample ID file exists
check_dirfile_exists "$control_sampleID_file" "f"

analysis_outdir="${outdir}/${analysis_ID}"

IGV_batchscript_generator_script="$(dirname $0)/IGV_batchscript_generator.py"
IGV_run_batchscript_script="$(dirname $0)/run_IGV_batchscript.py"





#~~~~~ CHECK FOR COMBINED ANALYSIS ~~~~~~# 
# if a 'combined_sample_barcode_IDs.tsv' file exists in the dir,
# parse it to find the 'NC' or 'NC HAPMAP' sample and its BAM file
# to use as controls

echo -e "\n-----------------------------------\n"
echo -e "Checking for combined analysis dir..."

# get the first found combined barcode file
combined_barcode_file="$(find "$analysis_outdir" -type f -name "combined_sample_barcode_IDs.tsv" | head -1)"

# test to see if one was found
# error_on_zerolength "$combined_barcode_file" "TRUE" "Testing if combined barcode file was found..."
# check_dirfile_exists "$combined_barcode_file" "f"

# if one was found, get the NC sample from it:
if [ ! -z $combined_barcode_file ]; then 
    echo -e "Combined analysis dir found..."
    echo -e "Combine analysis barcodes file is:\n$combined_barcode_file"
    echo -e "Getting NC control sample from combined barcode file..."
    find_NC_control_sample "$combined_barcode_file" "$control_sampleID_file" "$outdir"

elif [ -z $combined_barcode_file ]; then  
    # find the single analysis barcode file instead.. 
    echo -e "No combined analysis found, searching for single analysis sample barcode file..."
    barcode_file="$(find "$analysis_outdir" -type f -name "sample_barcode_IDs.tsv" | head -1)"
    error_on_zerolength "$barcode_file" "TRUE" "Checking to make sure barcode file was found..."
    echo -e "Getting NC sample from barcode file:\n$barcode_file"
    find_NC_control_sample "$barcode_file" "$control_sampleID_file" "$outdir"
fi






#~~~~~ FIND ANALYIS SAMPLES ~~~~~~# 
# find all samples in the analysis dir
# then find for each sample:
# BAM file
# IGV outdir
# sumamry table
# ? control BAM
echo -e "\n-----------------------------------\n"
echo -e "Finding samples in analysis dir..."
analysis_samples="$(find "$analysis_outdir" -type d -path "*coverageAnalysis_out*" -name "*IonXpress_*")"

for i in $analysis_samples; do
    echo "$i"
    sample_barcode="$(basename "$i")"
    echo -e "\nSample barcode is:\n$sample_barcode"

    # FIND BAM FILE
    echo -e "\nFinding BAM file in sample dir..."
    sample_bamfile="$(find_sample_file "$i" "coverageAnalysis_out" "$sample_barcode" ".bam" | head -1)"
    error_on_zerolength "$sample_bamfile" "TRUE" "Checking to make sure sample BAM file was found..."
    echo -e "sample_bamfile is:\n$sample_bamfile"

    # MAKE IGV OUTDIR
    echo -e "\nMaking IGV snapshot dir..."
    sample_IGV_dir="$(dirname "$sample_bamfile")/IGV_snapshots"
    echo -e "\nIGV snapshot dir is:\n$sample_IGV_dir\n"
    mkdir -p "$sample_IGV_dir"
    check_dirfile_exists "$sample_IGV_dir" "d"

    # FIND SUMMARY TABLE
    echo -e "\nFinding sample summary table file..."
    sample_summary_file="$(find_sample_file "$analysis_outdir" "variantCaller_out" "$sample_barcode" "_summary.tsv" | head -1)"
    error_on_zerolength "$sample_summary_file" "TRUE" "Checking to make sure sample file was found..."
    echo -e "\nSample summary table file is:\n$sample_summary_file\n"

    # CREATE IGV BATCH SCRIPT
    # only run if at least 2 lines in the summary table file..
    # with or without control!
    
    echo -e "Checking number of lines in summary table file..."
    num_lines="$(cat "$sample_summary_file" | wc -l)"
    min_number_lines="1"
    if (( $num_lines > $min_number_lines )); then 
        echo -e "Running IGV batcscript generator script..."
        [ -z "${IGV_control_param:-}" ] && echo -e "Including control BAM parameters:\n${IGV_control_param}"
        set -x
        $IGV_batchscript_generator_script "$sample_summary_file" "$sample_bamfile" "$sample_IGV_dir" ${IGV_control_param:-}
        set +x

        # find the new batch script.. IGV_script.bat
        echo -e "Finding IGV batchs script..."
        sample_IGV_batchscript="$(find_sample_file "$i" "coverageAnalysis_out" "$sample_barcode" "IGV_script.bat" | head -1)"
        error_on_zerolength "$sample_IGV_batchscript" "TRUE" "Checking to make sure IGV batch script was found..."
        if [ ! -z $sample_IGV_batchscript ]; then
            echo -e "IGV batch script is:\n$sample_IGV_batchscript\n"

            # run IGV snapshotter
            echo -e "Running IGV snapshot batch script..."
            set -x
            $IGV_run_batchscript_script "$sample_IGV_batchscript" 
            set +x
        fi
        
    elif (( ! $num_lines > $min_number_lines )); then 
        echo -e "Summary table has only:\n$num_lines\nnumber of lines."
        echo -e "Minimum lines needed:\n$min_number_lines"
        echo -e "Skipping IGV snapshot step..."
    fi


done

