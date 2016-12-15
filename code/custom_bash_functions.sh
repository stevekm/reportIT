#!/bin/bash

# custom functions for the pipeline


#~~~~~ PARSE ARGS ~~~~~~# 

function num_args_should_be {
    local func_type="$1" # "less_than", "greater_than", "equal"
    local arg_limit="$2"
    local num_args="$3"
    # USAGE: num_args_should_be "equal" "0" "$#"

    if [ "$func_type" == "less_than" ]; then
        if (( "$num_args" >= "$arg_limit" )); then
            echo "ERROR: Wrong number of arguments supplied"
            grep '^##' $0
            exit
        fi
    fi

    if [ "$func_type" == "greater_than" ]; then
        if (( "$num_args" <= "$arg_limit" )); then
            echo "ERROR: Wrong number of arguments supplied"
            grep '^##' $0
            exit
        fi
    fi

    if [ "$func_type" == "equal" ]; then
        if (( "$num_args" != "$arg_limit" )); then
            echo "ERROR: Wrong number of arguments supplied"
            grep '^##' $0
            exit
        fi
    fi

}




function echo_script_name {
    echo -e "Now running script:\n${0}\n"
}

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

function check_num_file_lines {
    local input_file="$1"
    local min_number_lines="$2"

    num_lines="$(cat "$input_file" | wc -l)"
    (( $num_lines <  $min_number_lines )) && echo -e "ERROR: File has fewer than $min_number_lines lines:\n$input_file\nExiting..." && exit
}


function find_NC_control_sample {
    # parse a barcodes file to find the NC control sample
    local barcode_file="$1"
    local control_sampleID_file="$2" # "data/control_sampleIDs.txt"
    local outdir="$3"

    echo -e "Searching for NC control sample in file:\n$barcode_file"
    set -x
    nc_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f1)"
    nc_barcode="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f2)"
    nc_run_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f3)"
    nc_analysis_ID="$(grep -E -f "$control_sampleID_file" "$combined_barcode_file" | cut -f4)"
    set +x

    # dir for the control sample
    nc_analysis_outdir="${outdir}/${nc_analysis_ID}"
    check_dirfile_exists "$nc_analysis_outdir" "d"

    echo -e "\nnc_ID is:\n$nc_ID"
    echo -e "\nnc_barcode is :\n$nc_barcode"
    echo -e "\nnc_run_ID is:\n$nc_run_ID"
    echo -e "\nnc_analysis_ID is:\n$nc_analysis_ID"
    echo -e "\nnc_analysis_outdir is:\n$nc_analysis_outdir"
    if [ ! -z $nc_ID ] && [ ! -z $nc_barcode ] && [ -d $nc_analysis_outdir ]; then
        # find the control BAM file
        echo -e "Finding the control bam...\n"
        nc_bamfile="$(find_sample_file "$nc_analysis_outdir" "coverageAnalysis_out" "$nc_barcode" ".bam" | head -1)"
        error_on_zerolength "$nc_bamfile" "TRUE" "Checking to make sure control sample BAM file was found..."
        echo -e "nc_bamfile is :$nc_bamfile"

        # save the IGV script control params
        IGV_control_param="-cb $nc_bamfile"
    fi
}