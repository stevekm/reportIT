#!/usr/bin/env python
# python 2.7

'''
This is a quick test script to split some columns in the WC IPMKB sheet

'''


import pandas as pd
import numpy as np
import sys
import os
import errno
import re


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

columns = ['Tumor Type(s)',  'Tissue Type(s)']

new_df = pd.DataFrame(xls_df, columns = columns)

new_df = split_df_col2rows(new_df, 'Tissue Type(s)', ", ", 'Tissue Type', delete_old = True, reset_indexes = True)
new_df = split_df_col2rows(new_df, 'Tumor Type(s)', ", ", 'Tumor Type', delete_old = True, reset_indexes = True)

print new_df
new_df.to_csv("IPMKB_tumor_tissue_types.tsv",sep ='\t', index = False)








