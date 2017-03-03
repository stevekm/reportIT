This is a folder where you can store your sample sheets for running the reportIT pipeline, with the `run_samplesheet.py` script. 

A samplesheet should be a tab-separated (.tsv) text file, with either one or two columns. 

Each line of the sample sheet should contain the analysis ID's of runs to be processed with the pipeline. If you have paired runs, then you can list the two of them together on the same line. 

An example sample sheet can look like this:

```
analysis_1-1	analysis_1-2
analysis_2
analysis_3-1	analysis_3-2
```

In this sheet, `analysis_1-1` and `analysis_1-2` are 'paired', meaning they share control samples. 

As you can see, a 'ragged' table is perfectly acceptable for this; `analysis_2` is listed by itself since it does not have any other paired runs. 

The only part of the pipeline where the 'pairs' matters is in the IGV snapshots, which will need this extra information in order to search both of the listed runs for the NC control sample to use. All other parts of the pipeline function the same whether a run is 'paired' or not. 

By listing all your analysis runs together in a sample sheet like this, you can automatically run the pipeline for a large number of runs. 
