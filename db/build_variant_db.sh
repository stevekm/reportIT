#!/bin/bash
# set -x

## USAGE: build_variant_db.sh /path/to/sqlite3_db.sql <table_name>
## DESCRIPTION: This script will ... ...
## eventually build a database from all analyzed variants


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~# 
source "global_settings.sh"
source "db_functions.sh"

#~~~~~ PARSE ARGS ~~~~~~# 
num_args_should_be "greater_than" "0" "$#"
echo_script_name


sqlite_db="$1"
table_name="$2"
# analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg

echo -e "sqlite_db is:\n$sqlite_db\n"
echo -e "table_name is:\n$table_name\n"

if $(check_for_table "$sqlite_db" "$table_name"); then
    echo -e "SUCCESS: Table $table_name exists in $sqlite_db."
else 
    echo -e "ERROR: Table $table_name does not exist in $sqlite_db."
fi
