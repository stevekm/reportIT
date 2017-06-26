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

def ssh_exec_command(command):
    '''
    Run a command remotely on the IonTorrent server via ssh, return stdout for parsing
    '''
    import time
    # get the address to the remote IonTorrent server
    server_address = get_server_address()
    # wrap the validation command in an ssh command to execute it remotely
    ssh_command = '''
ssh {0} << EOF
{1}
EOF
'''.format(server_address, command)

    # get the output
    ssh_stdout = subprocess_cmd(ssh_command, return_stdout = True)
    time.sleep(1) # sleep timer so we don't blow up the IT server with requests
    return(ssh_stdout)

def get_remote_run_dirs():
    '''
    Return a list of the run dirs on the remote IonTorrent Server
    '''
    import global_settings
    IT_server_results_home_dir = global_settings.IT_server_results_home_dir # "/results/analysis/output/Home/"

    # build a system command to ssh into the remote server and check the current run dirs
    find_command = '''
find {0} -mindepth 1 -maxdepth 1 -type d
'''.format(IT_server_results_home_dir)

    # get the output
    ssh_stdout = ssh_exec_command(command = find_command)

    # only keep entries that match
    remote_run_dirs = []
    for item in ssh_stdout.split('\n'):
        if item.startswith(IT_server_results_home_dir):
            remote_run_dirs.append(os.path.basename(item))
    return(remote_run_dirs)


def validate_single_file_exists(filepath):
    '''
    Make sure a single file exists on the remote IT server
    '''
    # the ssh command prints a load of junk now after IT server OS upgrade;
    # I need a reference string to print so I know where the command output starts in stdout
    remote_validation_string = "VALIDATIONSTATUS:"

    # the command to run remotely on the IT server via ssh
    # will print out:
    # VALIDATIONSTATUS: True
    remote_validation_command = '''
[ -f "{0}" ] && printf "{1} True" || printf "{1} False"
'''.format(filepath, remote_validation_string)

    # run the command via ssh
    ssh_stdout = ssh_exec_command(command = remote_validation_command)

    # search for the validation line in the stdout
    for line in ssh_stdout.split('\n'):
        if line.startswith(remote_validation_string):
            if len(line.strip().split()) == 2:
                junk, remote_validation_output = line.strip().split()


    if remote_validation_output == "True":
        # print("The run is valid and has finished running on the IT server")
        return(True)
    elif remote_validation_output == "False":
        # print("File 'status.txt' does not exist for the run on the IT server, its not a valid run for downloading")
        return(False)
    else:
        # print("Did not recognize the run status output")
        return(False)


def remote_run_files_exist(run_ID):
    '''
    Check that the run on the remote IT server has desired files present:

    sample .bam files
    sample .vcf files
    ...
    (add more as we find things that are missing)

    Check for 'status.txt' file in the run dir;
    /results/analysis/output/Home/Auto_user_SN2-282-IT17-26-1_375_368/status.txt

    Need to ssh into the remote server to check for the presence of this file
    file only exists if run has finished! Thanks Yang!
    '''
    import global_settings
    run_validations = []

    # place on the remote server where files should be
    remote_results_dir = global_settings.IT_server_results_home_dir # "/results/analysis/output/Home"
    remote_run_dir = remote_results_dir + "/" + run_ID # IonTorrent server is running Linux!

    remote_run_dir_status_file = remote_run_dir + "/status.txt"

    # list of individual files that must exist on the remote run
    single_files = []
    single_files.append(remote_run_dir_status_file)

    for item in single_files:
        run_validations.append(validate_single_file_exists(filepath = item))

    # find ./Auto_user_SN2-281-IT17-25-2_374_367/plugin_out/ -name "*.bam" ! -name "*rawlib*" | wc -l

    if all(run_validations):
        return(True)
    else:
        return(False)




def validate_remote_run_completion(run_ID):
    '''
    Check the run on the remote IonTorrent server to determine if the run has finished
    '''
    import time
    import global_settings
    run_validations = []
    run_complete = False

    run_validations.append(remote_run_files_exist(run_ID = run_ID))


    # all are True
    if all(run_validations):
        return(True)
    else:
        return(False)



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

    print("\nmissing_runs:")
    print(missing_runs)
    print('\n')
    for item in missing_runs:
        if validate_remote_run_completion(run_ID = item) == True:
            validated_missing_runs.append(item)

    print("\nvalidated_missing_runs:")
    print(validated_missing_runs)
    print('\n')

    if len(validated_missing_runs) > 0:
        print('Missing runs available for download:')
        for item in validated_missing_runs:
            print(item)
        print('\n')
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
