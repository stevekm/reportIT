#/usr/bin/env python

'''
Contains copies of settings from 'global_settings.sh'
for use in Python scripts
make sure to keep these up to date with 'global_settings.sh'
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



# ~~~~~~ ANNOTATION PARAMETERS ~~~~~~ #
# ANNOVAR version:
# Version: $Date: 2015-06-17 21:43:53 -0700 (Wed, 17 Jun 2015) $
build_version="hg19"


# ~~~~~~ REMOTE IONTORRENT SERVER LOCATION NAMES AND PATTERNS ~~~~~~ #
# e.g. a path to remote IT server results looks like this:
# /results/analysis/output/Home/Auto_user_SN2-282-IT17-26-1_375_368/plugin_out/coverageAnalysis_out.1070/IonXpress_001
# ^^ this is the coverage output dir (.bam, .bai) for a single sample

# /results/analysis/output/Home/Auto_user_SN2-282-IT17-26-1_375_368/plugin_out/variantCaller_out.1071/IonXpress_001
#
# ^^ this is the coverage output dir (.vcf) for a single sample

# path to the 'Home' directory on the IonTorrent remote server that holds the
# run output results
IT_server_results_home_dir="/results/analysis/output/Home"

# subdir name prefix for IT results dir that hold the coverege files for all samples; .bam and .bai files
IT_coverage_dir_name_pattern="coverageAnalysis_out"
# same but for the variant calling output
IT_variant_dir_name_pattern="variantCaller_out"
# subdir basename pattern for each sample on the IonTorrent output coverage and variant dirs
IT_sample_results_dir_name_pattern="IonXpress"



# source VCF file name on the remote IonTorrent server: TSVC_variants.vcf
source_vcf_basename="TSVC_variants.vcf"



# ~~~~~~~~~~~~ # file extensions & naming # ~~~~~~~~~~~~ #
# split VCF extensions
split_vcf_ext=".split"
# ANNOVAR converted avinput
avinput_ext=".avinput"
# ANNOVAR annotated output; automatically added by ANNOVAR
annovar_output_ext=".{0}_multianno.txt".format(build_version) # .hg19_multianno.txt
# rebuilt VCF file from ANNOVAR avinput
rebuilt_ext=".rebuilt"
# VCF field query tables
query_ext="_query.tsv"
# VCF converted to TSV
tsv_ext=".tsv"

## NOTE: These are hardcoded in merge_vcf_annotations.py
# variant summary table
summary_table_ext="_summary.tsv"
# variant table without summary criteria (not actually filtered why is it called that??)
filtered_table_ext="_filtered.tsv"
# full table with all variants and all fields
full_table_ext="_full_table.tsv"

# summary table with version control information
summary_version_ext="_summary_version.tsv"
