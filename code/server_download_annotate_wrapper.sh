#!/bin/bash

## USAGE: server_download_annotate_wrapper.sh <analysis ID> <analysis ID> <analysis ID> ...  

## DESCRIPTION: This script will download files needed for the pipeline from the IonTorrent server
## then annotate all VCF files found, and create the barcode : sample ID mappings
## needed for the pipeline
## This script operates on all supplied analyses


#~~~~~ PARSE ARGS ~~~~~~# 
if (( $# < 1 )); then
    echo "ERROR: Wrong number of arguments supplied"
    grep '^##' $0
    exit
fi

echo -e "Now running script:\n${0}"

analysis_ID="${@:1}" # accept a space separated list of ID's
outdir="output"

echo -e "Output directory is:\n$outdir"
echo -e "Analysis IDs are :\n$analysis_ID"

#~~~~~ RUN PIPELINE ~~~~~~# 
echo -e "Running pipeline..."

# download the files for all the ID's passed
echo -e "Downloading files from server..."
set -x
$(dirname $0)/get_server_files.sh "$analysis_ID"
set +x

echo -e "Now running annotation and data summary steps for each analysis..."
for ID in $analysis_ID; do
    echo -e "Analyis is:\n$ID"

    # annotate all of the VCFs in the analysis dirs
    analysis_outdir="${outdir}/${ID}"
    echo -e "Analysis output directory is:\n$analysis_outdir"
    echo -e "Annotating analysis VCF files..."
    set -x
    $(dirname $0)/annotate_vcfs.sh "$analysis_outdir"
    set +x

    # make the barcode : sampleID mappings
    echo -e "Mapping barcode and sample IDs..."
    set -x
    $(dirname $0)/get_run_IDs.sh "$analysis_outdir"
    set +x

    # make the summary tables, etc., for each sample in the analysis
    echo -e "Making summary tables..."
    set -x
    $(dirname $0)/merge_vcf_annotations_wrapper.sh "$analysis_outdir" "$ID"
    set +x
done

