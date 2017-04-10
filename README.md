# reportIT
### IonTorrent Variant Reporting Pipeline

This program will annotate, aggregate, and summarize clinical variant information from the [IonTorrent suite](https://www.thermofisher.com/us/en/home/life-science/sequencing/next-generation-sequencing/ion-torrent-next-generation-sequencing-workflow/ion-torrent-next-generation-sequencing-data-analysis-workflow/ion-torrent-suite-software.html)

# Overview

Data from an IonTorrent sequencing run will be parsed to create a summary report for each sample in the run. Variant data will be downloaded from the IonTorrent server in VCF format for each sample, paired with a tab-separated XLS table of analyzed data (not used but needed for metadata). Coverage data will be downloaded from the server for each sample in BAM format files.

All VCF files will be annotated and processed with ANNOVAR and bcftools, and a summary table will be created based on established lists of canonical gene transcripts, and genes included in the panel. 

Sequencing reads will be visualized by loading the BAM file for each test sample, paired with the corresponding control sample for the run, into IGV for automated snapshots to manually review & determine variant qualities. 

An HTML formatted analysis overview report will be generated to show a summary of significant cancer variants found amongst all samples in the IonTorrent run, with IGV snapshots for each variant. 

## In Progress

- Per-sample reports showing variant summary table and clinical interpretation of variants supplied by the Weill Cornell [Precision Medicine Knowledgebase](https://pmkb.weill.cornell.edu/). 

- Analysis review feedback system to mark sequencing artifacts 

- Deposition of pipeline output in a central database

# Installation

First, run the `dir_setup.sh` script; 
```bash
./dir_setup.sh
```

This should set up the `bin` and `ref` directories, along with creating and symlinking the external `input`, `output`, and `data` directories. You should verify these symlinks and directories, and then populate the `data` directory with files required for the pipeline (see the 'Data directory' section, below). You should also set up automatic ssh for your IonTorrent server as described [here](https://gist.github.com/stevekm/93de1539d8008d220c9a1c4d19110b3e).

# Usage

## Check For Available Runs

Before you can run the pipeline, you need to know which runs are available on your IonTorrent server. Use the following script for this:

```bash
code/get_server_run_list.sh
```

This requires that your `data/server_info.txt` file is set correctly, as described below. 

The selected runs should be entered into a samplesheet file, as described in the `samplesheets` directory, and used for running the pipeline. 

## Run the Pipeline

The simplest way to run the reportIT pipeline is to use the `run_samplesheet.py` script, and specify which actions you would like to take on the analysis ID's specified in your sample sheet. 

### Download Files

First, you should download all files needed for the analyses:

```bash
$ code/run_samplesheet.py samplesheets/example-samplesheet.tsv -d
```
### Annotate Variants

Then, you should annotate the variants in the VCF files downloaded, and create summary tables:

```bash
$ code/run_samplesheet.py samplesheets/example-samplesheet.tsv -a
```
### Visualize Coverages & Generate Reports

Finally, you can create IGV snapshots of the BAM files, and generate reports:

- for unpaired analyses

```bash
$ code/run_samplesheet.py samplesheets/example-samplesheet.tsv -r
```

- for paired analyses (runs unpaired analyses as well)

```bash
$ code/run_samplesheet.py samplesheets/example-samplesheet.tsv -p
```

### Using HPC Cluster

The annotation and reporting steps for all analyses can be run in parrallel by submitting the jobs to run on a computer cluster using `qsub`. To enable this feature, simply pass the `-q` argument with the previous commands:

```bash
# annotate with qsub
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -aq

# report with qsub
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -rq
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -pq
```
This method has been configured to work with the phoenix compute cluster at NYULMC, and might need to be reconfigured to work on other HPC systems. 

### Usage Notes

Rough estimates for pipeline completeion time are ~5-10 minutes to download all files and annotate variants, and ~5-15 minutes to create all IGV snapshots and generate reports. In total this comes to roughly 10 - 30 minutes per analysis, depending on the number of variants present. 

Running the pipeline without the `-q` argument will run all pipeline steps for all analyses in the current session; if you plan to do this, you should probably run the pipeline in `screen` in order to allow it to run in the background indepedent of your terminal connection. Note that running with `qsub` is currently disabled for the file download step, so all file downloads will always run in the current session. If you have a lot of analyses, this might take a while. 

Multiple pipeline actions can be chained together. For example:

```bash
# download all files, then annotate with qsub
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -daq
```

```bash
# download all files, then annotate and create reports (no qsub)
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -dap
```

Reporting steps depend on the completion of annotation steps, so if you plan to use the `-q` argument to submit jobs to `qsub`, you need to run the annotation, wait for the jobs to complete, then run the reports. Your workflow would look like this:


```bash
# download all files, then annotate with qsub
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -daq

# ... wait for jobs to finish ...

# run the reports
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -pq
```
# Analysis Report Example

An HTML formatted analysis overview report displays the significant variants found across all samples in the run. 'SC' control samples are shown in a separate table (hidden by default).

<img width="810" alt="screen shot 2017-03-17 at 4 21 43 pm" src="https://cloud.githubusercontent.com/assets/10505524/24061536/2f11cd3e-0b2e-11e7-9684-4cb9f4d2e0a6.png">

IGV snapshots shown for all significant variants. For low frequency variants, a "long view" snapshot is included to ensure mutations can be seen amongst reads. If available, 'NC' control sample is included on the lower track. 

<img width="800" alt="screen shot 2017-03-17 at 4 22 28 pm" src="https://cloud.githubusercontent.com/assets/10505524/24061635/9111af4a-0b2e-11e7-9870-8485ccf38ec2.png">

# Files & Directories

Input, output, and reference data for the program is stored external to the program's directory and is set by symlinks.

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
