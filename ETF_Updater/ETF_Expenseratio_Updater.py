#To update the ETF expense ration details to DB
import os
import re
import glob
import subprocess
import pymysql
import pandas as pd
from datetime import datetime


# DB connection setup
def connect_db():
    password = os.getenv('MYSQL_PASSWORD')
    connection = pymysql.connect(host='localhost',user='root',password=password,db='etf')
    return connection

# SQL Queries
#To retrieve from the ETF table
retrieve_sql = "SELECT `etf_id` FROM `etf` WHERE TRIM(`etf_name`) = %s"
#To retrieve from the ETF mapping table
mapping_sql = "SELECT `etf_id` FROM `etf_mapping` WHERE TRIM(`etf_name`) = %s"

# SQL to insert TER data
insert_sql = """
        INSERT INTO `etf_expenseratio`
        (`etf_id`, `etf_expenseratio_value`, `etf_expenseratiomonth`, `etf_expenseratioyear`)
        VALUES (%s, %s, %s, %s)
    """


# Step 1: Process the CSV file and check if etf information is present
def process_csv_file(file_location, file_pattern,excluded_etfs):
    
    connection = connect_db()
    cursor = connection.cursor()

    search_path = os.path.join(file_location, file_pattern)
    matching_files = glob.glob(search_path)

    if not matching_files:
        print("No matching files found.")
        return
    
    file_to_process = matching_files[0]
    print(f"Processing file: {file_to_process}")

    
      
    #Read the excel data
    df = pd.read_excel(file_to_process)

    # Extract month string
    # Get the first month in the data as a string like 'April'
    monthinfo = pd.to_datetime(df['Month'].iloc[0]).strftime('%B')


    if "Scheme Name" not in df.columns:
        print("Missing 'Scheme Name' column in Excel.")
        return

    missing_rows = []

    for _, row in df.iterrows():
        scheme_name = str(row["Scheme Name"]).strip()
        normalized_scheme_name = normalize_etf_name(scheme_name)
       
        
        
        #Skips the row in the list
        if normalized_scheme_name in excluded_etfs:
            print(f"Excluded ETF (ignored): {scheme_name}")
            continue  # Skip this row

        # Primary lookup
        
        cursor.execute(retrieve_sql, (normalized_scheme_name,))
        result = cursor.fetchone()

        if not result:
            # Fallback to mapping table
            cursor.execute(mapping_sql, (normalized_scheme_name,))
            result = cursor.fetchone()

        if result:
            etf_id = result[0]
            print(f"Found ETF: {scheme_name} -> ID: {etf_id}")
        else:
            print(f"ETF not found: {scheme_name}")
            missing_rows.append(row)

    # Save missing rows
    if missing_rows:
        missingETFDataFrame = pd.DataFrame(missing_rows)
        file_name = f"MissingETF_{monthinfo}.xlsx"
        file_path = os.path.join(r"D:\ETF_Data\ETF_Error\\", file_name)
        missingETFDataFrame.to_excel(file_path, index=False)
        print(f"Missing ETFs saved to: {file_path}")

    cursor.close()
    connection.close()

#Step3:Update the DB
def db_update(file_location, file_pattern, excluded_etfs):
    connection = connect_db()
    cursor = connection.cursor()

    

    search_path = os.path.join(file_location, file_pattern)
    matching_files = glob.glob(search_path)

    if not matching_files:
        print("No matching files found.")
        return

    file_to_process = matching_files[0]
    print(f"Processing file: {file_to_process}")

    df = pd.read_excel(file_to_process)

    if "Scheme Name" not in df.columns or "Total TER (%)" not in df.columns:
        print("Missing required columns in Excel.")
        return

    for _, row in df.iterrows():
        
        scheme_name = str(row["Scheme Name"]).strip()
        normalized_scheme_name = normalize_etf_name(scheme_name)

        if normalized_scheme_name in excluded_etfs:
            print(f"Excluded ETF (ignored): {scheme_name}")
            continue

        # Convert Month column to datetime
        try:
            dateinfo = pd.to_datetime(str(row["Month"]))
        except Exception as e:
            print(f"Invalid Month format for {normalized_scheme_name}: {e}")
            continue

        return_month = dateinfo.strftime("%b")   # e.g., Apr
        return_year = dateinfo.year

        # TER value
        try:
            expense_ratio = float(row["Total TER (%)"])
        except Exception as e:
            print(f"Invalid TER value for {normalized_scheme_name}: {e}")
            continue

        # Lookup ETF ID
        cursor.execute(retrieve_sql, (normalized_scheme_name,))
        result = cursor.fetchone()

        if not result:
            # Fallback to mapping table
            cursor.execute(mapping_sql, (normalized_scheme_name,))
            result = cursor.fetchone()

        if result:
            etf_id = result[0]
            print(f"Inserting TER for {scheme_name} (ID: {etf_id}) - {return_month} {return_year} - {expense_ratio}")
            try:
                #cursor.execute(insert_sql, (etf_id, expense_ratio, return_month, return_year))
                print()
            except Exception as e:
                print(f"Failed to insert TER for {scheme_name}: {e}")
        else:
            print(f"ETF not found: {scheme_name}")

    #connection.commit()
    cursor.close()
    connection.close()


# Step 3: Process etf expense details details files in the repository location
def process_etf_expenseratio(excluded_etfs):
    file_location=r'D:\ETF_Data\ETFDataProcessing\ETFProcessedData\ExpenseRatio'
    file_pattern="ETF_Data_*"     
    process_csv_file(file_location,file_pattern,excluded_etfs)
    db_update(file_location,file_pattern,excluded_etfs)

def normalize_etf_name(name):
    return re.sub(r'\s+', ' ', name).strip().upper()
    
 

if __name__ == '__main__':
    excluded_etfs_raw = [
    "BANDHAN S&P BSE Sensex ETF",
    "Bandhan BSE Sensex ETF",
    "Kotak S&P BSE Sensex ETF",
    "Kotak BSE Sensex ETF",
    "Nippon India ETF S&P BSE Sensex",
    "Nippon India ETF BSE Sensex",
    "Nippon India ETF S&P BSE Sensex Next 50",
    "Nippon India ETF BSE Sensex Next 50",
    "SBI S&P BSE 100 ETF",
    "SBI BSE 100 ETF",
    "SBI S&P BSE Sensex ETF",
    "SBI BSE Sensex ETF",
    "SBI S&P BSE Sensex Next 50 ETF",
    "SBI BSE Sensex Next 50 ETF",
    "Motilal Oswal Nifty 50 ETF",
    "Nippon India ETF Nifty CPSE Bond Plus SDL Sep2024 50:50"
    ]
    excluded_etfs = set(normalize_etf_name(name) for name in excluded_etfs_raw)
    process_etf_expenseratio(excluded_etfs)

    
