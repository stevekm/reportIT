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
    local zipfile="$5"
    local vcf_zipfile="$6"
    local tables_zip="$7"

    local file_fullpath="$(readlink -f "$attachment_file")"
    local file_basename="$(basename "$attachment_file")"
    local summary_file_basename="$(basename "$summary_file")"
    local file_owner="$(ls -ld "$attachment_file" | awk '{print $3}')"
    local file_date="$(ls -l --time-style=long-iso "$attachment_file" | awk '{print $6 " " $7}')"
    local git_branch="$(git rev-parse --abbrev-ref HEAD)"
    local git_commit="$(git rev-parse HEAD)"
    local sys_hostname="$(hostname)"

    # custom mail settings
    source "mail_settings.sh"

    local SUBJECT_LINE="IonTorrent Analysis: ${ID} Overview Report"

    echo -e "\nEmail recipient list:\n$recipient_list\n"
    echo -e "\nAttachment file is:\n$attachment_file\n"
    echo -e "\nEmail subject line is:\n$SUBJECT_LINE\n"

    mutt -s "$SUBJECT_LINE" -a "$attachment_file" -a "$summary_file" -a "$zipfile" -a "$vcf_zipfile" -a "$tables_zip" -- "$recipient_list" <<E0F

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

System:
$sys_hostname

Pipeline code current git branch and commit version:
$git_branch
$git_commit

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
    # analysis_summary_file="$(find "$analysis_outdir" -name "*${ID}*" -name "*_summary.tsv")"
    analysis_summary_file="$(find "$analysis_outdir" -name "*${ID}*" -name "*_summary_version.tsv")"
    check_dirfile_exists "$analysis_summary_file" "f" "Making sure the analysis summary file exists..."

    # find the analysis overview IGV snapshot dir
    # output/Auto_user_SN2-248-IT17-08-1_306_335/reports/analysis_overview_report/IGV_snapshots/
    echo "Now searching for the IGV snapshot dir..."
    analysis_IGV_dir="$(find "$analysis_outdir" -type d -path "*reports/analysis_overview_report*" -name "IGV_snapshots")"
    check_dirfile_exists "$analysis_IGV_dir" "d" "Making sure the IGV snapshot dir exists..."
    # zipfile="${analysis_IGV_dir}.zip"
    zipfile="$(dirname "$analysis_IGV_dir")/${ID}_$(basename "${analysis_IGV_dir}").zip"
    zip -r "$zipfile" "$analysis_IGV_dir"
    check_dirfile_exists "$zipfile" "f" "Making sure the IGV snapshot zip was created..."

    # find all VCF files for the run
    echo "Now searching for the VCF files..."
    vcf_zipfile="${analysis_outdir}/${ID}_vcf.zip"
    find "${analysis_outdir}" -type f -name "*.vcf" | xargs zip "$vcf_zipfile"
    check_dirfile_exists "$vcf_zipfile" "f" "Making sure the VCF zip was created..."

    # find all variant tables from the run
    echo "Now searching for variant tables..."
    tables_zip="${analysis_outdir}/${ID}_tables.zip"
    find "${analysis_outdir}" -type f -name "*${ID}*" -name "*.tsv" | xargs zip "$tables_zip"
    check_dirfile_exists "$tables_zip" "f" "Making sure the variant table zip was created..."


    # email the files!
    mail_analysis_report "$ID" "$analysis_report_file" "$analysis_barcodes_file" "$analysis_summary_file" "$zipfile" "$vcf_zipfile" "$tables_zip"
    )
done
