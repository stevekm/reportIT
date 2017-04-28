#!/usr/bin/env Rscript

## USAGE: 

# install.packages('redcapAPI')
library("redcapAPI") # https://github.com/nutterb/redcapAPI/wiki
library("httr")

dir()

data_dict_file <- "DataDictionary.csv"
data_dict <- read.delim(file = data_dict_file, header = TRUE, sep = ',')




redcapConnection(url=readLines(con = "API_url.txt", n = 1), 
                 token=readLines(con = "Clincal_Genomic_Reporting_API_key.txt", n = 1))
