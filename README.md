# ION Variant Reporter 

This program will annotate, aggregate, and summarize clinical variant information from the IonTorrent suite

# Overview

Data from an IonTorrent sequencing run (`<Run_data>.xls.zip`, `<Run_data>.vcf.zip`) will be extracted and parsed to create a summary table highlightling desired information on detected genomic variants which have been deemed significant based on sequencing quality and attributes, and known attributes of the established variants. 

A sparse plain text report will then be created to summarize this information, including clinical comments describing the known significance of the variants drawn from scientific literature. 

Snapshots of each significant variant will be created by passing the BAM files for each sample and its control to IGV. These snapshots will be used for manual review of the detected variants and quality control measures. 

Variants that passed manual review will be included in downstream processing to create a full report designed for use by clinicians for patient cancer diagnosis and treatment. 

# Usage

Program usage will change as development progresses. Current usage is:

```
# change to the program's directory
$ cd ion_variant_reporter

# make summary table from IonTorrent Suite data
# code/IonTorrent_summary_table.py -o <output_parent_directory> <IonTorrent_data.vcf.zip> <IonTorrent_data.xls.zip>
$ code/IonTorrent_summary_table.py -o output input/R_2016_07_28_15_04_57_user_ABV-999-GH360-974.*

# copy the previously downloaded IonTorrent run bams from some dir 
# into the correct subdirs for the run that was just processed
# code/move_bams.sh <output_run_directory> <dir_containing_run_bams>
$ code/move_bams.sh output/R_2016_07_28_15_04_57_user_ABV-999-GH360-974 output/tmp_bams

# generate IGV screenshots for the run bams just copied
# code/IGV_batchscript_generator.py <output_run_directory>
$ code/IGV_batchscript_generator.py output/R_2016_07_28_15_04_57_user_ABV-999-GH360-974

# generate a sparse plain text report
$ code/compile_sparse_report.R -f output/<run_dir>/summary_table.tsv

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
$ ll -g  data/
total 432K
drwxr-s--- 8 kellys04  339 Oct  8 15:15 .
drwxr-s--- 5 kellys04   69 Sep  9 12:42 ..
-rw-r----- 1 kellys04   50 Sep  6 16:07 actionable_genes.txt
drwxr-s--- 2 kellys04  299 Oct  7 14:49 hg19
-rw-r----- 1 kellys04  266 Aug 18 16:53 panel_genes.txt
drwxr-s--- 2 kellys04 1.7K Oct  8 15:15 report_comments
-rw-r----- 1 kellys04  159 Aug 20 01:34 summary_fields.txt

```

Important files:

`data/panel_genes.txt` : A list of genes to be included in the gene panel; one per line

`data/actionable_genes.txt` : A list of genes detertmined to be actionable; one per line

`data/summary_fields.txt` : A list of fields (column names) from the `<Run_data>.xls` files to be included in the summary report; one per line

`data/report_comments` : A directory containing clinical comments to be included in the reports. Each clinical comment should be a separate markdown file following the naming convention`data/report_comments/EGFR-T790M.md` (naming convention details in development)

`data/hg19/canonical_transcr_descr_comment.tsv` : A table containing gene ID, RefSeq ID, description, and path to comment file for each variant's canonical transcript


## To Do:

Summary table

- fix coverage filter
- fix canonical transcript filter
- fix canonical transcript db for cross referencing
- make sub-table saved separately per sample in the run

IGV Screenshots

- add control bam to screenshot track

Sparse Report

- update clinical comments
- fix clinical comment filename formatting
- update variant knowledge base

Full Report

- IGV screenshot review feedback integration
- create full report

API Plug-in

- get data from IonTorrent API automatically per run, pass to program scripts


## Software Requirements

This program has been developed in a Linux environment running CentOS 6. Some scripts issue system commands which rely on standard GNU Linux utilities.  

    - Python 2.7
    - pandoc version 1.12.3 or higher
    - R 3.3.0 or higher
    - IGV_2.3.81
    - ANNOVAR version 2015-06-17 21:43:53 -0700 (Wed, 17 Jun 2015)
    - GNU bash, version 4.1.2(1)-release (x86_64-redhat-linux-gnu)

### Python packages

    - sys
    - os
    - errno
    - pandas
    - numpy
    - fnmatch
    - re
    - subprocess
    - csv
    - collections
    - pickle
    - argparse
    - zipfile
    - gzip

### R packages

    - rmarkdown
    - optparse
