#!/bin/bash

# download bcftools
# http://www.htslib.org/download/
wget https://github.com/samtools/bcftools/releases/download/1.3.1/bcftools-1.3.1.tar.bz2

# download samtools
wget https://github.com/samtools/samtools/releases/download/1.3.1/samtools-1.3.1.tar.bz2

# hstlib
wget https://github.com/samtools/htslib/releases/download/1.3.2/htslib-1.3.2.tar.bz2

# vcflib for vcf2tsv
# https://github.com/vcflib/vcflib
(
git clone --recursive https://github.com/ekg/vcflib.git
cd vcflib
make
)

# IGV
# http://software.broadinstitute.org/software/igv/download
wget http://data.broadinstitute.org/igv/projects/downloads/IGV_2.3.88.zip
