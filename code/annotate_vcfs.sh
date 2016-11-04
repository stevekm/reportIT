#!/bin/bash
# set -x

## USAGE: annotate_vcfs.sh output/run_dir

## Description: This script will find all VCF files in your Run dir and annotate them with ANNOVAR

 
# ~~~~~~ script args ~~~~~~ #
input_dir="$1"

# ANNOVAR version: 
# Version: $Date: 2015-06-17 21:43:53 -0700 (Wed, 17 Jun 2015) $
build_version="hg19"
annovar_db_dir="$(readlink -f "bin/annovar/db")"
convert2annovar_bin="$(readlink -f "bin/annovar/convert2annovar.pl")"
table_annovar_bin="$(readlink -f "bin/annovar/table_annovar.pl")"
annovar_protocol="-protocol refGene,cosmic68,clinvar_20150629,1000g2015aug_all -operation g,f,f,f"
# ~~~~~~~~~~~~ # 


# find VCF files
vcf_files="$(find "$input_dir" -type f -name "*.vcf")"

for i in $vcf_files; do 
vcf_input="$(basename $i)"
file_dir="$(dirname $i)"
avinput_file="$(basename $(dirname $i)).avinput"
avoutput_file="${avinput_file%%.avinput}"
# echo $i

(
    cd $file_dir
    # ls -l
    # convert the VCF to ANNOVAR input format
    # convert2annovar.pl -format vcf4old vcf_input_file -includeinfo > av_output_file
    if [ -f $vcf_input ]; then 
        $convert2annovar_bin -format vcf4old "$vcf_input" -includeinfo > "$avinput_file"
    else
        echo -e "ERROR: VCF input file not found:\n$vcf_input"
        echo "Exiting.."
        exit
    fi
    # run ANNOVAR on the avinput
    if [ -f $avinput_file ]; then
        table_annovar.pl "$avinput_file" "$annovar_db_dir" -buildver "$build_version" -out "$avoutput_file" -remove $annovar_protocol -nastring .
    else
        echo -e "ERROR: AVINPUT file not found:\n$avinput_file"
        echo "Exiting.."
        exit
    fi
) # & 
done




