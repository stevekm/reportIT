#!/usr/bin/env python
# python 2.7

'''
USAGE: run_IGV_batchscript.py /path/to/IGV_batchscript.bat
DESCRIPTION: This script will run an IGV batch script
primarily for the purpose of creating automatic snapshots of genomic regions
'''


# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys
import os
import re
import errno
import glob
import subprocess as sp
import argparse
from datetime import datetime


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def subprocess_cmd(command):
    # run a terminal command with stdout piping enabled
    process = sp.Popen(command,stdout=sp.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

def run_IGV_script(igv_script, igv_jar, memMB):
    # run the IGV script
    igv_command = "(Xvfb :10 &) && DISPLAY=:10 java -Xmx{}m -jar {} -b {} && killall Xvfb".format(memMB, igv_jar, igv_script)
    startTime = datetime.now()
    print "\nStarting IGV\nCurrent time is:\t", startTime
    print "\nIGV command is:\n", igv_command
    subprocess_cmd(igv_command)
    print "\n\nTime to process completion:\t", datetime.now() - startTime



# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='IGV batchscript runner.')

# positional args
parser.add_argument("batchscript_file", help="Path to the IGV batchscript file to run in IGV")

# optional args
parser.add_argument("-bin", default = "bin/IGV_2.3.81/igv.jar", type = str, dest = 'igv_jar_bin', metavar = 'IGV bin path', help="Path to the IGV jar binary to run")
parser.add_argument("-mem", default = "1000", type = str, dest = 'igv_mem', metavar = 'IGV memory (MB)', help="Amount of memory to allocate to IGV, in Megabytes (MB)")

args = parser.parse_args()

batchscript_file = args.batchscript_file
igv_jar_bin = args.igv_jar_bin
igv_mem = args.igv_mem



if __name__ == "__main__":
    # ~~~~ RUN BATCH SCRIPT ~~~~~~ #
    print "Running script:\n", sys.argv[0]
    print "\nbatchscript_file is :\n", batchscript_file
    print "\nigv_jar_bin is :\n", igv_jar_bin
    print "\nigv_mem is :\n", igv_mem
    run_IGV_script(igv_script = batchscript_file, igv_jar = igv_jar_bin, memMB = igv_mem)






