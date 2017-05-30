#!/usr/bin/env python

## USAGE: .... /path/to/input.tsv
## DESCRIPTION: This script will set up a TSV table for REDCap import


import csv
import collections
import os
import sys



def code_REDCap_csv(input_csv):
    '''
    Replaces values in 'dropdown' fields in the CSV file with their coding based on the REDCap data dictionary
    Saves the output to a new CSV
    '''
    output_csv = output_csv = os.path.splitext(input_csv)[0] + ".REDCap_coded.csv"
    print(output_csv)
    coding = collections.defaultdict(dict)
    # get the coding for the 'dropdown' fields
    with open('DataDictionary.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Field Type'] == 'dropdown':
                field_name = row['Variable / Field Name']
                print(field_name)
                options = row['Choices, Calculations, OR Slider Labels'].split('|')
                for item in options:
                    value, key = item.split(',')
                    key = key.strip()
                    value = value.strip()
                    print('{0}\t{1}'.format(key, value))
                    coding[field_name][key] = value
    # preview the coding dict
    for key, value in coding.items():
        print('{0}\t{1}'.format(key, value))
    # read in the entries and write out the changes
    with open(input_csv) as infile, open(output_csv, 'wb') as outfile:
        read_in = csv.DictReader(infile)
        write_out = csv.DictWriter(outfile, None)
        for row in read_in:
            print([x for x in row.keys() if x in coding.keys()])
            if write_out.fieldnames is None:
                # initialize and write b's headers
                row_header = dict((h, h) for h in read_in.fieldnames)
                write_out.fieldnames = read_in.fieldnames
                write_out.writerow(row_header)
            write_out.writerow(row)
    return(output_csv)


def find_summary_tables():
    for root, dirs, files in os.walk("output"):
        for file in files:
            if file.endswith("summary_version.tsv"):
                if not file.startswith("IonXpress"):
                     print(os.path.join(root, file))

def replace_headers(input_tsv):
    '''
    Convert the CSV to TSV and change the headers
    '''
    output_csv = os.path.splitext(input_tsv)[0] + ".csv"
    # reaplce headers; old: new
    # these *might* be present
    headers_preprocessing = {
    'Sample Name': "Sample",
    'Run Name': "Run",
    'Analysis ID': "Analysis",
    'Tissue.Type': "Tissue Type",
    'Tumor.Type': "Tumor Type",
    'Allele.Coverage': "Allele Coverage",
    'Strand.Bias': "Strand Bias",
    'Amino.Acid.Change': "Amino Acid Change",
    'Git.Commit': "Git Commit",
    'Git.Branch': "Git Branch",
    'Git.Remote.URL': "Git Remote URL"
    }
    # these *should* be present
    headers_index = {
    "Sample": "sample",
    "Barcode": "barcode",
    "Analysis": "analysis",
    "Run": "run",
    "Tissue Type": "tissue_type",
    "Tumor Type": "tumor_type",
    "Concordance": "concordance",
    "Chrom": "chrom",
    "Position": "position",
    "Ref": "ref",
    "Variant": "variant",
    "Gene": "gene",
    "Quality": "quality",
    "Coverage": "coverage",
    "Allele Coverage": "allele_coverage",
    "Strand Bias": "strand_bias",
    "Coding": "coding",
    "Amino Acid Change": "amino_acid_change",
    "Transcript": "transcript",
    "Frequency": "frequency",
    "Review": "review",
    "Date": "date",
    "Git Commit": "git_commit",
    "Git Branch": "git_branch",
    "Git Remote URL": "git_remote_url"
    }
    with open(input_tsv) as infile, open(output_csv, 'wb') as outfile:
        r = csv.reader(infile, delimiter='\t')
        w = csv.writer(outfile)
        # get the header
        for row in r:
            header = row
            break
        # change some if they're present
        processed_header = []
        for item in header:
            if item in headers_preprocessing.keys():
                processed_header.append(headers_preprocessing[item])
            else:
                processed_header.append(item)
        # change all the rest
        new_header = []
        for item in processed_header:
            if item in headers_index.keys():
                new_header.append(headers_index[item])
            else:
                new_header.append(item)
        # print(new_header)
        # write new header
        w.writerow(new_header)
        # copy the rest
        for row in r:
            w.writerow(row)
    return(output_csv)


# ~~~~ GET SCRIPT ARGS ~~~~~~ #
input_file = sys.argv[1]

if __name__ == "__main__":
    # records_input_file = "/ifs/data/molecpathlab/IonTorrent_reporter/system_files/data/misc/REDCap/variant_master_list_with_tissue_concordance-2017-04-03-21-12-editted.csv"
    # summary_table="output/Auto_user_SN2-218-IT16-051-2_275_307/Auto_user_SN2-218-IT16-051-2_275_307_summary_version.tsv"
    # code_REDCap_csv()
    # find_summary_tables()
    print(input_file)
    summary_csv = replace_headers(input_file)
    print(code_REDCap_csv(summary_csv))
    # need to add 'unique_id'
