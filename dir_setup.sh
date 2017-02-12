#!/bin/bash

## USAGE: dir_setup.sh
## DESCRIPTION: This script will set up the external directory structure for the reportIT pipeline


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

# dirs to make...
# bin -> ../bin/
# data -> ../reporter_files/data
# input -> ../reporter_files/input
# output -> ../reporter_files/output
echo "Creating external pipeline directories..."
mkdir -p ../reporter_files/data && ln -fs ../reporter_files/data
mkdir -p ../reporter_files/input && ln -fs ../reporter_files/input
mkdir -p ../reporter_files/output && ln -fs ../reporter_files/output

check_dirfile_exists ../reporter_files/data "d" "Checking to make sure data dir was created..."
check_dirfile_exists ../reporter_files/input "d" "Checking to make sure input dir was created..."
check_dirfile_exists ../reporter_files/output "d" "Checking to make sure output dir was created..."

check_dirfile_exists data "l" "Checking to make sure data symlink was created..."
check_dirfile_exists input "l" "Checking to make sure input symlink was created..."
check_dirfile_exists output "l" "Checking to make sure output symlink was created..."



# script to make the bin dir
bin_setup_script="bin_setup.sh"
# make the bin dir
echo "Attempting to create bin dir..."
mkdir -p ../bin && ln -fs ../bin
check_dirfile_exists ../bin "d" "Checking to make sure bin dir was created..."
check_dirfile_exists bin "l" "Checking to make sure bin symlink was created..."

# download and compile bins
echo -e "Setting up binaries in the bin dir..."
(
cd bin
../bin_setup.sh
)

# set up the reference data
echo "Setting up the reference data..."
(
cd ref
./cannonical_transcript_table.py
)
