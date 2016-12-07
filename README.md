# ION Variant Reporter 

This program will annotate, aggregate, and summarize clinical variant information from the IonTorrent suite

# Overview

Data from an IonTorrent sequencing run will be parsed to create a summary report for each sample in the run. Variant data will be downloaded from the IonTorrent server in VCF format for each sample, paired with a tab-separated XLS table of analyzed data (not used but needed for metadata). Coverage data will be downloaded from the server for each sample in BAM format files.

All VCF files will be annotated and processed with ANNOVAR and bcftools, and a summary table will be created based on established lists of canonical gene transcripts, and genes included in the panel. 

Sequencing reads will be visualized by loading the BAM file for each test sample, paired with the corresponding control sample for the run, into IGV for automated snapshots to manually review & determine variant qualities. 

A preliminary sparse plain-text report will be generated from the summary table of variants, and a rich full report will be generated from the IGV snapshots, summary table, and other visualizations. Both reports will include clinical significance and interpretations supplied by the Weill Cornell [Precision Medicine Knowledgebase](https://pmkb.weill.cornell.edu/). 


# Usage

Program usage will change as development progresses. Current usage is:

```bash
# example analysis ID = 'Auto_user_SNX-XXX-XXXX-XXX'

# get list of recent analysis runs
code/get_server_run_list.sh

# pick one or more from the list and download files for the pipeline
code/server_download_annotate_wrapper.sh Auto_user_SN2-1XX-XXXX-XXX Auto_user_SN2-2XX-XXXX-XXX
```
# Files & Directories

## Program Directory

Input, output, and reference data for the program is stored external to the program's directory and is set by symlinks. The current program directory structure is:

```
variant_reporter$ tree
.
|-- README.md
|-- bin -> ../bin/
|-- code
|   |-- IGV_batchscript_generator.py
|   |-- IGV_test.bat
|   |-- IonTorrent_summary_table.py
|   |-- cannonical_transcript_table.py
|   |-- compile_sparse_report.R
|   |-- make_all_sparse_reports.sh
|   `-- move_bams.sh
|-- data -> ../reporter_files/data
|-- input -> ../reporter_files/input
|-- output -> ../reporter_files/output
`-- report
    |-- report_comments -> ../data/report_comments/
    `-- sparse_report.Rmd
```

## Data directory

The `data` directory should contain the following items:

```
data/
|-- actionable_genes.txt
|-- panel_genes.txt
|-- server_info.txt

```

Important files:

`data/panel_genes.txt` : A list of genes to be included in the gene panel. Example:

```bash
$ head data/panel_genes.txt
AKT1
ALK
APC
ATM
```

`data/actionable_genes.txt` : A list of genes detertmined to be actionable. Example:

```bash
$ head data/actionable_genes.txt
BRAF
EGFR
FLT3
```

`server_info.txt` : The login info for the IonTorrent server. Example:

```bash
$ cat data/server_info.txt
username@server_IP
```



## References Directory

This directory contains the following items:

```bash
ref
|-- cannonical_transcript_table.py
`-- hg19
    |-- canonical_transcript_list.txt
    |-- download_refs.txt
    |-- kgXref.txt
    |-- kgXref.txt.gz
    |-- knownCanonical.txt
    `-- knownCanonical.txt.gz
```

Important files:

`data/hg19/canonical_transcript_list.tsv` : A list of canonical transcripts . Example:

```bash
$ head ref/hg19/canonical_transcript_list.tsv
NR_026820
NM_001005484
NR_039983
NM_001005277
```

## Output Directory

The current data output directory format mirrors the directory format of the analysis results on the IonTorrent server. An example output directory looks like this:

```
output
|-- Auto_user_SNX-XXX-XXX-XXX-X_analysis_files.txt
|-- Auto_user_SNX-XXX-XXX-XXX-X_analysis_manifest.txt
|-- R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1
|   `-- Auto_user_SNX-XXX-XXX-XXX-X
|       `-- plugin_out
|           |-- coverageAnalysis_out.777
|           |   |-- IonXpress_001
|           |   |   |-- IonXpress_001_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |   |   `-- IonXpress_001_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           |   |-- IonXpress_002
|           |   |   |-- IonXpress_002_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |   |   `-- IonXpress_002_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           |   |-- IonXpress_003
|           |   |   |-- IonXpress_003_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |   |   `-- IonXpress_003_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           |   |-- IonXpress_004
|           |   |   |-- IonXpress_004_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |   |   `-- IonXpress_004_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           |   |-- IonXpress_005
|           |   |   |-- IonXpress_005_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |   |   `-- IonXpress_005_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           |   |-- IonXpress_006
|           |   |   |-- IonXpress_006_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |   |   `-- IonXpress_006_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           |   |-- IonXpress_007
|           |   |   |-- IonXpress_007_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |   |   `-- IonXpress_007_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           |   `-- IonXpress_008
|           |       |-- IonXpress_008_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam
|           |       `-- IonXpress_008_R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1_Auto_user_SNX-XX-XX-XX-1_243.bam.bai
|           `-- variantCaller_out.778
|               |-- IonXpress_001
|               |   |-- IonXpress_001.avinput
|               |   |-- IonXpress_001.hg19_multianno.txt
|               |   |-- IonXpress_001.tsv
|               |   |-- IonXpress_001_filtered.tsv
|               |   |-- IonXpress_001_full_table.tsv
|               |   |-- IonXpress_001_query.tsv
|               |   |-- IonXpress_001_summary.tsv
|               |   `-- TSVC_variants.vcf
|               |-- IonXpress_002
|               |   |-- IonXpress_002.avinput
|               |   |-- IonXpress_002.hg19_multianno.txt
|               |   |-- IonXpress_002.tsv
|               |   |-- IonXpress_002_filtered.tsv
|               |   |-- IonXpress_002_full_table.tsv
|               |   |-- IonXpress_002_query.tsv
|               |   |-- IonXpress_002_summary.tsv
|               |   |-- TSVC_variants.vcf
|               |   |-- TSVC_variants.vcf.gz
|               |   `-- TSVC_variants.vcf.gz.tbi
|               |-- IonXpress_003
|               |   |-- IonXpress_003.avinput
|               |   |-- IonXpress_003.hg19_multianno.txt
|               |   |-- IonXpress_003.tsv
|               |   |-- IonXpress_003_filtered.tsv
|               |   |-- IonXpress_003_full_table.tsv
|               |   |-- IonXpress_003_query.tsv
|               |   |-- IonXpress_003_summary.tsv
|               |   `-- TSVC_variants.vcf
|               |-- IonXpress_004
|               |   |-- IonXpress_004.avinput
|               |   |-- IonXpress_004.hg19_multianno.txt
|               |   |-- IonXpress_004.tsv
|               |   |-- IonXpress_004_filtered.tsv
|               |   |-- IonXpress_004_full_table.tsv
|               |   |-- IonXpress_004_query.tsv
|               |   |-- IonXpress_004_summary.tsv
|               |   `-- TSVC_variants.vcf
|               |-- IonXpress_005
|               |   |-- IonXpress_005.avinput
|               |   |-- IonXpress_005.hg19_multianno.txt
|               |   |-- IonXpress_005.tsv
|               |   |-- IonXpress_005_filtered.tsv
|               |   |-- IonXpress_005_full_table.tsv
|               |   |-- IonXpress_005_query.tsv
|               |   |-- IonXpress_005_summary.tsv
|               |   `-- TSVC_variants.vcf
|               |-- IonXpress_006
|               |   |-- IonXpress_006.avinput
|               |   |-- IonXpress_006.hg19_multianno.txt
|               |   |-- IonXpress_006.tsv
|               |   |-- IonXpress_006_filtered.tsv
|               |   |-- IonXpress_006_full_table.tsv
|               |   |-- IonXpress_006_query.tsv
|               |   |-- IonXpress_006_summary.tsv
|               |   `-- TSVC_variants.vcf
|               |-- IonXpress_007
|               |   |-- IonXpress_007.avinput
|               |   |-- IonXpress_007.hg19_multianno.txt
|               |   |-- IonXpress_007.tsv
|               |   |-- IonXpress_007_filtered.tsv
|               |   |-- IonXpress_007_full_table.tsv
|               |   |-- IonXpress_007_query.tsv
|               |   |-- IonXpress_007_summary.tsv
|               |   `-- TSVC_variants.vcf
|               |-- IonXpress_008
|               |   |-- IonXpress_008.avinput
|               |   |-- IonXpress_008.hg19_multianno.txt
|               |   |-- IonXpress_008.tsv
|               |   |-- IonXpress_008_filtered.tsv
|               |   |-- IonXpress_008_full_table.tsv
|               |   |-- IonXpress_008_query.tsv
|               |   |-- IonXpress_008_summary.tsv
|               |   `-- TSVC_variants.vcf
|               |-- R_2016_X-XX-XX-XX_user_SNX-XX-XX-XX-1.xls
|               `-- sample_barcode_IDs.tsv
```



# To Do:


Sparse Report

- update clinical comments
- fix clinical comment filename formatting
- update variant knowledge base

Full Report

- IGV screenshot review feedback integration
- create full report


# Software Requirements

This program has been developed in a Linux environment running CentOS 6. Some scripts issue system commands which rely on standard GNU Linux utilities. The current list of all binary dependencies are contained in the file `bin.txt`. Some download notes for obtaining these programs can be found in `bin_downloads.txt`

    - Python 2.7
    - pandoc version 1.12.3 or higher
    - R 3.3.0 or higher
    - IGV_2.3.81
    - bcftools-1.3.1
    - htslib-1.3.1
    - samtools-1.3.1
    - ANNOVAR version 2015-06-17 21:43:53 -0700 (Wed, 17 Jun 2015)
    - GNU bash, version 4.1.2(1)-release (x86_64-redhat-linux-gnu)

## Python packages

    - numpy==1.11.0
    - pandas==0.17.1

## R packages

    - rmarkdown
    - optparse
