#!/usr/bin/env python

'''
This script will run the reportIT pipeline from a tab-separated samplesheet
'''
import sys
import os
import argparse
import pipeline_functions as pl
import csv



# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='This script will run the reportIT pipeline from a tab-separated samplesheet.')
# # positional args
parser.add_argument("samplesheet_file", nargs='+', help="path to the summary samplesheet to run") # , nargs='?', default = "samplesheet.tsv",

# optional args
parser.add_argument("-d", default = False, action='store_true', dest = 'download',  help="whether the analyses should be downloaded from the IonTorrent server")
parser.add_argument("-a", default = False, action='store_true', dest = 'annotate', help="whether the analyses should be annotated")
parser.add_argument("-r", default = False, action='store_true', dest = 'report',  help="whether the reports should be generated for the analyses")
parser.add_argument("-p", default = False, action='store_true', dest = 'paired_report',  help="whether paired reports should be generated for the analyses that are paired in the sample sheet; analyses that are unpaired will be run as such as well")
parser.add_argument("-q", default = False, action='store_true', dest = 'use_qsub',  help="whether pipeline scripts should be submitted with qsub to run on the cluster")


args = parser.parse_args()

samplesheet_file = args.samplesheet_file[0]
download = args.download
annotate = args.annotate
report = args.report
paired_report = args.paired_report
use_qsub = args.use_qsub

print "Running pipeline with the following parameters:\n"
print "Samplesheet file: {:>29}".format(samplesheet_file)
print "Download files (d): {:>24}".format(str(download))
print "Annotate files (a): {:>24}".format(str(annotate))
print "Run unpaired reports (r): {:>18}".format(str(report))
print "Run paired reports (p): {:>20}".format(str(paired_report))
print "Submit jobs to HPC cluster (q): {:>12}".format(str(use_qsub))

def print_lines(myfile):
    '''
    Prints every line in the file
    '''
    # make sure the myfile exists before continuing
    pl.file_exists(myfile, kill = True)
    with open(myfile) as file:
        for line in file: print line,


def get_samplesheet_list(samplesheet_file):
    '''
    Returns a list of every analysis ID in the samplesheet file
    '''
    # make sure the samplesheet exists before continuing
    pl.file_exists(samplesheet_file, kill = True)
    analysis_list = []
    with open(samplesheet_file) as file:
        for line in file:
            for item in line.split():
                analysis_list.append(item)
    if len(analysis_list) > 0:
        return analysis_list
    else:
        print "ERROR: Analysis ID list is length < 1; were analysis ID's passed?"
        print "Exiting...."
        sys.exit()

def get_samplesheet_paired_unpaired_lists(samplesheet_file):
    '''
    Returns separate lists of the paired and unpaired analyses in the samplesheet
    '''
    # make sure the myfile exists before continuing
    pl.file_exists(samplesheet_file, kill = True)
    paired_analysis_list = []
    single_analysis_list = []
    with open(samplesheet_file) as file:
        for line in file:
            if len(line.split()) == 2:
                paired_analysis_list.append(line.split())
            elif len(line.split()) == 1:
                single_analysis_list.append(line.split()[0])
    return (paired_analysis_list, single_analysis_list)

def download_analysis_files(samplesheet_file, use_qsub = False):
    '''
    Runs the download script on all the analyses in the sample sheet
    '''
    if use_qsub == True:
        download_script = "code/qsub_download_wrapper.sh"
    elif use_qsub == False:
        download_script = "code/get_server_files.sh"
    else:
        print "ERROR: object 'use_qsub' must be 'True' or 'False'"
    ### !! don't use the qsub wrapper yet because something is wrong with it
    download_script = "code/get_server_files.sh"
    ###
    # get the list of analysis ID's
    analysis_list = get_samplesheet_list(samplesheet_file)
    # build the command to run
    command = '{} {}'.format(download_script, ' '.join(analysis_list))
    # pass command to the shell
    pl.subprocess_cmd(command)

def annotate_analyses(samplesheet_file, use_qsub = False):
    '''
    Runs the annotation script on all the analyses in the sample sheet
    '''
    if use_qsub == True:
        annotate_script = "code/qsub_annotate_wrapper.sh"
    elif use_qsub == False:
        annotate_script = "code/annotate_wrapper.sh"
    else:
        print "ERROR: object 'use_qsub' must be 'True' or 'False'"
    analysis_list = get_samplesheet_list(samplesheet_file)
    command = '{} {}'.format(annotate_script, ' '.join(analysis_list))
    pl.subprocess_cmd(command)

def report_analyses(samplesheet_file, use_qsub = False):
    '''
    Runs the reporting script on all the analyses in the sample sheet
    '''
    if use_qsub == True:
        report_script = "code/qsub_report_wrapper.sh"
    elif use_qsub == False:
        report_script = "code/IGV_report_wrapper.sh"
    else:
        print "ERROR: object 'use_qsub' must be 'True' or 'False'"
    analysis_list = get_samplesheet_list(samplesheet_file)
    command = '{} {}'.format(report_script, ' '.join(analysis_list))
    pl.subprocess_cmd(command)

def paired_report_analyses(samplesheet_file, use_qsub = False):
    '''
    Runs the paired report script on all the paired analyses in the sample sheet
    AND runs the regular report script on the unpaired analyses
    '''
    if use_qsub == True:
        report_script = "code/qsub_report_wrapper.sh"
        paired_report_script = "code/qsub_paired_report_wrapper.sh"
    elif use_qsub == False:
        report_script = "code/IGV_report_wrapper.sh"
        paired_report_script = "code/IGV_report_wrapper-paired.sh"
    else:
        print "ERROR: object 'use_qsub' must be 'True' or 'False'"
    paired_analysis_list, single_analysis_list = get_samplesheet_paired_unpaired_lists(samplesheet_file)
    # pl.my_debugger(locals().copy())
    # run the unpaired reports first; don't kill if none were passed
    if len(single_analysis_list) > 0:
        unpaired_command = '{} {}'.format(report_script, ' '.join(single_analysis_list))
        pl.subprocess_cmd(unpaired_command)
    # run each pair of paired analyses
    # make sure at least one pair of analyses was passed
    pl.kill_on_false(pl.check_list_len_greaterthan(paired_analysis_list, 0))
    for analysis_pair in paired_analysis_list:
        paired_command = '{} {}'.format(paired_report_script, ' '.join(analysis_pair))
        pl.subprocess_cmd(paired_command)


print("\nSamplesheet provided:\n")
print_lines(samplesheet_file)


# d
if download == True:
    print("Downloading files...")
    download_analysis_files(samplesheet_file, use_qsub)

# a
if annotate == True:
    print("Annotating the analyses...")
    annotate_analyses(samplesheet_file, use_qsub)

# r
if report == True:
    print("Running the unpaired report scripts...")
    report_analyses(samplesheet_file, use_qsub)

# p
if paired_report == True:
    print("Running the paired & unpaired report scripts...")
    paired_report_analyses(samplesheet_file, use_qsub)
