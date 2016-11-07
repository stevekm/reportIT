#!/usr/bin/env python
# python 2.7

# This script will import data from an Excel XLSX file

import pandas as pd
import sys
import os
import errno
import collections

class OrderedDefaultDict(collections.OrderedDict, collections.defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        #in python3 you can omit the args to super
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory



def append_string(string, output_file):
    # append string to file
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')

def initialize_file(string, output_file):
    # write string to file, overwriting contents
    with open(output_file, "w") as myfile:
        myfile.write(string + '\n')


def file_exists(filepath):
    # make sure file exists at filepath
    if os.path.isfile(filepath):
        return True
    elif not os.path.isfile(filepath):
        print "ERROR: File does not exist:\n{}".format(filepath)
        return False

def print_clinical_df(clin_df):
    # column names 
    # Gene  Tumor Type(s)   Tissue Type(s)  Variant(s)  Tier    Interpretations Citations
    # for index, row in xls_df.iterrows(): 
    # for row in xls_df.itertuples():
    for row in xls_df.values.tolist():
        clinical_coment = OrderedDefaultDict()
        clinical_coment["Gene"] = row.pop(0)
        clinical_coment["Tumor_Types"] = row.pop(0)
        clinical_coment["Tissue_Types"] = row.pop(0)
        clinical_coment["Variants"] = row.pop(0)
        clinical_coment["Tier"] = row.pop(0)
        clinical_coment["Interpretations"] = unicode(row.pop(0)).encode('utf8')
        clinical_coment["Citations"] = [unicode(x).encode('utf8') for x in row if "nan" not in unicode(x).encode('utf8') ]
        for key, value in clinical_coment.iteritems():
            if type(value) is list or type(value) is tuple:
                print key + ":"
                for item in value:
                    print item
            else:
                print key + ":", value
        print ""



out_dir = sys.argv[1]
file_name = "/ifs/home/kellys04/projects/clinical_genomic_reporting/reporter_files/data/WC_PMKB_clinical_interpretations/IPM_Knowledgebase_Interpretations_Complete_20161101-0012.xlsx"

# read excel file
xls_file = pd.ExcelFile(file_name)
# load each excel sheet into a dict entry
xls_dict = {sheet_name: xls_file.parse(sheet_name) for sheet_name in xls_file.sheet_names}
# print xls_dict.keys()



# get the first sheet dataframe
xls_df = xls_dict.itervalues().next()
# xls_dict.itervalues().next().to_csv(os.path.join(output_dir, sample + "_av_table.tsv"), sep='\t', index=False)

# peel off the citation colums
cite_df = xls_df.iloc[:, 6:]
# get rid of NaN's
cite_df.fillna('',inplace = True)
# concatenate all row entries with newlines
cite_df = cite_df.apply(lambda row: u"\n".join(map(unicode, row)), axis = 1)
# print cite_df


# remove the excessive newlines from end of line
cite_df = cite_df.map(lambda x: x.rstrip())
# print cite_df.head()
# print cite_df[0]


# merge the two back together
final_df = pd.concat([xls_df.iloc[:,0:6].reset_index(drop = True), cite_df], axis = 1)

# rename the column
final_df.rename(columns = {0 : 'Citation'}, inplace = True)
# print final_df.head()

# need UTF-16 encoding !! 
final_df.to_csv("data/WC_PMKB_clinical_interpretations/comment_files/citations.tsv",sep ='\t', encoding = "utf-16", index = False)





# print_clinical_df(xls_df)
# print xls_df.Gene.unique()

# print xls_df[xls_df['Gene'] == "EGFR"]
# dataframe["period"] = dataframe["Year"].map(str) + dataframe["quarter"]
#.map(str).encode('utf8') + dataframe[:, 6:25].map(str).encode('utf8')
# df['Period'] = df.Year.astype(str).str.cat(df.Quarter.astype(str), sep='q')

# print the row as a bunch of lists
# egfr_df = xls_df[xls_df['Gene'] == "EGFR"]
# print egfr_df["Tier"].astype(unicode).str.cat(egfr_df["Gene"], sep = u'\n')
# print egfr_df.iloc[:,6:25].values.tolist()
