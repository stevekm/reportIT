#!/usr/bin/env python

'''
USAGE: run_parser.py <analysis ID> <analysis ID> <analysis ID> ...

This script will look for BAM files in analysis output directories and run the IGV snapshot automator on them

1. Get list of analysis IDs for projects to process
2. for each ID:
    - get list of samples in the coverage dir
    - check for presence of NC sample either in current run or another run paired with current run
3. for each sample in the coverage dir:
    - run IGV snapshot on sample BAM file
    - include NC BAM file if found
'''
import sys
import os
import csv
import argparse
import pipeline_functions as pl
import global_settings
import run_IGV_snapshot_automator

def find_coverage_samples(parent_dir):
    '''
    Find the samples listed in the coverage dir
    , item_type = "d", pattern = "*coverageAnalysis_out*"

    return dict of barcode:path to sample coverage dirs
    '''
    import os
    import fnmatch
    coverage_dir = ''
    # find the coverage dir, ex: coverageAnalysis_out.1052
    for root, dirs, files in os.walk(parent_dir):
        for dir in dirs:
            if fnmatch.fnmatch(dir, "*coverageAnalysis_out*"):
                coverage_dir = os.path.join(root, dir)
                break

    # make sure a results was found
    pl.dir_exists(coverage_dir, kill = True)

    # get the samples in the coverage dir
    samples = []
    for root, dirs, files in os.walk(coverage_dir):
        for dir in dirs:
            if fnmatch.fnmatch(dir, "IonXpress_*"): # IonXpress_002
                samples.append(os.path.join(root, dir))

    # make sure samples were found
    pl.kill_on_false(pl.check_list_len_greaterthan(mylist = samples, min_size = 1, my_message = "ERROR: No samples were found! Cannot run IGV snapshots"))

    # return dict of results
    results = {}
    for sample in samples:
        barcode = os.path.basename(sample)
        results[barcode] = sample
    return(results)


def find_analysis_barcode_file(parent_dir):
    '''
    Find the barcodes file for the analysis
    # analysis_barcode_file="$(find "$analysis_outdir"  -path "*variantCaller_out*" -name "sample_barcode_IDs.tsv" | head -1)"
    '''
    import os
    import fnmatch
    analysis_barcode_file = None
    for root, dirs, files in os.walk(parent_dir):
        if fnmatch.fnmatch(root, "*variantCaller_out*"):
            for file in files:
                if fnmatch.fnmatch(file, "sample_barcode_IDs.tsv"):
                    analysis_barcode_file = os.path.join(root, file)
                    break
    # make sure file exists
    if analysis_barcode_file == None:
        print("ERROR: Analysis barcode file not found")
    pl.file_exists(analysis_barcode_file, kill = True)
    return(analysis_barcode_file)

def find_combined_sample_barcode_IDs_file(analysis_dir):
    '''
    Search the analysis dir for file: combined_analysis/combined_sample_barcode_IDs.tsv
    this indicates that it is a paired analysis and the NC sample bam may be in the other analysis
    '''
    import os
    import fnmatch
    combined_sample_barcode_IDs_file = None
    for root, dirs, files in os.walk(analysis_dir):
        if fnmatch.fnmatch(root, "*combined_analysis*"):
            for file in files:
                if fnmatch.fnmatch(file, "combined_sample_barcode_IDs.tsv"):
                    combined_sample_barcode_IDs_file = os.path.join(root, file)
                    break
    return(combined_sample_barcode_IDs_file)


def find_analysis_coverage_dir(analysis_dir):
    '''
    Find the coverage dir for an analysis
    ex: coverageAnalysis_out.1052
    '''
    import os
    import fnmatch
    coverage_dir = None
    for root, dirs, files in os.walk(analysis_dir):
        for dir in dirs:
            if fnmatch.fnmatch(dir, "*coverageAnalysis_out*"):
                coverage_dir = os.path.join(root, dir)
                return(coverage_dir)
    if coverage_dir == None:
        pl.kill_on_false(False, my_message = "ERROR: Analysis coverage dir not found!")

def find_analysis_variant_dir(analysis_dir):
    '''
    Find the variant dir for an analysis
    ex: variantCaller_out.1046
    '''
    import os
    import fnmatch
    variant_dir = None
    for root, dirs, files in os.walk(analysis_dir):
        for dir in dirs:
            if fnmatch.fnmatch(dir, "*variantCaller_out*"):
                variant_dir = os.path.join(root, dir)
                return(variant_dir)
    if variant_dir == None:
        pl.kill_on_false(False, my_message = "ERROR: Analysis coverage dir not found!")

