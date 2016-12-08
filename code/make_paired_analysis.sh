#!/bin/bash

## USAGE: make_paired_analysis.sh <analysis ID 1> <analysis ID 2>
## DESCRIPTION: This script will set up two analysis runs to act as a paired
## analysis, meaning a single set of samples was split over two analyses

#~~~~~ CUSTOM FUNCTIONS ~~~~~~# 
function check_num_file_lines {
    local input_file="$1"
    local min_number_lines="$2"

    num_lines="$(cat "$input_file" | wc -l)"
    (( $num_lines <  $min_number_lines )) && echo -e "ERROR: File has fewer than $min_number_lines lines:\n$input_file\nExiting..." && exit
}


#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 2 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

analysis_ID_1="$1"
analysis_ID_2="$2"

outdir="output"

analysis_outdir_1="${outdir}/${analysis_ID_1}"
analysis_outdir_2="${outdir}/${analysis_ID_2}"

echo -e "analysis_outdir_1 is $analysis_outdir_1"
echo -e "analysis_outdir_2 is $analysis_outdir_2"

#~~~~~ SANITY CHECK ~~~~~~# 
# make sure ID's were passed correctly, >0 characters long
[ -z $analysis_ID_1 ] && echo -e "ERROR: Analysis ID 1 is zero characters long:\n$analysis_ID_1\nExiting..." && exit 
[ -z $analysis_ID_2 ] && echo -e "ERROR: Analysis ID 2 is zero characters long:\n$analysis_ID_2\nExiting..." && exit 

# make sure the dirs already exist!
[ ! -d $analysis_outdir_1 ] && echo -e "ERROR: Directory does not exist:\n$analysis_outdir_1\nExiting..." && exit
[ ! -d $analysis_outdir_2 ] && echo -e "ERROR: Directory does not exist:\n$analysis_outdir_2\nExiting..." && exit


#~~~~~ MAKE COMBINED DIR ~~~~~~# 
# make combine analysis dir in the 1st dir, symlink in the 2nd
combined_analysis_dir="$(readlink -f $analysis_outdir_1)/combined_analysis"
combined_analysis_2_link="${analysis_outdir_2}/combined_analysis"

mkdir -p "$combined_analysis_dir"

echo -e "combined_analysis_dir is $combined_analysis_dir"
echo -e "combined_analysis_2_link is $combined_analysis_2_link"

ln -fs "$combined_analysis_dir" "$combined_analysis_2_link"

analysis_outdir_1_fullpath="$(readlink -f "$analysis_outdir_1")"
analysis_outdir_2_fullpath="$(readlink -f "$analysis_outdir_2")"

ln -fs "$analysis_outdir_1_fullpath" "${combined_analysis_dir}/"
ln -fs "$analysis_outdir_2_fullpath" "${combined_analysis_dir}/"



#~~~~~ COMBINE BARCODES ~~~~~~# 
# combine the sample_barcode_IDs.tsv files for each analysis
combined_barcode_file="${combined_analysis_dir}/combined_sample_barcode_IDs.tsv"
echo "combined_barcode_file is $combined_barcode_file"

barcodes_file_1="$(find "$analysis_outdir_1_fullpath" -type f -name "sample_barcode_IDs.tsv")"
barcodes_file_2="$(find "$analysis_outdir_2_fullpath" -type f -name "sample_barcode_IDs.tsv")"

# make sure files were found!
[ -z $barcodes_file_1 ] && echo -e "\nERROR: No barcode file found in:\n$analysis_outdir_1_fullpath\nExiting..." && exit
[ -z $barcodes_file_2 ] && echo -e "\nERROR: No barcode file found in:\n$analysis_outdir_2_fullpath\nExiting..." && exit

# make sure the files have at least two lines (one header, one entry)
check_num_file_lines "$barcodes_file_1" 2
check_num_file_lines "$barcodes_file_2" 2

echo "barcodes_file_1 is $barcodes_file_1"
echo "barcodes_file_2 is $barcodes_file_2"

# get the header, add analysis ID field
head -1 "$barcodes_file_1" | sed 's/$/\tAnalysis ID/' > "$combined_barcode_file"

# add file 1
tail -n +2 "$barcodes_file_1" | sed "s/$/\t$analysis_ID_1/" >> "$combined_barcode_file"

# add file 2
tail -n +2 "$barcodes_file_2" | sed "s/$/\t$analysis_ID_2/" >> "$combined_barcode_file"





# dir for XLS and VCF
# variant_dir="\$(find \$analysis_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*variantCaller_out*")"
# echo "# Variants dir: \$variant_dir"

# dir for BAMs and BAIs
# coverage_dir="\$(find \$analysis_dir/plugin_out -mindepth 1 -maxdepth 1 -type d -name "*coverageAnalysis_out*")"
# echo "# Coverage dir: \$coverage_dir"