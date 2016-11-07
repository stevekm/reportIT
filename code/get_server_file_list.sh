#!/bin/bash

## USAGE: get_server_run_files.sh /path/to/server_info_file.txt <analysis ID> /path/to/outdir

## DESCRIPTION: This script will generate a list of files needed for the pipeline
## based on the supplied IonTorrent run ID 

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

server_info_file="$1"
analysis_ID="$2"
outdir="$3"

if [[ -z "$outdir" ]]; then 
echo "No outdir supplied" 
echo 'USAGE: get_server_run_files.sh /path/to/server_info_file.txt <analysis ID> /path/to/outdir'
echo 'Exiting'
exit
else 
mkdir -p "${outdir}"
analysis_manifest_file="${outdir}/${analysis_ID}_analysis_manifest.txt"
analysis_files_file="${outdir}/${analysis_ID}_analysis_files.txt"
fi

# get info from the file
# username@server
server_info="$(head -1 $server_info_file)"

# make sure there is info
if [[ -z "$server_info" ]]; then echo "No info read from file, exiting"; exit; fi


# pick a run dir to access

# log into the server and find the files
# write out all the files and information needed 
echo "PLEASE LOG INTO SERVER TO GET RUN FILE LIST"
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

echo -e "\nRun manifest written to:\n$analysis_manifest_file\n"

# # make files list for rsync
grep -Ev '^#' "$analysis_manifest_file" > "$analysis_files_file" && echo -e "Run files written to:\n$analysis_files_file\n"




echo -e "Analysis ID:\n$(cat $analysis_manifest_file | grep 'Analysis ID' | cut -d ':' -f2 | cut -d ' ' -f2)\n"
echo -e "Run ID:\n$(cat $analysis_manifest_file | grep 'Run ID' | cut -d ':' -f2 | cut -d ' ' -f2)\n"




