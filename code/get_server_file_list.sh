#!/bin/bash

## USAGE: get_server_run_files.sh /path/to/server_info_file.txt /path/to/outdir <analysis ID> 

## DESCRIPTION: This script will generate a list of files needed for the pipeline
## based on the supplied IonTorrent run ID 

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

server_info_file="$1"

#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 3 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

server_info_file="$1"
# make sure its actually a file
[ ! -f $server_info_file ] && echo -e "ERROR: File not recognized:\n${1}\n\nExiting..." && exit


outdir="$2"
# analysis_ID="$3"
analysis_ID="${@:3}" # accept a space separated list of ID's


#~~~~~ CUSTOM FUNCTIONS ~~~~~~# 
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

function get_server_file_mainfest {
    # log into the server and find the files
    # write out all the files and information needed 
    local server_info="$1"
    local analysis_manifest_file="$2"
    local analysis_ID="$3"
    
    echo -e "\nPLEASE LOG INTO SERVER TO GET RUN FILE LIST\n"
    ssh $server_info > "$analysis_manifest_file" << EOF
        echo "# Analysis ID: $analysis_ID"
        #
        # parent dir for the run
        analysis_dir="\$(find /results/analysis/output/Home/ -mindepth 1 -maxdepth 1 -type d -name "$analysis_ID")"
        echo "# Analysis dir: \$analysis_dir"
        #
        # dir for XLS and VCF
        variant_dir="\$(find \$analysis_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*variantCaller_out*")"
        echo "# Variants dir: \$variant_dir"
        #
        # dir for BAMs and BAIs
        coverage_dir="\$(find \$analysis_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*coverageAnalysis_out*")"
        echo "# Coverage dir: \$coverage_dir"
        #
        run_xls="\$(find \$variant_dir -maxdepth 1 -name "*.xls" ! -name "*.cov.xls" | sed -n 's|^/results/analysis/output/Home/||p')"
        echo -e "# Run XLS:\n\$run_xls"
        #
        # run XLS name = run ID
        run_ID="\$(basename \$run_xls)"
        run_ID="\${run_ID%%.xls}"
        echo "# Run ID: \$run_ID"
        #
        sample_dirs="\$(find \$variant_dir -type d -name "*IonXpress_*")"
        # echo "# Sample dirs: \$sample_dirs"
        #
        # the VCFs for the samples
        sample_vcfs="\$(find \$variant_dir -type f -name "TSVC_variants.vcf" | sed -n 's|^/results/analysis/output/Home/||p')"
        echo -e "# Sample VCFs:\n\$sample_vcfs" 
        #
        # the BAMs for the samples # these are all symlinks !
        sample_bams="\$(find \$coverage_dir -name "Ion*" -name "*.bam" | sed -n 's|^/results/analysis/output/Home/||p')"
        echo -e "# Sample BAMs:\n\$sample_bams" 
        #
        # the BAIs for the samples
        sample_bais="\$(find \$coverage_dir -name "Ion*" -name "*.bai" | sed -n 's|^/results/analysis/output/Home/||p')"
        echo -e "# Sample BAIs:\n\$sample_bais" 
        # 
        #
EOF

    [ -f $analysis_manifest_file ] && echo -e "\nRun manifest written to:\n$analysis_manifest_file\n"
    [ ! -f $analysis_manifest_file ] && echo -e "ERROR: File not created:\n$analysis_manifest_file" && exit

}


function make_file_list {
    # parse the file manifest into a list of files for rsync
    local analysis_manifest_file="$1"
    local analysis_files_file="$2"
    grep -Ev '^#' "$analysis_manifest_file" > "$analysis_files_file" 
    [ -f $analysis_files_file ] && echo -e "Run file list written to:\n$analysis_files_file\n"
    [ ! -f $analysis_files_file ] && echo -e "ERROR: File list not created:\n$analysis_files_file\n"
}


function get_run_ID {
    local analysis_manifest_file="$1"
    echo -e "Run ID:\n$(cat $analysis_manifest_file | grep 'Run ID' | cut -d ':' -f2 | cut -d ' ' -f2)\n"
}

function get_analysis_ID {
    local analysis_manifest_file="$1"
    echo -e "Analysis ID:\n$(cat $analysis_manifest_file | grep 'Analysis ID' | cut -d ':' -f2 | cut -d ' ' -f2)\n"
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


    get_server_file_mainfest "$server_info" "$analysis_manifest_file" "$analysis_ID"
    make_file_list "$analysis_manifest_file" "$analysis_files_file"
    get_analysis_ID "$analysis_manifest_file"
    get_run_ID "$analysis_manifest_file"

}

#~~~~~ RUN PIPELINE ~~~~~~# 
for ID in $analysis_ID; do
    get_server_files_pipeline "$server_info_file" "$outdir" "$ID"
done





