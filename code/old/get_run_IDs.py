#!/usr/bin/env python
# python 2.7



"""
1. Get XLS file (ex: R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1.xls)
2. Get the list of SampleID, Barcode, and RunID (one entry for each)
3. Save it to a file to be used later

outdir="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1"
run_xls="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1.xls"
FILES="$(find output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1 -type f -name "*multianno*")"
code/make_merged_summary_tables.py $outdir $run_xls $FILES


"""


# ~~~~ LOAD PACKAGES ~~~~~~ #
# virtualenv : /ifs/home/kellys04/.local/lib/python2.7/site-packages
import sys
import os
import errno
import pandas as pd # pandas==0.17.1
import numpy as np # numpy==1.11.0
import fnmatch
import re
import subprocess as sp
import csv
import collections
import pickle
import argparse
import zipfile
import gzip


# ~~~~ GET SCRIPT ARGS ~~~~~~ #
# print 'script name is:', sys.argv[0]
# python test.py arg1 arg2 arg3
# print 'Number of arguments:\n', len(sys.argv)
# print 'Argument List:', str(sys.argv)
arg_list = sys.argv
# remove script name
arg_list.pop(0)

# get XLS file from 1st arg
run_xls_file = arg_list.pop(0)

# get the outdir
outdir = os.path.dirname(run_xls_file)
output_file = os.path.join(outdir, "sample_barcode_IDs.txt")

# read in the raw XLS file
run_xls_df = pd.read_table(run_xls_file,sep='\t',header=0,na_values=['.'])

# Sample NameBarcode	Run Name
run_xls_df = run_xls_df[["Sample Name", "Barcode", "Run Name"]]

# remove duplicate records
run_xls_df = run_xls_df.drop_duplicates()

# save to file
run_xls_df.to_csv(output_file, sep='\t', index=False)


