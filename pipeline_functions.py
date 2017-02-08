#!/usr/bin/env python
# python 2.7


def my_debugger(vars):
    # starts interactive Python terminal at location in script
    # call with pl.my_debugger(globals().copy()) anywhere in your script
    # or call my_debugger(locals().copy()) from anywhere within this package
    import readline # optional, will allow Up/Down/History in the console
    import code
    # vars = globals().copy() # in python "global" variables are actually module-level
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()

def mkdir_p(path, return_path=False):
    # make a directory, and all parent dir's in the path
    import sys
    import os
    import errno

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    if return_path:
        return path

def initialize_file(string, output_file):
    # write string to file
    # !! THIS WILL OVERWRITE CONTENTS !!
    with open(output_file, "w") as myfile:
        myfile.write(string + '\n')

def append_string(string, output_file):
    # append string to file
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')

def subprocess_cmd(command):
    # run a terminal command with stdout piping enabled
    import subprocess as sp
    process = sp.Popen(command,stdout=sp.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout


def get_files(dir_path, ends_with = '', trunc = False):
    # get the files in the dir that match the end pattern
    # trunc : return just the file dirname + basename (truncate)
    import sys
    import os
    file_list = []
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(ends_with):
                file_path = os.path.join(subdir,file)
                if (trunc):
                    file_dir = os.path.basename(os.path.dirname(file_path))
                    file_base = os.path.basename(file_path)
                    file_path = os.path.join(file_dir,file_base)
                file_list.append(file_path)
    return file_list


def download_file(my_URL, my_outfile = ''):
    # function to download a file from a URL
    # !! This will overwrite the output file
    # https://gist.github.com/hughdbrown/c145b8385a2afa6570e2

    import urllib2
    import urlparse
    import os

    URL_basename = os.path.basename(urlparse.urlsplit(my_URL).path)

    # if no output file specified, save to URL filename in current dir
    if my_outfile == '':
        my_outfile = URL_basename

    my_URL = urllib2.urlopen(my_URL)
    with open(my_outfile, 'wb') as output:
        while True:
            data = my_URL.read(4096) # download in chunks
            if data:
                output.write(data)
            else:
                break



def py_unzip(zip_file, outdir = "."):
    zip_ref = zipfile.ZipFile(zip_file, 'r')
    zip_ref.extractall(outdir)
    zip_ref.close()

def gz_unzip(gz_file, outdir = '', outfile = '', return_path = False):
    import gzip
    import os
    # extract a .gz file
    # !! This reads the entire file into memory !!

    # make sure the input file is a .gz file
    if not gz_file.lower().endswith('.gz'):
        print "ERROR: File is not a .gz file; ", gz_file
        return

    # read in the contents
    input_file = gzip.GzipFile(gz_file, 'rb')
    file_contents = input_file.read()
    input_file.close()

    # set the output path
    output_file_path = os.path.splitext(gz_file)[0]

    # if an outdir was passed, save the output there instead
    if outdir != '':
        output_file_path = os.path.join(outdir, os.path.basename(output_file_path))

    # if an output file was passed, use that instead
    if outfile != '':
        output_file_path = outfile

    # write the contents
    output_file = open(output_file_path, 'wb')
    output_file.write(file_contents)
    output_file.close()

    # return the path if requested
    if return_path:
        if os.path.exists(output_file_path):
            return output_file_path


def dict_from_tabular(inputfile, sep = ','):
    import csv
    lines_dict = {}
    reader = csv.reader(open(inputfile, 'r'), delimiter=sep)
    for key, value in reader:
        lines_dict[key] = value
    return lines_dict
