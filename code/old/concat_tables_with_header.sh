#!/bin/bash
# set -x

## USAGE: concat_tables_with_header.sh /path/to/output_file.tsv <input_file_1> <input_file_2> ... <input_file_n>

## Description: This script will concatenate a list of tab separated tables
## which share a common header on the first line
## WARNING: This will probably NOT work with filenames with spaces

## WARNING: CURRENT IMPLEMENTATION OVERWRITES FIRST FILE IF OUTFILE IS FORGOTTEN THIS IS BAD CHANGE THIS!
#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#" # "less_than", "greater_than", "equal"
echo_script_name

# output location
output_file="$1"
output_dir="$(dirname "$output_file")"

# get the rest of the args as file inputs
file_list="${@:2}" # accept a space separated list of ID's

# process the header from the first file in the list
# file_header="$(head -1 $(echo $file_list | cut -d ' ' -f 1))"
# file to save the header to
# file_header_file="${output_dir}/tmp_header"

touch "$output_file"
if [ -f "$output_file" ]; then
    # head -1 $(echo $file_list | cut -d ' ' -f 1) > "$output_file"
    for i in $file_list; do
        check_dirfile_exists "$i" "f"
        # tail -n +2 "$i" >> "$output_file"
    done
else
    echo -e "ERROR: Temp header file could not be created:\n${file_header_file}\nExiting..."
    exit
fi

echo -e "Table written to file:\n$output_file\n"

# exit
# awk -v header="$file_header" '
#     FNR==1 && NR!=1 { while (/^header/) getline; }
#     1 {print}
# ' $file_list 
# >all.txt