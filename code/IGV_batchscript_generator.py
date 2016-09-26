#!/usr/bin/env python
# python 2.7


# this script will load an IonTorrent summary table
# parse out the variants to create snapshots of
# generate an IGV bat script to run with IGV for making the snapshots
# run IGV to create the snapshots

# # this will probably require X11 installation on connected computer ??


# # sample IGV script
# new
# snapshotDirectory /ifs/home/kellys04/projects/clinical_genomic_reporting/reporter_files/output/R_2016_07_28_15_04_57_user_SN2-182-IT16-034/IGV_snapshot
# load /ifs/home/kellys04/projects/clinical_genomic_reporting/reporter_files/output/R_2016_07_28_15_04_57_user_SN2-182-IT16-034/bam/IonXpress_002_R_2016_07_28_15_04_57_user_SN2-182-IT16-034_Auto_user_SN2-182-IT16-034_233.bam
# genome hg19
# maxPanelHeight 2000
# goto chr11:108138003-108138003
# snapshot
# goto chr9:21971111-21971111
# snapshot
# goto chr17:7577548-7577548
# exit

# $ bin/IGV_2.3.81/igv.sh -b code/IGV_test.bat
# (Xvfb :10 &) && DISPLAY=:10 java -Xmx750m -jar bin/IGV_2.3.81/igv.jar -b code/IGV_test.bat && killall Xvfb
# Xvfb - virtual framebuffer X server for X Version 11


# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys
import os
import errno
import pandas as pd
import subprocess as sp
import collections



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
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
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')


# find the VCF files in the input dir
# for subdir, dirs, files in os.walk(input_dir):
#     for file in files:
#     	if file.endswith('.vcf'):
# 			raw_vcf_paths.append((os.path.join(subdir,file)))

# raw_vcf_paths.sort()


# ~~~~ GET SCRIPT ARGS ~~~~~~ #

run_dir = "/ifs/home/kellys04/projects/clinical_genomic_reporting/reporter_files/output/R_2016_07_28_15_04_57_user_SN2-182-IT16-034"
summary_table_file = run_dir + "/summary_table.tsv"
run_bam_dir = run_dir + "/bam"
build_version = "hg19"
image_height = "2000"
# run_snapshot_dir = mkdir_p(run_dir + "/IGV_snapshots", return_path = True)
# IGV_batch_file = run_dir + "/igv_snapshot_script2.bat"


# ~~~~ RUN PIPELINE ~~~~~~ #

# make a default dict for the samples in the run
samples_dict = collections.defaultdict(dict)

# load summary table
summary_df = pd.read_table(summary_table_file)

# get the coordinates from the table per barcode per run
for run_name in summary_df['Run_Name'].unique():
    # samples_dict[run_name]
    for barcode in summary_df['Barcode'].unique():
        print barcode
        # set locations and dirs for the sample
        IGV_batch_file = run_dir + "/IGV_snapshots_" + barcode + ".bat"
        print IGV_batch_file
        snapshot_dir = mkdir_p(run_dir + "/" + barcode + "/IGV_snaptshots", return_path = True)
        print snapshot_dir
        # get the rows from the df that match the Run and Sample name
        subset_df = summary_df.loc[ (summary_df['Run_Name'] == run_name ) &
        (summary_df['Barcode'] == barcode ), ["Chrom", "Position"] ]
        # make a list of the unique entries to be printed
        locations = subset_df[['Chrom','Position', 'Position']].apply(lambda x : '{}:{}-{}'.format(x[0],x[1], x[2]), axis=1).unique()
        # start the IGV script
        append_string("new", IGV_batch_file)
        append_string("snapshotDirectory " + snapshot_dir, IGV_batch_file)
        append_string("load ", IGV_batch_file) # <- NEED BAM HERE
        append_string("genome " + build_version, IGV_batch_file)
        append_string("maxPanelHeight " + image_height, IGV_batch_file)
        for location in locations: #  loc_len < len(locations) + 1:
            print type(location)
            append_string("goto " + location, IGV_batch_file)
            append_string("snapshot", IGV_batch_file)
        append_string("exit", IGV_batch_file)


print IGV_batch_file


# print summary_df['Barcode'].unique()
# print summary_df['Run_Name'].unique()

# Sample_Name
# Barcode
# Run_Name


# output_handle = open(output_file, "a")
#     SeqIO.write(record, output_handle, "fasta")
#     output_handle.close()





