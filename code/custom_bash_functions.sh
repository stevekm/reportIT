#!/bin/bash

# custom functions for the pipeline

function num_args_should_be {
    # USAGE: num_args_should_be "equal" "0" "$#"
    local func_type="$1" # "less_than", "greater_than", "equal"
    local arg_limit="$2"
    local num_args="$3"

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
    echo -e "-----------------------------------"
    echo -e "-----------------------------------"
    echo -e "-----------------------------------"
    echo -e "Now running script:\n${0}\n"
}

function check_dirfile_exists {
    local dirfile="$1"
    local dirfile_type="$2" # d or f or l
    local default_message="Checking to make sure an item was passed to check_dirfile_exists function..."
    local test_message="${3:-$default_message}"

    # watch out for ''
    error_on_zerolength "$dirfile" "TRUE" "$test_message"

    # check if dir exists
    if [ "$dirfile_type" == "d" ]; then
        [ ! -d "$dirfile" ] && echo -e "ERROR: Item is not a dir:\n$dirfile\nDoes it exist?\nExiting..." && exit
    fi

    # check if dir exists
    if [ "$dirfile_type" == "f" ]; then
        [ ! -f "$dirfile" ] && echo -e "ERROR: Item is not a file:\n$dirfile\nDoes it exist?\nExiting..." && exit
    fi

    # check if symlink exists
    if [ "$dirfile_type" == "l" ]; then
        [ ! -L "$dirfile" ] && echo -e "ERROR: Item is not a symlink:\n$dirfile\nDoes it exist?\nExiting..." && exit
    fi
}

function link_relative_dirpaths {
    # path1/somedir path2/somedir
    local path1_source="$1"
    local path2_dest="$2"
    local path2_dest_basename="$(basename "$path2_dest")"
    local default_message="Linking paths...\nPath 1:\n$path1_source\nPath 2:\n$path2_dest\n"
    local link_message="${3:-$default_message}"

    path1_source_fullpath="$(readlink -f "$path1_source")"
    error_on_zerolength "$path1_source_fullpath" "TRUE" "Checking that path1_source fullpath was found..."

    (
        # change to path2 parent dir
        cd "$(dirname "$path2_dest")"

        # link to the source with the path2 name
        ln -fs "$path1_source_fullpath" "$path2_dest_basename"
    )
}


function error_on_zerolength {
    local test_string="$1"
    local test_type="$2" # TRUE or FALSE
    local default_message="Testing for zero length string...\n"
    local test_message="${3:-$default_message}"

    echo -e "$test_message"

    # check if zero length string
    if [ "$test_type" == "TRUE" ]; then
        [ -z "$test_string" ] && echo -e "ERROR: String is length zero\nExiting..." && exit
    fi

    # check if non-zero length string
    if [ "$test_type" == "FALSE" ]; then
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

function find_analysis_files {
    # find a list of all matching files from analysis dir
    local analysis_dir="$1"
    local file_pattern="$2" # coverageAnalysis_out OR variantCaller_out

    # find output/Auto_user_SN2-213-IT16-049-2_269_302 -type f -path "*coverageAnalysis_out*" -path "*IonXpress_011*" -name "*.bam"
    find "$analysis_dir" -type f -name "*$file_pattern"
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
    # set -x
    local nc_ID="$(grep -E -f "$control_sampleID_file" "$barcode_file" | cut -f1)"
    local nc_barcode="$(grep -E -f "$control_sampleID_file" "$barcode_file" | cut -f2)"
    local nc_run_ID="$(grep -E -f "$control_sampleID_file" "$barcode_file" | cut -f3)"
    local nc_analysis_ID="$(grep -E -f "$control_sampleID_file" "$barcode_file" | cut -f4)"
    # set +x

    # dir for the control sample
    local nc_analysis_outdir="${outdir}/${nc_analysis_ID}"
    local check_dirfile_exists "$nc_analysis_outdir" "d"

    echo -e "\nnc_ID is:\n$nc_ID"
    echo -e "\nnc_barcode is :\n$nc_barcode"
    echo -e "\nnc_run_ID is:\n$nc_run_ID"
    echo -e "\nnc_analysis_ID is:\n$nc_analysis_ID"
    echo -e "\nnc_analysis_outdir is:\n$nc_analysis_outdir"
    if [ ! -z "$nc_ID" ] && [ ! -z "$nc_barcode" ] && [ -d "$nc_analysis_outdir" ]; then
        # find the control BAM file
        echo -e "Finding the control bam...\n"
        local nc_bamfile="$(find_sample_file "$nc_analysis_outdir" "coverageAnalysis_out" "$nc_barcode" ".bam" | head -1)"
        error_on_zerolength "$nc_bamfile" "TRUE" "Checking to make sure control sample BAM file was found..."
        echo -e "nc_bamfile is :$nc_bamfile"

        # save the IGV script control params
        IGV_control_param="-cb $nc_bamfile"
    fi
}

function find_open_X_server {
    for serv_num in $(seq 1 1000); do
        if ! (xdpyinfo -display :${serv_num})&>/dev/null; then
            echo "$serv_num" && break
        fi
    done
}


# functions for the file download pipeline

function make_outdir {
    # make sure outdir arg provided, and make it
    local outdir="$1"
    if [[ -z "$outdir" ]]; then
        echo "No outdir supplied"
        grep '^##' $0
        exit
    else
        mkdir -p "${outdir}"
    fi
}


function get_run_ID {
    # gets the run ID from the analysis_manifest_file; used by the following scripts:
    # code/annotate_wrapper.sh
    # code/server_download_annotate_wrapper.sh
    # code/get_server_files.sh
    # code/old/multi_wrapper.sh
    # code/custom_bash_functions.sh
    # code/get_run_IDs.sh
    # also copied in `code/get_server_files.sh`
    local analysis_manifest_file="$1"
    echo -e "Run ID:\n$(cat $analysis_manifest_file | grep 'Run ID' | cut -d ':' -f2 | cut -d ' ' -f2)\n"
}

function update_dirfiles_permissions {
    # remove global read write from all downloaded files; o-rw
    local outdir="$1"
    find "$outdir" -type f -exec chmod o-rw {} \;
}

timestamp () {
    date +"%Y-%m-%d-%H-%M-%S"
}
