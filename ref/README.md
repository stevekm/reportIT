This folder contains the reference genome information. Currently, only hg19 is configured. 

The `cannonical_transcript_table.py` script will download the required files from UCSC, and set up the `canonical_transcript_list.txt` file needed for the pipeline. 

The `IDs_to_replace.csv` file contains transcript ID's to use in the `canonical_transcript_list.txt` file, in place of the default values. This is in the format of "oldID,newID", with one pair per line.
