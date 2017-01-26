#!/bin/bash

## USAGE: qsub_paired_report_wrapper.sh <analysis_1> <analysis_2>

## DESCRIPTION: This script will submit a qsub job to run the IGV snapshot and paired analysis

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "equal" "2" "$#"
echo_script_name

analysis_1="$1"
analysis_2="$2"

IGV_wrapper_script="${codedir}/IGV_report_wrapper-paired.sh"

job_threads="8"
job_mem="10G"
job_name="IGV_wrapper"
# job_options="-j y -l mem_free=$job_mem -l h_vmem=$job_mem -l mem_token=$job_mem" # merge stderr and stdout
job_options="-j y " # merge stderr and stdout

echo -e "Analysis 1 is:\n$analysis_1\n"
echo -e "Analysis 2 is:\n$analysis_2\n"

# setup outdirs and logdirs for qsub
analysis1_outdir="${outdir}/${analysis_1}"
analysis2_outdir="${outdir}/${analysis_2}"
analysis1_logdir="${analysis1_outdir}/paired_logs"
analysis2_logdir="${analysis2_outdir}/paired_logs"

echo -e "analysis1_outdir is:\n$analysis1_outdir\n"
echo -e "analysis2_outdir is:\n$analysis2_outdir\n"
echo -e "analysis1_logdir is:\n$analysis1_logdir\n"
echo -e "analysis2_logdir is:\n$analysis2_logdir\n"

echo -e "Creating analysis1_logdir..."
mkdir -p "$analysis1_logdir"
check_dirfile_exists "$analysis1_logdir" "d" "Making sure analysis1_logdir was created... "

echo -e "Linking analysis2_logdir to analysis1_logdir..."
link_relative_dirpaths "$analysis1_logdir" "$analysis2_logdir"
check_dirfile_exists "$analysis2_logdir" "l" "Making sure analysis2_logdir was created... "

# run!
echo -e "Submitting job..."
qsub -wd $PWD -o :${analysis1_logdir}/ -e :${analysis1_logdir}/ -pe threaded "$job_threads" -N "$job_name" $job_options "$IGV_wrapper_script" "$analysis_1" "$analysis_2"
