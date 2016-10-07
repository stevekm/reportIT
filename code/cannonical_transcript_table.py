#!/usr/bin/env python
# python 2.7

# need to get the UCSC Known Canonical Transcripts
# UCSC transcripts with unique ID's (also available for hg38) (UCSC_id) from here: 
# http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/knownCanonical.txt.gz
# need to match 5th col ID's with RefGene ID's (Ref_id) from here:
# http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/kgXref.txt.gz
# # as per this dicussion
# # https://groups.google.com/a/soe.ucsc.edu/forum/#!topic/genome/_6asF5KciPc


import sys
import os
import pandas as pd

def get_files(dir_path, ends_with = '', trunc = False):
    # get the files in the dir that match the end pattern
    # trunc : return just the file dirname + basename (truncate)
    file_list = []
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(ends_with):
                file_path = os.path.join(subdir,file)
                if (trunc):
                    file_dir = os.path.basename(os.path.dirname(file_path))
                    file_base = os.path.basename(file_path)
                    file_path = os.path.join(file_dir,file_base)
                file_list.append(file_path)
    return file_list

# files & places to use
proj_dir = "/ifs/home/kellys04/projects/clinical_genomic_reporting/variant_reporter"

crossref_file = os.path.join(proj_dir, "data/hg19/kgXref.txt")
canon_file = os.path.join(proj_dir, "data/hg19/knownCanonical.txt")
comments_dir = os.path.join(proj_dir, "data/report_comments")
outdir= os.path.join(proj_dir, "data/hg19")

# get the report comment files from the dir
comment_files = get_files(comments_dir, ends_with = ".md", trunc = True)

# df of the crossrefence ID's
cross_cols = ['UCSC_id', 'B', 'C', 'D', 'Gene', 'Ref_id', 'G', 'Description', 'I']
crossref_df = pd.read_table(crossref_file,sep='\t', header = None, index_col=False, names = cross_cols) # 


# get list of UCSC ID's for canonical transcripts
canon_cols = ['Chrom', 'Start', 'Stop', 'Num', 'UCSC_id']
canon_df = pd.read_table(canon_file,sep='\t', header = None, index_col=False, names = canon_cols)

# merge the df's 
merge_df = pd.merge(canon_df, crossref_df, on = 'UCSC_id', how = 'inner')

# remove some cols
cols_to_keep = ['UCSC_id', 'Ref_id', 'Chrom', 'Start', 'Stop', 'Gene', 'Description']
merge_df = merge_df[merge_df.columns.drop([col for col in merge_df.columns if col not in cols_to_keep])]
# print merge_df
# save file
# merge_df.to_csv(outdir + "/" + "canonical_transcript_table.tsv", sep='\t', index=False)

# peel off just the transcripts
canon_refs = merge_df[['Gene','Ref_id', 'Description']]
canon_refs = canon_refs.dropna()
canon_refs.drop_duplicates(inplace = True)
# fix indexes
canon_refs = canon_refs.reset_index(drop=True)


# add the Comment file path
# !! THIS MATCHES ONLY THE FIRST COMMENT FILE WITH THE GENE NAME; DOES NOT DISTINGUISH WHICH MUTATION
canon_refs['Comment'] = ''
for i in range(0, len(canon_refs)):
    # get Gene ID
    gene = canon_refs['Gene'][i]
    # match the Gene ID against the Gene ID in the comment file filename, ex: EGFR-G719A.md
    canon_refs.loc[i, 'Comment'] = next((comm for comm in comment_files if gene.upper() == os.path.splitext(os.path.basename(comm.upper()))[0].split('-')[0] ), None)

# save file
canon_refs.to_csv(os.path.join(outdir, "canonical_transcr_descr_comment.tsv"), sep='\t', index=False)


sys.exit()
