# reportIT
### IonTorrent Variant Reporting Pipeline

This program will annotate, aggregate, and summarize clinical variant information from the [IonTorrent suite](https://www.thermofisher.com/us/en/home/life-science/sequencing/next-generation-sequencing/ion-torrent-next-generation-sequencing-workflow/ion-torrent-next-generation-sequencing-data-analysis-workflow/ion-torrent-suite-software.html)

- A brief graphical overview of the pipeline can be found [here](https://github.com/stevekm/reportIT/blob/master/docs/reportIT_pipeline_designs.pdf). 

# Overview

Sequencing results are accessed directly from the lab's IonTorrent server via scripts using `ssh` and `rsync`. After downloading files for a given run to the local system, VCF formatted variant call files are annotated and summarized to identify mutations of known significance (ANNOVAR, `bcftools`), while BAM formatted coverage files are visualized with IGV. An HTML formatted report is generated from variant summary information and IGV snapshots. Results can be easily emailed to clinicians for review with the provided script. 

## In Progress
Development of the following items is currently planned for the future:
- Per-sample reports showing variant summary table and clinical interpretation of variants supplied by the Weill Cornell [Precision Medicine Knowledgebase](https://pmkb.weill.cornell.edu/). 

- Analysis review feedback system to mark sequencing artifacts and remove them from report output

- Deposition of pipeline output in a central database (REDCap, or other)


# Analysis Report Example
__[[ A full HTML version of the report can be previewed [here](https://cdn.rawgit.com/stevekm/reportIT/d8b0304f90064bcc1337cc8e4eb0c7a2005431a5/example_report/ExampleIonTorrentRun123_overview_report.html) or [here](http://htmlpreview.github.io/?https://github.com/stevekm/reportIT/blob/d8b0304f90064bcc1337cc8e4eb0c7a2005431a5/example_report/ExampleIonTorrentRun123_overview_report.html). ]]__

An analysis overview report displays the significant variants found across all samples in the run. 'SC' sensitivity control samples are shown in a separate table (hidden by default).

<img width="810" alt="screen shot 2017-03-17 at 4 21 43 pm" src="https://cloud.githubusercontent.com/assets/10505524/24061536/2f11cd3e-0b2e-11e7-9684-4cb9f4d2e0a6.png">

IGV snapshots shown for all significant variants. For low frequency variants, a "long view" snapshot is included to ensure mutations can be seen amongst reads. If available, 'NC' control sample is included on the lower track. 

<img width="800" alt="screen shot 2017-03-17 at 4 22 28 pm" src="https://cloud.githubusercontent.com/assets/10505524/24061635/9111af4a-0b2e-11e7-9870-8485ccf38ec2.png">



# Installation

- First, clone this repo:
```bash
git clone --recursive https://github.com/stevekm/reportIT.git
cd reportIT
```

- Then, run the `dir_setup.sh` script; 
```bash
./dir_setup.sh
```
This should set up the `bin` and `ref` directories, along with creating and symlinking the external `input`, `output`, and `data` directories. You should verify these symlinks and directories, and then populate the `data` directory with files required for the pipeline (see the 'Data directory' section, below). You should also set up automatic ssh for your IonTorrent server as described [here](https://gist.github.com/stevekm/93de1539d8008d220c9a1c4d19110b3e).

- Review the items described in the [Files & Directories](#files--directories) and [Pipeline Settings](#pipeline-settings) sections to make sure everything is set properly.


# Usage

## Check For Runs

Before you can run the pipeline, you need to know which runs are available on your IonTorrent server. The following steps require that your `data/server_info.txt` file is set correctly, as described below. It is also recommended to have ssh key authentication set up for your user account on the IonTorrent server. 

### Missing Runs Only

If you only want to know which runs on the IonTorrent server are not present on your local system, you can use this script:

```bash
code/check_for_new_runs.py
```

By default, it will validate each missing run to make sure that IonTorrent sequencing data has been produced in the remote run directory. It will also automatically create an unpaired samplesheet for the missing runs. If you inlclude the `-d` argument to the script, it will also download the missing runs entered on the sample sheet produced. 

### All Available Runs

The following script will log into your IonTorrent server, and output a list of all run directories found:

```bash
code/get_server_run_list.sh
```

## Make Samplesheet

The best way to run the reportIT pipeline is by using a samplesheet. These are stored in the `samplesheets` directory by default, and an example can be found [here](https://github.com/stevekm/reportIT/blob/3945df853ba6dc679eebc0924f9f8d1f4e5c118e/samplesheets/example-samplesheet.tsv). A samplesheet must be in TSV (tab-separated) format, preferably with one run ID per line. If two runs should be treated as a 'pair', then both run ID's should be on the same line. Note that paired run processing only affects report and IGV snapshot generation, not downloading or annotation.

The best way to create a samplesheet is to use the `make_samplesheet.py` script. This script can take any number of unpaired run ID's, and a single set of paired ID's. 


```bash
code/make_samplesheet.py unpaired_run1 unpaired_run2 -p paired_run3.1 -p paired_run3.2
```
A samplesheet produced this way will look like this:

```
unpaired_run1
unpaired_run2
paired_run3.1	paired_run3.2
```

## Run Pipeline

The simplest way to run the reportIT pipeline is to use the `run_samplesheet.py` script, and specify which actions you would like to take on the analysis ID's specified in your sample sheet. The following actions are available:

- Download: `-d`
- Annotate: `-a`
- Report: `-r`

The following modifiers are available:
- Submit to cluster with `qsub`: `-q`



Multiple actions can be combined in a single command:

```bash
# download all files, then annotate and report with qsub
$ code/run_samplesheet.py samplesheets/samplesheet.tsv -darq
```

__NOTE:__ The `-q` method has been configured to work with the phoenix SGE compute cluster at NYULMC, and might need to be reconfigured to work on other HPC systems. 


## Mail Results

After manually reviewing the HTML report output, pipeline results can be delivered in a pre-formatted email using the following script:

```
code/mail_analysis_report.sh <analysis_ID>
```

Multiple `analysis_ID`'s can be passed to email all results sequentially. All summary tables, VCF files, IGV snapshots, and the analysis overview report will be included as email attachments. Configuration for emailing is saved in the file `mail_settings.sh`.


### Usage Notes

Rough estimates for pipeline completeion time are ~5-10 minutes to download all files and annotate variants, and ~5-15 minutes to create all IGV snapshots and generate reports. In total this comes to roughly 10 - 30 minutes per analysis, depending on the number of variants present. 

Running the pipeline without the `-q` argument will run all pipeline steps for all analyses in the current session; if you plan to do this, you should probably run the pipeline in `screen` in order to allow it to run in the background indepedent of your terminal connection. Note that running with `qsub` is currently disabled for the file download step, so all file downloads will always run in the current session. If you have a lot of analyses, this might take a while. 

### Program Validation
As a safety feature against undesired usage, the `run_samplesheet.py` script includes self-validating features to make sure the following items are set correctly before running the pipeline:

- check that the proper `git` branch is currently in use
- check that the proper output directory has been symlinked

These validations can be skipped by adding the `--debug` argument to the script.

# Files & Directories

Input, output, and reference data for the program is stored external to the program's directory and is set by symlinks. These should be automatically created when you run the `dir_setup.sh` script during initial installation.

## Data directory

The `data` directory should contain the following items:

```
data/
|-- control_sample_IDs.txt
|-- control_sample_regex.txt
|-- email_recipients.txt
|-- actionable_genes.txt
|-- panel_genes.txt
|-- server_info.txt
`-- summary_fields.txt
```

Important files:

- `control_sample_IDs.txt`: ID's for IonTorrent samples which are used to denote 'control' samples, which should not be used for IGV snapshots. Example:

```bash
NC
SC
NTC
NC HAPMAP
HAPMAP
Sc
SC-ACROMETRIX
```

- `control_sample_regex.txt`: Regex patterns to use with `grep -F` in some scripts which try to identify NC control samples. Example:

```bash
^NC[[:space:]]
^NC[[:space:]]HAPMAP[[:space:]]
^HAPMAP[[:space:]]
```

- `SC_control_sample_IDs.txt`: ID's to identify SC control samples. Example:

```bash
SC
Sc
SC-ACROMETRIX
```

- `email_recipients.txt`: A list of email addresses to use in the `To:` field of the outgoing email with analysis results. The addresses must be on a single line, formatted as such:

```bash
email1@gmail.com, email2@gmail.com
```

- `panel_genes.txt` : A list of genes to be included in the gene panel. Example:

```bash
AKT1
ALK
APC
ATM
```

- `actionable_genes.txt` : A list of genes determined to be actionable. Example:

```bash
BRAF
EGFR
FLT3
```

- `server_info.txt` : The login info for the IonTorrent server. Must be formatted as such:

```bash
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

- `hg19/canonical_transcript_list.txt` : A list of canonical transcripts to use with the given genome (hg19). Each gene for should have only one 'canonical transcript' given in the list. Example:

```bash
NR_026820
NM_001005484
NR_039983
NM_001005277
```

- `IDs_to_replace.csv`: Transcript ID's that should be replaced in the default `canonical_transcript_list.txt` list during setup, in the format of `OLD,NEW`. Example:

```bash
NM_001276760,NM_000546
```

# Pipeline Settings

Settings used by the pipeline have been saved in several files, for ease of access & modification. 

- `filter_criteria.json`: Filtering criteria used identify quality variants for inclusion in the variant summary tables. The sample file `example_filter_criteria.json` has been provided, and should be renamed to `filter_criteria.json`

- `global_settings.sh`: Global pipeline locations and settings used by `bash` scripts. References to hard-coded locations on your local system or IonTorrent system should be reviewed, and updated to match your criteria. 

- `global_settings.py`: Many of the same settings as set in `global_settings.sh`, intended for use in Python scripts. 

- `mail_settings.sh`: Settings to use with the `bash` email script(s).

# Control Samples

An important aspect of the IonTorrent reporting pipeline is the ability to recognize control samples included in a run. Unlike patient samples, these samples are included in a run for quality control purposes. Since the IonTorrent system is agnostic to the nature of samples in a run, these control samples must be denoted by their sample ID entered in the system during run setup. Similarly, the reporting pipeline is only able to identify which samples are controls by their sample ID. This makes sample labeling of control samples important during wet-lab IonTorrent run setup. The following control samples are typically used:

- `SC`: Sensitivity control (positive control). This sample is expected to show a large number of mutations. Typically uses AcroMetrix Hotspot control sample.

- `NC`: Negative control. DNA sample that should not have any mutations. Typically a HapMap sample. 

- `NTC`: No template control. No DNA included in the sample, only water. 

The best practice is to label these control samples as `SC`, `NC`, and `NTC` in every run. The ID's to be used should be entered in the appropriate settings files as described in the section [Files & Directories](#files--directories). 

These control samples have special treatment when running the pipeline. During processing, IGV snapshots will not be taken for any sample that has a label matching a control sample. Instead, the pipeline will attempt to identify the `NC` control sample for a run, or pair of runs, and use it's corresponding .bam file as the lower track in IGV snapshots for all samples in the given run(s). During report generation, variants from the `SC` sample will be excluded from the primary variant summary table displayed, since it is expected to have a large number of variants. 

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
