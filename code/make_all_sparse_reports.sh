#!/bin/bash

run_dir="output/"
compile_script="code/compile_sparse_report.R"
report_template="report/sparse_report.Rmd"
act_genes="data/actionable_genes.txt"
canon_transcr="data/hg19/canonical_transcr_descr_comment.tsv"

FILES="$(find ${run_dir} -type f -name "summary_table.tsv")"

for i in $FILES; do
echo "$i"

"$compile_script" "$i" "$report_template" "$act_genes" "$canon_transcr"

done