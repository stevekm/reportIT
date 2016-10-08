#!/usr/bin/env Rscript

## USAGE: param_report_compile.R -f summary_table_file 
# module load pandoc/1.13.1

# ~~~~~ CUSTOM FUNCTIONS ~~~~~~~ #
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


# ~~~~~ GET SCRIPT ARGS ~~~~~~~ #
library("optparse")

# set script optional args
option_list = list(
    # summary table file
    make_option(c("-f", "--file"), 
                type="character", 
                default=NULL, 
                help="Path to summary_table.tsv file. Parent directory will be used for output report name and location.", 
                metavar="summary_table.tsv"),
    # report template
    make_option(c("-t", "--template"), 
                type="character", 
                default='report/sparse_report.Rmd',
                help="Path to report template Rmd file. [default= %default]", 
                metavar="report_template.Rmd"),
    # actionable genes file
    make_option(c("-ag", "--act-gene-file"), 
                type="character", 
                default='data/actionable_genes.txt', 
                help="Path to actionable genes file. [default= %default]", 
                metavar='actionable_genes.txt'),
    # canonical transcript file
    make_option(c("-ct", "--canon-transcr-file"), 
                type="character", 
                default='data/hg19/canonical_transcr_descr_comment.tsv', 
                help="Path to canonical transcript gene file containing associated descriptive comment file paths. [default= %default]", 
                metavar='canonical_transcripts.tsv')
)

# parse args
opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

# make sure -f file exists
if (is.null(opt$file)){
    print_help(opt_parser)
    stop("At least one argument must be supplied (input file).n", call.=FALSE)
}


# args <- commandArgs(TRUE); cat("Script args are:\n"); args
# summary_table_file <- normalizePath(args[1])
summary_table_file <- normalizePath(opt$file); print(summary_table_file)
output_dir <- dirname(summary_table_file); print(output_dir)

# Rmdfile <- args[2]
Rmdfile <- opt$template; print(Rmdfile)

# act_gene_file <- normalizePath(args[3])
act_gene_file <- normalizePath(opt[['act-gene-file']]); print(act_gene_file)

# canonical_transcript_file <- normalizePath(args[4])
canonical_transcript_file <- normalizePath(opt[['canon-transcr-file']]); print(canonical_transcript_file)



# ~~~~~ RUN ~~~~~~~ #
# compile the report
renderMyDocument(Rmdfile = Rmdfile,
                 output_dir = output_dir,
                 summary_table_file = summary_table_file,
                 act_gene_file = act_gene_file,
                 canonical_transcript_file = canonical_transcript_file)