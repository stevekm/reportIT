SHELL:=/bin/bash
NXF_VER:=0.31.1
HOSTNAME:=$(shell echo $$HOSTNAME)
CONFIGFILE:=/gpfs/data/molecpathlab/private_data/reportIT-config.json

# no default action to take
none:

# ~~~~~ INSTALL NEXTFLOW ~~~~~ #
# need to adjust modules on 'phoenix' HPC
./nextflow:
	@if grep -q 'phoenix' <<<'$(HOSTNAME)'; then module unload java && module load java/1.8; fi ; \
	export NXF_VER="$(NXF_VER)" && \
	printf ">>> Installing Nextflow in the local directory\n" && \
	curl -fsSL get.nextflow.io | bash

install: ./nextflow


# ~~~~~ RUN ~~~~~ #
download:
	@if grep -q 'phoenix' <<<'$(HOSTNAME)'; then module unload java && module load java/1.8; fi ; \
	./nextflow run download.nf --configFile "$(CONFIGFILE)"



# ~~~~~ CLEANUP ~~~~~ #
clean-traces:
	rm -f trace*.txt.*

clean-logs:
	rm -f .nextflow.log.*

clean-reports:
	rm -f *.html.*

clean-flowcharts:
	rm -f *.dot.*

clean-output:
	[ -d output ] && mv output oldoutput && rm -rf oldoutput &

clean-work:
	[ -d work ] && mv work oldwork && rm -rf oldwork &

# deletes files from previous runs of the pipeline, keeps current results
clean: clean-logs clean-traces clean-reports clean-flowcharts

# deletes all pipeline output in current directory
clean-all: clean clean-output clean-work
	[ -d .nextflow ] && mv .nextflow .nextflowold && rm -rf .nextflowold &
	rm -f .nextflow.log
	rm -f *.png
	rm -f trace*.txt*
	rm -f *.html*
