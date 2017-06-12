#!/usr/bin/env python

'''
This script will make a samplesheet for the reportIT pipeline
Make sure to call this from the pipeline parent directory!

Single ID's will be written one per line,
A set of Paired ID's will be written tab-separated on one line

e.g.
$ code/make_samplesheet.py bar baz -p foo1 -p foo2 -n my_samplesheet
Single IDs:
['bar', 'baz']
Paired IDs:
['foo1', 'foo2']
New samplesheet file:
samplesheets/my_samplesheet.tsv

$ cat samplesheets/my_samplesheet.tsv
bar
baz
foo1	foo2

'''
# import sys
import os
import argparse
import pipeline_functions as pl
import global_settings

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #

def main(analysis_IDs, samplesheet_file, analysis_ID_pair = None):
    '''
    Main control function for the program
    '''
    print('Single IDs:')
    print(analysis_IDs)
    print('Paired IDs:')
    print(analysis_ID_pair)
    pl.backup_file(samplesheet_file)
    with open(samplesheet_file, "w") as myfile:
        for item in analysis_IDs:
            myfile.write(item + '\n')
        if analysis_ID_pair != None:
            if len(analysis_ID_pair) == 2:
                myfile.write('\t'.join(analysis_ID_pair) + '\n')
            elif len(analysis_ID_pair) != 2:
                print('ERROR: Number of paired analysis IDs does not equal 2! They will not be written to the samplesheet!')
    print('New samplesheet file:')
    print(samplesheet_file)

def make_default_samplesheet_filepath(samplesheet_dir, name = pl.timestamp()):
    '''
    Make a default samplesheet file path and name
    '''
    samplesheet_dir = global_settings.samplesheet_dir
    samplesheet_file = os.path.join(samplesheet_dir, '{0}.tsv'.format(name))
    return(samplesheet_file)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    samplesheet_dir = global_settings.samplesheet_dir

    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    parser = argparse.ArgumentParser(description='This script will set up a samplesheet for the reportIT pipeline in the "{0}" directory.'.format(samplesheet_dir))

    # a pair of ID's
    parser.add_argument("-p", dest = 'pair', action='append', metavar = 'pair of IDs', help="Paired analysis IDs to add to the sample sheet")

    # optional flags
    parser.add_argument("-n", "--name", default = pl.timestamp(), type = str, dest = 'name', metavar = 'sample name', help="Name to use for the samplesheet file")

    # the rest of the IDs
    parser.add_argument("analysis_IDs", nargs='*', help="ID's of individual analyses to add to the sample sheet")

    # import pdb; pdb.set_trace()
    args = parser.parse_args()

    analysis_IDs = args.analysis_IDs
    analysis_ID_pair = args.pair
    samplesheet_file =  make_default_samplesheet_filepath(samplesheet_dir, name = args.name)

    main(analysis_IDs = analysis_IDs, analysis_ID_pair = analysis_ID_pair, samplesheet_file = samplesheet_file)

if __name__ == "__main__":
    run()
