# ION Variant Reporter 

This program will annotate, aggregate, and summarize clinical variant information from the IonTorrent suite

# Overview

Data from an IonTorrent sequencing run (`<Run_data>.xls.zip`, `<Run_data>.vcf.zip`) will be extracted and parsed to create a summary table highlightling desired information on detected genomic variants which have been deemed significant based on sequencing quality and attributes, and known attributes of the established variants. 

A sparse plain text report will then be created to summarize this information, including clinical comments describing the known significance of the variants drawn from scientific literature. 

Snapshots of each significant variant will be created by passing the BAM files for each sample and its control to IGV. These snapshots will be used for manual review of the detected variants and quality control measures. 

Variants that passed manual review will be included in downstream processing to create a full report designed for use by clinicians for patient cancer diagnosis and treatment. 

# Usage

Input, output, and reference data for the program is stored external to the program's directory and is set by symlinks. 

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

    - Python 2.7
    - pandoc version 1.12.3 or higher
    - R 3.3.0 or higher
    - IGV_2.3.81
    - ANNOVAR version 2015-06-17 21:43:53 -0700 (Wed, 17 Jun 2015)

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