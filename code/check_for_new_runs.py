#!/usr/bin/env python

'''
This script will check the IonTorrent server for new runs to be processed

Requires ssh key authentication set up for current user on the IT server with
the default login account!
'''
import os
import pipeline_functions as pl
import global_settings
import argparse


def subprocess_cmd(command, return_stdout = False):
    # run a terminal command with stdout piping enabled
    import subprocess as sp
    process = sp.Popen(command,stdout=sp.PIPE, shell=True, universal_newlines=True)
     # universal_newlines=True required for Python 2 3 compatibility with stdout parsing
     # https://stackoverflow.com/a/27775464/5359531
    proc_stdout = process.communicate()[0].strip()
    if return_stdout == True:
        return(proc_stdout)
    elif return_stdout == False:
        print(proc_stdout)


def get_server_address():
    '''
    Get the server address from the file
    '''
    # check for the server settings to login to the IT server
    server_addresses = pl.list_file_lines(global_settings.server_info_file)

    # make sure at least one value was passed
    check_len = pl.check_list_len_greaterthan_equal(server_addresses, min_size = 1)
    pl.kill_on_false(mybool = check_len, my_message = "ERROR: Server address file did not have at least 1 entry")

    # only keep the first value
    server_address = server_addresses[0]
    return(server_address)

def get_remote_run_dirs():
    '''
    Return a list of the run dirs on the remote IonTorrent Server
    '''
    # get the address to the remote server
    server_address = get_server_address()

    # build a system command to ssh into the remote server and check the current run dirs
    ssh_command = '''
ssh {0} << EOF
find /results/analysis/output/Home/ -mindepth 1 -maxdepth 1 -type d
EOF
'''.format(server_address)

    # get the output
    ssh_stdout = subprocess_cmd(ssh_command, return_stdout = True)

    # only keep entries that match
    remote_run_dirs = []
    for item in ssh_stdout.split('\n'):
        if item.startswith('/results/analysis/output/Home/'):
            remote_run_dirs.append(os.path.basename(item))
    return(remote_run_dirs)

def validate_remote_run_completion(run_ID):
    '''
    Check the run on the remote IonTorrent server to determine if the run has finished
    '''
    import time
    run_complete = False

    # print("now validating run: {0}".format(run_ID))
    # get the address to the remote server
    server_address = get_server_address()
    # build a system command to ssh into the remote server and check the current run dirs
    remote_results_dir = "/results/analysis/output/Home"
    remote_run_dir = remote_results_dir + "/" + run_ID # IonTorrent server is running Linux
    remote_run_dir_status_file = remote_run_dir + "/status.txt" # only exists if run has finished! Thanks Yang!

    ssh_command = '''
ssh {0} << EOF
python -c 'import os; print(os.path.exists("{1}"))'
EOF
'''.format(server_address, remote_run_dir_status_file)

    # get the output
    ssh_stdout = subprocess_cmd(ssh_command, return_stdout = True)
    time.sleep(1) # sleep timer so we don't blow up the IT server with requests

    if ssh_stdout == "True":
        # print("The run is valid and has finished running on the IT server")
        run_complete = True
        return(run_complete)
    elif ssh_stdout == "False":
        # print("File 'status.txt' does not exist for the run on the IT server, its not a valid run for downloading")
        return(run_complete)
    else:
        # print("Did not recognize the run status output")
        return(run_complete)


def get_local_run_dirs():
    '''
    Check for locally held IonTorrent runs
    '''
    local_output_dir = global_settings.outdir
    run_dirs = []
    for item in os.listdir(local_output_dir):
        item_path = os.path.join(local_output_dir, item)
        if os.path.isdir(item_path):
            run_dirs.append(os.path.basename(item_path))
    return(run_dirs)


def make_samplesheet_for_missing_runs(missing_runs):
    '''
    Make a samplesheet for the missing runs
    '''
    import make_samplesheet
    samplesheet_dir = global_settings.samplesheet_dir
    samplesheet_file = make_samplesheet.make_default_samplesheet_filepath(samplesheet_dir)
    # make a samplesheet for just individual runs
    # use the returned final samplesheet path
    print('Making Samplesheet')
    samplesheet_file = make_samplesheet.main(analysis_IDs = missing_runs, samplesheet_file = samplesheet_file, analysis_ID_pair = None, return_path = True)
    print('Samplesheet file is: {0}'.format(samplesheet_file))
    return(samplesheet_file)

def download_runs(samplesheet_file, debug_mode = False):
    '''
    Download the runs from the samplesheet
    '''
    import run_samplesheet
    run_samplesheet.main(samplesheet_file = samplesheet_file, download = True, debug_mode = debug_mode)


def main(download = False, debug_mode = False):
    '''
    Main control function for the program
    '''
    remote_run_dirs = get_remote_run_dirs()
    local_run_dirs = get_local_run_dirs()
    missing_runs = []
    validated_missing_runs = []

    for item in remote_run_dirs:
        if item not in local_run_dirs:
            missing_runs.append(item)

    for item in missing_runs:
        if validate_remote_run_completion(run_ID = item) == True:
            validated_missing_runs.append(item)

    if len(validated_missing_runs) > 0:
        print('Missing runs available for download:')
        for item in validated_missing_runs:
            print(item)
        samplesheet_file = make_samplesheet_for_missing_runs(missing_runs = validated_missing_runs)
        if download == True:
            download_runs(samplesheet_file = samplesheet_file, debug_mode = debug_mode)
    else:
        print("No missing runs found. ")



def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    parser = argparse.ArgumentParser(description='This script will run the reportIT pipeline and check for new runs, optionally downloading them.')
    # optional args
    parser.add_argument("-d", default = False, action='store_true', dest = 'download',  help="whether the analyses should be downloaded from the IonTorrent server")
    parser.add_argument("--debug", default = False, action='store_true', dest = 'debug_mode',  help="Skip git branch checking when running")
    args = parser.parse_args()
    download = args.download
    debug_mode = args.debug_mode
    main(download = download, debug_mode = debug_mode)


if __name__ == "__main__":
    run()
