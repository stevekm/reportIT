#!/bin/bash

## USAGE: test_args.sh data/server_info.txt output foo bar bax baz

server_info_file="$1"
echo "server info file is $server_info_file"

outdir="$2"
echo "Outdir is $outdir"

run_IDs="${@:3}"
for i in $run_IDs; do echo "Run ID is: $i"; done
