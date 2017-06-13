#!/bin/bash

## USAGE: qsub_annotate_wrapper.sh <analysis ID> <analysis ID> <analysis ID> ...

## DESCRIPTION: This script will submit a qsub job to run the annotation wrapper


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#"
echo_script_name

analysis_ID="${@:1}" # accept a space separated list of ID's

annotate_wrapper_script="${codedir}/annotate_wrapper.sh"

job_threads="8"
job_mem="5G"
job_name="annotate_wrapper"
# job_options="-j y -l mem_free=$job_mem -l h_vmem=$job_mem -l mem_token=$job_mem" # merge stderr and stdout
job_options="-j y" # merge stderr and stdout



for ID in $analysis_ID; do
    echo -e "\n-----------------------------------\n"
    echo -e "Analyis is:\n$ID\n"

    analysis_outdir="${outdir}/${ID}"
    echo -e "Analysis outdir will be:\n$analysis_outdir\n"


    analysis_logdir="${analysis_outdir}/logs"
    echo -e "Analysis logdir will be:\n$analysis_logdir\n"
    mkdir -p "$analysis_logdir"
    check_dirfile_exists "$analysis_logdir" "d" "Making sure logdir was created... "

    echo -e "Submitting job..."
    qsub -wd $PWD -o :${analysis_logdir}/ -e :${analysis_logdir}/ -pe threaded "$job_threads" -N "$job_name" $job_options "$annotate_wrapper_script" "$ID"
    sleep 3
done
