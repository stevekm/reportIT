#!/bin/bash

## USAGE: get_server_run_list.sh

## DESCRIPTION: This script will print out a list of the most recent runs on the IonTorrent server

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

#~~~~~ PARSE ARGS ~~~~~~# 
# if (( $# != 1 )); then
#     echo "ERROR: Wrong number of arguments supplied"
#     grep '^##' $0
#     exit
# fi
echo -e "Now running script:\n${0}"

# server_info_file="$1"
server_info_file="data/server_info.txt"
echo -e "Server info file is:\n$server_info_file"
# make sure its actually a file
[ ! -f $server_info_file ] && echo -e "ERROR: File not recognized:\n${1}\n\nExiting..." && exit

# get info from the file
echo -e "Getting data from server info file..."
server_info="$(head -1 $server_info_file)"

# make sure there is info
if [[ -z "$server_info" ]]; then echo "No info read from file, exiting"; exit; fi
echo -e "Data read from server info file..."

echo -e "Now attempting server login..."
# get the latest runs
echo -e "\nPLEASE LOG INTO SERVER TO GET RUN ANALYSIS LIST\n"
ssh $server_info << EOF
    ls -1tr /results/analysis/output/Home | tail -20
EOF
