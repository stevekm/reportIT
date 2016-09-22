#!/usr/bin/env python
# python 2.7


# this script will load an IonTorrent summary table
# parse out the variants to create snapshots of
# generate an IGV bat script to run with IGV for making the snapshots
# run IGV to create the snapshots

# # this will probably require X11 installation on connected computer ??


# sample IGV script
# new
# snapshotDirectory /ifs/home/kellys04/projects/clinical_genomic_reporting/reporter_files/output/R_2016_07_28_15_04_57_user_SN2-182-IT16-034/IGV_snapshot
# load /ifs/home/kellys04/projects/clinical_genomic_reporting/reporter_files/output/R_2016_07_28_15_04_57_user_SN2-182-IT16-034/bam/IonXpress_002_R_2016_07_28_15_04_57_user_SN2-182-IT16-034_Auto_user_SN2-182-IT16-034_233.bam
# genome hg19
# goto chr11:108138003-108138003
# snapshot
# goto chr9:21971111-21971111
# snapshot
# goto chr17:7577548-7577548
# exit

# $ bin/IGV_2.3.81/igv.sh -b code/IGV_test.bat
(Xvfb :10 &) && DISPLAY=:10 java -Xmx750m -jar bin/IGV_2.3.81/igv.jar -b code/IGV_test.bat && killall Xvfb



summary_table_file = ""
run_dir = ""
run_bam_dir = ""
run_snapshot_dir = ""