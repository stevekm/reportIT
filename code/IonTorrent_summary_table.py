#!/usr/bin/env python
# python 2.7


# ~~~~ LOAD PACKAGES ~~~~~~ #
# virtualenv : /ifs/home/kellys04/.local/lib/python2.7/site-packages
import sys
import os
import errno
import pandas as pd
import numpy as np
import fnmatch
import re
import subprocess as sp
import csv
import collections
import pickle
import argparse


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def mkdir_p(path, return_path=False):
    # make a directory, and all parent dir's in the path
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    if return_path:
        return path

def subprocess_cmd(command):
    # run a terminal command with stdout piping enabled
    process = sp.Popen(command,stdout=sp.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

def get_file_path(search_dir='.',name='',path='', more=''):
    # find files in a given path using terminal 'find'
    filepath = [line for line in sp.check_output("find {} -name '{}' -path '{}'{}".format(search_dir,name,path,more), shell=True).splitlines()]
    return filepath[0] # return first result


def unzip_input_files(path):
    # find and unzip all .zip, .gz files
    subprocess_cmd('cd "{}" && find . -name "*.zip" -exec unzip -n {{}} \; && $(for file in *.gz; do [ ! -f "${{file%%.gz}}" ] && gunzip "$file"; done)'.format(path))


def convert_2_annovar(vcf_input_file, av_output_file):
  # convert a VCF file to ANNOVAR format
    if not os.path.exists(av_output_file) and not os.path.isfile(av_output_file):
        subprocess_cmd('convert2annovar.pl -format vcf4old {} -includeinfo > {}'.format(vcf_input_file,av_output_file))


def annovar_table(avinput, annovar_output, annovar_db_dir="/ifs/home/kellys04/software/annovar/db", build_version="hg19", annovar_protocol="-protocol refGene,cosmic68,clinvar_20150629,1000g2015aug_all -operation g,f,f,f"
):
    # run ANNOVAR table command
    # avinput : file path to avinput
    # annovar_output : file path to annovar output
    #  --otherinfo # http://annovar.openbioinformatics.org/en/latest/user-guide/startup/
    file_suffix = '.' + build_version + '_multianno.txt'
    output_file = annovar_output + file_suffix
    if not os.path.exists(output_file) and not os.path.isfile(output_file):
        print "\nRunning ANNOVAR annotation on:\n", avinput
        subprocess_cmd('table_annovar.pl {} {} -buildver {} -out {} -remove {} -nastring .'.format(avinput, annovar_db_dir, build_version, annovar_output, annovar_protocol))
    # file.endswith('multianno.txt') # TSVC_variants_IonXpress_015_filtered.hg19_multianno.txt
    output_path = get_file_path(search_dir=os.path.dirname(output_file), name='*{}*'.format(os.path.basename(output_file)), path='*')
    print "\nAnnotated file is:\n", output_path
    return output_path


def vcf_header_skip(file_path):
    # count the number of header lines to be skipped in the VCF file
    skip_rows = 0
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('##'):
                skip_rows += 1
            else:
                break
    return skip_rows

def vcf_qual_filter(vcf_table, qual_score = 250):
    # apply quality filter to vcf table
    filtered_table = vcf_table.loc[vcf_table['QUAL'] > qual_score]
    return filtered_table


def av_table_filter(av_table, gene_func = "exonic", exonic_func_remove = "synonymous SNV", maf_cutoff = 0.01):
    # filter ANNOVAR table
    filtered_table = av_table.loc[ (av_table['ExonicFunc.refGene'] != exonic_func_remove) & ((av_table['1000g2015aug_all'] < maf_cutoff) | pd.isnull(av_table['1000g2015aug_all'])) & (av_table['Func.refGene'] == gene_func) ]
    return filtered_table

def xls_table_filter(xls_table, strand_bias_cutoff = 0.8, frequency_cutoff = 5):
    # filter XLS table
    filtered_table = xls_table.loc[ (xls_table['Strand Bias'] < strand_bias_cutoff) & (xls_table['Frequency'] > frequency_cutoff)]
    return filtered_table

def key0(data):
    # return the first key in the data; convenience function for code truncation
    key_0 = data.keys()[0]
    return key_0

def val0(data):
    # return the first value in the data; convenience function for code truncation
    value0 = data.values()[0]
    return value0

def custom_table_filter(dataframe, gene_func_include = ['Func.refGene', 'exonic'], 
    exonic_func_remove = ['ExonicFunc.refGene', 'synonymous SNV'], maf_cutoff_upper = ['1000g2015aug_all', 0.01],
    strand_bias_cutoff_upper = ['Strand Bias', 0.8], frequency_cutoff_lower = ['Frequency', 5]): 
    # apply filters to the df
    filtered_df = dataframe.loc[ ( dataframe[gene_func_include[0]] == gene_func_include[1] ) &
    ( dataframe[exonic_func_remove[0]] != exonic_func_remove[1] ) &
    ( ( dataframe[maf_cutoff_upper[0]] < maf_cutoff_upper[1] ) | pd.isnull(dataframe[maf_cutoff_upper[0]]) ) &
    ( dataframe[strand_bias_cutoff_upper[0]] < strand_bias_cutoff_upper[1]) &
    ( dataframe[frequency_cutoff_lower[0]] > frequency_cutoff_lower[1]) ]
    return filtered_df


def save_pydata(data, outfile):
    # save py data in pickle format
    with open(outfile, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        print 'Object saved to file:\n', outfile



def load_pydata(infile):
    # open py pickle data
    with open(infile, 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        data = pickle.load(f)
        return data

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

def av_df_fixcolnames(av_df):
    # # reformat the ANNOVAR dataframe for merging
    # Bad:Good
    fix_colnames = {'Ref':'Ref', 'Alt':'Variant', 'Chr':'Chrom', 'Start':'Position'}
    # replace the bad colnames with the good ones for merging
    for i in range(0,len(fix_colnames)):
        bad_colname = fix_colnames.keys()[i]
        good_colname = fix_colnames[fix_colnames.keys()[i]]
        av_df = av_df.rename(columns = {bad_colname:good_colname})
    # make sure they are all caps for merging
    av_df['Ref'] = av_df['Ref'].str.upper()
    av_df['Variant'] = av_df['Variant'].str.upper()
    return av_df

def partial_reorder_list(old_list, reference_list, verbose = False):
    # put the entries in the reference list at the front of the old list, if present
    if verbose is True:
        print '\nOld list contents:\n', old_list
    i = 0
    for entry in reference_list:
        if entry in old_list:
            old_list.insert(i, old_list.pop(old_list.index(entry)))
            i += 1
    if verbose is True:
        print '\nNew list contents:\n', old_list
    return old_list

def list_file_lines(file_path):
    # return the list of entries in a file, one per line
    # not blank lines, no trailing \n
    with open(file_path, 'r') as f:
        entries = [line.strip() for line in f if line.strip()]
    return entries

def shell_unzip(file, outdir = '.'):
    # unzip a file with the shell command
    subprocess_cmd('unzip -n {} -d {}'.format(file,outdir))

def shell_gunzip(file):
    # gunzip a file with the shell command
    subprocess_cmd('file="{}"; [ ! -f "${{file%%.gz}}" ] && gunzip {}'.format(file,file))

def pipeline_unzip(input_file, outdir):
    # unzip the input files
    if input_file.endswith('.zip'): shell_unzip(input_file,outdir = outdir)
    # find and unzip the .gz files extracted
    for subdir, dirs, files in os.walk(outdir):
        for file in files:
            if file.endswith('.gz'):
                # print os.path.join(subdir,file)
                shell_gunzip(os.path.join(subdir,file))

def pipeline_find_annotate_samples(input_dir):
    divider = '\n---------------------------------------------------\n'
    # ~~~~ ANNOTATION PIPELINE ~~~~~~ #
    # make dict of dict's to hold all the sample datas
    samples_dict = collections.defaultdict(dict)
    #
    # iterate over all files in the input dir
    # find the VCF, XLS files, and process them 
    print "\nFinding XLS and VCF files to be processed...\n"
    for subdir, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.vcf'):
                print divider + 'Found file:\t', file
                # barcode = 'IonXpress_xxx'
                barcode = re.search(r'^.*(IonXpress_\d+).*\..*$', file)
                barcode = barcode.group(1)
                print 'Barcode is:\t', barcode
                # start sample entry in dict
                samples_dict[barcode]['barcode'] = barcode
                #
                # set a sample outdir
                output_dir = mkdir_p(input_dir + '/' + barcode, return_path=True)
                print 'Outdir is:\t', output_dir
                #
                # ~~~~ FILTER VCF QUALITY ~~~~~~ #
                # raw VCF file path
                # EDIT: SKIP THIS STEP FILTER IN THE XLS INSTEAD..
                raw_vcf_path = (os.path.join(subdir,file))
                # read raw VCF
                print 'Reading in VCF file:\n', raw_vcf_path
                raw_vcf_df = pd.read_table(raw_vcf_path,sep='\t',skiprows=vcf_header_skip(raw_vcf_path),header=0)
                # add to dict
                samples_dict[barcode]['raw_vcf_dataframe'] = raw_vcf_df
                # ~~~~~~~~~~~~ #
                #
                #
                # ~~~~ ANNOTATE VCF FILES ~~~~~~ #
                # convert filtered VCF to AVINPUT
                print 'Converting to ANNOVAR format'
                avinput = os.path.dirname(raw_vcf_path) + '/' + os.path.basename(raw_vcf_path).replace('.vcf', '.avinput')
                # ANNOVAR output file path
                annovar_output = output_dir + '/' + os.path.basename(raw_vcf_path).replace('.vcf', '')
                print 'ANNOVAR input is:\n', avinput
                print 'ANNOVAR output is:\n', annovar_output
                # convert the file to ANNOVAR format
                # convert_2_annovar(filtered_vcf_path,avinput)
                convert_2_annovar(raw_vcf_path,avinput)
                # run ANNOVAR ; returns the final output path
                annovar_output_path = annovar_table(avinput, annovar_output)
                print 'Annotated file is:\n', annovar_output_path
                # ~~~~~~~~~~~~ #
                #
                #
                # ~~~~ FILTER ANNOVAR OUTPUT ~~~~~~ #
                # read in the ANNOVAR output
                print 'Reading in the annotated file'
                annovar_df = pd.read_table(annovar_output_path,na_values=['.'])
                # filter the ANNOVAR table
                # annovar_df = av_table_filter(annovar_df)
                # add to dict
                samples_dict[barcode]['raw_annovar_dataframe'] = annovar_df
                # ~~~~~~~~~~~~ #
                #
                #
            if file.endswith('.xls'):
                print divider + 'Found file:\t', file
                barcode = re.search(r'^.*(IonXpress_\d+).*\..*$', file)
                barcode = barcode.group(1)
                print 'Barcode is:\t', barcode
                samples_dict[barcode]['barcode'] = barcode
                # ~~~~ PROCESS XLS FILE ~~~~~~ #
                # raw XLS file path
                raw_xls_path = (os.path.join(subdir,file))
                print 'XLS file is:\n', raw_xls_path
                # read raw XLS
                print 'Reading in raw XLS file'
                raw_xls_df = pd.read_table(raw_xls_path,sep='\t',header=0,na_values=['.'])
                # print 'Raw XLS df is:\n', raw_xls_df
                # remove the 'Filter' columns
                print 'Filtering raw XLS columns'
                raw_xls_df = raw_xls_df[raw_xls_df.columns.drop([col for col in raw_xls_df.columns if 'Filter' in col])]
                samples_dict[barcode]['raw_xls_dataframe'] = raw_xls_df
                print 'XLS df length:\n', raw_xls_df.size
                # ~~~~~~~~~~~~ #
                # 
                #
                # ~~~~ FILTER XLS ~~~~~~ #
                # EDIT: HOLD OFF ON FILTER UNTIL AFTER MERGE
                # filtered_xls_df = xls_table_filter(raw_xls_df)
                xls_cols = ['Sample Name', 'Barcode', 'Run Name', 'Chrom', 'Position', 'Ref', 'Variant', 'Frequency', 'Quality', 'Original Coverage', 'Allele Cov', 'Strand Bias']
                # filtered_xls_df = filtered_xls_df[xls_cols]
                # samples_dict[barcode]['filtered_xls_dataframe'] = filtered_xls_df
                # ~~~~~~~~~~~~ #
                #
                #
                # get the run name (first entry)
                # QQ: This breaks if there are no variants.. 
                if len(raw_xls_df) > 0:
                    run_name = raw_xls_df['Run Name'].unique()[0]
                    samples_dict[barcode]['run_name'] = run_name
                    print 'Run name is:\t', run_name
                    # get the sample name (first entry)
                    sample_name = raw_xls_df['Sample Name'].unique()[0]
                    samples_dict[barcode]['sample_name'] = sample_name
                    print 'Sample name is:\t', sample_name
                else:
                    print 'WARNING: NO VARIANTS IN XLS FILE'
                    print 'REMOVING ENTRY FROM PIPELINE'
                    samples_dict.pop(barcode)
                # ~~~~~~~~~~~~ #
    return samples_dict

def pipeline_filter_merge_sampledata(samples_dict, summary_cols, outdir):
    output_dir = outdir
    divider = '\n---------------------------------------------------\n'
    # ~~~~ FILTER & MERGE DATASETS ~~~~~~ #
    print divider + divider + 'Filtering and Merging XLS and ANNOVAR datasets...\n'
    for i in range(0,len(samples_dict.keys())):
        sample = samples_dict.keys()[i]
        print divider + 'PROCESSING SAMPLE:\t', sample
        # print "\nSAMPLE keys:\n", samples_dict[sample].keys()
        # print "\nOLD AV keys:\n" , samples_dict[sample]['annovar_dataframe'].keys()
        # print samples_dict[sample]['raw_xls_dataframe'].keys()
        #
        # get the AV and XLS dataframes
        av_df = samples_dict[sample]['raw_annovar_dataframe']
        xls_df = samples_dict[sample]['raw_xls_dataframe']
        # save copies of the originals..
        output_dir = outdir + '/' + samples_dict[sample]['barcode']
        xls_df.to_csv(output_dir + "/" + sample + "_xls_table_raw.tsv", sep='\t', index=False)
        av_df.to_csv(output_dir + "/" + sample + "_av_table_raw.tsv", sep='\t', index=False)
        #
        # ~~~~ MERGE AV AND XLS DATAFRAMES ~~~~~~ #
        # rename some colnames for the merge
        av_df = av_df_fixcolnames(av_df)
        # split the AAChange rows in the table
        av_df = split_df_col2rows(dataframe = av_df, split_col = 'AAChange.refGene', split_char = ',', new_colname = 'AAChange', delete_old = True)
        # split the new columns into separate columns
        av_df = split_df_col2cols(dataframe = av_df, split_col = 'AAChange', split_char = ':', new_colnames = ['Gene', 'Transcript', 'Exon', 'Coding', 'Amino Acid Change'], delete_old = True)
        #
        #
        # make sure the XLS has uppercase for the merge
        xls_df['Ref'] = xls_df['Ref'].str.upper()
        xls_df['Variant'] = xls_df['Variant'].str.upper()
        # 
        # merge the XLS and AV dataframes
        merge_df = pd.merge(xls_df, av_df, on=['Chrom', 'Position', 'Ref', 'Variant'], how = 'left')
        #
        # ~~~~ RE-ORDER MERGED DF COLUMNS ~~~~~~ #
        # re-order the columns
        old_cols = merge_df.columns.tolist()
        new_cols = partial_reorder_list(old_list = old_cols, reference_list = summary_cols)
        merge_df = merge_df.reindex(columns= new_cols)
        #
        # ~~~~ FILTER MERGED DF ~~~~~~ #
        merge_df = custom_table_filter(merge_df)
        #
        # update the old DF's and add the merge df
        samples_dict[sample]['annovar_dataframe'] = av_df
        samples_dict[sample]['xls_dataframe'] = xls_df
        samples_dict[sample]['merged_dataframe'] = merge_df
        #
        # ~~~~ SAVE TABLES TO FILES ~~~~~~ #
        merge_df.to_csv(output_dir + "/" + sample + "_merge_table.tsv", sep='\t', index=False)
        xls_df.to_csv(output_dir + "/" + sample + "_xls_table.tsv", sep='\t', index=False)
        av_df.to_csv(output_dir + "/" + sample + "_av_table.tsv", sep='\t', index=False)
    return samples_dict

def pipeline_concat_sampledata(samples_dict):
    summary_table = pd.concat([samples_dict[sample]['merged_dataframe'] for sample in samples_dict.keys()], join = 'outer')
    return summary_table

def pipeline_filter_summarytable(summary_table, table_gene_colname, summary_cols, panel_genes, actionable_genes):
    # remove samples 'SC' 
    summary_table = summary_table.loc[ summary_table['Sample Name'] != 'SC']
    # keep only desired cols
    summary_table = summary_table[summary_table.columns.drop([col for col in summary_table.columns if col not in summary_cols])]
    # remove whitespace in colnames 
    summary_table.columns = [c.replace(' ', '_') for c in summary_table.columns]
    table_gene_colname = table_gene_colname.replace(' ', '_')
    # find rows that contain gene ID's in the panel
    gene_rows = summary_table[table_gene_colname]
    # fix the table indexes
    summary_table = summary_table.reset_index(drop=True)
    # keep only rows that contain the panel genes; iterate over the list of genes
    # new table for genes to keep
    new_table = pd.DataFrame()
    for gene in panel_genes:
        data = summary_table[summary_table[table_gene_colname].str.contains(gene)]
        new_table = new_table.append(data)
    # add review column
    new_table['Review'] = 'US'
    # # update review for KS genes
    for i in range(0, len(new_table)):
        if new_table[table_gene_colname][i] in actionable_genes:
            new_table['Review'][i] = 'KS'
    # sort the cols
    new_table = new_table.sort(['Sample_Name'])
    return new_table


# ~~~~ COMMON LOCATIONS & ITEMS ~~~~~~ #
build_version = "hg19"
project_dir = "/ifs/home/kellys04/projects/clinical_genomic_reporting/clinical_genomics_development"
panel_genes = list_file_lines(project_dir + "/panel_genes.txt")
actionable_genes = list_file_lines(project_dir + "/actionable_genes.txt")
summary_cols = list_file_lines(project_dir + "/summary_fields.txt")
divider = '\n---------------------------------------------------\n'

# ~~~~ GET SCRIPT ARGS ~~~~~~ #
# python test.py arg1 arg2 arg3
# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)
# print 'script name is:', sys.argv[0]
parser = argparse.ArgumentParser(description='IonTorrent annotation pipeline.')
parser.add_argument("input_files",help="Path to input files; .zip IonTorrent run files", nargs=2)
parser.add_argument("-o", help="Path to output directory. Defaults to the current directory", default = '.', type = str, dest = 'output')
parser.add_argument("-id", help="Run ID value. Defaults to the portion of the input filename preceeding the first '.' character ")
args = parser.parse_args()

print 'outdir is:', args.output



# ~~~~ RUN PIPELINE ~~~~~~ #
# create a dict of dicts to hold information on the input files
run_dict = collections.defaultdict(dict)

# process and load each input file
for value in args.input_files:
    input_file = value
    print 'file is:\t', input_file
    # get run ID from filename
    if not args.id:
        run_ID = os.path.basename(value).split('.')[0]
    else:
        run_ID = args.id
    print 'run ID is:\t', run_ID
    # add entries to the dict
    run_dict[run_ID]['input_dir'] = os.path.dirname(value)
    outdir_path = args.output + '/' + run_ID
    run_dict[run_ID]['output_dir'] = mkdir_p(path= outdir_path, return_path=True)
    # unzip the input file
    pipeline_unzip(input_file, outdir_path)
    # find samples among the unzipped output
    run_dict[run_ID]['samples'] = pipeline_find_annotate_samples(outdir_path)


# filter and merge the loaded data
for value in run_dict.iterkeys():
    run_ID = value
    print 'Run ID is:\t', run_ID
    print 'Run samples are:\n', run_dict[run_ID]['samples'].keys()
    # process the data for each sample; filter & merge the XLS with the ANNOVAR data
    run_dict[run_ID]['samples'] = pipeline_filter_merge_sampledata(samples_dict = run_dict[run_ID]['samples'],
        summary_cols = summary_cols, outdir = run_dict[run_ID]['output_dir'])
    # create a summary table for all samples
    run_dict[run_ID]['merged_summary'] = pipeline_concat_sampledata(run_dict[run_ID]['samples'])
    # filter the summary table for desired entries
    run_dict[run_ID]['filtered_summary'] = pipeline_filter_summarytable(run_dict[run_ID]['merged_summary'], table_gene_colname = 'Gene ID', summary_cols=summary_cols, 
        panel_genes = panel_genes, actionable_genes = actionable_genes)
    # save files
    summary_outpath = run_dict[run_ID]['output_dir'] + "/summary_table.tsv"
    run_dict[run_ID]['filtered_summary'].to_csv(summary_outpath, sep='\t', index=False)
    print "\nFinal summary file:\n", summary_outpath
    save_pydata(run_dict, run_dict[run_ID]['output_dir'] + '/run_data.py.pickle')

