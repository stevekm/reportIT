#!/bin/bash

## USAGE: mail_analysis_report.sh <analysis_ID> <analysis_ID> <analysis_ID> ...

## DESCRIPTION: This script will mail an analysis overview report
## for all analyses

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"


function mail_analysis_report {
    # function args
    local ID="$1"
    error_on_zerolength "$ID" "TRUE" "Checking that an analysis ID was passed... "

    local attachment_file="$2"
    check_dirfile_exists "$attachment_file" "f" "Checking to make sure attachment file exists..."

    local barcodes_file="$3"
    local summary_file="$4"

    local file_fullpath="$(readlink -f "$attachment_file")"
    local file_basename="$(basename "$attachment_file")"
    local summary_file_basename="$(basename "$summary_file")"
    local file_owner="$(ls -ld "$attachment_file" | awk '{print $3}')"
    local file_date="$(ls -l --time-style=long-iso "$attachment_file" | awk '{print $6 " " $7}')"

    # custom mail settings
    source "mail_settings.sh"

    local SUBJECT_LINE="IonTorrent Analysis: ${ID} Overview Report"

    echo -e "\nEmail recipient list:\n$recipient_list\n"
    echo -e "\nAttachment file is:\n$attachment_file\n"
    echo -e "\nEmail subject line is:\n$SUBJECT_LINE\n"

    # cat - <<E0F
    mutt -s "$SUBJECT_LINE" -a "$attachment_file" -a "$summary_file" -- "$recipient_list" <<E0F

IonTorrent Analysis overview report is attached: $file_basename
IonTorrent Analysis variant summary table is attached: $summary_file_basename

Analysis ID:
${ID}

Report date:
$file_date

Report created by:
$file_owner

System location:
$file_fullpath

$(cat $barcodes_file)

$message_footer

E0F

}





#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#"
echo_script_name

analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg


#~~~~~ RUN PIPELINE ~~~~~~#
for ID in $analysis_ID_list; do
    (
    echo -e "\n-----------------------------------\n"
    echo -e "Analyis is:\n$ID\n"

    analysis_outdir="${outdir}/${ID}"
    echo -e "\nAnalysis outdir is:\n$analysis_outdir\n"
    check_dirfile_exists "$analysis_outdir" "d" "Making sure the analysis dir exists..."

    analysis_reports_dir="${analysis_outdir}/reports"
    echo -e "\nAnalysis reports dir is:\n$analysis_reports_dir\n"
    check_dirfile_exists "$analysis_reports_dir" "d" "Making sure the analysis reports dir exists..."

    echo -e "\nSearching for analysis overview report..."
    analysis_report_file="$(find "$analysis_reports_dir" -type f -type f -name "*_overview_report.html" -exec readlink -f {} \; | tail -n +1 | head -1)"
    check_dirfile_exists "$analysis_report_file" "f" "Making sure the analysis report was found..."
    echo -e "\nAnalysis report file is:\n$analysis_report_file\n"

    # find the analysis barcodes file
    echo -e "Searching for analysis barcodes file..."
    analysis_barcodes_file="$(find "$analysis_outdir" -path "*variantCaller*" -name "sample_barcode_IDs.tsv" | head -1)"
    check_dirfile_exists "$analysis_barcodes_file" "f" "Making sure the analysis barcode file exists..."

    # find the analysis summary sheet
    echo -e "Now searching for the analysis summary file..."
    analysis_summary_file="$(find "$analysis_outdir" -name "*${ID}*" -name "*_summary.tsv")"
    check_dirfile_exists "$analysis_summary_file" "f" "Making sure the analysis summary file exists..."

    # email the file!
    mail_analysis_report "$ID" "$analysis_report_file" "$analysis_barcodes_file" "$analysis_summary_file"
    )
done
