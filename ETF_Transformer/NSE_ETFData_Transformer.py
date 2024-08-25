#NSE provides historical information of the ETF's.NSE provides the ETF's information in two different files but files has mostly the
#same information.
#Code combines the two files and outputs the required data into a single file
import pandas as pd
import os
import glob

# Specify the columns to extract
columns_to_extract = [
    "Date", "Symbol", "OPEN", "HIGH", "LOW", "PREV CLOSE", 
    "ltp", "close", "vwap", "52W H", "52W L", "VOLUME", 
    "VALUE", "No of trades", "Deliverable Qty", 
    "% Dly Qt to Traded Qty"
]

# Prompt the user for the folder containing the CSV files
input_folder = input("Please enter the path of the folder containing the CSV files: ")

# Prompt the user for the output file path
output_file = input("Please enter the path for the output CSV file (including the filename and .csv extension): ")

# Get a list of all CSV files in the folder
csv_files = glob.glob(os.path.join(input_folder, '*.csv'))

# Initialize an empty DataFrame to hold the combined data
df_combined = pd.DataFrame()

# Loop through each CSV file in the folder
for file in csv_files:
    # Read the CSV file
    df = pd.read_csv(file)
    
    # Trim spaces from the column names
    df.columns = df.columns.str.strip()
    
    # Check if 'Date' column exists
    if 'Date' not in df.columns:
        print(f"'Date' column not found in file: {file}. Skipping this file.")
        continue
    
    # Convert 'Date' column to datetime format for consistency
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Extract only the columns that are present in the DataFrame
    available_columns = [col for col in columns_to_extract if col in df.columns]

    #Ensure 'Date' is included only once in the list of columns
    if "Date" not in available_columns:
        df_extracted = df[["Date"] + available_columns]  # Ensure 'Date' is included
    else:
        df_extracted=df[available_columns]
    
    # Merge the extracted data into the combined DataFrame on 'Date'
    if df_combined.empty:
        # If df_combined is empty, initialize it with the first file's data
        df_combined = df_extracted
    else:
        # Merge based on 'Date', keeping all data from both DataFrames
        df_combined = pd.merge(df_combined, df_extracted, on='Date', how='outer', suffixes=('', '_dup'))
        
        # Handle duplicate columns (those ending with '_dup')
        for col in available_columns:
            if f"{col}_dup" in df_combined.columns:
                # Prioritize non-null values from the original column
                df_combined[col] = df_combined[col].combine_first(df_combined[f"{col}_dup"])
                df_combined.drop(columns=[f"{col}_dup"], inplace=True)

# Drop duplicates based on 'Date'
df_combined.drop_duplicates(subset=['Date'], inplace=True)

# Save the combined dataframe to a new CSV file
df_combined.to_csv(output_file, index=False)

print(f"Extracted and merged data from {len(csv_files)} files based on 'Date' saved to {output_file} without duplicates.")
