#/bin/bash

## USAGE: make_run_index.sh > sample_barcode_run_analysis_index.tsv
## DESCRIPTION: Run this script to make an index of all samples, barcodes, run IDs, and analysis IDs

make_barcodes_list () {
local sheet_path="$1"
analysis_ID="$(echo "$sheet_path" | sed -e 's|output/||g' -e 's|^\(.*\)/plug.*$|\1|g')"
sheet_path="$(readlink -f "$sheet_path")"
analysis_date="$(stat -c %y "$sheet_path" | cut -d ' ' -f1)"
tail -n +2 "$sheet_path" | cut -f46-48 | sort -u | sed -e "s|$|\t${analysis_ID}|g" -e "s|$|\t${analysis_date}|g"
}

print_analysis_index () {
cd /results/analysis/output/Home
for i in *; do
runID="$(find "$i" -name "*.xls" -name "R_*" -path "*variantCaller_out.*" ! -name "*.cov.xls" -exec basename {} \; | sed -e 's|.xls||g')"
analID="$(basename "$i")"
printf "%s\t%s\n" "${runID}" "${analID}"
done

}

find output/ -name "*.xls" -name "R_*" -path "*variantCaller_out.*" ! -name "*cov.xls" | while read file; do 
    make_barcodes_list "$file" | grep -Ev '^#' | grep -Ev '^$'
done

