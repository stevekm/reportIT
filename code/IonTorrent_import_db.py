#!/usr/bin/env python
# python 2.7

# http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html

import sqlite3

sqlite_file = 'my_first_db.sqlite'    # name of the sqlite database file
table_name1 = 'my_table_1'  # name of the table to be created
table_name2 = 'my_table_2'  # name of the table to be created
new_field = 'my_1st_column' # name of the column
field_type = 'INTEGER'  # column data type

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

# Creating a new SQLite table with 1 column
c.execute('CREATE TABLE {tn} ({nf} {ft})'\
        .format(tn=table_name1, nf=new_field, ft=field_type))

# Creating a second table with 1 column and set it as PRIMARY KEY
# note that PRIMARY KEY column must consist of unique values!
c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
        .format(tn=table_name2, nf=new_field, ft=field_type))

# Committing changes and closing the connection to the database file
conn.commit()
conn.close()

import pandas as pd
file_path = "/ifs/home/kellys04/projects/clinical_genomic_reporting/reporter_files/output/R_2016_07_28_15_04_57_user_SN2-182-IT16-034/R_2016_07_28_15_04_57_user_SN2-182-IT16-034.xls"

