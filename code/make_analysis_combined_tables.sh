#!/bin/bash

## USAGE: make_analysis_combined_tables.sh <analysis_ID> <analysis_ID> <analysis_ID> ...

## DESCRIPTION: This script will find and concatenate tables found in multiple analysis directories



#~~~~~ CUSTOM ENVIRONMENT ~~~~~~# 
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~# 
num_args_should_be "greater_than" "0" "$#"
echo_script_name

analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg


#~~~~~ RUN PIPELINE ~~~~~~# 
for i in $analysis_ID_list; do
    analysis_ID="$i"
    analysis_outdir="${outdir}/${analysis_ID}"

    # make list of summary tables
    summary_pattern="*summary.tsv"
    if [ -z "${summary_table_list:-}" ]; then
        # if list doesn't exit, make it
        summary_table_list="$(find_analysis_files "$analysis_outdir" "$summary_pattern")"
    elif [ ! -z "${summary_table_list:-}" ]; then
        # if list exists, add to it
        summary_table_list="${summary_table_list} $(find_analysis_files "$analysis_outdir" "summary_pattern")"
    fi

    # make list of all annotation files
    annotation_pattern="*_multianno.txt"
    if [ -z "${annotation_table_list:-}" ]; then
        # if list doesn't exit, make it
        annotation_table_list="$(find_analysis_files "$analysis_outdir" "$annotation_pattern")"
    elif [ ! -z "${annotation_table_list:-}" ]; then
        # if list exists, add to it
        annotation_table_list="${annotation_table_list} $(find_analysis_files "$analysis_outdir" "$annotation_pattern")"
    fi

done


# write the concatenated tables
for i in $analysis_ID_list; do
    analysis_ID="$i"
    analysis_outdir="${outdir}/${analysis_ID}"
    ${codedir}/concat_tables.py $summary_table_list > "${analysis_outdir}/all_samples_summary_table.tsv"
    ${codedir}/concat_tables.py $annotation_table_list > "${analysis_outdir}/all_samples_annotations.tsv"
done

