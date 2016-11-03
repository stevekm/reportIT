#!/bin/bash

## USAGE: get_server_run_files.sh /path/to/server_info_file.txt <run ID> /path/to/outdir

## DESCRIPTION: This script will generate a list of files needed for the pipeline
## based on the supplied IonTorrent run ID 

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

server_info_file="$1"
run_ID="$2"
outdir="$3"

if [[ -z "$outdir" ]]; then 
echo "No outdir supplied" 
echo 'USAGE: get_server_run_files.sh /path/to/server_info_file.txt <run ID> /path/to/outdir'
echo 'Exiting'
exit
else 
mkdir -p "${outdir}"
run_manifest_file="${outdir}/${run_ID}_run_manifest.txt"
run_files_file="${outdir}/${run_ID}_run_files.txt"
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
ssh $server_info > "$run_manifest_file" << EOF
    echo "# Run ID: $run_ID"
    #
    # parent dir for the run
    run_dir="\$(find /results/analysis/output/Home/ -mindepth 1 -maxdepth 1 -type d -name "$run_ID")"
    echo "# Run dir: \$run_dir"
    #
    # dir for XLS and VCF
    variant_dir="\$(find \$run_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*variantCaller_out*")"
    echo "# Variants dir: \$variant_dir"
    #
    # dir for BAMs and BAIs
    coverage_dir="\$(find \$run_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*coverageAnalysis_out*")"
    echo "# Coverage dir: \$coverage_dir"
    #
    run_xls="\$(find \$variant_dir -maxdepth 1 -name "*.xls" ! -name "*.cov.xls" | sed -n 's|^/results/analysis/output/Home/||p')"
    echo -e "# Run XLS:\n\$run_xls"
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

echo -e "Run manifest written to:\n$run_manifest_file"

# # make files list for rsync
grep -Ev '^#' "$run_manifest_file" > "$run_files_file" && echo -e "Run files written to:\n$run_files_file"

# copy the files
echo "PLEASE LOG INTO SERVER TO GET COPY RUN FILES"
rsync --dry-run -vzheR --copy-links --progress -e "ssh" --files-from="$run_files_file" ${server_info}:/results/analysis/output/Home/ "${outdir}"
