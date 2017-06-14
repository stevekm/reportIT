#!/usr/bin/env python
# tested on python 2.7

'''
functions for using 'qsub' in Python
'''


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


def get_qsub_job_ID_name(proc_stdout):
    '''
    return a tuple of the form (<id number>, <job name>)
    usage:
    proc_stdout = submit_qsub_job(return_stdout = True) # 'Your job 1245023 ("python") has been submitted'
    job_id, job_name = get_qsub_job_ID_name(proc_stdout)
    '''
    import re
    proc_stdout_list = proc_stdout.split()
    job_id = proc_stdout_list[2]
    job_name = proc_stdout_list[3]
    job_name = re.sub(r'^\("', '', str(job_name))
    job_name = re.sub(r'"\)$', '', str(job_name))
    return((job_id, job_name))


def submit_qsub_job(command = 'echo foo', params = '-j y', name = "python", stdout_log_dir = '${PWD}', stderr_log_dir = '${PWD}', return_stdout = False, verbose = False):
    '''
    submit a job to the SGE cluster with qsub
    '''
    import subprocess
    qsub_command = '''
qsub {0} -N {1} -o :{2}/ -e :{3}/ <<E0F
{4}
E0F
'''.format(params, name, stdout_log_dir, stderr_log_dir, command)
    if verbose == True:
        print('Command is:\n{0}'.format(qsub_command))
    proc_stdout = subprocess_cmd(command = qsub_command, return_stdout = True)
    if return_stdout == True:
        return(proc_stdout)
    elif return_stdout == False:
        print(proc_stdout)

def check_qsub_job_status(job_id, desired_status = "r"):
    '''
    Use 'qstat' to check on the run status of a qsub job
    returns True or False if the job status matches the desired_status
    job running:
    desired_status = "r"
    job waiting:
    desired_status = "qw"
    '''
    import re
    from sh import qstat
    job_id_pattern = r"^.*{0}.*\s{1}\s.*$".format(job_id, desired_status)
    # using the 'sh' package
    qstat_stdout = qstat()
    # using the standard subprocess package
    # qstat_stdout = subprocess_cmd('qstat', return_stdout = True)
    job_match = re.findall(str(job_id_pattern), str(qstat_stdout), re.MULTILINE)
    job_status = bool(job_match)
    if job_status == True:
        status = True
        return(job_status)
    elif job_status == False:
        return(job_status)

def wait_qsub_job_start(job_id, return_True = False):
    '''
    Monitor the output of 'qstat' to determine if a job is running or not
    equivalent of
    '''
    from time import sleep
    import sys
    print('waiting for job to start')
    while check_qsub_job_status(job_id = job_id, desired_status = "r") != True:
        sys.stdout.write('.')
        sys.stdout.flush()
        sleep(3) # Time in seconds.
    print('')
    if check_qsub_job_status(job_id = job_id, desired_status = "r") == True:
        print('job {0} has started'.format(job_id))
        if return_True == True:
            return(True)

def wait_all_jobs_start(job_id_list):
    '''
    Wait for every job in a list to start
    '''
    import datetime
    from time import sleep
    import sys
    jobs_started = False
    startTime = datetime.datetime.now()
    print("\nwaiting for all jobs {0} to start...".format(job_id_list))
    while not all([check_qsub_job_status(job_id = job_id, desired_status = "r") for job_id in job_id_list]):
        sys.stdout.write('.')
        sys.stdout.flush()
        sleep(3) # Time in seconds.
    elapsed_time = datetime.datetime.now() - startTime
    print("all jobs have started; elapsed time: {0}".format(elapsed_time))
    if all([check_qsub_job_status(job_id = job_id, desired_status = "r") for job_id in job_id_list]):
        jobs_started = True
    return(jobs_started)

def check_qsub_job_absent(job_id):
    '''
    Check that a single job is not in the 'qstat' list
    '''
    import re
    from sh import qstat
    qstat_stdout = qstat()
    job_id_pattern = r"^.*{0}.*$".format(job_id)
    job_match = re.findall(str(job_id_pattern), str(qstat_stdout), re.MULTILINE)
    job_status = bool(job_match)
    if job_status == True:
        return(False)
    elif job_status == False:
        return(True)


def wait_all_jobs_finished(job_id_list):
    '''
    Wait for all jobs in the list to finish
    A finished job is no longer present in the 'qstat' list
    '''
    import datetime
    from time import sleep
    import sys
    jobs_finished = False
    startTime = datetime.datetime.now()
    print("\nwaiting for all jobs {0} to finish...".format(job_id_list))
    while not all([check_qsub_job_absent(job_id = job_id) for job_id in job_id_list]):
        sys.stdout.write('.')
        sys.stdout.flush()
        sleep(3) # Time in seconds.
    elapsed_time = datetime.datetime.now() - startTime
    print("all jobs have finished; elapsed time: {0}".format(elapsed_time))
    if all([check_qsub_job_absent(job_id = job_id) for job_id in job_id_list]):
        jobs_finished = True
    return(jobs_finished)

def demo_qsub():
    '''
    Demo the qsub code functions
    '''
    command = '''
    set -x
    cat /etc/hosts
    sleep 300
    '''
    proc_stdout = submit_qsub_job(command = command, verbose = True, return_stdout = True)
    job_id, job_name = get_qsub_job_ID_name(proc_stdout)
    print('Job ID: {0}'.format(job_id))
    print('Job Name: {0}'.format(job_name))
    wait_qsub_job_start(job_id)

def demo_multi_qsub():
    '''
    Demo the qsub code functions
    '''
    command = '''
    set -x
    cat /etc/hosts
    sleep 30
    '''
    job_id_list = []
    for i in range(5):
        proc_stdout = submit_qsub_job(command = command, verbose = True, return_stdout = True)
        job_id, job_name = get_qsub_job_ID_name(proc_stdout)
        print("Job submitted...")
        print('Job ID: {0}'.format(job_id))
        print('Job Name: {0}'.format(job_name))
        print("")
        job_id_list.append(job_id)
    wait_all_jobs_start(job_id_list)
    wait_all_jobs_finished(job_id_list)
