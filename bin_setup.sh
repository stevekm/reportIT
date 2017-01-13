#!/bin/bash

# download bcftools
# http://www.htslib.org/download/
if [ ! -f bcftools-1.3.1.tar.bz2 ]; then wget https://github.com/samtools/bcftools/releases/download/1.3.1/bcftools-1.3.1.tar.bz2 ; fi


# download samtools
if [ ! -f samtools-1.3.1.tar.bz2 ]; then wget https://github.com/samtools/samtools/releases/download/1.3.1/samtools-1.3.1.tar.bz2 ; fi


# hstlib
if [ ! -f htslib-1.3.2.tar.bz2 ]; then wget https://github.com/samtools/htslib/releases/download/1.3.2/htslib-1.3.2.tar.bz2 ; fi


# vcflib for vcf2tsv
# https://github.com/vcflib/vcflib

if [ ! -d vcflib ]; then
    git clone --recursive https://github.com/ekg/vcflib.git
fi

if [ ! -f vcflib/bin/vcf2tsv ]; then
    if [ -d vcflib ]; then
        (
            cd vcflib
            make
        )
    fi
fi


# pandoc
if [ ! -f pandoc-1.13.1.zip ]; then wget https://s3.amazonaws.com/rstudio-buildtools/pandoc-1.13.1.zip; fi

# IGV
# http://software.broadinstitute.org/software/igv/download
# if [ ! -f IGV_2.3.88.zip ]; then wget http://data.broadinstitute.org/igv/projects/downloads/IGV_2.3.88.zip ; fi
wget http://data.broadinstitute.org/igv/projects/downloads/IGV_2.3.88.zip

# $ tree bin
# bin
# |-- IGV_2.3.81
# |   |-- batik-codec__V1.7.jar
# |   |-- goby-io-igv__V1.0.jar
# |   |-- igv.bat
# |   |-- igv.command
# |   |-- igv.jar
# |   |-- igv.sh
# |   `-- readme.txt
# |-- IGV_2.3.81.zip
# |-- annovar -> /ifs/home/kellys04/software/annovar
# |-- bcftools -> /ifs/home/kellys04/software/bcftools-1.3.1/bcftools
# |-- bgzip -> /ifs/home/kellys04/software/htslib-1.3.1/bgzip
# |-- samtools -> /ifs/home/kellys04/software/samtools-1.3.1/samtools
# |-- tabix -> /ifs/home/kellys04/software/htslib-1.3.1/tabix
# `-- vcf2tsv -> /ifs/home/kellys04/software/vcflib/bin/vcf2tsv
