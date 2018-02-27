#!/usr/bin/env python
"""
This script will read in a tab-separated summary table file, count the number of characters in the 'Ref' column, and add a new column with the number of characters in the Ref entry

USAGE: code/paste_ref_len.py foo_summary_version.tsv foo_summary_version.len.tsv
"""
import csv
import sys


def main():
    """
    Main control function for the program
    """
    input_tsv = sys.argv[1] # "data/aggregate/NS50_all_summary_version.tsv"
    output_tsv = sys.argv[2] # "data/aggregate/NS50_all_summary_version.len.tsv"

    with open(input_tsv) as fin, open(output_tsv, 'w') as fout:
        reader = csv.DictReader(fin, delimiter = '\t')

        fieldnames_out = [h for h in reader.fieldnames]
        fieldnames_out.append('Ref_Len')
        fieldnames_out.append('Variant_Len')

        writer = csv.DictWriter(fout, fieldnames = fieldnames_out, delimiter = '\t')
        writer.writeheader()
        for row in reader:
            row['Ref_Len'] = len(row['Ref'].replace('-',''))
            row['Variant_Len'] = len(row['Variant'].replace('-',''))
            writer.writerow(row)

if __name__ == '__main__':
    main()
