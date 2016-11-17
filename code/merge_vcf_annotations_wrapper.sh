#!/bin/bash
# set -x

## USAGE: merge_vcf_annotations_wrapper.sh output/run_dir

## Description: This script will find parse an annotated run dir, 
## find all files needed to make the merged summary tables, 
## and pass them to the merge_vcf_annotations.py script for merging
 

# qfile="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/IonXpress_001/IonXpress_001_query.tsv"
# afile="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/IonXpress_001/IonXpress_001.hg19_multianno.txt"
# bfile="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/sample_barcode_IDs.tsv"
# tlist="data/hg19/canonical_transcript_list.tsv"
# pgenes="data/panel_genes.txt"
# agenes="data/actionable_genes.txt"

# code/merge_vcf_annotations.py $bfile $qfile $afile $tlist $pgenes $agenes

# ~~~~~~ script args ~~~~~~ #
input_dir="$1"

# ~~~~~~ parameters ~~~~~~ #
# list of canonical transcripts to use; one per line
transcr_file="data/hg19/canonical_transcript_list.tsv"

# genes in the panel
panel_genes_file="data/panel_genes.txt"

# genes considered actionable
actionable_genes_file="data/actionable_genes.txt"

# merge script location
merge_script="$(dirname $0)/merge_vcf_annotations.py"
chmod +x "$merge_script"



# ~~~~~~ Find Barcode file ~~~~~~ #
# sample_barcode_IDs.tsv
barcodes_file="$(find "$input_dir" -type f -name "sample_barcode_IDs.tsv")"
# echo $barcodes_file

# ~~~~~~ Find Sample dirs ~~~~~~ #
# under run dir, parent subdir is variantCaller_out.*
# sample dirs labeled IonXpress_001, IonXpress_002, ... 

sample_dirs="$(find "$input_dir" -type d -path "*variantCaller_out*" -name "IonXpress_*")"

# ~~~~~~ Find Sample files ~~~~~~ #
# need :
# query file; IonXpress_*_query.tsv
# annotation file: IonXpress_*.hg19_multianno.txt

for i in $sample_dirs; do
    samplei="$i"
    # echo $samplei
    query_file="$(find "$samplei" -type f -name "IonXpress_*" -name "*_query.tsv")"
    # echo $query_file
    annot_file="$(find "$samplei" -type f -name "IonXpress_*" -name "*.hg19_multianno.txt")"
    # echo $annot_file
done

