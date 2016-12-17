#!/bin/bash
# set -x

## USAGE: code/make_full_report_dir.sh <analysis_ID> <analysis_ID> ...
## Description: This script will set up the reports directories in an analysis dir and compile the reports for each sample

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~# 
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~# 
num_args_should_be "greater_than" "0" "$#" # "less_than", "greater_than", "equal"
echo_script_name


# ~~~~~~ script args ~~~~~~ #
analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg

for i in $analysis_ID_list; do
    analysis_ID="$i"
    echo -e "\nAnalysis ID is:\n$analysis_ID\n"

    compile_report_script="${codedir}/compile_RMD_report.R"

    analysis_outdir="${outdir}/${analysis_ID}"
    analysis_report_parentdir="${analysis_outdir}/reports"


    echo -e "\n-----------------------------------\n"
    echo -e "\n-----------------------------------\n"
    echo -e "\nanalysis_ID is:\n$analysis_ID"
    echo -e "\nanalysis_report_parentdir is :\n$analysis_report_parentdir"
    echo -e "\nfull_report_template is :\n$full_report_template"
    echo -e "\nactionable_genes_file is :\n$actionable_genes_file"



    #~~~~~ FIND ANALYIS SAMPLES ~~~~~~# 
    # find all samples in the analysis dir
    echo -e "Finding samples in analysis dir..."
    analysis_samples="$(find "$analysis_outdir" -type d -path "*variantCaller_out*" -name "*IonXpress_*")"
    error_on_zerolength "$analysis_samples" "TRUE" "Checking to make sure samples were found..."

    echo -e "Finding analysis barcodes file..."
    barcodes_file="$(find "$analysis_outdir" -type f -path "*variantCaller_out*" -name "sample_barcode_IDs.tsv")"
    error_on_zerolength "$barcodes_file" "TRUE" "Checking to make sure barcode file was found..."
    echo -e "Barcode file is:\n$barcodes_file"

    for i in $analysis_samples; do
        (
        echo -e "\n-----------------------------------\n"
        # need to get the following:
        # summary_table_file
        # IGV_snapshot_dir
        # clinical_report_comments
        # analysis_ID
        # sample_ID
        # barcode_ID

        echo "$i"
        sample_barcode="$(basename "$i")"
        echo -e "\nSample barcode is:\n$sample_barcode"

        echo -e "Searching for sample_report_dir... "
        sample_report_dir="${analysis_report_parentdir}/${sample_barcode}"
        echo -e "\nSample report dir is:\n$sample_report_dir"
        mkdir -p "$sample_report_dir"

        # find sample IGV dir
        echo -e "Searching for IGV snapshot dir..."
        sample_IGV_dir="$(find "$analysis_outdir" -type d -path "*coverageAnalysis_out*" -path "*$sample_barcode*" -name "*IGV_snapshots*")"
        echo -e "\nIGV snapshot dir is:\n$sample_IGV_dir"

        # set report IGV link path
        echo -e "\nLinking IGV snapshot dir to report dir..."
        if [ ! -z $sample_IGV_dir ] && [ -d $sample_IGV_dir ] && [ -d $sample_report_dir ]; then
            sample_IGV_dir_fullpath="$(readlink -f "$sample_IGV_dir")"
            sample_IGV_report_dir="$(readlink -f $sample_report_dir)/IGV_snapshots"
            echo -e "Full path to sample_IGV_dir_fullpath is:\n$sample_IGV_dir_fullpath"
            # (cd $sample_report_dir && ln -fs "$sample_IGV_dir_fullpath")
            ln -fs "$sample_IGV_dir_fullpath" "$sample_IGV_report_dir"
        fi

        # get sample ID from barcode file
        echo -e "Searching barcodes file for sample ID..."
        sample_ID="$(cat $barcodes_file | grep $sample_barcode | cut -f1)"
        error_on_zerolength "$sample_ID" "TRUE" "Checking to make sample ID was found..."
        echo -e "Sample ID is:\n$sample_ID"

        # FIND SUMMARY TABLE
        echo -e "\nFinding sample summary table file..."
        sample_summary_file="$(find_sample_file "$analysis_outdir" "variantCaller_out" "$sample_barcode" "_summary.tsv" | head -1)"
        # error_on_zerolength "$sample_summary_file" "TRUE" "Checking to make sure sample file was found..."
        echo -e "\nSample summary table file is:\n$sample_summary_file\n"

        # link to the SUMMARY TABLE
        echo -e "\nLinking comments file to to report dir..."
        if [ ! -z $sample_summary_file ] && [ -f $sample_summary_file ] && [ -d $sample_report_dir ]; then
            sample_summary_file_fullpath="$(readlink -f "$sample_summary_file")"
            sample_summary_report_file="$(readlink -f $sample_report_dir)/summary_table.tsv"
            echo -e "Full path to sample_IGV_dir_fullpath is:\n$sample_summary_file"
            ln -fs "$sample_summary_file_fullpath" "$sample_summary_report_file"
        fi

        # find comments file.. # IonXpress_008_comments.md
        echo -e "\nFinding sample report comments file..."
        sample_comments_file="$(find_sample_file "$analysis_outdir" "variantCaller_out" "$sample_barcode" "_comments.md" | head -1)"
        # error_on_zerolength "$sample_summary_file" "TRUE" "Checking to make sure sample file was found..."
        echo -e "\nSample comments file is:\n$sample_comments_file\n"

        # link to the comments file
        echo -e "\nLinking comments file to to report dir..."
        if [ ! -z $sample_comments_file ] && [ -f $sample_comments_file ] && [ -d $sample_report_dir ]; then
            sample_comments_file_fullpath="$(readlink -f "$sample_comments_file")"
            sample_comments_report_file="$(readlink -f $sample_report_dir)/report_comments.md"
            echo -e "Full path to sample_IGV_dir_fullpath is:\n$sample_IGV_dir_fullpath"
            ln -fs "$sample_comments_file_fullpath" "$sample_comments_report_file"
        fi


        # copy over the report template
        sample_report_file="${sample_report_dir}/$(basename "$full_report_template")"
        /bin/cp -v "$full_report_template" "$sample_report_file"

        if [ ! -z $sample_IGV_report_dir ] && [ ! -z $sample_summary_report_file ] && [ ! -z $sample_comments_report_file ] && [ -f $sample_report_file ]; then
            # do things
            module load pandoc/1.13.1
            $compile_report_script "$sample_report_file"
        fi
        )
    done
done





