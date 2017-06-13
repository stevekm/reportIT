#!/bin/bash

## USAGE: IGV_report_wrapper.sh <analysis_ID> <analysis_ID> <analysis_ID> ...

## DESCRIPTION: This script will run the IGV snapshot scripts, followed by the reporting scripts



#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#"
echo_script_name

analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg

#~~~~~ RUN PIPELINE ~~~~~~#
for i in $analysis_ID_list; do
    analysis_ID="$i"

    # generate concatenated summary and annotation tables for the run
    ${codedir}/make_analysis_combined_tables.sh "$analysis_ID"

    # generate IGV snapshots for analysess
    # ${codedir}/IGV_snapshot_parser.sh "$analysis_ID"
    python ${codedir}/run_parser.py "$analysis_ID"

    # make clinical comment files for analyses
    ${codedir}/make_report_comments_wrapper.sh "$analysis_ID"

    # make report for the whole analysis
    ${codedir}/make_analysis_overview_report.sh "$analysis_ID"

    # make reports for each sample in the analyses
    ${codedir}/make_full_report.sh "$analysis_ID"
done
