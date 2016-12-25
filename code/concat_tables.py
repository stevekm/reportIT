#!/usr/bin/env python
# python 2.7

'''
USAGE: 
FILES="$(find some_dir/ -name "*file.tsv")"
concat_tables.py $FILES > output_table.tsv

DESCRIPTION: This script will concatenate multiple flat text 
based tables which have a common 1-line header

bash equivalent:
$ head -1 $(echo $FILES | cut -d ' ' -f1) > test_output.tsv
$ for i in $FILES; do tail -n +2 "$i" >> test_output.tsv; done
'''

# ~~~~ LOAD PACKAGES ~~~~~~ #
import sys
import os
import errno
import re
import argparse

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def my_debugger():
    # starts interactive Python terminal at location in script
    # call with my_debugger() anywhere in your script
    import readline # optional, will allow Up/Down/History in the console
    import code
    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()

def initialize_file(string, output_file):
    # write string to file, overwriting contents
    with open(output_file, "w") as myfile:
        myfile.write(string + '\n')

def append_string(string, output_file):
    # append string to file
    # append_string(get_file_lines(header_file, [1]), output_file)
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')

def get_file_lines(file, line_nums_list):
    # return a list of lines from file matching list of line indexes
  return [x for i, x in enumerate(open(file)) if i in line_nums_list]

def count_file_lines(file):
    # count the number of lines in the file
    return sum(1 for line in open(file))

def print_header_to_output(header_file):
    # get the first line from file and print it to stdout
    line_nums_list = [0]
    sys.stdout.write(get_file_lines(file = header_file, line_nums_list = line_nums_list)[0])

def print_file_minus_header(file):
    # print all lines in file except for header line
    num_lines = count_file_lines(file)
    for line in get_file_lines(file = file, line_nums_list = range(1, num_lines)):
        sys.stdout.write(line)



# ~~~~ GET SCRIPT ARGS ~~~~~~ #
parser = argparse.ArgumentParser(description='This script will concatenate multiple table files with a common header')

# positional args
parser.add_argument("file_list", help="Paths to input table files", nargs="+")

# optional args
# parser.add_argument("-o", default = "output.txt", type = str, dest = 'output_file', metavar = 'Table output file', help="Path to the output table file")

args = parser.parse_args()

file_list = args.file_list
# output_file = args.output_file

if __name__ == "__main__":
    # print header from the first file
    print_header_to_output(header_file = file_list[0])
    # print all lines except header from all other files
    for file in file_list:
        print_file_minus_header(file = file)






