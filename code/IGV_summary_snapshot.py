#!/usr/bin/env python
# python 2.7

# USAGE: $ code/IGV_batchscript_generator.py barcodes_file.txt summary_table.tsv  

'''
this script will load an IonTorrent summary table
parse out the variants to create snapshots of
generate an IGV bat script to run with IGV for making the snapshots
run IGV to create the snapshots

code/IGV_summary_snapshot.py output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/sample_barcode_IDs.tsv output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/coverageAnalysis_out.777 output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/
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


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def get_NC_barcode(run_xls_table):
    # return the barcode of the NC sample; control for IGV snapshots
    # NC_barcode = run_xls_table.loc[run_xls_table['Sample Name'] == 'NC']['Barcode'].unique()[0]
    return NC_barcode





# ~~~~ GET SCRIPT ARGS ~~~~~~ #
# print 'script name is:', sys.argv[0]
# print 'Number of arguments:\n', len(sys.argv)
# print 'Argument List:', str(sys.argv)
barcodes_file = sys.argv[1] # barcodes_file = 'output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/sample_barcode_IDs.tsv'
coverage_dir = sys.argv[2] # location of BAMS
varaints_dir = sys.argv[3] # location of VCFs, annotations, summary tables

# IGV settings
build_version = "hg19"
image_height = "500" 
# 400 = 25 rows


# ~~~~ GET SAMPLE BARCODE ID ~~~~~~ #
barcodes_df = pd.read_table(barcodes_file,sep='\t',header=0,na_values=['.'])

control_sampleID = barcodes_df.loc[barcodes_df['Sample Name'] == 'NC', 'Barcode'].values[0] 
# this breaks if NC not present

print barcodes_df

sys.exit()

outdir = os.path.dirname(annotation_file)


# ~~~~ LOAD TABLES ~~~~~~ #
barcodes_df = pd.read_table(barcodes_file,sep='\t',header=0,na_values=['.'])
query_df = pd.read_table(query_file,sep='\t',header=0,na_values=['.'])
annotation_df = pd.read_table(annotation_file,sep='\t',header=0,na_values=['.'])


# ~~~~ GET SAMPLE BARCODE ID ~~~~~~ #
barcode_ID = os.path.basename(os.path.dirname(query_file))
sample_ID = barcodes_df.loc[barcodes_df['Barcode'] == barcode_ID, 'Sample Name'].values[0]
run_ID = barcodes_df.loc[barcodes_df['Barcode'] == barcode_ID, 'Run Name'].values[0]
