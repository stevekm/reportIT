#!/bin/bash

# this script will set up the binary dependencies for the reportIT pipeline

# download bcftools
# http://www.htslib.org/download/
if [ ! -f bcftools-1.3.1.tar.bz2 ]; then wget https://github.com/samtools/bcftools/releases/download/1.3.1/bcftools-1.3.1.tar.bz2 ; fi
tar xvfj bcftools-1.3.1.tar.bz2
(cd bcftools-1.3.1; make)
ln -fs bcftools-1.3.1/bcftools
ln -fs htslib-1.3.1/tabix

# download samtools
if [ ! -f samtools-1.3.1.tar.bz2 ]; then wget https://github.com/samtools/samtools/releases/download/1.3.1/samtools-1.3.1.tar.bz2 ; fi
tar xvfj samtools-1.3.1.tar.bz2
(cd samtools-1.3.1; make)
ln -fs samtools-1.3.1/samtools

# hstlib
if [ ! -f htslib-1.3.1.tar.bz2 ]; then wget https://github.com/samtools/htslib/releases/download/1.3.1/htslib-1.3.1.tar.bz2 ; fi
tar xvfj htslib-1.3.1.tar.bz2
(cd htslib-1.3.1; make)
ln -fs htslib-1.3.1/bgzip

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
ln -fs vcflib/bin/vcf2tsv


# pandoc
if [ ! -f pandoc-1.13.1.zip ]; then wget https://s3.amazonaws.com/rstudio-buildtools/pandoc-1.13.1.zip; fi
unzip pandoc-1.13.1.zip
ln -fs pandoc-1.13.1/linux/rpm/x86_64/pandoc


# IGV
# http://software.broadinstitute.org/software/igv/download
# if [ ! -f IGV_2.3.88.zip ]; then wget http://data.broadinstitute.org/igv/projects/downloads/IGV_2.3.88.zip ; fi
if [ ! -f IGV_2.3.81.zip ]; then wget http://data.broadinstitute.org/igv/projects/downloads/IGV_2.3.81.zip; fi
unzip IGV_2.3.81.zip

# ANNOVAR
# http://annovar.openbioinformatics.org/en/latest/user-guide/download/
# currently using: refGene,cosmic68,clinvar_20150629,1000g2015aug_all
if [ ! -f annovar.latest.tar.gz ]; then
    wget http://www.openbioinformatics.org/annovar/download/0wgxR2rIVP/annovar.latest.tar.gz
    tar -zxvf annovar.latest.tar.gz
fi
db_dir="annovar/db"
mkdir -p "$db_dir"
# install ANNOVAR db's
annovar/annotate_variation.pl -downdb -buildver hg19 -webfrom annovar 1000g2015aug "$db_dir"
annovar/annotate_variation.pl -downdb -buildver hg19 -webfrom annovar refGene "$db_dir"
annovar/annotate_variation.pl -downdb -buildver hg19 -webfrom annovar cosmic68 "$db_dir"
annovar/annotate_variation.pl -downdb -buildver hg19 -webfrom annovar clinvar_20150629 "$db_dir"
annovar/annotate_variation.pl -downdb -buildver hg19 -webfrom annovar 1000g2015aug "$db_dir"


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
