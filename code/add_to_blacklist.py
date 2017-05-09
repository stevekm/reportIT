#!/usr/bin/env python

'''
This script will add variants to a 'blacklist' file based on their variant ID's,
which are found in the analysis overview report

USAGE: add_to_blacklist.py ExampleIonTorrentRun123.IonXpress_002.KRAS.chr12.25398285.c.G34T

ID format:
AnalysisID.Barcode.Gene.Chrom.Pos.c.coding
Analysis ID.Barcode.Gene.Chrom.Position.prefix.Coding
'''
# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def check_list_len(input_list, cutoff, mode = "min", kill = False):
    '''
    Check to make sure a list meets length criteria
    '''
    import sys
    pass_test = True
    list_len = len(input_list)
    if mode == "min":
        if list_len < int(cutoff):
            print("ERROR: List is length {0}, and is below cutoff value of {1}".format(list_len, cutoff))
            pass_test = False
    if pass_test != True:
        if kill == True:
            print('Exiting...')
            sys.exit()

def parse_variant_ID(variant_ID):
    '''
    Return a dictionary of field names & values for the items in the variant ID
    Field name should correspond to summary table header fields
    '''
    keys = ['Analysis ID', 'Barcode', 'Gene', 'Chrom', 'Position', 'prefix', 'Coding']
    split_ID = variant_ID.split('.')
    check_list_len(split_ID, 6, kill = True)
    ID_dict = {}
    for key, value in zip(keys, split_ID):
        ID_dict[key] = value
    return(ID_dict)


# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    variant_IDs = []
    for ID in sys.argv[1:]:
        variant_IDs.append(ID)
    for ID in variant_IDs:
        print(parse_variant_ID(ID))