def find_sample_variant_dir(variant_dir, barcode):
    '''
    Find the parent variant dir containing the varaint files for the sample
    '''
    import os
    import fnmatch
    for root, dirs, files in os.walk(variant_dir):
        for dir in dirs:
            if fnmatch.fnmatch(dir, "*{0}*".format(barcode)):
                return(os.path.join(root, dir))


def find_sample_summary_table(analysis_outdir, barcode):
    '''
    Find the "IonXpress_009_summary.tsv" file for a sample
    '''
    import os
    import fnmatch
    variant_dir = find_analysis_variant_dir(analysis_outdir)
    sample_variant_dir = find_sample_variant_dir(variant_dir, barcode)
    for root, dirs, files in os.walk(sample_variant_dir):
        for file in files:
            if fnmatch.fnmatch(file, "*_summary.tsv"):
                return(os.path.join(root, file))


def find_sample_bam_dir(coverage_dir, barcode):
    '''
    Find the parent coverage dir containing the bam file for the sample
    '''
    import os
    import fnmatch
    for root, dirs, files in os.walk(coverage_dir):
        for dir in dirs:
            if fnmatch.fnmatch(dir, "*{0}*".format(barcode)):
                return(os.path.join(root, dir))

def find_sample_bam(analysis_outdir, barcode):
    '''
    Find the .bam file for a sample
    '''
    import os
    import fnmatch
    coverage_dir = find_analysis_coverage_dir(analysis_outdir)
    sample_bam_dir = find_sample_bam_dir(coverage_dir, barcode)
    for root, dirs, files in os.walk(sample_bam_dir):
        for file in files:
            if fnmatch.fnmatch(file, "*.bam"):
                return(os.path.join(root, file))


def get_analysis_barcode_index(analysis_barcode_file):
    '''
    Return a list of dictionaries containing the items from the analysis index file
    '''
    analysis_barcode_index = []
    with open(analysis_barcode_file, 'r') as tsvin:
        reader = csv.DictReader(tsvin, delimiter='\t')
        for item in reader:
            analysis_barcode_index.append(item)
    pl.kill_on_false(pl.check_list_len_greaterthan(mylist = analysis_barcode_index, min_size = 1, my_message = "ERROR: No samples were found in the analysis barcode index file! Cannot run IGV snapshots"))
    return(analysis_barcode_index)

def get_combined_sample_barcode_IDs_index(combined_sample_barcode_IDs_file):
    '''
    Return a list of dictionaries contaiing the items from the combined_sample_barcode_IDs_file, if present
    '''
    if combined_sample_barcode_IDs_file == None:
        return(None)
    elif combined_sample_barcode_IDs_file != None:
        combined_sample_barcode_IDs_index = []
        with open(combined_sample_barcode_IDs_file, 'r') as tsvin:
            reader = csv.DictReader(tsvin, delimiter='\t')
            for item in reader:
                combined_sample_barcode_IDs_index.append(item)
        pl.kill_on_false(pl.check_list_len_greaterthan(mylist = combined_sample_barcode_IDs_index, min_size = 1, my_message = "ERROR: No samples were found in the combined sample barcode IDs file! Cannot run IGV snapshots"))
        return(combined_sample_barcode_IDs_index)


def get_control_sample_IDs():
    '''
    Get the sample ID's that are known to be control samples
    from the saved .txt file
    '''
    return(pl.list_file_lines(global_settings.control_sample_ID_file))

