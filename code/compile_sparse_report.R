#!/usr/bin/env Rscript

## USAGE: param_report_compile.R output_dir Rmdfile summary_table_file act_gene_file canonical_transcript_file

# module load pandoc/1.13.1
# kellys04@phoenix2:~/projects/clinical_genomic_reporting/variant_reporter/report$ ./param_report_compile.R test_report/ test.Rmd ../output/R_2016_07_28_15_04_57_user_SN2-182-IT16-034/summary_table.tsv ../data/actionable_genes.txt ../data/hg19/canonical_transcr_descr_comment.tsv

# ~~~~~ GET SCRIPT ARGS ~~~~~~~ #
args <- commandArgs(TRUE); cat("Script args are:\n"); args

renderMyDocument <- function(Rmdfile, output_dir, 
                             summary_table_file, 
                             act_gene_file, 
                             canonical_transcript_file) {
    output_filename <- paste0(basename(dirname(summary_table_file)),".html")
    rmarkdown::render(Rmdfile, 
                      output_file = output_filename,
                      output_dir = output_dir,
                      # intermediates_dir = output_dir, 
                      params = list(
                          summary_table_file = summary_table_file,
                          act_gene_file = act_gene_file,
                          canonical_transcript_file = canonical_transcript_file
                      ))
}

output_dir <- args[1]
Rmdfile <- args[2]

summary_table_file <- normalizePath(args[3])
print(summary_table_file)

act_gene_file <- normalizePath(args[4])
print(act_gene_file)

canonical_transcript_file <- normalizePath(args[5])
print(canonical_transcript_file)

renderMyDocument(Rmdfile = Rmdfile, 
                 output_dir = output_dir, 
                 summary_table_file = summary_table_file,
                 act_gene_file = act_gene_file,
                 canonical_transcript_file = canonical_transcript_file)