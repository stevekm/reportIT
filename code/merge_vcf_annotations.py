#!/usr/bin/env python
# python 2.7


"""
1. Get VCF Query and Annotation files (IonXpress_008_query.tsv, IonXpress_008.hg19_multianno.txt), and sample_barcode_IDs.tsv
2. Merge the VCF and Annotation tables
3. Split the Annotaton transcript fields into separate rows
4. Add sample ID, barcode, and run fields
5. Save full merged table


code/make_merged_summary_tables.py $outdir $run_xls $FILES

qfile="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/IonXpress_001/IonXpress_001_query.tsv"
afile="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/IonXpress_001/IonXpress_001.hg19_multianno.txt"
bfile="output/R_2016_09_01_14_26_55_user_SN2-192-IT16-039-1/Auto_user_SN2-192-IT16-039-1_243_275/plugin_out/variantCaller_out.778/sample_barcode_IDs.tsv"
tlist="data/hg19/canonical_transcript_list.tsv"
pgenes="data/panel_genes.txt"
agenes="data/actionable_genes.txt"

code/merge_vcf_annotations.py $bfile $qfile $afile $tlist $pgenes $agenes
"""

# ~~~~ LOAD PACKAGES ~~~~~~ #
# virtualenv : /ifs/home/kellys04/.local/lib/python2.7/site-packages
import sys
import os
import errno
import pandas as pd # pandas==0.17.1
import numpy as np # numpy==1.11.0


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
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


# ~~~~ GET SCRIPT ARGS ~~~~~~ #
# print 'script name is:', sys.argv[0]
# print 'Number of arguments:\n', len(sys.argv)
# print 'Argument List:', str(sys.argv)
barcodes_file = sys.argv[1]
query_file = sys.argv[2]
annotation_file = sys.argv[3]
canon_trancr_file = sys.argv[4]
panel_genes_file = sys.argv[5]
actionable_genes_file = sys.argv[6]

canon_trancr_list = list_file_lines(canon_trancr_file)
panel_genes = list_file_lines(panel_genes_file)
actionable_genes = list_file_lines(actionable_genes_file)
outdir = os.path.dirname(annotation_file)
# Summary Table Fields:
summary_cols = ["Chrom", "Position", "Ref", "Variant", "Gene", "Quality", "Coverage", "Allele Coverage", "Strand Bias", "Coding", "Amino Acid Change", "Transcript", "Frequency", "Sample Name", "Barcode", "Run Name", "Review"]



# ~~~~ LOAD TABLES ~~~~~~ #
barcodes_df = pd.read_table(barcodes_file,sep='\t',header=0,na_values=['.'])
query_df = pd.read_table(query_file,sep='\t',header=0,na_values=['.'])
annotation_df = pd.read_table(annotation_file,sep='\t',header=0,na_values=['.'])



# ~~~~ GET SAMPLE BARCODE ID ~~~~~~ #
barcode_ID = os.path.basename(os.path.dirname(query_file))
sample_ID = barcodes_df.loc[barcodes_df['Barcode'] == barcode_ID, 'Sample Name'].values[0]
run_ID = barcodes_df.loc[barcodes_df['Barcode'] == barcode_ID, 'Run Name'].values[0]


# ~~~~ PROCESS & MERGE TABLES ~~~~~~ #
# rename the columns for merging
annotation_df = annotation_df.rename(columns = {'Chr':'Chrom', 'Start':'Position', 'Ref':'Ref', 'Alt':'Variant', 'Gene.refGene':'Gene'})

query_df = query_df.rename(columns = {'Chrom':'Chrom', 'Position':'Position', 'Ref':'Ref'})

# merge
merge_df = pd.merge(annotation_df, query_df, on=['Chrom', 'Position', 'Ref', 'Variant']) # , how = 'left'

# split the AAChange rows in the table
merge_df = split_df_col2rows(dataframe = merge_df, split_col = 'AAChange.refGene', split_char = ',', new_colname = 'AAChange', delete_old = True)

# split the new columns into separate columns
merge_df = split_df_col2cols(dataframe = merge_df, split_col = 'AAChange', split_char = ':', new_colnames = ['Gene.AA', 'Transcript', 'Exon', 'Coding', 'Amino Acid Change'], delete_old = True)

# the merged fields:
# Chrom Position    End Ref Variant Func.refGene    Gene.refGene    GeneDetail.refGene  
# ExonicFunc.refGene  cosmic68    clinvar_20150629    1000g2015aug_all    
# Quality Allele Frequency    Coverage    Allele Coverage Strand Bias Gene    
# Transcript  Exon    Coding  Amino Acid Change   Barcode Sample Name Run Name



# ~~~~ FILTER TABLE ~~~~~~ #
'''
merge table: 
filter for only canon transcripts # canon_trancr_list
filter for desired variant qualities

summary table: 
filter for desired columns
'''

# get the list of unique genes in the table
table_genes = merge_df.Gene.unique()

# keep only canonical transcripts
merge_df = merge_df[merge_df['Transcript'].isin(canon_trancr_list)]

# sanity check:
# make sure only canonical transcripts passed the filter
test_canonical_transcripts(merge_df, canon_trancr_list)
# make sure that all unique genes are represented after filtering for canonical transcripts
test_filtered_genes(merge_df, table_genes)



# add sample IDs to table
merge_df['Barcode'] = barcode_ID
merge_df['Sample Name'] = sample_ID
merge_df['Run Name'] = run_ID


# keep only the panel genes; default Unknown Significance
# panel_genes
merge_df = merge_df[merge_df["Gene"].isin(panel_genes)]


# actionable_genes
# add review; Known Signficance, Unknown Significance ; panel genes
# default is Unknown Signficiance
merge_df['Review'] = 'US'
# change actionable genes to Known Signficance
merge_df.loc[merge_df["Gene"].isin(actionable_genes), 'Review'] = "KS"

# !! need tests for these ^^ 

# make a copy of the complete table before filtering for qualities
full_df = merge_df

# filter for qualities
merge_df = custom_table_filter(merge_df)

# make the summary table; filter columns
summary_df = merge_df[summary_cols]



# ~~~~ SAVE TABLES ~~~~~~ #
summary_file = os.path.join(outdir, barcode_ID + "_summary.tsv")
summary_df.to_csv(summary_file, sep='\t', index=False)
print "Summary table saved to:\n" + summary_file + "\n"

full_table_file = os.path.join(outdir, barcode_ID + "_full_table.tsv")
full_df.to_csv(full_table_file, sep='\t', index=False)
print "Full table saved to :\n" + full_table_file + "\n"


merge_file = os.path.join(outdir, barcode_ID + "_filtered.tsv")
merge_df.to_csv(merge_file, sep='\t', index=False)
print "Merged table saved to:\n" + merge_file + "\n"

# sys.exit()
