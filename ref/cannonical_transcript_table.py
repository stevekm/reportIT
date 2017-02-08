#!/usr/bin/env python
# python 2.7

# need to get the UCSC Known Canonical Transcripts
# UCSC transcripts with unique ID's (also available for hg38) (UCSC_id) from here:
# http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/knownCanonical.txt.gz
# need to match 5th col ID's with RefGene ID's (Ref_id) from here:
# http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/kgXref.txt.gz
# # as per this dicussion
# # https://groups.google.com/a/soe.ucsc.edu/forum/#!topic/genome/_6asF5KciPc


import sys
import os
import argparse
import urllib2
import urlparse
import pipeline_functions as pl

def create_crossreference_tables(crossref_file, canon_file, outdir, replace_values_dict = None):
    import pandas as pd

    # colnames to use for the cross ref dataframe
    cross_cols = ['UCSC_id', 'B', 'C', 'D', 'Gene', 'Ref_id', 'G', 'Description', 'I']
    crossref_df = pd.read_table(crossref_file,sep='\t', header = None, index_col=False, names = cross_cols)
    # get list of UCSC ID's for canonical transcripts
    canon_cols = ['Chrom', 'Start', 'Stop', 'Num', 'UCSC_id']
    canon_df = pd.read_table(canon_file,sep='\t', header = None, index_col=False, names = canon_cols)

    # list of UCSC ID's for canonical transcripts
    canon_ucsc_list = canon_df['UCSC_id'].tolist()

    # get the RefId's for the transcripts that have a matching UCSC ID in the canonical transcripts list
    # save to file
    canon_ref_list = crossref_df[crossref_df['UCSC_id'].isin(canon_ucsc_list)]['Ref_id'].dropna().tolist()


    output_path = os.path.join(outdir, "canonical_transcript_list.txt")
    with open(output_path, "a") as myfile:
        for item in canon_ref_list:
            # replace bad ID's if they've been passed in the dict
            if replace_values_dict != None:
                if item in replace_values_dict.keys():
                    item = replace_values_dict[item]
            myfile.write("%s\n" % item)

# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='Canonical Transcript table creation script')

parser.add_argument("-b", default = "hg19", type = str, dest = 'build_version', help="Reference genome build version")

parser.add_argument("-cnf", default = "knownCanonical.txt", type = str, dest = 'canon_file', help="Canonical transcript file")
parser.add_argument("-crf", default = "kgXref.txt", type = str, dest = 'crossref_file', metavar = "Cross reference file")

parser.add_argument("-cnu", default = "http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/knownCanonical.txt.gz", type = str, dest = 'canon_URL', help="Canonical transcript URL")
parser.add_argument("-cru", default = "http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/kgXref.txt.gz", type = str, dest = 'crossref_URL', metavar = "Cross reference URL")

parser.add_argument("-o", default = ".", type = str, dest = 'outdir', metavar = "Parent outdir")
parser.add_argument("-r", default = "IDs_to_replace.csv", type = str, dest = 'IDs_to_replace', metavar = "A CSV formatted list of transcript IDs to replace, one per line. Format: <old ID>,<new ID>")


args = parser.parse_args()

build_version = args.build_version

canon_file = args.canon_file
crossref_file = args.crossref_file
canon_URL = args.canon_URL
crossref_URL = args.crossref_URL

parent_outdir = args.outdir
# make path to the output for the build version
outdir = os.path.abspath(os.path.join(parent_outdir, build_version))

IDs_to_replace_file = args.IDs_to_replace


if __name__ == "__main__":
    # make outdir
    pl.mkdir_p(outdir, return_path=True)

    # download the URL files to the new location
    crossref_outfile = os.path.join(outdir, os.path.basename(urlparse.urlsplit(crossref_URL).path))
    pl.download_file(crossref_URL, my_outfile = crossref_outfile)
    # unzip the file
    crossref_file = pl.gz_unzip(crossref_outfile, return_path = True)

    # pl.my_debugger(globals().copy())

    canon_outfile = os.path.join(outdir, os.path.basename(urlparse.urlsplit(canon_URL).path))
    pl.download_file(canon_URL, my_outfile = canon_outfile)
    canon_file = pl.gz_unzip(canon_outfile, return_path = True)

    # check if a list of ID's to replace is present
    if os.path.exists(IDs_to_replace_file):
        replace_values_dict = pl.dict_from_tabular(IDs_to_replace_file)
    else:
        replace_values_dict = None

    create_crossreference_tables(crossref_file, canon_file, outdir, replace_values_dict = replace_values_dict)
