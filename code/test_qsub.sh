#!/bin/bash
set -x

# this script is for testing out submitting pipeline with qsub

tmp_outdir="output"
tmp_logdir="${tmp_outdir}/logs"
mkdir -p "$tmp_logdir"

tmp_script="code/IGV_report_wrapper-paired.sh" 

job_threads="8"
job_mem="10G"


# qsub -wd $tmp_outdir  -o :${tmp_logdir}/ -e :${tmp_logdir}/ -pe threaded "$job_threads" -l mem_free="$job_mem" -l h_vmem="$job_mem" -l mem_token="$job_mem" "$tmp_script" Auto_user_SN2-198-IT16-042-1_250_282 Auto_user_SN2-199-IT16-042-2_251_283

qsub -wd $PWD -pe threaded "$job_threads" -l mem_free="$job_mem" -l h_vmem="$job_mem" -l mem_token="$job_mem" "$tmp_script" Auto_user_SN2-198-IT16-042-1_250_282 Auto_user_SN2-199-IT16-042-2_251_283

# check if the X server is running
# if (xdpyinfo -display :10)&>/dev/null; then echo "its running"; else echo "no"; fi