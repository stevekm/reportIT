#!/usr/bin/env python

'''
This script will add variants to a 'blacklist' file based on their variant ID's,
which are found in the analysis overview report
All of the old entries will be read in, new entries will be parsed from script args,
and all entries will be written back out

- hard-backup will be made of old blacklist file if present
- only unique entries will be written out

USAGE: add_to_blacklist.py ExampleIonTorrentRun123.IonXpress_002.KRAS.chr12.25398285.c.G34T

ID format in:
AnalysisID.Barcode.Gene.Chrom.Pos.c.coding
Analysis ID.Barcode.Gene.Chrom.Position.prefix.Coding

File output:
$ cat blacklisted_variants/blacklisted_variants.tsv
Analysis ID	Barcode	Gene	Chrom	Position	Coding
ExampleIonTorrentRun123	IonXpress_002	KRAS	chr12	25398285	c.G34T
ExampleIonTorrentRun123	IonXpress_002	TP53	chr17	7574012	c.G1015T
ExampleIonTorrentRun123	IonXpress_006	TP53	chr17	7577539	c.C742T
'''
# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys
import os
import pipeline_functions as pl


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

def get_blacklist_entries(blacklist_file):
    '''
    Get all the current entries in the blacklist file
    '''
    import csv
    import os
    entries = []
    if os.path.isfile(blacklist_file):
        with open(blacklist_file) as infile:
            reader = csv.DictReader(infile, delimiter='\t')
            for row in reader:
                entries.append({key: value for key, value in row.items()})
    return(entries)

def write_blacklist_entries(dict_list, keys, blacklist_file):
    '''
    Write all of the blacklist entries to the file
    '''
    import csv
    with open(blacklist_file, 'wb') as outfile:
        write_out = csv.DictWriter(outfile, delimiter='\t', fieldnames = keys)
        write_out.writeheader()
        write_out.writerows(dict_list)

def parse_variant_ID(variant_ID, keys):
    '''
    Return a dictionary of field names & values for the items in the variant ID
    Field name should correspond to summary table header fields
    Also coding field (e.g. 'c.G34T') gets split apart so need to re-merge it
    '''
    split_ID = variant_ID.split('.')
    check_list_len(split_ID, len(keys), kill = True)
    ID_dict = {}
    for key, value in zip(keys, split_ID):
        ID_dict[key] = value
    # re-merge the 'prefix' and 'Coding' fields to a single field again
    if 'prefix' in ID_dict.keys() and 'Coding' in ID_dict.keys():
        prefix = ID_dict.pop('prefix')
        ID_dict['Coding'] = '.'.join([prefix, ID_dict['Coding']])
    return(ID_dict)


# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    # ~~~~ KEYS ~~~~~~ #
    variant_keys_for_splitting = ['Analysis ID', 'Barcode', 'Gene', 'Chrom', 'Position', 'prefix', 'Coding']
    variant_keys_for_writing = ['Analysis ID', 'Barcode', 'Gene', 'Chrom', 'Position', 'Coding']
    # ~~~~ BLACKLIST FILE ~~~~~~ #
    blacklist_dir = pl.mkdir_p("blacklisted_variants", return_path = True)
    blacklist_file = os.path.join(blacklist_dir, "blacklisted_variants.tsv")
    blacklist_entries = get_blacklist_entries(blacklist_file)
    pl.backup_file(blacklist_file)
    # ~~~~ GET NEW VARIANTS ~~~~~~ #
    variant_IDs = []
    variant_dict_list = []
    for ID in sys.argv[1:]:
        variant_IDs.append(ID)
    for ID in variant_IDs:
        variant_dict_list.append(parse_variant_ID(ID, keys = variant_keys_for_splitting))
    for entry in blacklist_entries:
        if entry not in variant_dict_list:
            variant_dict_list.append(entry)
    # ~~~~ WRITE NEW FILE ~~~~~~ #
    write_blacklist_entries(variant_dict_list, keys = variant_keys_for_writing, blacklist_file = blacklist_file)
