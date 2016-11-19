#!/bin/bash
set -x

## USAGE: multi_wrapper.sh data/server_info.txt <analysis ID> <run ID> /path/to/outdir

## DESCRIPTION: This is a wrapper script for other clinical pipeline scripts
## run this after 
# code/get_server_file_list.sh data/server_info.txt Auto_user_SN2-207-IT16-046-2_259_291 output

server_info_file="$1"
analysis_id="$2"
run_ID="$3"
output_dir="$4"

analysis_file_list="${output_dir}/${analysis_id}_analysis_files.txt"

run_dir="${output_dir}/${run_ID}"
mkdir -p "$run_dir"

$(dirname $0)/download_server_files.sh "$server_info_file" "$analysis_file_list" "$run_dir"

$(dirname $0)/annotate_vcfs.sh "$run_dir"

$(dirname $0)/get_run_IDs.sh "$run_dir"

$(dirname $0)/merge_vcf_annotations_wrapper.sh "$run_dir"