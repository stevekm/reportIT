#!/bin/bash

# USAGE: move_bams.sh </to/run/dir> </from/bam/dir>

# move all the run bam and bai files from the bam directory to the correct subdirectories
# per barcode in the run

run_dir="$1"
bam_dir="$2"

echo -e "COPYING BAM FILES FROM:\t${bam_dir}"
echo -e "TO:\t${run_dir}\n\n"

bam_files="$(find "$bam_dir" -name '*.bam' -name 'IonXpress_00*')"
bai_files="$(find "$bam_dir" -name '*.bai' -name 'IonXpress_00*')"

echo -e "BAM FILES:\n"
for i in $bam_files; do echo "$i"; done

echo ""

echo -e "BAI FILES:\n"
for i in $bai_files; do echo "$i"; done

echo ""

# for i in ${bam_dir}/IonXpress_00*.ba*; do
for i in $bam_files $bai_files; do
# echo "$i"
barcode="$(echo "$(basename $i)" | sed -e 's/^\(IonXpress_00[[:digit:]]\).*$/\1/g')"
# echo "$barcode"
barcode_dir="${run_dir}/${barcode}"
# echo "$barcode_dir"
mkdir -p "$barcode_dir"
# mv "$i" "${barcode_dir}/"
/bin/cp -v "$i" "${barcode_dir}/"
done

# to reverse... 
# $ find . -type f -name "*.bam" -exec cp -v {} ../tmp_bams/ \;
# $ find . -type f -name "*.bai" -exec cp -v {} ../tmp_bams/ \;