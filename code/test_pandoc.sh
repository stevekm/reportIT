#!/bin/bash

echo ""
echo ">>> LOADING R AND PANDOC MODULES"
echo ""
module unload r
module load r/3.3.0
module load pandoc/1.13.1
which R

echo ""
echo ">>> CHECKING MODULES LOADED"
echo ""
module list

echo ""
echo ">>> CHECKING R AND PANDOC VERSION"
echo ""

/usr/bin/env Rscript - <<< "sessionInfo()"
/usr/bin/env Rscript - <<< "cat('\n\n>>> PANDOC VERSION IS:\n'); rmarkdown::pandoc_version()"

