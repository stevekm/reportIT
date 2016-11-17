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

code/merge_vcf_annotations.py $bfile $qfile $afile
"""

# ~~~~ LOAD PACKAGES ~~~~~~ #
# virtualenv : /ifs/home/kellys04/.local/lib/python2.7/site-packages
import sys
import os
import errno
import pandas as pd # pandas==0.17.1
import numpy as np # numpy==1.11.0


# ~~~~ GET SCRIPT ARGS ~~~~~~ #
# print 'script name is:', sys.argv[0]
# python test.py arg1 arg2 arg3
# print 'Number of arguments:\n', len(sys.argv)
# print 'Argument List:', str(sys.argv)
barcodes_file = sys.argv[1]
query_file = sys.argv[2]
annotation_file = sys.argv[3]

# ~~~~ LOAD TABLES ~~~~~~ #
barcodes_df = pd.read_table(barcodes_file,sep='\t',header=0,na_values=['.'])
query_df = pd.read_table(query_file,sep='\t',header=0,na_values=['.'])
annotation_df = pd.read_table(annotation_file,sep='\t',header=0,na_values=['.'])

# rename the columns for merging
annotation_df = annotation_df.rename(columns = {'Chr':'Chrom', 'Start':'Position', 'Ref':'Ref', 'Alt':'Variant'})
query_df = query_df.rename(columns = {'Chrom':'Chrom', 'Position':'Position', 'Ref':'Ref'})

# merge
merge_df = pd.merge(annotation_df, query_df, on=['Chrom', 'Position', 'Ref', 'Variant'], how = 'left')


'''
need to split the transcripts into separate rows here
'''


# ~~~~ GET SAMPLE BARCODE ID ~~~~~~ #
barcode_ID = os.path.basename(os.path.dirname(query_file))
sample_ID = barcodes_df.loc[barcodes_df['Barcode'] == barcode_ID]['Sample Name'][0]
run_ID = barcodes_df.loc[barcodes_df['Barcode'] == barcode_ID]['Run Name'][0]
print barcode_ID, sample_ID, run_ID

# add sample IDs to table
merge_df['Barcode'] = barcode_ID
merge_df['Sample Name'] = sample_ID
merge_df['Run Name'] = run_ID

print merge_df

