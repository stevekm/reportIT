#!/bin/bash
# set -x

## USAGE: build_variant_db.sh /path/to/output.db <table_name> <input1.tsv> <input2.tsv> ...
## DESCRIPTION: This script will import all given files into a common SQLite database
## all imported files must share the TSV format and have a common header
## WARNING: output.db and all intermediary files will be overwritten!


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~# 
source "global_settings.sh"
source "db_functions.sh"
source "custom_bash_functions.sh"


function initialize_db {
    local sqlite_db="$1"
    local table_name="$2"
    local first_input_file="$3"

cat > main.sql <<E0F
.mode tabs
.import ${first_input_file} ${table_name}
E0F
# .dump
sqlite3 "$sqlite_db" < main.sql
}


function append_to_db {
    local sqlite_db="$1"
    local table_name="$2"
    local input_file="$3"
    local tmp_output="tmp"
    
    # need to strip header for appended files
    tail -n +2 "$input_file" > "$tmp_output"
cat > append.sql <<E0F
.mode tabs
.import ${tmp_output} ${table_name}
E0F
    sqlite3 "$sqlite_db" < append.sql
    # tail -n +2 $input_file | sqlite3 foo.sqlite '.imp "/dev/stdin" "foo"'
}

#~~~~~ PARSE ARGS ~~~~~~# 
num_args_should_be "greater_than" "2" "$#"
echo_script_name


sqlite_db="$1"
table_name="$2"
input_data_file_list="${@:3}" # accept a space separated list of files starting at the third arg


echo -e "sqlite_db is:\n$sqlite_db\n"
echo -e "table_name is:\n$table_name\n"


# delete the file if it already exists
[ -f "$sqlite_db" ] && echo -e "File exists:\n$sqlite_db\nDeleting..." && rm -rf "$sqlite_db"

#~~~~~~~~~~~~~~~~~~~~~~# 
#import first file with header
first_input_file="$(echo $input_data_file_list | cut -d ' ' -f 1)"
echo -e "First file for import to db is:\n$first_input_file\n"
initialize_db "$sqlite_db" "$table_name" "$first_input_file"


#~~~~~~~~~~~~~~~~~~~~~~# 
# import the rest of the files
input_files="$(echo $input_data_file_list | cut -d ' ' -f 2-)"

# tmp_output="tmp"
for input_file in $input_files; do
    echo "$input_file"
    append_to_db "$sqlite_db" "$table_name" "$input_file"
done





