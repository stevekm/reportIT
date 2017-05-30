#!/bin/bash
# set -x

## USAGE: merge_vcf_annotations_wrapper.sh /path/to/analysis_dir <analysis_ID>

## Description: This script will find parse an annotated analysis dir,
## find all files needed to make the merged summary tables per sample,
## and pass them to the merge_vcf_annotations.py script for merging
## This script will output summary tables, and filtered annotation tables
## This script operates on a single analysis dir


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "equal" "2" "$#" # "less_than", "greater_than", "equal"
echo_script_name



# ~~~~~~ script args ~~~~~~ #
input_dir="$1"
analysis_ID="$2"

echo -e "Input directory is:\n$input_dir"
echo -e "Analysis ID is:\n$analysis_ID"

# ~~~~~~ parameters ~~~~~~ #
# merge script location
merge_script="${codedir}/merge_vcf_annotations.py"

# ~~~~~~ Find Barcode file ~~~~~~ #
echo -e "Finding barcodes file for the analysis..."
barcodes_file="$(find "$input_dir" -type f -name "sample_barcode_IDs.tsv")"
echo -e "Barcode file is:\n$barcodes_file"

# ~~~~~~ Find Sample dirs ~~~~~~ #
echo -e "Finding sample directories for the analysis..."
# under run dir, parent subdir is variantCaller_out.*
# sample dirs labeled IonXpress_001, IonXpress_002, ...
sample_dirs="$(find "$input_dir" -type d -path "*variantCaller_out*" -name "IonXpress_*")"

# ~~~~~~ Find Sample files ~~~~~~ #
echo -e "Finding files for each sample in the analysis..."

for i in $sample_dirs; do
    samplei="$i"
    echo -e "---------------------------------------"
    echo -e "\nMaking summary tables for:\n$samplei\n"
    query_file="$(find "$samplei" -type f -name "IonXpress_*" -name "*${query_ext}")"
    annot_file="$(find "$samplei" -type f -name "IonXpress_*" -name "*${annovar_output_ext}")"
    vcf_file="$(find "$samplei" -type f -name "TSVC_variants.vcf")"
    set -x
    $merge_script "$barcodes_file" "$query_file" "$annot_file" "$transcr_file" "$panel_genes_file" "$actionable_genes_file" "$analysis_ID" "$vcf_file"
    set +x
    echo -e "---------------------------------------"

    echo -e "---------------------------------------"
    printf "\nAdding version control information to the summary table...\n"
    barcode_ID="$(basename "$samplei")"
    version_control_output_file="${samplei}/${barcode_ID}${summary_version_ext}"
    git_remote_URL="$(git remote -v | head -1 | tr ' ' '\t' | cut -f2)"
    git_branch_name="$(printf "%s\t%s" "$(git rev-parse --abbrev-ref HEAD)" "$(git rev-parse HEAD)" | cut -f1)"
    git_current_commit_ID="$(printf "%s\t%s" "$(git rev-parse --abbrev-ref HEAD)" "$(git rev-parse HEAD)" | cut -f2)"
    (
    # find the summary table we just made; don't kill the whole loop if this step breaks
    echo "Searching for the summary table..."
    sample_summary_table="$(find "$samplei" -name "*${summary_table_ext}" | head -1)"
    check_dirfile_exists "$sample_summary_table" "f" "Checking to make sure summary table was found..."
    # print the header to the versioning file
    head -1 "$sample_summary_table" | sed -e "s|$|\tGit Commit\tGit Branch\tGit Remote URL|g" > "$version_control_output_file"
    # print the file contents
    tail -n +2 "$sample_summary_table" | sed -e "s|$|\t${git_current_commit_ID}\t${git_branch_name}\t$git_remote_URL|g" >> "$version_control_output_file"
    )
done
