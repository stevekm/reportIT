#!/bin/bash

## USAGE: get_server_run_files.sh <analysis ID> <analysis ID> <analysis ID> ...  

## DESCRIPTION: This script will download files needed for the pipeline from the IonTorrent server

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~# 
source "global_settings.sh"

function get_server_files_pipeline {
    local server_info_file="$1"
    local outdir="$2"
    local analysis_ID="$3"

    # get info from the file
    # username@server
    local server_info="$(head -1 $server_info_file)"

    # make sure there is info
    if [[ -z "$server_info" ]]; then echo -e "No info read from file:\n${server_info}\nExiting"; exit; fi


    make_outdir "$outdir"

    analysis_outdir="${outdir}/${analysis_ID}"
    make_outdir "$analysis_outdir"

    analysis_manifest_file="${analysis_outdir}/analysis_manifest.txt"
    analysis_files_file="${analysis_outdir}/analysis_files.txt"

    echo -e "\n--------------------------------------------"
    echo -e "--------------------------------------------\n"
    echo -e "PROCESSING ANALYSIS:\n${analysis_ID}\n"
    get_server_file_mainfest "$server_info" "$analysis_manifest_file" "$analysis_ID"
    make_file_list "$analysis_manifest_file" "$analysis_files_file"
    get_analysis_ID "$analysis_manifest_file"
    get_run_ID "$analysis_manifest_file"
    download_server_files "$server_info_file" "$outdir" "$analysis_files_file"
    # update_dirfiles_permissions "$analysis_outdir"

}

#~~~~~ PARSE ARGS ~~~~~~# 
num_args_should_be "greater_than" "0" "$#"
echo_script_name


# [ ! -f $server_info_file ] && echo -e "ERROR: File not recognized:\n${server_info_file}\n\nExiting..." && exit
check_dirfile_exists "$server_info_file" "f" "Making sure server_info_file exists... "

analysis_ID="${@:1}" # accept a space separated list of ID's


#~~~~~ RUN PIPELINE ~~~~~~# 
for ID in $analysis_ID; do
    get_server_files_pipeline "$server_info_file" "$outdir" "$ID"
done





