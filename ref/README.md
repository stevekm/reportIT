This folder contains the reference genome information. Currently, only hg19 is configured. 

The `cannonical_transcript_table.py` script will download the required files from UCSC, and set up the 'cannonical transcripts' file needed for the pipeline. 

The `IDs_to_replace.csv` file contains transcript ID's to be use in the 'cannonical transcripts' file, in place of the default values. This is in the format of "oldID,newID".
