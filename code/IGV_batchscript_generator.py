#!/usr/bin/env python
# python 2.7


# this script will load an IonTorrent summary table
# parse out the variants to create snapshots of
# generate an IGV bat script to run with IGV for making the snapshots
# run IGV to create the snapshots


# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys
import os
import re
import errno
import glob
import pandas as pd
import subprocess as sp
import collections



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def subprocess_cmd(command):
    # run a terminal command with stdout piping enabled
    process = sp.Popen(command,stdout=sp.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

def mkdir_p(path, return_path=False):
    # make a directory, and all parent dir's in the path
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    if return_path:
        return path

def append_string(string, output_file):
    # append string to file
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')

def initialize_file(string, output_file):
    # write string to file, overwriting contents
    with open(output_file, "w") as myfile:
        myfile.write(string + '\n')


def file_exists(filepath):
    # make sure file exists at filepath
    if os.path.isfile(filepath):
        return True
    elif not os.path.isfile(filepath):
        print "ERROR: File does not exist:\n{}".format(filepath)
        return False

def check_file_list(files):
    # make sure only 1 file is present in the list
    if len(files) == 1:
        return True
    elif len(files) > 1:
        print "WARNING: multiple files found:\n"
        for file in files: print file
        return False
    elif len(files) < 1: 
        print "WARNING: no files found"
        return False

def find_sample_bam(samplename, sampledir):
    # find the correct bam file in the dir
    res = glob.glob(sampledir + '/{}*.bam'.format(samplename))
    # make sure only 1 item returned, and it exists
    if check_file_list(res) and file_exists(res[0]):
        return res[0]

def write_IGV_script(IGV_batch_file, IGV_snapshot_dir, bam_file, build_version, image_height, locations):
    # generate an IGV script for batch processing
    # IGV_batch_file : file the script will be written to
    # IGV_snapshot_dir : dir to hold the snapshots that will be created
    # bam_file : bam file to be used; bai file must be present as well!
    # build_version : reference genome to use e.g. hg19, mm10, etc.
    # image_height : height of the snapshot image
    # locations : a list of the chromosome locations in the format ['chr9:21971111-21971111', 'chr9:21971111-21971111', ... etc. ]
    initialize_file("new", IGV_batch_file)
    append_string("snapshotDirectory " + IGV_snapshot_dir, IGV_batch_file)
    append_string("load " + bam_file, IGV_batch_file) 
    append_string("genome " + build_version, IGV_batch_file)
    append_string("maxPanelHeight " + image_height, IGV_batch_file)
    for location in locations: 
        append_string("goto " + location, IGV_batch_file)
        append_string("snapshot", IGV_batch_file)
    append_string("exit", IGV_batch_file)


def run_IGV_script(igv_script, igv_jar = "bin/IGV_2.3.81/igv.jar", memMB = "750"):
    # run the IGV script
    subprocess_cmd("(Xvfb :10 &) && DISPLAY=:10 java -Xmx{}m -jar {} -b {} && killall Xvfb".format(memMB, igv_jar, igv_script))

# ~~~~ GET SCRIPT ARGS ~~~~~~ #

run_dir = sys.argv[1]

summary_table_file = os.path.join(run_dir, "summary_table.tsv")
build_version = "hg19"
image_height = "2000"


# ~~~~ RUN PIPELINE ~~~~~~ #
# make a default dict for the samples in the run
# samples_dict = collections.defaultdict(dict)

# load summary table
summary_df = pd.read_table(summary_table_file)

# get the coordinates from the table per barcode per run
for run_name in summary_df['Run_Name'].unique():
    # samples_dict[run_name]
    for barcode in summary_df['Barcode'].unique():
        barcode_dir = os.path.join(run_dir, barcode)
        print barcode
        # set locations and dirs for the sample
        # 
        bam_file = find_sample_bam(barcode, barcode_dir)
        print bam_file
        #
        IGV_snapshot_dir = os.path.join(barcode_dir, "IGV_snapshots")
        mkdir_p(IGV_snapshot_dir)
        print IGV_snapshot_dir
        #
        IGV_batch_file = os.path.join(IGV_snapshot_dir,"IGV_script_" + barcode + ".bat")
        print IGV_batch_file
        #
        # get the rows from the df that match the Run and barcode
        subset_df = summary_df.loc[ (summary_df['Run_Name'] == run_name ) &
        (summary_df['Barcode'] == barcode ), ["Chrom", "Position"] ]
        # make a list of the unique entries to be printed
        locations = subset_df[['Chrom','Position', 'Position']].apply(lambda x : '{}:{}-{}'.format(x[0],x[1], x[2]), axis=1).unique()
        # start the IGV script
        write_IGV_script(IGV_batch_file, IGV_snapshot_dir, bam_file, build_version, image_height, locations)
        run_IGV_script(IGV_batch_file)


print IGV_batch_file




