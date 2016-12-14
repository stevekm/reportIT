#!/usr/bin/env python
# python 2.7

'''
This script will parse a sample's Summary Table, and 
generate a clinical interpretations comment file 
for use in the sample's report
'''

# ~~~~ LOAD PACKAGES ~~~~~~ #
import pandas as pd
import numpy as np
import sys
import os
import errno
import re
import argparse

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def my_debugger():
    # starts interactive Python terminal at location in script
    # call with my_debugger() anywhere in your script
    import readline # optional, will allow Up/Down/History in the console
    import code
    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()

def initialize_file(string, output_file):
    # write string to file, overwriting contents
    with open(output_file, "w") as myfile:
        myfile.write(string + '\n')

def append_string(string, output_file):
    # append string to file
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')

from unidecode import unidecode
def remove_non_ascii(text):
    return unidecode(unicode(text.encode("utf-16"), encoding = "utf-8"))


def print_clin_comment(gene, tumor_types, tissue_types, variants, tier, interpretations, citations, output_file):
    # 
    append_string("## " + gene, output_file = output_file)
    append_string("### Tumor Types:\n\n" + tumor_types + "\n\n", output_file = output_file)
    append_string("### Tissue Types:\n\n" + tissue_types + "\n\n", output_file = output_file)
    append_string("### Variants:\n\n" + variants + "\n\n", output_file = output_file)
    append_string("### Clinical Interpretation:\n\n" + interpretations + "\n\n", output_file = output_file)
    append_string("### Citations:\n\n" + citations + "\n\n", output_file = output_file)
    # DEBUGGING: trying to convert UTF16 to UTF8 in the script... 
    # append_string("### Clinical Interpretation:\n\n" + remove_non_ascii(interpretations), output_file = output_file)
    # append_string("### Citations:\n\n" + remove_non_ascii(citations), output_file = output_file)
    # append_string("### Clinical Interpretation:\n\n" + interpretations.decode("utf-16",'ignore').encode("utf-8"), output_file = output_file)
    # append_string("### Citations:\n\n" + citations.decode("utf-16",'ignore').encode("utf-8"), output_file = output_file)
    # append_string("### Clinical Interpretation:\n\n" + interpretations.encode("utf-16"), output_file = output_file)
    # append_string("### Citations:\n\n" + citations.encode("utf-16"), output_file = output_file)


# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='This script will create a clinical comment file for use in a sample variant report')

# positional args
parser.add_argument("summary_table_file", help="Path summary table file for the sample")

# optional args
# parser.add_argument("-clin", default = "clinical_interpretations/IPMKB_interpretations.tsv", type = str, dest = 'clin_file', metavar = 'Clinical Interpretations file', help="Path to the Weill Cornell IPMKB clinical interpretations file in TSV format")
parser.add_argument("-clin", default = "clinical_interpretations/IPMKB_interpretations_utf8.tsv", type = str, dest = 'clin_file', metavar = 'Clinical Interpretations file', help="Path to the Weill Cornell IPMKB clinical interpretations file in TSV format")
parser.add_argument("-o", default = "clinical_coments.md", type = str, dest = 'output_file', metavar = 'Comment output file', help="Path the the markdown file to be used as output for the clinical comments found by the script")

args = parser.parse_args()

summary_table_file = args.summary_table_file
clin_file = args.clin_file
output_file = args.output_file


if __name__ == "__main__":
    print summary_table_file
    print clin_file

    summary_df = pd.read_table(summary_table_file)
    # print summary_df

    # clin_df = pd.read_table(clin_file, encoding='utf-16')
    clin_df = pd.read_table(clin_file)
    # print clin_df


    # get list of genes
    gene_list = []
    for gene in summary_df['Gene'].tolist():
        if gene not in gene_list:
            gene_list.append(gene)
    print gene_list

    

    # get the clin comment entries that match the gene list
    clin_match_df = clin_df[clin_df['Gene'].isin(gene_list)] # ['Gene']
    # start initialize the output file
    initialize_file("\n", output_file)
    # write entries to the output file
    clin_match_df.apply(lambda row: print_clin_comment(gene = row['Gene'], 
        tumor_types = row['Tumor Type(s)'], 
        tissue_types = row['Tissue Type(s)'], 
        variants = row['Variant(s)'], 
        tier = row['Tier'], 
        interpretations = row['Interpretations'], 
        citations = row['Citation'], 
        output_file = output_file), axis=1)
    # my_debugger()