def find_NC_control_sample(analysis_ID, analysis_barcode_index, combined_sample_barcode_IDs_index):
    '''
    Parse the analysis_barcode_index list of dicts to find the sample that matches the NC sample ID's for the run
    If a match is found, returns (index, barcode, sample name)
    otherwise returns None
    '''
    import re
    import copy
    # # # # # # #
    # Set up the NC Sample ID search params
    # # # # # # #
    # mess with this if I need to do this kind of matching again later; trying to convert the file contents grep regex to Python regex dynamically...
    # # # # # ## #
    # NC_sampleID_patterns = pl.list_file_lines(global_settings.control_sample_regex_file)
    # # # ['^NC[[:space:]]', '^NC[[:space:]]HAPMAP[[:space:]]', '^HAPMAP[[:space:]]'] # # file contents grep regex
    # NC_sampleID_patterns = [re.escape(item.replace(r'[[:space:]]', r'\s')) for item in NC_sampleID_patterns]
    # NC_sampleID_patterns = [r'{0}'.format(item) for item in NC_sampleID_patterns]
    # NC_sampleID_patterns = [item.replace(r'[[:space:]]', r'\s' ) for item in NC_sampleID_patterns]
    # NC_sampleID_patterns = r'|'.join(NC_sampleID_patterns)
    # # # no trailing [[:space:]] because reading in the items strips them out
    NC_sampleID_patterns_regex = r'^NC|^NC\sHAPMAP|^HAPMAP'
    NC_sampleID_patterns = re.compile(NC_sampleID_patterns_regex, re.IGNORECASE)

    # first search the combined_sample_barcode_IDs_index
    if combined_sample_barcode_IDs_index != None:
        for i, item in enumerate(combined_sample_barcode_IDs_index):
            sample_name = item['Sample Name']
            match = re.match(NC_sampleID_patterns, sample_name)
            if match is not None:
                result = copy.deepcopy(item)
                result['NC_sampleID_patterns_regex'] = NC_sampleID_patterns_regex
                result['found_in_current_run'] = False
                result['found_in_paired_run'] = True
                return(result)

    # next search the analysis_barcode_index
    for i, item in enumerate(analysis_barcode_index):
        sample_name = item['Sample Name']
        match = re.match(NC_sampleID_patterns, sample_name)
        if match is not None:
            result = copy.deepcopy(item)
            result['NC_sampleID_patterns_regex'] = NC_sampleID_patterns_regex
            result['Analysis ID'] = analysis_ID # not present in the analysis_barcode_index but required later
            result['found_in_current_run'] = True
            result['found_in_paired_run'] = False
            return(result)
    # else, return None
    return(None)

def test_for_paired_analysis(analysis_outdir):
    '''
    Check if an analysis was a paired analysis
    by searching for the combined_sample_barcode_IDs.tsv file
    '''
    is_paired = False
    combined_sample_barcode_IDs_file = None
    combined_sample_barcode_IDs_file = find_combined_sample_barcode_IDs_file(analysis_outdir)
    if combined_sample_barcode_IDs_file != None:
        is_paired = True
    return((is_paired, combined_sample_barcode_IDs_file))

def test_for_control_sample(analysis_barcode_index, control_sample_IDs):
    '''
    Evalutate each 'Sample Name' in dict list coverage_samples to determine if it matches an entry in list of known control_sample_IDs
    If an entry matches a known control sample, remove it from the dict of coverage samples

    This lets us exclude known control samples from being snapshotted later, since controls dont need snapshots on their own
    '''
    for item in analysis_barcode_index:
        barcode = item['Barcode']
        sample_ID = item['Sample Name']
        if sample_ID in control_sample_IDs:
            item['is_control_sample'] = True
        elif sample_ID not in control_sample_IDs:
            item['is_control_sample'] = False
    return(analysis_barcode_index)

def make_sample_IGV_dir(analysis_outdir, barcode, return_path = True):
    '''
    Create the IGV snapshot dir for a sample
    '''
    import os
    coverage_dir = find_analysis_coverage_dir(analysis_outdir)
    sample_bam_dir = find_sample_bam_dir(coverage_dir, barcode)
    IGV_snapshots_dir = pl.mkdir_p(os.path.join(sample_bam_dir, 'IGV_snapshots'), return_path = True)
    if return_path == True:
        return(IGV_snapshots_dir)

