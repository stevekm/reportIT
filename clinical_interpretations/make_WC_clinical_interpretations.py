#!/usr/bin/env python
# python 2.7

# This script will convert the WC PMKB clinical interpretation Excel file into 
# a TSV file formatted for use in the reporting pipeline    

import pandas as pd
import numpy as np
import sys
import os
import errno
import re




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

# save out TSV file
# need UTF-16 encoding !! For international names in citations
final_df.to_csv("IPMKB_interpretations.tsv",sep ='\t', encoding = "utf-16", index = False)

