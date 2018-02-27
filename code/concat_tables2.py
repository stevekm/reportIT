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
import argparse

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def file_len(fname):
    """
    Counts the number of lines in a file
    """
    with open(fname) as f:
        num_lines = sum(1 for line in f)
    return(num_lines)

def append_string(string, output_file):
    '''
    append string to file
    '''
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')

def get_lines(file_list):
    """
    Print the first line from the first file, then print all lines except the first from all subsequent files

    """
    with open(file_list[0]) as f:
        for line in f:
            yield(line)
            break
    for input_file in file_list:
        num_lines = file_len(input_file)
        if num_lines > 0:
            with open(input_file) as f:
                next(f)
                for line in f:
                    yield(line)


def main(file_list, output_file = False):
    """
    Main control function for the program. Concatenates all files passed and prints output to stdout

    Parameters
    ----------
    file_list: list
        list of paths to files to be concatenated
    """
    for line in get_lines(file_list):
        if output_file:
            append_string(string = line, output_file = output_file)
        else:
            sys.stdout.write(line)

def parse():
    """
    parse script args and pass them to `main`
    """
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    parser = argparse.ArgumentParser(description='This script will concatenate multiple table files with a common header')

    # positional args
    parser.add_argument("file_list", help="Paths to input table files", nargs="+")

    # optional args
    parser.add_argument("-o", default = False, dest = 'output_file', metavar = 'Table output file', help="Path to the output table file")

    args = parser.parse_args()

    file_list = args.file_list
    output_file = args.output_file
    main(file_list, output_file)

if __name__ == "__main__":
    parse()
