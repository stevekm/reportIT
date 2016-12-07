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

analysis_ID="${@:1}" # accept a space separated list of ID's
outdir="output"



#~~~~~ RUN PIPELINE ~~~~~~# 
# download the files for all the ID's passed
$(dirname $0)/get_server_files.sh "$analysis_ID"

for ID in $analysis_ID; do
    # annotate all of the VCFs in the analysis dirs
    analysis_outdir="${outdir}/${ID}"
    $(dirname $0)/annotate_vcfs.sh "$analysis_outdir"

    # make the barcode : sampleID mappings
    $(dirname $0)/get_run_IDs.sh "$analysis_outdir"

    # make the summary tables, etc., for each sample in the analysis
    $(dirname $0)/merge_vcf_annotations_wrapper.sh "$analysis_outdir"
done

