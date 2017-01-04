#!/bin/bash
# set -x

## USAGE: code/make_full_report.sh <analysis_ID> <analysis_ID> ...
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
    echo -e "\n-----------------------------------\n"
    echo -e "\nProcessing Analysis. Analysis ID is:\n$analysis_ID\n"

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
    echo -e "Searching for samples in analysis dir..."
    analysis_samples="$(find "$analysis_outdir" -type d -path "*variantCaller_out*" -name "*IonXpress_*")"
    error_on_zerolength "$analysis_samples" "TRUE" "Checking to make sure samples were found..."

    echo -e "Searching for analysis barcodes file..."
    barcodes_file="$(find "$analysis_outdir" -type f -path "*variantCaller_out*" -name "sample_barcode_IDs.tsv")"
    error_on_zerolength "$barcodes_file" "TRUE" "Checking to make sure barcode file was found..."
    echo -e "Barcode file is:\n$barcodes_file"

    for i in $analysis_samples; do
        ( # run each iteration in a subshell, so 'exit' kills just the subshell, not the whole loop
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
        echo -e "\nSample barcode is:\n$sample_barcode\n"

        echo -e "Trying to create sample report dir... "
        sample_report_dir="${analysis_report_parentdir}/${sample_barcode}"
        echo -e "\nSample report dir will be:\n$sample_report_dir\n"
        mkdir -p "$sample_report_dir"
        check_dirfile_exists "$sample_report_dir" "d" "Checking to make sure sample report dir was created successfully..."
        sample_report_dir_fullpath="$(readlink -f $sample_report_dir)"
        # error_on_zerolength "$sample_report_dir_fullpath" "TRUE" "Checking to make sure sample report dir was created successfully..."
        check_dirfile_exists "$sample_report_dir_fullpath" "d" "Checking to make sure sample report dir was created successfully..."



        # find sample IGV dir
        echo -e "\nSearching for IGV snapshot dir..."
        sample_IGV_dir="$(find "$analysis_outdir" -type d -path "*coverageAnalysis_out*" -path "*$sample_barcode*" -name "*IGV_snapshots*")"
        check_dirfile_exists "$sample_IGV_dir" "d" "Checking to make sure IGV dir was found..."
        echo -e "\nIGV snapshot dir is:\n$sample_IGV_dir"

        # set report IGV link path
        echo -e "\nLinking IGV snapshot dir to report dir..."



        if [ ! -z $sample_IGV_dir ] && [ -d $sample_IGV_dir ] && [ -d $sample_report_dir ]; then
            sample_IGV_dir_fullpath="$(readlink -f "$sample_IGV_dir")"
            sample_IGV_report_dir="$(readlink -f $sample_report_dir)/IGV_snapshots"
            echo -e "Full path to sample_IGV_dir_fullpath is:\n$sample_IGV_dir_fullpath"
            # (cd $sample_report_dir && ln -fs "$sample_IGV_dir_fullpath")
            ln -fs "$sample_IGV_dir_fullpath" "$sample_IGV_report_dir"
        else
            echo -e "ERROR: IGV snapshot dir not linked; does it exist?"
        fi

        # get sample ID from barcode file
        echo -e "\nSearching barcodes file for sample ID..."
        sample_ID="$(cat $barcodes_file | grep $sample_barcode | cut -f1)"
        error_on_zerolength "$sample_ID" "TRUE" "Checking to make sure sample ID was found..."
        echo -e "Sample ID is:\n$sample_ID"

        # FIND SUMMARY TABLE
        echo -e "\nSearching for sample summary table file..."
        sample_summary_file="$(find_sample_file "$analysis_outdir" "variantCaller_out" "$sample_barcode" "_summary.tsv" | head -1)"
        # error_on_zerolength "$sample_summary_file" "TRUE" "Checking to make sure sample file was found..."
        check_dirfile_exists "$sample_summary_file" "f" "Checking to make sure sample file was found..."
        echo -e "\nSample summary table file is:\n$sample_summary_file\n"

        # MAKE SURE ITS GOT AT LEAST ONE ENTRY
        echo -e "\nMaking sure entries exist in the summary table..."
        check_num_file_lines "$sample_summary_file" "2"

        # link to the SUMMARY TABLE
        echo -e "\nLinking summary table file to to report dir..."
        if [ ! -z $sample_summary_file ] && [ -f $sample_summary_file ] && [ -d $sample_report_dir ]; then
            sample_summary_file_fullpath="$(readlink -f "$sample_summary_file")"
            sample_summary_report_file="$(readlink -f $sample_report_dir)/summary_table.tsv"
            echo -e "Full path to summary table link will be:\n$sample_summary_report_file"
            ln -fs "$sample_summary_file_fullpath" "$sample_summary_report_file"
        fi

        # find comments file.. # IonXpress_008_comments.md
        echo -e "\nSearching for sample report comments file..."
        sample_comments_file="$(find_sample_file "$analysis_outdir" "variantCaller_out" "$sample_barcode" "_comments.md" | head -1)"
        # error_on_zerolength "$sample_summary_file" "TRUE" "Checking to make sure sample file was found..."
        check_dirfile_exists "$sample_comments_file" "f" "Checking to make sure report comments file was found..."
        echo -e "\nSample comments file is:\n$sample_comments_file\n"

        # link to the comments file
        echo -e "\nLinking comments file to to report dir..."
        if [ ! -z $sample_comments_file ] && [ -f $sample_comments_file ] && [ -d $sample_report_dir ]; then
            sample_comments_file_fullpath="$(readlink -f "$sample_comments_file")"
            sample_comments_report_file="$(readlink -f $sample_report_dir)/report_comments.md"
            echo -e "Full path to sample_IGV_dir_fullpath is:\n$sample_IGV_dir_fullpath"
            ln -fs "$sample_comments_file_fullpath" "$sample_comments_report_file"
        fi
        
        # write the ID informations to files for the report
        echo -e "Writing sample ID information for the report..."
        echo "$sample_ID" > "${sample_report_dir_fullpath}/sample_ID.txt"
        echo "$sample_barcode" > "${sample_report_dir_fullpath}/barcode_ID.txt"
        echo "$analysis_ID" > "${sample_report_dir_fullpath}/analysis_ID.txt"

        # copy over the report template
        sample_report_file="${sample_report_dir}/${analysis_ID}_${sample_barcode}_report.Rmd"
        /bin/cp -v "$full_report_template" "$sample_report_file"

        if [ ! -z $sample_IGV_report_dir ] && [ ! -z $sample_summary_report_file ] && [ ! -z $sample_comments_report_file ] && [ -f $sample_report_file ]; then
            # compile the report for the sample
            module load pandoc/1.13.1
            $compile_report_script "$sample_report_file"
        fi
        )
    done
done





