#!/bin/bash

# this script will set up a dir with the items needed for the clinical report

# USAGE: ./report_setup.sh . ../output/R_2016_08_26_10_53_39_user_SN2-191-IT16-038-2/summary_table.tsv ../data/actionable_genes.txt ../data/hg19/canonical_transcr_descr_comment_demo.tsv test.Rmd

# ~~~~ get script args ~~~~~~ #
outdir="$1"
summary_table="$(readlink -f $2)"
actionable_genes="$(readlink -f $3)"
canonical_transcript_file="$(readlink -f $4)"
report_template="$(readlink -f $5)"

# ~~~~ setup report outdir ~~~~~~ #
run_name="$(basename $(dirname ${summary_table}) )"
outdir="${outdir}/"

mkdir -p "$outdir"

cd "$outdir"

ln -fs $summary_table
ln -fs $actionable_genes
ln -fs $canonical_transcript_file
cp $report_template "${run_name}_report.Rmd" 