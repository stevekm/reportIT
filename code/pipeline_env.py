#!/usr/bin/env python
# python 2.7

'''
functions for Python scripts in the reporting pipeline
'''

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
    # # Splits a column into multiple columns 
    # dataframe : pandas dataframe to be processed
    # split_col : chr string of the column name to be split
    # split_char : chr to split the col on
    # new_colnames : list of new name for the columns
    # delete_old : logical True / False, remove original column?
    # ~~~~~~~~~~~~~~~~ # 
    # save the split column as a separate object
    new_cols = dataframe[split_col].str.split(split_char).apply(pd.Series, 1)
    '''
    # PROBLEM: after split, there might be fewer columns! 
    # add extra empty columns to fill..
    for i in range(len(new_cols.columns)):
        print new_cols.columns[i]
        print new_colnames[i]
        new_cols.rename(columns = {new_cols.columns[i]:new_colnames[i]}, inplace = True)
    new_colnames_df = pd.DataFrame(columns=new_colnames)
    # pd.concat([df,pd.DataFrame(columns=list('BCD'))])
    pd.concat([new_colnames_df, new_cols])
    ....
    ...
    '''
    # rename the cols
    new_cols.columns = new_colnames
    # remove the original column from the df
    if delete_old is True:
        del dataframe[split_col]
    # merge with df
    new_df = dataframe.join(new_cols)
    return new_df

def list_file_lines(file_path):
    # return the list of entries in a file, one per line
    # not blank lines, no trailing \n
    with open(file_path, 'r') as f:
        entries = [line.strip() for line in f if line.strip()]
    return entries

def custom_table_filter(dataframe, 
    gene_func_include = ['Func.refGene', 'exonic'], 
    exonic_func_remove = ['ExonicFunc.refGene', 'synonymous SNV'], 
    maf_cutoff_upper = ['1000g2015aug_all', 0.01],
    strand_bias_cutoff_upper = ['Strand Bias', 0.8], 
    frequency_cutoff_lower = ['Frequency', .05],
    coverage_cutoff_lower = ['Coverage', 250]): 
    # apply filters to the df
    filtered_df = dataframe.loc[ ( dataframe[gene_func_include[0]] == gene_func_include[1] ) 
    & ( dataframe[exonic_func_remove[0]] != exonic_func_remove[1] ) 
    & ( ( dataframe[maf_cutoff_upper[0]] < maf_cutoff_upper[1] ) | pd.isnull(dataframe[maf_cutoff_upper[0]]) ) 
    & ( dataframe[strand_bias_cutoff_upper[0]] < strand_bias_cutoff_upper[1]) 
    & ( dataframe[frequency_cutoff_lower[0]] > frequency_cutoff_lower[1]) 
    & ( dataframe[coverage_cutoff_lower[0]] > coverage_cutoff_lower[1])
    ]
    return filtered_df

def test_canonical_transcripts(df, canon_trancr_list):
    # check to make sure that only canonical transcript ID's are in the df
    for transcript in  df['Transcript'].tolist():
        transcript = str(transcript)
        # print transcript
        if not transcript in canon_trancr_list:
            print "ERROR: Transcript in table is not in the canonical transcript list:\n" + transcript
            print "Exiting..."
            sys.exit()

def test_filtered_genes(df, unique_genes_list):
    # test to make sure that all unique genes are in the table
    for gene in table_genes:
        gene = str(gene)
        if not gene in merge_df['Gene'].tolist():
            print "ERROR: Gene was not present in the table after filtering:\n" + gene
            print "Did the gene lack a canonical transcript? Better check!"
            print "Exiting..."
            sys.exit()

def find_vcf_timestamp(vcf_file):
    ##fileUTCtime=2016-09-23T16:46:51
    with open(vcf_file) as f:
        for line in f:
            if "fileUTCtime" in line:
                return line.strip().split("=")[1]


def my_debugger():
    # starts interactive Python terminal at location in script
    # call with my_debugger() anywhere in your script
    import readline # optional, will allow Up/Down/History in the console
    import code
    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()

