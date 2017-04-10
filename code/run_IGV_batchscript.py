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
# import subprocess as sp
import argparse
from datetime import datetime
import pipeline_functions as pl


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
# def subprocess_cmd(command):
#     import subprocess as sp
#     # run a terminal command with stdout piping enabled
#     process = sp.Popen(command,stdout=sp.PIPE, shell=True)
#     proc_stdout = process.communicate()[0].strip()
#     print proc_stdout

def get_open_X_server():
    '''
    Search for an open Xvfb port to render into
    '''
    x_serv_command= '''
for serv_num in $(seq 1 1000); do
    if ! (xdpyinfo -display :${serv_num})&>/dev/null; then
        echo "$serv_num" && break
    fi
done
'''
    import subprocess as sp
    # run the command, capture the output
    process = sp.Popen(x_serv_command,stdout=sp.PIPE, shell=True)
    x_serv_port = int(process.communicate()[0].strip())
    return(x_serv_port)

def run_IGV_script(igv_script, igv_jar, memMB, x_serv_num):
    # run the IGV script
    x_serv_num = get_open_X_server()
    igv_command = "(Xvfb :{} &) && DISPLAY=:{} java -Xmx{}m -jar {} -b {} && killall Xvfb".format(x_serv_num, x_serv_num, memMB, igv_jar, igv_script)
    startTime = datetime.now()
    print('\nOpen Xvfb port found on:\n{}\n'.format(x_serv_num))
    print "\nStarting IGV\nCurrent time is:\t", startTime
    print "\nIGV command is:\n", igv_command
    pl.subprocess_cmd(igv_command)
    print "\n\nTime to process completion:\t", datetime.now() - startTime



# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='IGV batchscript runner.')

# positional args
parser.add_argument("batchscript_file", help="Path to the IGV batchscript file to run in IGV")

# optional args
parser.add_argument("-bin", default = "bin/IGV_2.3.81/igv.jar", type = str, dest = 'igv_jar_bin', metavar = 'IGV bin path', help="Path to the IGV jar binary to run")
parser.add_argument("-mem", default = "4000", type = str, dest = 'igv_mem', metavar = 'IGV memory (MB)', help="Amount of memory to allocate to IGV, in Megabytes (MB)")
parser.add_argument("-x", default = "1", type = str, dest = 'x_serv', metavar = 'X server to use for IGV', help="X server to use for IGV")

args = parser.parse_args()

batchscript_file = args.batchscript_file
igv_jar_bin = args.igv_jar_bin
igv_mem = args.igv_mem
x_serv = args.x_serv # this gets ignored



if __name__ == "__main__":
    # ~~~~ RUN BATCH SCRIPT ~~~~~~ #
    print "Now running script:\n", sys.argv[0]
    print "\nbatchscript_file is :\n", batchscript_file
    print "\nigv_jar_bin is :\n", igv_jar_bin
    print "\nigv_mem is :\n", igv_mem
    run_IGV_script(igv_script = batchscript_file, igv_jar = igv_jar_bin, memMB = igv_mem, x_serv_num = x_serv)
