#!/bin/bash

# this script will aggregate the output from from various tables for all runs in the 'output' directory
output_dir="data/aggregate"
tmp_file="${output_dir}/tmp"

patterns="_summary.tsv _full_table.tsv _filtered.tsv _summary_version.tsv"
for pattern in $patterns; do

    search_pattern="*${pattern}"
    output_file="${output_dir}/NS50_all${pattern}"

    printf "output file: %s\n" "$output_file"

    find output/ -maxdepth 3 -type f -name "${search_pattern}" ! -path "*/plugin_out/*" | xargs code/concat_tables2.py > "${tmp_file}" && code/paste_ref_len.py "${tmp_file}" "${output_file}"

done

[ -f "${tmp_file}" ] && rm -f "${tmp_file}"
