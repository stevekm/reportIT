# ION Variant Reporter 

This program will annotate, aggregate, and summarize clinical variant information from the IonTorrent suite

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
