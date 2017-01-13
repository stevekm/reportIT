#!/bin/bash

## USAGE: qsub_paired_report_wrapper.sh <analysis_ID> <analysis_ID> <analysis_ID> ...

## DESCRIPTION: This script will submit a qsub job to run the IGV snapshot and reporting scripts
## for all analyses

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~# 
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~# 
num_args_should_be "greater_than" "0" "$#"
echo_script_name

analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg

IGV_wrapper_script="${codedir}/IGV_report_wrapper.sh"

job_threads="8"
job_mem="20G"
job_name="IGV_wrapper"
job_options="-j y" # merge stderr and stdout


#~~~~~ RUN PIPELINE ~~~~~~# 
for ID in $analysis_ID_list; do
    echo -e "\n-----------------------------------\n"
    echo -e "Analyis is:\n$ID\n"

    analysis_outdir="${outdir}/${ID}"
    echo -e "Analysis outdir will be:\n$analysis_outdir\n"


    analysis_logdir="${analysis_outdir}/logs"
    echo -e "Analysis logdir will be:\n$analysis_logdir\n"
    mkdir -p "$analysis_logdir"
    check_dirfile_exists "$analysis_logdir" "d" "Making sure logdir was created... "

    echo -e "Submitting job..."
    qsub -wd $PWD -o :${analysis_logdir}/ -e :${analysis_logdir}/ -pe threaded "$job_threads" -l mem_free="$job_mem" -l h_vmem="$job_mem" -l mem_token="$job_mem" -N "$job_name" $job_options "$IGV_wrapper_script" "$ID"
done
