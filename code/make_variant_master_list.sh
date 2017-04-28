#!/bin/bash

## USAGE: make_variant_master_list.sh
## DESCRIPTION: This script will aggregate all of the summary tables from the output directory
## and merge them with tables for sample ID index information, along with Tumor Type and Concordance information

version_table_file="data/misc/all_summary_table_variants-with_versioning.tsv"
sample_index_file="data/misc/sample_barcode_run_analysis_index.tsv"
master_list_file="data/misc/variant_master_list_clean_merge/variant_master_list_with_tissue_concordance.tsv"
run_index_script="code/make_run_index.sh"
merge_script="code/variant_master_list_merge.R"

backup_file () {
    backup_script="$(readlink -f code/toolbox/file_backup.sh)"
    [ -z "$backup_script" ] && printf "\nERROR: Couldn't find backup script!\n" && exit
    local input_file="$1"
    (
    cd "$(dirname "$input_file")"
    $backup_script "$(basename "$input_file")" old
    )
}

check_file () {
    local input_file="$1"
    printf "\nChecking for old version of file present:\n%s\n\n" "$input_file"
    [ -f "$input_file" ] && backup_file "$input_file"
}
# Make concatenated table of all IonTorrent variants
check_file "$version_table_file"
find output/ -name "*summary_version.tsv" ! -path "*IonXpress*" | xargs code/toolbox/concat_tables.py > "$version_table_file" && printf "Made new version of file:\n%s\n\n" "$version_table_file"

# make the sample Index file
check_file $sample_index_file
$run_index_script > $sample_index_file && printf "Made new version of file:\n%s\n\n" "$sample_index_file"

# Merge the two with the other concordance and tissue type files supplied by Yehonatan
check_file $master_list_file
$merge_script $master_list_file && printf "Made new version of file:\n%s\n\n" "$master_list_file"

# format the master list for REDCap
(
REDCap_script="./setup.py"
cd REDCap
$REDCap_script $master_list_file
)
