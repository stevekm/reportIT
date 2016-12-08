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


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def subprocess_cmd(command):
    # run a terminal command with stdout piping enabled
    process = sp.Popen(command,stdout=sp.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

def run_IGV_script(igv_script, igv_jar, memMB):
    # run the IGV script
    subprocess_cmd("(Xvfb :10 &) && DISPLAY=:10 java -Xmx{}m -jar {} -b {} && killall Xvfb".format(memMB, igv_jar, igv_script))


# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='IGV batchscript runner.')

# positional args
parser.add_argument("batchscript_file", help="Path to the IGV batchscript file to run in IGV")

# optional args
parser.add_argument("-bin", default = "bin/IGV_2.3.81/igv.jar", type = str, dest = 'igv_jar_bin', metavar = 'IGV bin path', help="Path to the IGV jar binary to run")
parser.add_argument("-mem", default = "750", type = str, dest = 'igv_mem', metavar = 'IGV memory (MB)', help="Amount of memory to allocate to IGV, in Megabytes (MB)")

args = parser.parse_args()

batchscript_file = args.batchscript_file
igv_jar_bin = args.igv_jar_bin
igv_mem = args.igv_mem

print "\nbatchscript_file is :\n", batchscript_file
print "\nigv_jar_bin is :\n", igv_jar_bin
print "\nigv_mem is :\n", igv_mem


# ~~~~ RUN BATCH SCRIPT ~~~~~~ #
run_IGV_script(igv_script = batchscript_file, igv_jar = igv_jar_bin, memMB = igv_mem)






