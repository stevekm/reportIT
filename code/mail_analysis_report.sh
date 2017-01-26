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

    # custom mail settings
    source "mail_settings.sh"

    local SUBJECT_LINE="IonTorrent Analysis: ${ID} Overview Report"

    echo -e "\nSending email to:\n$recipient_list\n"
    echo -e "\nAttachment file is:\n$attachment_file\n"
    echo -e "\nEmail subject line is:\n$SUBJECT_LINE\n"

    # mutt -s "subject" $( printf -- '-a %q ' *.csv ) ...
    mutt -s "$SUBJECT_LINE" -a "$attachment_file" -- "$recipient_list" <<E0F
Igor tell me if you get this email!!!

IonTorrent Analysis overview report for ${ID} is attached.

~${signature_name}

- This message was sent automatically by the reportIT IonTorrent analysis reporting pipeline -
E0F

}





#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#"
echo_script_name

analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg


#~~~~~ RUN PIPELINE ~~~~~~#
for ID in $analysis_ID_list; do
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

    # email the file!
    mail_analysis_report "$ID" "$analysis_report_file"
done
