#!/usr/bin/env python

'''
This module should be called by IGV_snapshot_parser.py and passed an 'analysis_data' object generated there
This will:
- load analysis data either from object or JSON
- run snapshot functions on each sample found in the analysis data
- - assemble list of bam files to include in the sample snapshots
- - convert the sample summary table to regions BED file
- - convert low frequency entries in the summary table to
- - run snapshot on the bam files and regions
'''
import sys
import os
import csv
import argparse
import pipeline_functions as pl
import global_settings
import make_IGV_snapshots

def print_analysis_data(analysis_data):
    '''
    Prints a bunch of items from the analysis_data
    for convenience
    '''
    # print stuff
    for key, value in analysis_data.items():
        if key not in ['analysis_barcode_index', 'combined_sample_barcode_IDs_index', 'coverage_samples', 'NC_control_sample']:
            print('{0}: {1}'.format(key, value))
    print('')

    print('- Analysis Coverage Samples')
    for item in analysis_data['coverage_samples']:
        for key, value in item.items():
            print('{0}: {1}'.format(key, value))
        print('')

    print('')
    print('- combined_sample_barcode_IDs_index')
    if analysis_data['combined_sample_barcode_IDs_index'] == None:
        print(analysis_data['combined_sample_barcode_IDs_index'])
    else:
        for item in analysis_data['combined_sample_barcode_IDs_index']:
            print(item)

    print('')
    print('- NC Control Sample:')
    if analysis_data['NC_control_sample'] != None:
        for key, value in analysis_data['NC_control_sample'].items():
            print('{0}: {1}'.format(key, value))
        print('')

    print('')
    print('- Control sample IDs')
    print(analysis_data['control_sample_IDs'])

    print('')
    print('- all analysis_data keys')
    for key in analysis_data.keys(): print(key)
    print('')

def validate_bed(bed_file):
    '''
    Validate a .bed file for use with the IGV snapshotter;
    - at least 1 line
    - exists...
    '''
    import os
    import sys
    file_is_safe = False
    # pl.file_exists(bed_file, kill = True)
    if not os.path.isfile(bed_file):
        print('WARNING: Bed file does not exist: {0}\nIGV snapshots should not be run'.format(bed_file))
        return(file_is_safe)
    if len(pl.list_file_lines(file_path = bed_file)) < 1:
        print('WARNING: Bed file {0} does not have enough lines, IGV snapshots should not be run'.format(bed_file))
        return(file_is_safe)
    file_is_safe = True
    return(file_is_safe)

def make_snapshot_filename(summary_dict, filename_suffix = '', file_extension = "png"):
    '''
    Take a DictReader dict of a single row from the summary table a convert it to an IGV snapshot filename to save in the BED
    # build the filename for the IGV snapshot, format required for downstream reporting
    '''
    analysis_ID = summary_dict['Analysis ID']
    barcode = summary_dict['Barcode']
    gene = summary_dict['Gene']
    chrom = summary_dict['Chrom']
    position = summary_dict['Position']
    coding = summary_dict['Coding']
    if filename_suffix != '':
        file_extension = '.'.join(map(str, [filename_suffix, file_extension]))
    snapshot_filename = '.'.join(map(str, [analysis_ID, barcode, gene, chrom, position, coding, file_extension]))
    return(snapshot_filename)


def summary_table_to_bed(sample_summary_table, output_file, filename_suffix = ''):
    '''
    Convert a summary table into BED coordinates
    use nf4 mode of 'make_IGV_snapshots.py' to stash a custom snapshot name for each BED entry in the 4th column
    '''
    import csv
    print('input file: {0}'.format(sample_summary_table))
    print('output file: {0}'.format(output_file))
    with open(sample_summary_table, 'r') as tsvin, open(output_file, 'w') as bedout:
        reader = csv.DictReader(tsvin, delimiter='\t')
        writer = csv.writer(bedout, delimiter='\t')
        for row in reader:
            # print()
            filename = make_snapshot_filename(summary_dict = row, filename_suffix = filename_suffix)
            entry = [row['Chrom'], row['Position'], row['Position'], filename]
            print(entry)
            writer.writerow(entry)

def summary_table_to_bed_long(sample_summary_table, output_file, filename_suffix = 'long', min_frequency = 0.25):
    '''
    Write out the low frequency variants
    '''
    import csv
    print('Find low frequency variants...')
    print('input file: {0}'.format(sample_summary_table))
    print('output file: {0}'.format(output_file))
    with open(sample_summary_table, 'r') as tsvin, open(output_file, 'w') as bedout:
        reader = csv.DictReader(tsvin, delimiter='\t')
        writer = csv.writer(bedout, delimiter='\t')
        for row in reader:
            if float(row['Frequency']) < min_frequency:
                print(row['Frequency'])
                filename = make_snapshot_filename(summary_dict = row, filename_suffix = filename_suffix)
                entry = [row['Chrom'], row['Position'], row['Position'], filename]
                print(entry)
                writer.writerow(entry)

