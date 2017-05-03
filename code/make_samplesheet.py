#!/usr/bin/env python

'''
This script will make a samplesheet for the reportIT pipeline
Make sure to call this from the pipeline parent directory!
e.g.
code/make_samplesheet.py
'''
import sys
import os
import argparse
import pipeline_functions as pl
import csv
import datetime

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #

# ~~~~ DEFAULT SETTINGS ~~~~~~ #
samplesheet_dir = "samplesheets"

# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='This script will set up a samplesheet for the reportIT pipeline.')

# a pair of ID's
parser.add_argument("-p", dest = 'pair', action='append', metavar = 'pair of IDs', help="Paired analysis IDs to add to the sample sheet") # nargs='2',

# optional flags
parser.add_argument("-n", "--name", default = pl.timestamp(), type = str, dest = 'name', metavar = 'sample name', help="Name to use for the samplesheet file")

# the rest of the IDs
parser.add_argument("analysis_IDs", nargs='+', help="ID's of individual analyses to add to the sample sheet")

# import pdb; pdb.set_trace()
args = parser.parse_args()

# print(args)
analysis_IDs = args.analysis_IDs
analysis_ID_pair = args.pair
# analysis_ID_pair = ['bar', 'baz']
samplesheet_file = os.path.join(samplesheet_dir, '{0}.tsv'.format(args.name))

if __name__ == "__main__":
    print('Single IDs:')
    print(analysis_IDs)
    print('Paired IDs:')
    print(analysis_ID_pair)
    print('Samplesheet file:')
    print(samplesheet_file)
    with open(samplesheet_file, "w") as myfile:
        for item in analysis_IDs:
            # print(item)
            myfile.write(item + '\n')
        if analysis_ID_pair != None:
            if len(analysis_ID_pair) == 2:
                myfile.write('\t'.join(analysis_ID_pair) + '\n')
