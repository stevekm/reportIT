#!/usr/bin/env python
# python 2.7


def my_debugger(vars):
    # starts interactive Python terminal at location in script
    # call with pl.my_debugger(globals().copy()) anywhere in your script
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