def sample_snapshot_run(sample_name, bam_files, IGV_regions_file, IGV_snapshots_dir, image_height = '500'):
    '''
    Final step in validating input files and running the snapshotter
    '''
    genome = 'hg19'
    # igv_jar_bin = "bin/IGV_2.3.81/igv.jar"
    igv_jar_bin = global_settings.igv_bin
    igv_mem = "4000"
    nf4_mode = True
    # make sure the regions file looks OK
    if validate_bed(bed_file = IGV_regions_file) != True:
        print('Sample {0} bed file {1} does not pass safety criteria, skipping IGV snapshot...'.format(sample_name, IGV_regions_file))
        return()
    make_IGV_snapshots.main(input_files = bam_files, region_file = IGV_regions_file, genome = genome, image_height = image_height, outdir = IGV_snapshots_dir, igv_jar_bin = igv_jar_bin, igv_mem = igv_mem, nf4_mode = nf4_mode)


def sample_snapshot_parse(sample, NC_control_bam = None):
    '''
    Parse out information for the snapshotter, then submit for running
    'sample' is a dict generated by the parser earlier
    '''
    # get some items from the sample dict
    is_control_sample = sample['is_control_sample']
    sample_name = sample['Sample Name']

    sample_bam_file = None
    if 'sample_bam_file' in sample.keys():
        sample_bam_file = sample['sample_bam_file']

    sample_summary_table = None
    if 'sample_summary_table' in sample.keys():
        sample_summary_table = sample['sample_summary_table']

    IGV_regions_file = None
    if 'IGV_regions_file' in sample.keys():
        IGV_regions_file = sample['IGV_regions_file']

    IGV_regions_file_long = None
    if 'IGV_regions_file_long' in sample.keys():
        IGV_regions_file_long = sample['IGV_regions_file_long']

    IGV_snapshots_dir = None
    if 'IGV_snapshots_dir' in sample.keys():
        IGV_snapshots_dir = sample['IGV_snapshots_dir']

    # make sure the sample is not a control sample
    if is_control_sample == True:
        print('Sample {0} is a control sample, skipping IGV snapshot...'.format(sample_name))
        return()

    # start list of bam files to include for the snapshots
    bam_files = []
    if sample_bam_file != None:
        bam_files.append(sample_bam_file)

    if NC_control_bam != None:
        bam_files.append(NC_control_bam)

    # only run if there are bam files present
    if len(bam_files) > 0:
        # convert the sample summary table to BED format
        if ( sample_summary_table != None and os.path.isfile(str(sample_summary_table)) ):
            # first do the regular regions file
            if IGV_regions_file != None:
                summary_table_to_bed(sample_summary_table = sample_summary_table, output_file = IGV_regions_file)
                sample_snapshot_run(sample_name = sample_name, bam_files = bam_files, IGV_regions_file = IGV_regions_file, IGV_snapshots_dir = IGV_snapshots_dir)
                # check the bed file before trying to run the snapshotter

            # check for long regions file
            if IGV_regions_file_long != None:
                summary_table_to_bed_long(sample_summary_table = sample_summary_table, output_file = IGV_regions_file_long)
                sample_snapshot_run(sample_name = sample_name, bam_files = bam_files, IGV_regions_file = IGV_regions_file_long, IGV_snapshots_dir = IGV_snapshots_dir, image_height = '5000')
        else:
            print("Could not validate sample summary table! IGV Snapshot will not be run.")
            return()
    else:
        print("No .bam files found for sample {0}, IGV snapshot will not be run!".format(sample_name))

def main(analysis_data, json_file = False):
    '''
    Main control function for the script
    parses the analysis_data for a single run and runs the IGV snapshot for each sample
    based on supplied criteria
    json_file : analysis_data is a JSON file that needs to be loaded first
    '''
    print('foo')
    if json_file != False:
        print('Loading analysis data from JSON input file: {0}'.format(str(analysis_data)))
        pl.file_exists(analysis_data, kill = False)
        analysis_data_file = analysis_data
        analysis_data = pl.load_json(input_file = analysis_data_file)
    print('Analysis data loaded:\n\n')
    print_analysis_data(analysis_data)
    # Check for an NC control sample and BAM file
    NC_control_bam = None
    if (
    analysis_data['NC_control_sample'] != None and
    'sample_bam_file' in analysis_data['NC_control_sample'].keys() and
    analysis_data['NC_control_sample']['sample_bam_file'] != None
    ):
        NC_control_bam = analysis_data['NC_control_sample']['sample_bam_file']

    for sample in analysis_data['coverage_samples']:
        sample_snapshot_parse(sample, NC_control_bam = NC_control_bam)