def check_for_IGV_long_regions_snapshot(sample_summary_table, min_frequency = 1):
    '''
    return path to the long regions file, or None
    (file doesnt exist yet we will write to it later)

    For variants in a sample with a Frequency < 0.25, a 'long' snapshot should be made in IGV
    In order to do this, we need to make a second regions BED file, so that we can embed 'long' snapshot names in it later
    in run_IGV_snapshot_automator.py
    To do this, we need to look at the 'Frequency' entry for each variant in the sample summary table
    if any variants have a low Frequency, then we will need a separate regions file for it
    This function will check if any variants from the sample summary table have low freq and if so, list this in the sample metadata

    # summary_df.ix[summary_df.ix[:,'Frequency'] < 0.25]

    NOTE: See 'summary_table_to_bed_long' function in run_IGV_snapshot_automator.py
    UPDATE: Naima wants long snapshots for ALL variants from now on.
    '''
    needs_long_regions_file = False
    any_variant_has_low_freq = False
    print("\nChecking {0} for low frequency variants that will need long snapshots".format(sample_summary_table))
    # make sure the variant table has at least 2 lines; 1 header, one entry
    min_lines = 2
    test_pass = pl.file_min_lines(file_path = sample_summary_table, min_lines = min_lines)
    if test_pass == False:
        print("File {0} has less than {1} lines and should not be used for IGV snapshots.".format(sample_summary_table, min_lines))
        return(needs_long_regions_file)
    elif test_pass == True:
        # check if ANY variants have low frequency
        with open(sample_summary_table, 'r') as tsvin:
            reader = csv.DictReader(tsvin, delimiter='\t')
            for row in reader:
                if float(row['Frequency']) < min_frequency:
                    any_variant_has_low_freq = True
        print("Low frequency variants present in sample: {0}".format(any_variant_has_low_freq))
    if any_variant_has_low_freq == True:
        needs_long_regions_file = True
    return(needs_long_regions_file)



def find_sample_files(analysis_outdir, sample):
    '''
    Find the files for a single sample
    sample is a dict that should have a Barcode
    '''
    barcode = sample['Barcode']
    coverage_dir = find_analysis_coverage_dir(analysis_outdir)
    variant_dir = find_analysis_variant_dir(analysis_outdir)
    sample_variant_dir = find_sample_variant_dir(variant_dir, barcode)
    sample_summary_table = find_sample_summary_table(analysis_outdir = analysis_outdir, barcode = barcode)
    sample_bam_dir = find_sample_bam_dir(coverage_dir, barcode)
    sample_bam_file = find_sample_bam(analysis_outdir = analysis_outdir, barcode = barcode)
    IGV_snapshots_dir = make_sample_IGV_dir(analysis_outdir = analysis_outdir, barcode = barcode)
    IGV_regions_file = os.path.join(IGV_snapshots_dir, "regions.bed") # doesnt exist yet will fill out later

    needs_long_regions_file = check_for_IGV_long_regions_snapshot(sample_summary_table)
    if needs_long_regions_file == True:
        IGV_regions_file_long = os.path.join(IGV_snapshots_dir, "regions_long.bed")
    elif needs_long_regions_file == False:
        IGV_regions_file_long = None

    sample['variant_dir'] = variant_dir
    sample['sample_summary_table'] = sample_summary_table
    sample['sample_variant_dir'] = sample_variant_dir
    sample['coverage_dir'] = coverage_dir
    sample['sample_bam_dir'] = sample_bam_dir
    sample['sample_bam_file'] = sample_bam_file
    sample['IGV_snapshots_dir'] = IGV_snapshots_dir
    sample['IGV_regions_file'] = IGV_regions_file
    sample['IGV_regions_file_long'] = IGV_regions_file_long
    return(sample)


def find_coverage_samples_files(analysis_outdir, coverage_samples):
    '''
    Find the files and dirs for each of the coverage samples
    coverage_samples is a list of dicts
    '''
    for item in coverage_samples:
        item = find_sample_files(analysis_outdir, sample = item)
    return(coverage_samples)

def find_NC_control_sample_files(analysis_outdir, NC_control_sample):
    '''
    Find the files related to the NC control sample
    NC_control_sample is a dict, or None
    '''
    if NC_control_sample != None:
        if NC_control_sample['found_in_current_run'] == True:
            NC_control_sample = find_sample_files(analysis_outdir = analysis_outdir, sample = NC_control_sample)
        elif NC_control_sample['found_in_current_run'] == False:
            if 'Analysis ID' in NC_control_sample.keys():
                analysis_ID = NC_control_sample['Analysis ID']
                NC_analysis_outdir = pl.dir_exists(os.path.join(global_settings.outdir, analysis_ID), kill = True, return_path = True)
                NC_control_sample = find_sample_files(analysis_outdir = NC_analysis_outdir, sample = NC_control_sample)
        else:
            print('WARNING: NC control sample files could not be found!')
    return(NC_control_sample)


def run_snapshot(analysis_data):
    '''
    Run the IGV snapshotter for every sample based on the analysis_data
    '''
    # whether or not to include the NC control sample bam in the IGV snapshots
    use_NC_bam = False
    if (
    analysis_data['is_paired'] == True and
    analysis_data['NC_control_sample'] != None
    ):
        print('')

