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

# relative paths to both dirs
analysis_outdir_1="${outdir}/${analysis_ID_1}"
analysis_outdir_2="${outdir}/${analysis_ID_2}"


# echo -e "analysis_outdir_1 is $analysis_outdir_1"
# echo -e "analysis_outdir_2 is $analysis_outdir_2"

#~~~~~ SANITY CHECK ~~~~~~# 
# make sure ID's were passed correctly, >0 characters long
[ -z $analysis_ID_1 ] && echo -e "ERROR: Analysis ID 1 is zero characters long:\n$analysis_ID_1\nExiting..." && exit 
[ -z $analysis_ID_2 ] && echo -e "ERROR: Analysis ID 2 is zero characters long:\n$analysis_ID_2\nExiting..." && exit 

# make sure the dirs already exist!
[ ! -d $analysis_outdir_1 ] && echo -e "ERROR: Directory does not exist:\n$analysis_outdir_1\nExiting..." && exit
[ ! -d $analysis_outdir_2 ] && echo -e "ERROR: Directory does not exist:\n$analysis_outdir_2\nExiting..." && exit



#~~~~~ MAKE COMBINED DIR ~~~~~~# 
# get full paths to both analysis dirs
analysis_outdir_1_fullpath="$(readlink -f "$analysis_outdir_1")"
analysis_outdir_2_fullpath="$(readlink -f "$analysis_outdir_2")"

# make combine analysis dir in both places
combined_analysis_dir_1="${analysis_outdir_1_fullpath}/combined_analysis"
combined_analysis_dir_2="${analysis_outdir_2_fullpath}/combined_analysis"
mkdir -p "$combined_analysis_dir_1"
mkdir -p "$combined_analysis_dir_2"



#~~~~~ COMBINE BARCODES ~~~~~~# 
# combine the sample_barcode_IDs.tsv files for each analysis
# make the file in the first dir, then HARDLINK to the second
combined_barcode_file="${combined_analysis_dir_1}/combined_sample_barcode_IDs.tsv"
echo "combined_barcode_file is $combined_barcode_file"

# find the barcode files in each analysis
barcodes_file_1="$(find "$analysis_outdir_1_fullpath" -type f -name "sample_barcode_IDs.tsv")"
barcodes_file_2="$(find "$analysis_outdir_2_fullpath" -type f -name "sample_barcode_IDs.tsv")"

# make sure files were found!
[ -z $barcodes_file_1 ] && echo -e "\nERROR: No barcode file found in:\n$analysis_outdir_1_fullpath\nExiting..." && exit
[ -z $barcodes_file_2 ] && echo -e "\nERROR: No barcode file found in:\n$analysis_outdir_2_fullpath\nExiting..." && exit

# make sure the files have at least two lines (one header, at least one entry)
check_num_file_lines "$barcodes_file_1" 2
check_num_file_lines "$barcodes_file_2" 2


echo -e "\nCreating combined barcode file:\n$combined_barcode_file"
# get the header, add analysis ID field
head -1 "$barcodes_file_1" | sed 's/$/\tAnalysis ID/' > "$combined_barcode_file"

# add file 1
tail -n +2 "$barcodes_file_1" | sed "s/$/\t$analysis_ID_1/" >> "$combined_barcode_file"

# add file 2
tail -n +2 "$barcodes_file_2" | sed "s/$/\t$analysis_ID_2/" >> "$combined_barcode_file"

# make sure the file writing worked! 
[ ! -f $combined_barcode_file ] && echo -e "\nERROR: Output file does not exist:\n$combined_barcode_file\nExiting..." && exit
check_num_file_lines "$combined_barcode_file" 2

# hardlink the combined barcode file in the second analysis dir
echo -e "\nLinking combined barcode file in analysis dir:\n${combined_analysis_dir_2}\n"
ln "$combined_barcode_file" "${combined_analysis_dir_2}/"


# make sure the linking worked & the files are discoverable
[ -z $(find "$analysis_outdir_1" -name "$(basename "$combined_barcode_file")") ] && echo -e "\nERROR: Linked file:\n$(basename "$combined_barcode_file")\n not discoverable in dir:\n$analysis_outdir_1\nExiting..." && exit
[ -z $(find "$analysis_outdir_2" -name "$(basename "$combined_barcode_file")") ] && echo -e "\nERROR: Linked file:\n$(basename "$combined_barcode_file")\n not discoverable in dir:\n$analysis_outdir_2\nExiting..." && exit

#~~~~~ INDEX PAIRED ANALYSES ~~~~~~# 
# record the cross-linked analysis dirs
index_file="${combined_analysis_dir_1}/paired_analysis_index.txt"

echo -e "${combined_analysis_dir_1}" > "$index_file"
echo -e "${combined_analysis_dir_2}" >> "$index_file"

# hardlink in the other combined dir
ln "$index_file" "${combined_analysis_dir_2}/"



