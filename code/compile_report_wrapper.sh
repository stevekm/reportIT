#!/bin/bash
# set -x


#~~~~~ CUSTOM ENVIRONMENT ~~~~~~#
source "global_settings.sh"

${codedir}/compile_RMD_report.R "$1"
