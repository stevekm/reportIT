#!/bin/bash

## USAGE: annotate_wrapper.sh <analysis ID> <analysis ID> <analysis ID> ...

## DESCRIPTION: This script will annotate all VCF files found in the provided analyses,
## and create the barcode : sample ID mappings
## needed for the pipeline


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#"
echo_script_name

analysis_ID="${@:1}" # accept a space separated list of ID's

echo -e "Output directory is:\n$outdir"
echo -e "Analysis IDs are :\n$analysis_ID"

#~~~~~ RUN PIPELINE ~~~~~~#
echo -e "Running pipeline..."

echo -e "Now running annotation and data summary steps for each analysis..."
for ID in $analysis_ID; do
    echo -e "\n-----------------------------------\n"
    echo -e "Analyis is:\n$ID"

    # annotate all of the VCFs in the analysis dirs
    analysis_outdir="${outdir}/${ID}"
    echo -e "Analysis output directory is:\n$analysis_outdir"
    echo -e "Annotating analysis VCF files..."
    # set -x
    ${codedir}/annotate_vcfs.sh "$analysis_outdir"
    # set +x

    # make the barcode : sampleID mappings
    echo -e "Mapping barcode and sample IDs..."
    # set -x
    ${codedir}/get_run_IDs.sh "$analysis_outdir"
    # set +x

    # make the summary tables, etc., for each sample in the analysis
    echo -e "Making summary tables..."
    # set -x
    ${codedir}/merge_vcf_annotations_wrapper.sh "$analysis_outdir" "$ID"
    # set +x

    # make combined tables for the analysis; all samples' entries in a single table
    echo -e "Making combined tables..."
    analysis_summary_table="${analysis_outdir}/${ID}${summary_table_ext}"
    analysis_full_table="${analysis_outdir}/${ID}${full_table_ext}"
    analysis_filtered_table="${analysis_outdir}/${ID}${filtered_table_ext}"
    analysis_summary_version_table="${analysis_outdir}/${ID}${summary_version_ext}"

    ${codedir}/concat_tables.py $(find "$analysis_outdir" -path "*variantCaller_out*" -name "*${summary_table_ext}") > "$analysis_summary_table"
    ${codedir}/concat_tables.py $(find "$analysis_outdir" -path "*variantCaller_out*" -name "*${full_table_ext}") > "$analysis_full_table"
    ${codedir}/concat_tables.py $(find "$analysis_outdir" -path "*variantCaller_out*" -name "*${filtered_table_ext}") > "$analysis_filtered_table"
    ${codedir}/concat_tables.py $(find "$analysis_outdir" -path "*variantCaller_out*" -name "*${summary_version_ext}") > "$analysis_summary_version_table"

done
