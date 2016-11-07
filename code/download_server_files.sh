#!/bin/bash

## USAGE: download_server_files.sh /path/to/server_info_file.txt /path/to/file_list.txt /path/to/outdir

## DESCRIPTION: This script will download files from the IonTorrent server

# server_info_file.txt = text file containing ssh login information; formatted like this:
# $ cat data/server_info.txt
# username@server

# outdir should be the parent outdir since the run folder with be created

server_info_file="$1"
server_file_list="$2"
outdir="$3"

if [[ -z "$outdir" ]]; then 
echo "No outdir supplied" 
echo 'USAGE: download_server_files.sh /path/to/server_info_file.txt /path/to/file_list.txt /path/to/outdir'
echo 'Exiting'
exit
else 
mkdir -p "${outdir}"
fi

# get info from the file
# username@server
server_info="$(head -1 $server_info_file)"

# make sure there is info
if [[ -z "$server_info" ]]; then echo "No info read from file, exiting"; exit; fi


# copy the files
echo "PLEASE LOG INTO SERVER TO GET COPY RUN FILES"
rsync -vzheR --copy-links --progress -e "ssh" --files-from="$server_file_list" ${server_info}:/results/analysis/output/Home/ "${outdir}"
