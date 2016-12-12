#!/usr/bin/env python
# python 2.7

'''
This script will convert the WC PMKB clinical interpretation Excel file into 
a TSV file formatted for use in the reporting pipeline    

this version of the script has conversion actions that are still under developement

need to split the Variants column apart, and then classify the 
entries by 'Type', 'Codon', 'Exon', etc
'''

import pandas as pd
import numpy as np
import sys
import os
import errno
import collections
import re

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

def split_df_col2rows(dataframe, split_col, split_char, new_colname, delete_old = False, reset_indexes = True):
    # # Splits a column into multiple rows 
    # dataframe : pandas dataframe to be processed
    # split_col : chr string of the column name to be split
    # split_char : chr to split the col on
    # new_colname : new name for the 
    # delete_old : logical True / False, remove original column?
    # ~~~~~~~~~~~~~~~~ # 
    # save the split column as a separate object
    tmp_col = dataframe[split_col].str.split(split_char).apply(pd.Series, 1).stack()
    # drop the last index level
    tmp_col.index = tmp_col.index.droplevel(-1)
    # set the new col name
    tmp_col.name = new_colname
    # remove the original column from the df
    if delete_old is True:
        del dataframe[split_col]
    # join them into a new df 
    new_df = dataframe.join(tmp_col)
    if reset_indexes is True:
        new_df = new_df.reset_index(drop=True)
    return new_df

def split_df_col2cols(dataframe, split_col, split_char, new_colnames, delete_old = False):
    # # Splits a column into multiple columns # # import pandas as pd
    # dataframe : pandas dataframe to be processed
    # split_col : chr string of the column name to be split
    # split_char : chr to split the col on
    # new_colnames : list of new name for the columns
    # delete_old : logical True / False, remove original column?
    # ~~~~~~~~~~~~~~~~ # 
    # save the split column as a separate object
    new_cols = dataframe[split_col].str.split(split_char).apply(pd.Series, 1)
    # rename the cols
    new_cols.columns = new_colnames
    # remove the original column from the df
    if delete_old is True:
        del dataframe[split_col]
    # merge with df
    new_df = dataframe.join(new_cols)
    return new_df


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



# out_dir = sys.argv[1]
file_name = "IPM_Knowledgebase_Interpretations_Complete_20161101-0012.xlsx"

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
cite_df = cite_df.apply(lambda row: u"\n\n".join(map(unicode, row)), axis = 1)
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


# split the tissue type column into separate rows
# final_df = split_df_col2rows(final_df, 'Tissue Type(s)', ",", 'Tissue Type', delete_old = True, reset_indexes = True)

# split Tumor Type(s)
# final_df = split_df_col2rows(final_df, 'Tumor Type(s)', ",", 'Tumor Type', delete_old = True, reset_indexes = True)

#'''
#######
# DEBUGGING !!
import readline # optional, will allow Up/Down/History in the console
import code
vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
shell.interact()

########
#'''


'''
Need to restructure the table 
old col:
'Variant(s)'

new cols:

Variant AAChange 
Variant Codon
Variant Type
'''
# var_str = "CTNNB1 S37Y, CTNNB1 codon(s) 32, 33, 34, 35, 36, 37, 41, 45 any, CTNNB1 any mutation"

# # get the gene for a row
# geneID = final_df['Gene'].iloc[1,]

# # get the variants for the row
# final_df['Variant(s)'].iloc[1,].split(geneID + " ")

# # tmp_col = dataframe[split_col].str.split(split_char).apply(pd.Series, 1).stack()
# tmp_col = final_df['Variant(s)'].iloc[1,].str.split(geneID + " ").apply(pd.Series, 1).stack()

# # list comp to remove '' strings
# new_rows_list = [geneID + " " + i for i in final_df['Variant(s)'].iloc[1,].split(geneID + " ") if i not in '']
# # [geneID + " " + i.replace(', ','') for i in final_df['Variant(s)'].iloc[1,].split(geneID + " ") if i not in '']
# pd.Series(new_rows_list)




# geneID = final_df['Gene'].iloc[1,]
# split_char = geneID + " "
# split_col = 'Variant(s)'
# dataframe = final_df

# # save the split column as a separate object
# tmp_col = dataframe[split_col].str.split(split_char).apply(pd.Series, 1).stack()
# # drop the last index level
# tmp_col.index = tmp_col.index.droplevel(-1)
# # set the new col name
# tmp_col.name = new_colname
# # remove the original column from the df
# if delete_old is True:
#     del dataframe[split_col]
# # join them into a new df 
# new_df = dataframe.join(tmp_col)
# if reset_indexes is True:
#     new_df = new_df.reset_index(drop=True)


def variant2list(geneID, variant_str): # *args, **kwargs
    # split the variant string by Gene ID
    split_char = geneID + " "
    new_variant_list = [split_char + i for i in variant_str.split(split_char) if i not in '']
    return new_variant_list

def df_stack_listcol(df, colname):
    # convert a column of lists into a new row per entry in the list
    return df[colname].apply(pd.Series, 1).stack()

def series_stack_listcol(series, colname):
    # convert a column of lists into a new row per entry in the list
    return series.apply(pd.Series, 1).stack()


# make a Series of variant entries in lists

new_variant_columns = ["Variant AAChange", "Variant Codon", "Variant Type"]

for i in new_variant_columns:
    print i
    final_df[i] = np.nan


new_variant_column = final_df.apply(lambda row: variant2list(row['Gene'], row['Variant(s)']), axis=1)
new_variant_column.name = "New Variants"
# split into separate rows for each list entry
new_variant_column = series_stack_listcol(new_variant_column, "New Variants")
# drop the last index level
new_variant_column.index = new_variant_column.index.droplevel(-1)


final_df = final_df.join(new_variant_column)
# df_stack_listcol(final_df, "New Variants")

######

# need UTF-16 encoding !! For international names in citations
final_df.to_csv("IPMKB_interpretations.tsv",sep ='\t', encoding = "utf-16", index = False)





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
