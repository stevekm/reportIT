#!/usr/bin/env python
# python 2.7


"""
1. Get XLS file (ex: R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1.xls)
2. Find annotated files (ex: IonXpress_001.hg19_multianno.txt)
3. Concatenate annotations to a single table
4. Merge the annotation table with the XLS table
5. Save full merged table
4. Save summary table

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
# get the outdir
outdir = arg_list.pop(0)
# get XLS file from 1st arg
run_xls_file = arg_list.pop(0)
# print "Run XLS:\n", run_xls_file

# empty list to map annotation file with its sample barcode ID
sample_annot_files = []

for arg_n in arg_list[1:]:
    sample_ID = os.path.basename(os.path.dirname(arg_n))
    # print sample_ID, arg_n
    sample_annot_files.append((sample_ID, arg_n))


# read in the raw XLS file
run_xls_df = pd.read_table(run_xls_file,sep='\t',header=0,na_values=['.'])
# get rid of the 'Filter' columns
run_xls_df = run_xls_df[run_xls_df.columns.drop([col for col in run_xls_df.columns if 'Filter' in col])]
# filter out indels because their coordinates don't match VCF 
# Type INS DEL
# print run_xls_df.head(n=50)
run_xls_df = run_xls_df.loc[ (run_xls_df['Type'] != "DEL") & (run_xls_df['Type'] != "INS") ]
print run_xls_df



# concatenate all of the annotation files
# need to add
# Sample Name	Barcode	Run Name
# Frame = Frame.append(pandas.DataFrame(data = SomeNewLineOfData), ignore_index=True)
annotation_df = pd.DataFrame()

for sample_ID, annot_file in sample_annot_files:
    df = pd.read_table(annot_file,na_values=['.'])
    # annotation_df = annotation_df.append(df, ignore_index=True)
    annotation_df = pd.concat([annotation_df, df])

print annotation_df


# av_df.to_csv(os.path.join(output_dir, sample + "_av_table_raw.tsv"), sep='\t', index=False)
annotation_df.to_csv(os.path.join(outdir, "annotation_df.tsv"), sep='\t', index=False)
run_xls_df.to_csv(os.path.join(outdir, "run_xls_df.tsv"), sep='\t', index=False)


