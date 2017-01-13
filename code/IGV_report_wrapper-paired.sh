#!/bin/bash

## USAGE: IGV_report_wrapper-paired.sh <analysis_1> <analysis_2>

## DESCRIPTION: This script will run the IGV snapshot and paired analysis setup scripts, followed by the reporting scripts

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "equal" "2" "$#"
echo_script_name

analysis_1="$1"
analysis_2="$2"

#~~~~~ RUN PIPELINE ~~~~~~#
# designate two runs as a 'paired' analysis
${codedir}/make_paired_analysis.sh "$analysis_1" "$analysis_2"

# generate concatenated summary and annotation tables for the runs
${codedir}/make_analysis_combined_tables.sh "$analysis_1" "$analysis_2"

# generate IGV snapshots for analysess
${codedir}/IGV_snapshot_parser.sh "$analysis_1" "$analysis_2"

# make clinical comment files for analyses
${codedir}/make_report_comments_wrapper.sh "$analysis_1" "$analysis_2"

# make report for the whole analysis
${codedir}/make_analysis_overview_report.sh "$analysis_1" "$analysis_2"

# make reports for each sample in the analyses
${codedir}/make_full_report.sh "$analysis_1" "$analysis_2"
