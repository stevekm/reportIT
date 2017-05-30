#!/usr/bin/env Rscript

## USAGE: variant_master_list_merge.R /path/to/outputfile.tsv
## DESCRIPTION: This script will merge the concatenated variant master list with the Tissue Type and Concordance lists


library("data.table")


# ~~~~~ GET SCRIPT ARGS ~~~~~~~ #
args <- commandArgs(TRUE)
output_file <- args[1]

# supplied by Yehonatan
tissue_file <- "data/misc/variant_master_list_clean_merge/Yehonatan_tumor_tissue_type_files/clinical_full_run_sample_annotated(complete).AnalysisList.tsv"
concordance_file <- "data/misc/variant_master_list_clean_merge/Yehonatan_concordance/Concordance_document-editted.Sheet1.tsv"

# made from the parent 'make_variant_master_list.sh' script
analysis_ID_index <- "data/misc/sample_barcode_run_analysis_index.tsv"
variant_summary_file <- "data/misc/all_summary_table_variants-with_versioning.tsv"


# ~~~~~~ LOAD YEHONATAN TISSUE TABLE ~~~~~~ # 
tissue_table <- read.delim(file = tissue_file, header = TRUE, sep = '\t', stringsAsFactors = FALSE)
# colnames(tissue_table)
setnames(x = tissue_table, old = c("Run.Name", "Sample.Name", "notes"), new = c("Run", "Sample", "notes.Tissue.Type"))
# colnames(tissue_table)
# head(tissue_table)

# ~~~~~~ LOAD YEHONATAN CONCORDANCE TABLE ~~~~~~ # 
concordance_table <- read.delim(file = concordance_file, header = TRUE, sep = '\t', stringsAsFactors = FALSE)
# colnames(concordance_table)
setnames(x = concordance_table, old = c("Run.Name", "Sample.Name"), new = c("Run", "Sample"))
# colnames(concordance_table)
# head(tissue_table)


# ~~~~~~ LOAD ANALYSIS ID TABLE ~~~~~~ # 
analysis_ID_table <- read.delim(file = analysis_ID_index, header = FALSE, sep = '\t', stringsAsFactors = FALSE)
colnames(analysis_ID_table) <- c("Sample", "Barcode", "Run", "Analysis", "Run Date")
# head(analysis_ID_table)



# ~~~~~~ LOAD SUMMARY TABLE ~~~~~~ # 
summary_table <- read.delim(file = variant_summary_file, header = TRUE, sep = '\t', stringsAsFactors = FALSE)
# colnames(summary_table)
#  [1] "Chrom"             "Position"          "Ref"               "Variant"           "Gene"              "Quality"           "Coverage"         
#  [8] "Allele.Coverage"   "Strand.Bias"       "Coding"            "Amino.Acid.Change" "Transcript"        "Frequency"         "Sample.Name"      
# [15] "Barcode"           "Run.Name"          "Review"            "Analysis.ID"       "Date"              "Git.Commit"        "Git.Branch"       
# [22] "Git.Remote.URL"   
setnames(x = summary_table, old = c("Run.Name", "Sample.Name", "Analysis.ID"), new = c("Run", "Sample", "Analysis"))
# head(summary_table)

# ~~~~~~ MERGE SUMMARY w/ TISSUE TYPE ~~~~~~ # 
summary_table <- merge(x = summary_table, y = tissue_table, by = c("Run", "Barcode", "Sample"), all.x = TRUE)

# ~~~~~~ MERGE SUMMARY w/ CONCORDANCE ~~~~~~ #
merge_cols <- c("Sample", "Barcode", "Run", "Chrom", "Position", "Ref", "Variant")
summary_table <- merge(x = summary_table, y = concordance_table[c(merge_cols, "Concordance")], by = , all.x = TRUE)

# ~~~~~~ REORDER COLUMS ~~~~~~ #
cols_in_front <- c("Sample", "Barcode", "Analysis", "Run", "Tissue.Type", "Tumor.Type", "Concordance")
col_order <- c(cols_in_front, colnames(summary_table)[! colnames(summary_table) %in% cols_in_front])
summary_table <- summary_table[col_order[! col_order %in% "notes.Tissue.Type"]]
# colnames(summary_table)

# my_time <- format(Sys.time(), "%F-%H-%M")
# file_output_path <- sprintf("/ifs/home/kellys04/projects/clinical_genomic_reporting/molecpathlab/IonTorrent_reporter/system_files/data/misc/variant_master_list_clean_merge/variant_master_list_with_tissue_concordance-%s.tsv", my_time)

# unique(summary_table[["Concordance"]])
summary_table[["Concordance"]] <- gsub(pattern = 'detected', replacement = 'concordant', x = summary_table[["Concordance"]])
summary_table[["Concordance"]] <- gsub(pattern = 'discrodant', replacement = 'discordant', x = summary_table[["Concordance"]])
summary_table[["Concordance"]] <- gsub(pattern = "concordant (?)", replacement = '', x = summary_table[["Concordance"]], fixed = TRUE)
summary_table[["Concordance"]] <- gsub(pattern = "(?)", replacement = '', x = summary_table[["Concordance"]], fixed = TRUE)

write.table(x = summary_table, quote = FALSE, sep = '\t', row.names = FALSE, col.names = TRUE, na = '',
            file = output_file)


