#!/bin/bash
set -x

## USAGE: annotate_vcfs.sh /path/to/output/analysis_dir

## Description: This script will find all VCF files in your Run dir and annotate them with ANNOVAR
## This script is set up to use Ion Torrent 5.0 VCF's

#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#"
echo_script_name

input_dir="$1"
echo -e "Input directory is:\n$input_dir\n"




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

# ~~~~~~~~~~~~ # find VCF files # ~~~~~~~~~~~~ #
echo -e "Searching for VCF files in directory:\n$input_dir"
vcf_files="$(find "$input_dir" -type f -name "$source_vcf_basename")"

# ~~~~~~~~~~~~ # Split multi-alt entries in VCF files # ~~~~~~~~~~~~ #
echo -e "\nSplitting multi-allele variant entries in VCF files\n"
for i in $vcf_files; do
    vcf_input="$i"
    file_dir="$(dirname $i)"
    vcf_split_output="${file_dir}/${source_vcf_basename}${split_vcf_ext}"
    echo -e "Processing file:\n$vcf_input"
    $bcftools_bin norm -m-both "$vcf_input" -o "$vcf_split_output"
done

# get VCF file list with new split VCFs
echo -e "Getting new list of processed VCF files for pipeline..."
split_vcf_files="$(find "$input_dir" -type f -name "${source_vcf_basename}${split_vcf_ext}")"


# ~~~~~~~~~~~~ # Annotate with ANNOVAR # ~~~~~~~~~~~~ #
echo -e "\nAnnotating VCF with ANNOVAR\n"
for i in $split_vcf_files; do
    vcf_input="$i"
    file_dir="$(dirname $i)"
    barcode_ID="$(basename $(dirname $i))"
    avinput_file="${file_dir}/${barcode_ID}${avinput_ext}"
    avoutput_file="${avinput_file%%$avinput_ext}" # ANNOVAR provides own extension !!

    # convert the VCF to ANNOVAR input format
    echo -e "\nConverting to ANNOVAR format\n"
    if [ -f $vcf_input ]; then
        # [ ! -f $avinput_file ] &&
        $convert2annovar_bin -format vcf4old "$vcf_input" -includeinfo -outfile "$avinput_file" # -comment
    else
        echo -e "ERROR: VCF input file not found:\n$vcf_input"
        echo "Exiting.."
        exit
    fi

    # run ANNOVAR on the avinput
    echo -e "Running ANNOVAR on file:\n$avinput_file"
    if [ -f $avinput_file ]; then
        # [ ! -f ${avoutput_file}.hg19_multianno.txt ] &&
        $table_annovar_bin "$avinput_file" "$annovar_db_dir" -buildver "$build_version" -out "$avoutput_file" -remove $annovar_protocol -nastring .
    else
        echo -e "ERROR: AVINPUT file not found:\n${avinput_file}"
        echo "Exiting.."
        exit
    fi

    # ~~~~~~~~~~~~ # Rebuild a standard VCF file from the ANNOVAR avinput # ~~~~~~~~~~~~ #
    # ANNOVAR corrects some features, such as indel notation, which we want in the output
    # while retaining the VCF metadata
    # the new VCF file
    rebuilt_vcf_file="${avinput_file}${rebuilt_ext}"
    # copy the header from the original VCF
    grep '^#' "$vcf_input" > "$rebuilt_vcf_file"
    # add the extra fields from the avinput file
    cut -f6- "$avinput_file" >> "$rebuilt_vcf_file"
done



# ~~~~~~~~~~~~ # Query VCF for fields # ~~~~~~~~~~~~ #
# reset list of VCF files to use the rebuilt VCFs
rebuilt_vcf_files="$(find "$input_dir" -type f -name "*${rebuilt_ext}")"

for i in $rebuilt_vcf_files; do
    file_dir="$(dirname $i)"
    barcode_ID="$(basename $(dirname $i))"
    vcf_input="$i"
    query_output_file="${file_dir}/${barcode_ID}${query_ext}"
    if [ -f $vcf_input ]; then
        echo -e "Running bcftools on:\n${vcf_input}\nOutputting to:\n${query_output_file}\n"
        echo -e 'You can probably ignore "contig is not defined in the header" messages...'
        echo -e "Chrom\tPosition\tRef\tVariant\tQuality\tFrequency\tCoverage\tAllele Coverage\tStrand Bias" > "$query_output_file"
        $bcftools_bin query -f '%CHROM\t%POS\t%REF\t%ALT\t%QUAL\t%AF\t%FDP\t%FAO\t%STB\n' "$vcf_input" >> "$query_output_file"
        # sanity tests
        [ ! -f $query_output_file ] && echo -e "ERROR: File not created properly:\n${query_output_file}\nExiting.." && exit
        query_len="$(tail -n +2 ${query_output_file} | wc -l)"; # echo "query_len is $query_len"
        vcf_len="$(cat $vcf_input | grep -Ev '^#' | wc -l)"; # echo "vcf_len is $vcf_len"
        [ ! $query_len -eq $vcf_len ] && echo 'ERROR: number of variants in TSV does not match VCF, EXITING' && exit
    else
        echo -e "ERROR: VCF input file not found:\n$vcf_input"
        echo "Exiting.."
        exit
    fi
done

# ~~~~~~~~~~~~ # Convert VCF to TSV # ~~~~~~~~~~~~ #
for i in $rebuilt_vcf_files; do
    file_dir="$(dirname $i)"
    barcode_ID="$(basename $(dirname $i))"
    vcf_input="$i"
    tsv_output_file="${file_dir}/${barcode_ID}${tsv_ext}"
    if [ -f $vcf_input ]; then
        echo -e "Converting VCF to TSV:\n${vcf_input}\n${tsv_output_file}\n"
        $vcf2tsv_bin "$vcf_input" > "$tsv_output_file"
        [ ! -f $tsv_output_file ] && echo -e "ERROR: TSV file not created properly;\n${tsv_output_file}" && exit
        tsv_len="$(tail -n +2 ${tsv_output_file} | wc -l)"; # echo "tsv_len is $tsv_len"
        vcf_len="$(cat $vcf_input | grep -Ev '^#' | wc -l)"; # echo "vcf_len is $vcf_len"
        [ ! $tsv_len -eq $vcf_len ] && echo 'ERROR: number of variants in TSV does not match VCF, EXITING' && exit
    else
        echo -e "ERROR: VCF input file not found:\n$vcf_input"
        echo "Exiting.."
        exit
    fi
done
