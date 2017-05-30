#!/usr/bin/env python
# python 2.7

'''
This script will rebuild a standard format VCF file out of an ANNOVAR avinput file
and the original VCF file
ANNOVAR corrects some features, such as indel notation, which we want in the output
But we also need to keep the VCF metadata
Read in the header from the VCF, and then add the CHROM POS REF ALT fields from the avinput
'''

import sys
import os
import errno
import pipeline_functions as pl

# ~~~~ GET SCRIPT ARGS ~~~~~~ #
vcf_file = sys.argv[1] # need the header
avinput_file = sys.argv[2] # need the contents

# output file
# rebuilt_output_file = os.path.splitext(avinput_file)[0] + ".rebuilt"
rebuilt_output_file = sys.argv[3]
# print rebuilt_output_file

# with open(vcf_file) as f:
#     for line in f:
#         if line.startswith("#"):
#             # append_string(string, output_file)
#             print line
with open(vcf_file) as vfile, open(avinput_file) as afile, open(rebuilt_output_file, 'w') as outfile:
    for line in vfile:
        if line.startswith("#"):
            outfile.write(line)
    for line2 in afile:
        if not line2.startswith("#"):
            # avout = '\t'.join(line2.split()[0:4]) + '\n'
            # pl.my_debugger(globals().copy())
            avout = [line2.split()[x] for x in [0, 1,7,3,4]]
            for x in line2.split()[10:]: avout.append(x)
            avout = '\t'.join(avout) + '\n'
            outfile.write(avout)
