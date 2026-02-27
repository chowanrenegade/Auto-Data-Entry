====================================
CSV DATA FILLER TOOL DOCUMENTATION
====================================

WHAT IT DOES:
This Python script automatically fills missing data (like 'Price' and 'Description') in one CSV file (the website inventory) using authoritative data from a second master database export CSV file. It links the two files using a common Part Number or ID.

------------------------------------
1. PREREQUISITES
------------------------------------

1.  Python 3.x must be installed.
2.  The 'pandas' library is required for data manipulation.

    INSTALLATION COMMAND:
    pip install pandas

------------------------------------
2. CONFIGURATION (REQUIRED)
------------------------------------

You MUST open the script file (update_csv.py) and modify the configuration variables at the top to match your file names and column headers.

CONFIG VARIABLES TO CHECK:

* WEBSITE_FILE = 'website_parts.csv'
    (The file you want to UPDATE)

* DATABASE_FILE = 'database_master.csv'
    (The file containing the AUTHORITATIVE data)

* PART_ID_COLUMN = 'PartNumber'
    (The column name common to BOTH files used for linking.)

* COLUMNS_TO_UPDATE = ['Price', 'Description']
    (The specific columns in WEBSITE_FILE that have blanks you want to fill.)

* OUTPUT_FILE = 'website_parts_updated.csv'
    (The name of the resulting file.)

------------------------------------
3. HOW TO RUN THE SCRIPT
------------------------------------

1.  Place the 'update_csv.py' script and your two CSV files in the same folder.
2.  Open your command prompt or terminal.
3.  Navigate to the folder containing the files.
4.  Execute the script using the command below:

    COMMAND:
    python update_csv.py

------------------------------------
4. OUTPUT AND LOGIC
------------------------------------

OUTPUT:
A new CSV file named 'website_parts_updated.csv' (or your chosen name) will be created in the same directory. This file is the original website data with the blank fields populated.

LOGIC OVERVIEW:
The script uses a Left Merge (or VLOOKUP equivalent) operation. It reads both files, merges them based on the PART_ID_COLUMN, and then uses the authoritative data to replace any blank (NaN) values in the target columns. 
