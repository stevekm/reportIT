#!/bin/bash
set -x

## USAGE: code/make_analysis_overview_report.sh <analysis_ID> <analysis_ID> ...
## Description: This script will set up the overall analysis report directory in an analysis dir
## and compile the reports

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
    echo -e "\noverview_report_template is :\n$overview_report_template"
    echo -e "\nactionable_genes_file is :\n$actionable_genes_file"

    #~~~~~ MAKE ANALYSIS REPORT DIR ~~~~~~#
    overview_report_dir="${analysis_report_parentdir}/analysis_overview_report"

    echo -e "\noverview_report_dir is:\n$overview_report_dir"
    echo -e "\nCreating the report dir..."
    mkdir -p "$overview_report_dir"
    check_dirfile_exists "$overview_report_dir" "d" "Checking to make sure report dir was created successfully..."

    overview_report_IGV_dir="${overview_report_dir}/IGV_snapshots"
    echo -e "\nIGV snapshot dir is:\n$overview_report_IGV_dir\n"
    mkdir -p "$overview_report_IGV_dir"
    check_dirfile_exists "$overview_report_IGV_dir" "d" "Checking to make sure IGV dir was created successfully..."

    #~~~~~ COLLECT REPORT FILES ~~~~~~#
    # get the IGV snapshots
    echo -e "Finding analysis IGV snapshots..."
    IGV_snapshots="$(find "$analysis_outdir" -type f -path "*IGV_snapshots*" -name "*.png" ! -path "*$(basename "$overview_report_dir")*" -exec readlink -f {} \;)"
    echo -e "\nIGV Snapshots found:\n"

    echo -e "\nLinking the IGV snapshots to the report dir..."
    for shot in $IGV_snapshots; do
        (
        cd "$overview_report_IGV_dir"
        ln -fs "$shot"
        )
    done

    # find analysis barcodes file
    echo -e "\nSearching for analysis barcodes file..."
    analysis_barcodes_file="$(find "$analysis_outdir"  -type f -path "*variantCaller_out*" -name "sample_barcode_IDs.tsv" | head -1)"
    analysis_barcodes_file="$(readlink -f "$analysis_barcodes_file")"
    check_dirfile_exists "$analysis_barcodes_file" "f" "Checking to make sure analysis barcodes file was found..."
    echo -e "\nAnalysis barcodes file is:\n$analysis_barcodes_file\n"
    echo -e "\nLinking to the analysis barcodes file..."
    (
    cd "$overview_report_dir"
    ln -fs "$analysis_barcodes_file"
    )


    # write the ID informations to files for the report
    echo -e "\nWriting sample ID information for the report...\n"
    echo "$analysis_ID" > "${overview_report_dir}/analysis_ID.txt"

    # find the analysis full summary table
    # Auto_user_SN2-237-IT17-02-1_295_324_summary.tsv
    echo -e "Searching for the analysis full summary table..."
    analysis_summary_table="$(find "$analysis_outdir" -type f -name "${analysis_ID}*" -name "*_summary.tsv")"
    analysis_summary_table="$(readlink -f "$analysis_summary_table")"
    check_dirfile_exists "$analysis_summary_table" "f" "Checking to make sure analysis summary table was found..."
    echo -e "\nAnalyis summary table is:\n$analysis_summary_table\n"
    echo -e "\nLinking to the summary table..."
    set -x
    analysis_summary_report_file="$(readlink -f $overview_report_dir)/summary_table.tsv"
    ln -fs "$analysis_summary_table" "$analysis_summary_report_file"
    set +x

    # copy over the report template
    echo -e "\nCopying over the report template..."
    check_dirfile_exists "$overview_report_template" "f" "Checking to make sure the report template exists...."
    overview_report_file="${overview_report_dir}/${analysis_ID}_overview_report.Rmd"
    /bin/cp -v "${overview_report_template}" "${overview_report_file}"
    check_dirfile_exists "$overview_report_file" "f" "Checking to make sure report file was copied..."
    echo -e "\nReport file is:\n$overview_report_file\n"

    #~~~~~ COMPILE REPORT ~~~~~~#
    echo -e "\nAttempting to compile the report.."
    set -x
    $compile_report_script "$overview_report_file"
    set +x

    # hardlink the report back to the parent dir
    analysis_report_output="${overview_report_file%%.Rmd}.html"
    if [ -f "$analysis_report_output" ]; then
        ln -f "$analysis_report_output" "${analysis_report_parentdir}/"
    fi





done
