#!/bin/bash

## USAGE: code/update_all_run_annotations.sh
## Description: This script will re-run the annotation portion of the pipeline for
## all analyses saved in 'output'


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"
echo_script_name


#~~~~~ RUN ~~~~~~#
output_samplesheet="${samplesheet_dir}/all_runs_$(timestamp).tsv"
(find "${outdir}/" -mindepth 1 -maxdepth 1 -type d ! -name ".git" ! -name "ExampleIonTorrentRun123" -exec basename {} \;) >> "$output_samplesheet"

echo "$output_samplesheet"

${codedir}/run_samplesheet.py $output_samplesheet -aq
