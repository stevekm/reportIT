#!/bin/bash

# move all the run bam and bai files from the bam directory to the correct subdirectories
# per barcode in the run

run_dir="$1"
bam_dir="$2"

for i in ${bam_dir}/IonXpress_00*.ba*; do
echo "$i"
barcode="$(echo "$i" | sed -e 's/^\(IonXpress_00[[:digit:]]\).*$/\1/g')"
echo "$barcode"
barcode_dir="${run_dir}/${barcode}"
echo "$barcode_dir"
mkdir -p "$barcode_dir"
mv "$i" "${barcode_dir}/"
done
