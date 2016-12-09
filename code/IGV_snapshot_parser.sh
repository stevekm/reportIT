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

function find_NC_control_sample {
    # parse a barcodes file to find the NC control sample
    local barcode_file="$1"
    local control_sampleID_file="$2" # "data/control_sampleIDs.txt"
    local outdir="$3"

    nc_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f1)"
    nc_barcode="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f2)"
    nc_run_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f3)"
    nc_analysis_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f4)"

    # dir for the control sample
    nc_analysis_outdir="${outdir}/${nc_analysis_ID}"
    check_dirfile_exists "$nc_analysis_outdir" "d"

    echo -e "\nnc_ID is:\n$nc_ID"
    echo -e "\nnc_barcode is :\n$nc_barcode"
    echo -e "\nnc_run_ID is:\n$nc_run_ID"
    echo -e "\nnc_analysis_ID is:\n$nc_analysis_ID"
    echo -e "\nnc_analysis_outdir is:\n$nc_analysis_outdir"

    # find the control BAM file
    echo -e "Finding the control bam...\n"
    nc_bamfile="$(find_sample_file "$nc_analysis_outdir" "coverageAnalysis_out" "$nc_barcode" ".bam" | head -1)"
    error_on_zerolength "$nc_bamfile" "TRUE" "Checking to make sure control sample BAM file was found..."
    echo -e "nc_bamfile is :$nc_bamfile"

    # save the IGV script control params
    IGV_control_param="-cb $nc_bamfile"
}


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
    

    # echo -e "Combined file found\n$combined_barcode_file" 
    # nc_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f1)"
    # nc_barcode="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f2)"
    # nc_run_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f3)"
    # nc_analysis_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f4)"

    # # dir for the control sample
    # nc_analysis_outdir="${outdir}/${nc_analysis_ID}"
    # check_dirfile_exists "$nc_analysis_outdir" "d"

    # echo -e "\nnc_ID is:\n$nc_ID"
    # echo -e "\nnc_barcode is :\n$nc_barcode"
    # echo -e "\nnc_run_ID is:\n$nc_run_ID"
    # echo -e "\nnc_analysis_ID is:\n$nc_analysis_ID"
    # echo -e "\nnc_analysis_outdir is:\n$nc_analysis_outdir"

    # # find the control BAM file
    # echo -e "Finding the control bam...\n"
    # nc_bamfile="$(find_sample_file "$nc_analysis_outdir" "coverageAnalysis_out" "$nc_barcode" ".bam" | head -1)"
    # error_on_zerolength "$nc_bamfile" "TRUE" "Checking to make sure control sample BAM file was found..."
    # echo -e "nc_bamfile is :$nc_bamfile"

    # # save the IGV script control params
    # IGV_control_param="-cb $nc_bamfile"

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
    
    num_lines="$(cat "$sample_summary_file" | wc -l)"
    min_number_lines="1"
    if (( $num_lines > $min_number_lines )); then 
        echo -e "Running IGV batcscript generator script..."
        $IGV_batchscript_generator_script "$sample_summary_file" "$sample_bamfile" "$sample_IGV_dir" ${IGV_control_param:-}

        # find the new batch script.. IGV_script.bat
        echo -e "Getting IGV batchs script..."
        sample_IGV_batchscript="$(find_sample_file "$i" "coverageAnalysis_out" "$sample_barcode" "IGV_script.bat" | head -1)"
        error_on_zerolength "$sample_IGV_batchscript" "TRUE" "Checking to make sure IGV batch script was found..."
        echo -e "IGV batch script is:\n$sample_IGV_batchscript\n"

        # run IGV snapshotter
        echo -e "Running IGV snapshot batch script..."
        echo -e "param is:tes1${IGV_control_param:-}tes2"
        $IGV_run_batchscript_script "$sample_IGV_batchscript" 

    fi


done

