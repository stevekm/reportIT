#!/bin/bash

## USAGE: git_init_run.sh
## DESCRIPTION: This script will set up a git repo in the give run dirs


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

#~~~~~ PARSE ARGS ~~~~~~#
num_args_should_be "greater_than" "0" "$#" # "less_than", "greater_than", "equal"



analysis_ID_list="${@:1}" # accept a space separated list of ID's starting at the first arg

for i in $analysis_ID_list; do
    (
    analysis_ID="$i"
    printf '%s' '------------------------'
    printf "\nAnalysis ID is:%s\n\n" "$analysis_ID"
    analysis_outdir="${outdir}/${analysis_ID}"

    cd "$analysis_outdir"

    if [ -d .git ]; then
        printf "git repo already exists in %s\n" "$analysis_outdir"
        printf "to remove this repo, run this command:\n\n"
        printf "rm -rf $(readlink -f .git)\n"
        printf "rm -f $(readlink -f .gitignore)\n"

        exit
    fi

    if [ ! -d .git ] ; then
        git init
        echo '*.bam' >> .gitignore
        echo '*.png' >> .gitignore
        echo 'logs/*' >> .gitignore
        echo '*.Rdata' >> .gitignore
        echo '*.html' >> .gitignore
        echo '*.zip' >> .gitignore
        echo '*.gz' >> .gitignore
        echo '*.gz.tbi' >> .gitignore
        echo '*.zip' >> .gitignore
        echo '*.bam.bai' >> .gitignore
        echo '*logs/*' >> .gitignore

        git add .
        git status
    fi
    )
done