def parse_analysis_dir(analysis_ID, analysis_outdir, control_sample_IDs):
    '''
    Gather all the data needed to run the IGV snapshotter
    '''
    # check if the analysis was paired
    is_paired, combined_sample_barcode_IDs_file = test_for_paired_analysis(analysis_outdir)
    # if it was paired, get the index for the pair
    combined_sample_barcode_IDs_index = get_combined_sample_barcode_IDs_index(combined_sample_barcode_IDs_file)
    # index of samples for the run; list of dicts
    analysis_barcode_file = find_analysis_barcode_file(analysis_outdir)
    analysis_barcode_index = get_analysis_barcode_index(analysis_barcode_file)
    # samples with coverage directories in the analysis run
    # samples_present_in_coverage_dir = find_coverage_samples(analysis_outdir)
    # exclude known control samples from being snapshotted; list of dicts
    coverage_samples = test_for_control_sample(analysis_barcode_index, control_sample_IDs)
    # get the coverage files and dirs for each sample; add to dict entries
    coverage_samples = find_coverage_samples_files(analysis_outdir, coverage_samples)
    # get the
    # the NC sample, if present in the run; otherwise None
    NC_control_sample = find_NC_control_sample(analysis_ID, analysis_barcode_index, combined_sample_barcode_IDs_index)
    # get the NC control sample files
    NC_control_sample = find_NC_control_sample_files(analysis_outdir = analysis_outdir, NC_control_sample = NC_control_sample)


    analysis_data = {}
    analysis_data['control_sample_IDs'] = control_sample_IDs
    analysis_data['analysis_ID'] = analysis_ID
    analysis_data['analysis_outdir'] = analysis_outdir
    analysis_data['is_paired'] = is_paired
    analysis_data['combined_sample_barcode_IDs_file'] = combined_sample_barcode_IDs_file
    analysis_data['analysis_barcode_file'] = analysis_barcode_file
    analysis_data['analysis_barcode_index'] = analysis_barcode_index
    analysis_data['coverage_samples'] = coverage_samples
    analysis_data['combined_sample_barcode_IDs_index'] = combined_sample_barcode_IDs_index
    analysis_data['NC_control_sample'] = NC_control_sample

    # run_IGV_snapshot_automator.print_analysis_data(analysis_data)
    # save JSON of the analysis_data
    output_JSON = os.path.join(analysis_outdir, '{0}.json'.format(analysis_ID))
    print('JSON output: {0}'.format(output_JSON))
    pl.write_json(object = analysis_data, output_file = output_JSON)
    pl.file_exists(output_JSON, kill = False)
    return(output_JSON)



def submit_to_IGV_runner(analysis_data):
    '''
    analysis_data can be either the dict object or the path to the JSON dump of the dict object;
    specify which it is in the call to the module here!
    '''
    print('submitting the analysis_data to be run by IGV snapshotter...')
    # run_IGV_snapshot_automator.main(analysis_data)
    run_IGV_snapshot_automator.main(analysis_data, json_file = True)
    # end
    print('------------------------------------')

def main(analysis_IDs, nosnap = False):
    '''
    Main control function for the script
    '''
    if len(analysis_IDs) < 1:
        print("ERROR: Not enough analysis_IDs! Need at least 1")
        sys.exit()

    # control sample ID's; do not run snapshots on these samples!
    control_sample_IDs = get_control_sample_IDs()

    for analysis_ID in analysis_IDs:
        analysis_outdir = pl.dir_exists(os.path.join(global_settings.outdir, analysis_ID), kill = True, return_path = True) #output/analysis_ID

        print('\n- {0}: {1}\n'.format(analysis_ID, analysis_outdir))
        output_JSON = parse_analysis_dir(analysis_ID, analysis_outdir, control_sample_IDs)
        if nosnap == False:
            submit_to_IGV_runner(analysis_data = output_JSON)


def run():
    '''
    Parse script args to run the script
    '''
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    parser = argparse.ArgumentParser(description='IGV snapshot parser')
    # required positional args
    parser.add_argument("analysis_IDs", nargs='+', help="path to the summary samplesheet to run") # , nargs='?'
    parser.add_argument("-nosnap", default = False, action='store_true', dest = 'nosnap', help="Do not run the IGV snapshot on the analyses passed, only run the parser to generate the JSON")

    args = parser.parse_args()
    analysis_IDs = args.analysis_IDs
    nosnap = args.nosnap
    main(analysis_IDs, nosnap = nosnap)

if __name__ == "__main__":
    run()
