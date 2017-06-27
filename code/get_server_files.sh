#!/bin/bash

## USAGE: get_server_run_files.sh <analysis ID> <analysis ID> <analysis ID> ...

## DESCRIPTION: This script will download files needed for the pipeline from the IonTorrent server

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"
function get_server_file_mainfest {
    # log into the server and find the files
    # write out all the files and information needed
    local server_info="$1"
    local analysis_manifest_file="$2"
    local analysis_ID="$3"
    local manifest_tmpfile="$(dirname "$analysis_manifest_file")/tmp"
    # global from this script
    local manifest_start_string="$manifest_start_string"
    # from global settings
    local IT_server_results_home_dir="$IT_server_results_home_dir"
    local IT_variant_dir_name_pattern="$IT_variant_dir_name_pattern" # variantCaller_out
    local IT_coverage_dir_name_pattern="$IT_coverage_dir_name_pattern" # coverageAnalysis_out
    local source_vcf_basename="$source_vcf_basename" # "TSVC_variants.vcf"
    local IT_sample_results_dir_name_pattern="$IT_sample_results_dir_name_pattern" # IonXpress

    echo -e "\n--------------------------------------------\n"
    echo -e "GENERATING FILE LIST FOR ANALYSIS"
    echo -e "\nPLEASE LOG INTO SERVER TO GET ANALYSIS FILE LIST\n"
    ssh $server_info > "$analysis_manifest_file" << EOF
        # set -x
        # unescaped shell variables get expanded locally by heredoc
        # escaped shell variables get expanded remotely during command execution on remote IT server
        echo "$manifest_start_string"
        echo "# Analysis ID: $analysis_ID"
        #
        # parent dir for the run
        analysis_dir="\$(find "$IT_server_results_home_dir" -mindepth 1 -maxdepth 1 -type d -name "$analysis_ID")"
        echo "# Analysis dir: \$analysis_dir"
        #
        # dir for XLS and VCF
        variant_dir="\$(find \$analysis_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*$IT_variant_dir_name_pattern*")"
        echo "# Variants dir: \$variant_dir"
        #
        # dir for BAMs and BAIs
        coverage_dir="\$(find \$analysis_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*$IT_coverage_dir_name_pattern*")"
        echo "# Coverage dir: \$coverage_dir"
        #
        run_xls="\$(find \$variant_dir -maxdepth 1 -name "*.xls" ! -name "*.cov.xls" | sed -n 's|^$IT_server_results_home_dir||p')"
        printf "# Run XLS:\n%s\n" "\$run_xls"
        #
        # run XLS name = run ID
        run_ID="\$(basename \$run_xls)"
        run_ID="\${run_ID%%.xls}"
        echo "# Run ID: \$run_ID"
        #
        sample_dirs="\$(find \$variant_dir -type d -name "*$IT_sample_results_dir_name_pattern*")"
        # echo "# Sample dirs: \$sample_dirs"
        #
        # the VCFs for the samples
        sample_vcfs="\$(find \$variant_dir -type f -name "$source_vcf_basename" | sed -n 's|^$IT_server_results_home_dir||p')"
        printf "# Sample VCFs:\n%s\n" "\$sample_vcfs"
        #
        # the BAMs for the samples # these are all symlinks !
        sample_bams="\$(find \$coverage_dir -name "$IT_sample_results_dir_name_pattern*" -name "*.bam" | sed -n 's|^$IT_server_results_home_dir||p')"
        printf "# Sample BAMs:\n%s\n" "\$sample_bams"
        #
        # the BAIs for the samples
        sample_bais="\$(find \$coverage_dir -name "$IT_sample_results_dir_name_pattern*" -name "*.bai" | sed -n 's|^$IT_server_results_home_dir||p')"
        printf "# Sample BAIs:\n%s\n" "\$sample_bais"

        # grab all the rest of the stuff in the sample coverage dirs
        # printf "# Extra Files:\n%s\n%s\n" "\$(find \$coverage_dir -type f | sed -n 's|^$IT_server_results_home_dir||p')" "\$(find \$variant_dir -type f | sed -n 's|^$IT_server_results_home_dir||p')"
        printf "# Extra Files:\n\n"
        find "\$analysis_dir" -name "report.pdf" | sed -n 's|^$IT_server_results_home_dir||p'
        find "\$coverage_dir" -name "*bcmatrix.xls" ! -name "link.bcmatrix.xls" | sed -n 's|^$IT_server_results_home_dir||p'
        # .bcmatrix.xls
        #
        #
EOF

    # strip the text before the start of the manifest;
    # find all lines starting at the 'start string' and ending to the end of the file
    grep -A"$(cat "$analysis_manifest_file" | wc -l)" "$manifest_start_string" "$analysis_manifest_file" > "$manifest_tmpfile" && /bin/mv "$manifest_tmpfile" "$analysis_manifest_file"

    # check that file was created
    [ -f "$analysis_manifest_file" ] && echo -e "\nFile manifest written to:\n$analysis_manifest_file\n"
    [ ! -f "$analysis_manifest_file" ] && echo -e "ERROR: File not created:\n$analysis_manifest_file" && exit

}


function make_file_list {
    # parse the file manifest into a list of files for rsync
    local analysis_manifest_file="$1"
    local analysis_files_file="$2"
    grep -Ev '^#' "$analysis_manifest_file" > "$analysis_files_file"
    [ -f "$analysis_files_file" ] && echo -e "File list written to:\n$analysis_files_file\n"
    [ ! -f "$analysis_files_file" ] && echo -e "ERROR: File list not created:\n$analysis_files_file\n"
}


function get_analysis_ID {
    # retrieve the analysis ID from the manifest file
    local analysis_manifest_file="$1"
    echo -e "Analysis ID:\n$(cat $analysis_manifest_file | grep 'Analysis ID' | cut -d ':' -f2 | cut -d ' ' -f2)\n"
}

function get_run_ID {
    # retrieve the run ID from the manifest file
    # also in `code/custom_bash_functions.sh`
    local analysis_manifest_file="$1"
    echo -e "Run ID:\n$(cat $analysis_manifest_file | grep 'Run ID' | cut -d ':' -f2 | cut -d ' ' -f2)\n"
}


function download_server_files {
    # download all the files written to the file list, created by truncating the file manifest
    local server_info_file="$1"
    local outdir="$2"
    local server_file_list="$3"

    # get info from the file
    # username@server
    local server_info="$(head -1 $server_info_file)"

    # download the files from the server
    echo -e "\n--------------------------------------------\n"
    echo -e "DOWNLOADING ANALYSIS FILES FROM SERVER"
    echo -e "\nPLEASE LOG INTO SERVER TO GET COPY FILES\n"
    rsync -avzheR --copy-links --chmod=o-rw --progress -e "ssh" --files-from="$server_file_list" ${server_info}:/results/analysis/output/Home/ "${outdir}"
}

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

# string to denote the beginning of the file manifest, so that it can be distinguished from
# the ssh login text that is now being prepended to ssh command stdout as of the latest
# IT server OS upgrade
# make this a global since we'll need it a few places
manifest_start_string="# FILEMANIFESTSTARTSHERE"
#~~~~~ RUN PIPELINE ~~~~~~#
for ID in $analysis_ID; do
    get_server_files_pipeline "$server_info_file" "$outdir" "$ID"
done
