#/usr/bin/env python

'''
Contains copies of settings from 'global_settings.sh'
for use in Python scripts

'''

#~~~~~ DEFAULT LOCATIONS & ITEMS ~~~~~~#
# path to output directory
outdir="output"

# path to code dir
codedir="code"

samplesheet_dir="samplesheets"

# path to report templates directory
report_template_dir="report"

# file for per sample full report template
full_report_template="report/full_report.Rmd"

# file for the overall analysis full report
overview_report_template="report/overview_report.Rmd"

# file containing list of actionable genes
actionable_genes_file="data/actionable_genes.txt"

# list of canonical transcripts to use; one per line
transcr_file="ref/hg19/canonical_transcript_list.txt"

# genes in the panel
panel_genes_file="data/panel_genes.txt"

# file with server login information
server_info_file="data/server_info.txt"

# file with extended regex NC sample ID's
control_sample_regex_file="data/control_sample_regex.txt"

# file with control sample ID's
control_sample_ID_file="data/control_sample_IDs.txt"

igv_bin="bin/IGV_2.3.81/igv.jar"
