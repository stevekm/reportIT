#!/usr/bin/env python

'''
This script will output all lines from the first file, and all missing lines from subsequent files
Lines are written to std.out for piping.
'''

# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys
import os
import argparse
from argparse import RawDescriptionHelpFormatter
from collections import OrderedDict

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def get_rolled_lines(file_list):
    # get lines from the first file
    first_file = file_list.pop(0)
    file_lines = [line for line in open(first_file)]
    # get missing lines from the other files
    for file in input_files:
        missing_lines = [line for line in open(file) if line not in file_lines]
        for line in missing_lines: file_lines.append(line)
    return(file_lines)


# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='''
File Roller: Roll up all lines in all files.

This script will output all lines from the first file, and all missing lines from subsequent files.

Notes:
Lines are written to std.out for piping.
By default, duplicates are only preserved in the first file.
Run time may greatly increase for large files when using '-u' and '-s' parameters.
''', formatter_class=RawDescriptionHelpFormatter)

# required positional args
parser.add_argument("input_files", nargs='+', help="path to input files")

# optional flags
parser.add_argument("-u", default = False, action='store_true', dest = 'unique_flag', help="Whether only unique lines should be output; remove duplicates")
parser.add_argument("-s", default = False, action='store_true', dest = 'sort_flag', help="Whether to sort the output lines")

args = parser.parse_args()
input_files = args.input_files
unique_flag = args.unique_flag
sort_flag = args.sort_flag


if __name__ == "__main__":
    file_lines = get_rolled_lines(input_files)
    # remove duplicates, preserve order
    if unique_flag == True:
        file_lines = list(OrderedDict.fromkeys(file_lines))
    # sort the lines
    if sort_flag == True:
        file_lines.sort()
    # print all the lines
    for line in file_lines:
        sys.stdout.write(line)
