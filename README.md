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
# 'Auto_user_SNX-XXX-XXXX-XXX' = example analysis ID
# 'R_2016_09_01_XX_XX_XX_XX-ITXX' = example run ID


# get list of recent analysis runs
code/get_server_run_list.sh data/server_info.txt


# pick one from the list and get its file list
code/get_server_file_list.sh data/server_info.txt Auto_user_SNX-XXX-XXXX-XXX /path/to/output_dir
# this generates:
# /path/to/output_dir/Auto_user_SNX-XXX-XXXX-XXX_analysis_manifest.txt : verbose description of files
# /path/to/output_dir/Auto_user_SNX-XXX-XXXX-XXX_analysis_files.txt : simple file list


# download the files in the list to a dir named with the run ID
code/download_server_files.sh data/server_info.txt /path/to/output_dir/Auto_user_SNX-XXX-XXXX-XXX_analysis_files.txt /path/to/output_dir/R_2016_09_01_XX_XX_XX_XX-ITXX


# annotate all the VCFs, and make TSV files we need for the summary tables
code/annotate_vcfs.sh /path/to/output_dir/R_2016_09_01_XX_XX_XX_XX-ITXX


# get a list of sample IDs, barcodes, and run ID, needed to map between Barcode & SampleID in the pipeline
code/get_run_IDs.sh /path/to/output_dir/R_2016_09_01_XX_XX_XX_XX-ITXX


# make the summary tables for all the samples
code/merge_vcf_annotations_wrapper.sh /path/to/output_dir/R_2016_09_01_XX_XX_XX_XX-ITXX
```


Input, output, and reference data for the program is stored external to the program's directory and is set by symlinks. The current directory structure is:

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

The `data` directory should contain the following items:

```
data/
|-- actionable_genes.txt
|-- hg19
|   |-- canonical_transcript_list.tsv
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

`data/hg19/canonical_transcript_list.tsv` : A list of canonical transcripts . Example:

```bash
$ head data/hg19/canonical_transcript_list.tsv
NR_026820
NM_001005484
NR_039983
NM_001005277
```


## To Do:


Sparse Report

- update clinical comments
- fix clinical comment filename formatting
- update variant knowledge base

Full Report

- IGV screenshot review feedback integration
- create full report


## Software Requirements

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

### Python packages

    - numpy==1.11.0
    - pandas==0.17.1

### R packages

    - rmarkdown
    - optparse
