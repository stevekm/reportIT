#!/bin/bash

## USAGE: get_server_run_list.sh /path/to/server_info_file.txt

## DESCRIPTION: This script will print out a list of the most recent runs on the IonTorrent server

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

server_info_file="$1"

# get info from the file
server_info="$(head -1 $server_info_file)"

# make sure there is info
if [[ -z "$server_info" ]]; then echo "No info read from file, exiting"; exit; fi

# get the latest runs
ssh $server_info << EOF
    ls -1tr /results/analysis/output/Home | tail -10
EOF
