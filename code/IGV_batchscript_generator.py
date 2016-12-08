#!/usr/bin/env python
# python 2.7

'''
USAGE: code/IGV_batchscript_generator.py 
DESCRITPION: Generate IGV batch script for creating snapshots of BAMs PER SAMPLE
based on the sample's summary table of variants

# files needed:
# sample BAM
# sample BAI
# IGV batch file output
# IGV snapshot dir
# build version
# image height
# sample summary table
# OPTIONAL: control bam
'''

# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys
import os
import re
import errno
import glob
import pandas as pd
import subprocess as sp
import collections
import argparse


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def write_IGV_script(IGV_batch_file, IGV_snapshot_dir, bam_file, build_version, image_height, locations, Control_bam_file = False):
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
    if Control_bam_file:
        append_string("load " + Control_bam_file, IGV_batch_file)
    append_string("genome " + build_version, IGV_batch_file)
    append_string("maxPanelHeight " + image_height, IGV_batch_file)
    for location in locations: 
        append_string("goto " + location, IGV_batch_file)
        append_string("snapshot", IGV_batch_file)
    append_string("exit", IGV_batch_file)

def initialize_file(string, output_file):
    # write string to file, overwriting contents
    with open(output_file, "w") as myfile:
        myfile.write(string + '\n')

def append_string(string, output_file):
    # append string to file
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')

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



# ~~~~ GET SCRIPT ARGS ~~~~~~ #
'''
# argparse example
parser = argparse.ArgumentParser(description='IGV snapshot batchscript generator.')
parser.add_argument("input_files", nargs=2, help="Path to input files; vcf.zip and xls.zip IonTorrent run files")
parser.add_argument("-o", default = './output', type = str, dest = 'output', metavar = '/OUTPUT_DIR', help="Path to output directory. Defaults to ./output")
parser.add_argument("-b", default = 'hg19', type = str, dest = 'build_version', metavar = 'build version', help="Build version. Name of the reference genome, Defaults to hg19")
parser.add_argument("-dd", default = './data', type = str, dest = 'data_dir', metavar = 'data dir', help="Path to data directory. Defaults to the ./data")
parser.add_argument("-pg", default = './data/panel_genes.txt', type = str, dest = 'panel_genes_file', metavar = 'panel genes file' , help="Path to panel genes file. Defaults to ./data/panel_genes.txt")
parser.add_argument("-ag", default = './data/actionable_genes.txt', type = str, dest = 'actionable_genes_file', metavar = 'actionable genes file', help="Path to actionable genes file. Defaults to ./data/actionable_genes.txt")
parser.add_argument("-sf", default = './data/summary_fields.txt', type = str, dest = 'summary_fields_file', metavar = 'summary fields file', help="Path to summary fields file. Defaults to ./data/summary_fields.txt")
parser.add_argument("-id", dest = 'run_id', metavar = 'run ID', help="Run ID value. Defaults to the portion of the input filename preceeding the first '.' character ")
args = parser.parse_args()

outdir = args.output
input_files = args.input_files # vcf.zip and xls.zip IonTorrent run files
build_version = args.build_version
data_dir = args.data_dir
panel_genes = list_file_lines(args.panel_genes_file)
actionable_genes = list_file_lines(args.actionable_genes_file)
summary_cols = list_file_lines(args.summary_fields_file)
'''

summary_table_file = sys.argv[1]
bam_file = sys.argv[2]
IGV_snapshot_dir = sys.argv[3]
NC_bam = False # the control bam file

build_version = "hg19"
image_height = "500" 
IGV_batch_file = os.path.join(IGV_snapshot_dir,"IGV_script.bat")
mkdir_p(IGV_snapshot_dir)

print "Sumamry table file is:", summary_table_file
print "Bam file is:", bam_file
print "IGV_snapshot_dir is:", IGV_snapshot_dir
print "IGV_batch_file is:", IGV_batch_file



# load summary table
summary_df = pd.read_table(summary_table_file)

# make a list of the unique entries to be printed
locations = summary_df[['Chrom','Position', 'Position']].apply(lambda x : '{}:{}-{}'.format(x[0],x[1], x[2]), axis=1).unique()
print locations

# sys.exit()

# start the IGV script
write_IGV_script(IGV_batch_file = IGV_batch_file, 
    IGV_snapshot_dir = IGV_snapshot_dir, 
    bam_file = bam_file, 
    build_version = build_version, 
    image_height = image_height, 
    locations = locations, 
    Control_bam_file = NC_bam)