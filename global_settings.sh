#!/bin/bash

# This file contains paths and settings to be used by all bash scripts in the pipeline
# this should be 'source'd
#~~~~~ DEFAULT LOCATIONS & ITEMS ~~~~~~#
# path to output directory
outdir="output"

# path to code dir
codedir="code"

samplesheet_dir="samplesheets"

# path to report templates directory
report_template_dir="report"

# file for per sample full report template
full_report_template="${report_template_dir}/full_report.Rmd"

# file for the overall analysis full report
overview_report_template="${report_template_dir}/overview_report.Rmd"

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

#~~~~~ CUSTOM FUNCTIONS ~~~~~~#
if [ -f "${codedir}/custom_bash_functions.sh" ]; then
    source "${codedir}/custom_bash_functions.sh"
elif [ ! -f "${codedir}/custom_bash_functions.sh" ]; then
    echo -e "ERROR: file not found:\n${codedir}/custom_bash_functions.sh"
    echo -e "WARNING: Pipeline might not work correctly unless the file has been sourced from elsewhere"
fi



#~~~~~ DEFAULT SCRIPTS ~~~~~~#
compile_report_script="${codedir}/compile_RMD_report.R"




# ~~~~~~ ANNOTATION PARAMETERS ~~~~~~ #
# ANNOVAR version:
# Version: $Date: 2015-06-17 21:43:53 -0700 (Wed, 17 Jun 2015) $
build_version="hg19"
annovar_db_dir="$(readlink -f bin/annovar/db)"
convert2annovar_bin="$(readlink -f bin/annovar/convert2annovar.pl)"
table_annovar_bin="$(readlink -f bin/annovar/table_annovar.pl)"
annovar_protocol="-protocol refGene,cosmic68,clinvar_20150629,1000g2015aug_all -operation g,f,f,f"
# bcftools-1.3.1
bcftools_bin="$(readlink -f bin/bcftools)"
vcf2tsv_bin="$(readlink -f bin/vcf2tsv)"

# ~~~~~~~~~~~~ # file extensions & naming # ~~~~~~~~~~~~ #
# source VCF file: TSVC_variants.vcf
source_vcf_basename="TSVC_variants.vcf"
# split VCF extensions
split_vcf_ext=".split"
# ANNOVAR converted avinput
avinput_ext=".avinput"
# ANNOVAR annotated output; automatically added by ANNOVAR
annovar_output_ext=".${build_version}_multianno.txt" # .hg19_multianno.txt
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

# current_date="$(date +%Y-%m-%d:%H:%M:%S)"
# ~~~~~~ REPORTING PARAMETERS ~~~~~~ #
# if the 'module' system is installed, try to load the correct versions
if (module)&>/dev/null ; then
    module unload r
    module load r/3.3.0
    module load pandoc/1.13.1
else
    echo "WARNING: 'module' system not found, R and pandoc were not loaded automatically"
fi
