#To update the ETF return and AUM details to the DB
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

    # Extract file type (Data or AUM) and monthinfo
    base_name = os.path.basename(file_to_process)

    if base_name.startswith("ETF_Data_"):
        file_type = "data"
    elif base_name.startswith("ETF_AUM_"):
        file_type = "aum"
    else:
        print("Unknown file type. Skipping.")
        return

    # Extract month string
    match = re.search(r'ETF_(?:Data|AUM)_(.+?)\.xlsx', base_name)
    monthinfo = match.group(1) if match else "UnknownMonth"

    df = pd.read_excel(file_to_process)


    if "Scheme Name" not in df.columns:
        print("Missing 'Scheme Name' column in Excel.")
        return

    missing_rows = []

    for _, row in df.iterrows():
        scheme_name = str(row["Scheme Name"]).strip()
        
        
        #Skips the row in the list
        if scheme_name in excluded_etfs:
            print(f"Excluded ETF (ignored): {scheme_name}")
            continue  # Skip this row

        # Primary lookup
        retrieve_sql = "SELECT `etf_id` FROM `etf` WHERE `etf_name` = UPPER(%s)"
        cursor.execute(retrieve_sql, (scheme_name,))
        result = cursor.fetchone()

        if not result:
            # Fallback to mapping table
            mapping_sql = "SELECT `etf_id` FROM `etf_mapping` WHERE `etf_name` = %s"
            cursor.execute(mapping_sql, (scheme_name,))
            result = cursor.fetchone()

        if result:
            etf_id = result[0]
            #print(f"Found ETF: {scheme_name} -> ID: {etf_id}")
        else:
            print(f"ETF not found: {scheme_name}")
            missing_rows.append(row)

    # Save missing rows
    if missing_rows:
        missingETFDataFrame = pd.DataFrame(missing_rows)
        file_name = f"MissingAsset_{file_type.upper()}_{monthinfo}.xlsx"
        file_path = os.path.join(r"D:\ETF_Data\ETF_Error\\", file_name)
        missingETFDataFrame.to_excel(file_path, index=False)
        print(f"Missing ETFs saved to: {file_path}")

    cursor.close()
    connection.close()


#Function to ensure  that column names are dynamically identified and updated
def get_etfreturn_columns(columns):
    etfreturn_columns = {}
    time_period_map = {
        '1year': '1Y',
        '3year': '3Y',
        '5year': '5Y',
        '10year': '10Y',
        'sincelaunch': 'SL'
    }

    for col in columns:
        col_lower = col.lower()
        col_normalized = re.sub(r'[^a-z0-9]', '', col_lower)
        for key in time_period_map:
            if key in col_normalized:
                etfreturn_columns[col] = time_period_map[key]
                break

    return etfreturn_columns

#Step3:Update the DB
def db_update(file_location,file_pattern,excluded_etfs):
       connection = connect_db()
       cursor = connection.cursor()
       #To retrieve ETF details
       retrieveetf_sql = "SELECT `etf_id` FROM `etf` WHERE `etf_symbol` = %s"

       #For the ETF data 
       insertetf_sql = """
        INSERT INTO `etf_returns`
        (`etf_id`, `etf_returns_timeperiod`, `etf_returnsvalue`, `etf_returnsmonth`, `etf_returnsyear`)
        VALUES (%s, %s, %s, %s, %s)
        """
       #For the AUM data
       insertetfaum_sql = """
        INSERT INTO `etf_aum`
        (`etf_id`, `etf_aum`, `etf_aum_month`, `etf_aum_year`)
        VALUES (%s, %s, %s, %s)
        """

       search_path = os.path.join(file_location, file_pattern)
       matching_files = glob.glob(search_path)

       if not matching_files:
        print("No matching files found.")
        return

       file_to_process = matching_files[0]
       print(f"Processing file: {file_to_process}")

       # Extract file type (Data or AUM) and monthinfo
       base_name = os.path.basename(file_to_process)

       if base_name.startswith("ETF_Data_"):
        file_type = "data"
       elif base_name.startswith("ETF_AUM_"):
           file_type = "aum"
       else:
        print("Unknown file type. Skipping.")
        return
       
       df = pd.read_excel(file_to_process)
       
       if "Scheme Name" not in df.columns:
        print("Missing 'Scheme Name' column in Excel.")
        return
 
             
       for _, row in df.iterrows():
        scheme_name = str(row["Scheme Name"]).strip()
        
                
        #Skips the row in the list
        if scheme_name in excluded_etfs:
            print(f"Excluded ETF (ignored): {scheme_name}")
            continue  # Skip this row
        try:
            if file_type == "data":
                nav_date = pd.to_datetime(row["NAV Date"])
                return_month = nav_date.strftime("%b")  # e.g., Sep
                return_year = nav_date.year
            else:
                AUM =str(row["AUM"]).strip()
                nav_date = pd.to_datetime(row["Month"])
                return_month = nav_date.strftime("%b")  # e.g., Sep
                return_year = nav_date.year

        except Exception as e:
            print(f"Invalid NAV Date for {scheme_name}: {e}")
            continue

        # Primary lookup
        retrieve_sql = "SELECT `etf_id` FROM `etf` WHERE `etf_name` = UPPER(%s)"
        cursor.execute(retrieve_sql, (scheme_name,))
        result = cursor.fetchone()

        if not result:
            # Fallback to mapping table
            mapping_sql = "SELECT `etf_id` FROM `etf_mapping` WHERE `etf_name` = %s"
            cursor.execute(mapping_sql, (scheme_name,))
            result = cursor.fetchone()

        if result:
            etf_id = result[0]
            print(f"Found ETF: {scheme_name} -> ID: {etf_id}")
            if file_type == "data":
                etfreturn_columns = get_etfreturn_columns(df.columns)
                if not etfreturn_columns:
                    print("No valid return columns found in the file.")
                    return
                for col, period_label in etfreturn_columns.items():
                    value_raw = row.get(col)
                    if pd.isna(value_raw):
                        print(f"Skipping {period_label} return for {scheme_name} as it's missing.")
                        continue
                    try:
                        value = float(row[col])
                        #cursor.execute(insertetf_sql, (etf_id, period_label, value, return_month, return_year))
                    except Exception as e:
                        print(f"Failed to insert {period_label} return for {scheme_name}: {e}")
            elif file_type == "aum":
                    if pd.isna(AUM):
                        print(f"Skipping AUM insert for {scheme_name} due to missing value.")
                        continue
                    try:
                        #cursor.execute(insertetfaum_sql,(etf_id,AUM,return_month,return_year))
                        print(f"Successfully inserted {scheme_name}")
                    except Exception as e:
                        print(f"Failed to insert {etf_id} return for {scheme_name}: {e}")
        else:
            print(f"ETF not found: {scheme_name}")
     
   
       #connection.commit()
       cursor.close()
       connection.close()
# Step 3: Process etf return details in the repository location
def process_etf_return(excluded_etfs):
    file_location=r'D:\ETF_Data\ETFDataProcessing\ETFProcessedData\AUM_Returns'
    file_pattern="ETF_Data_*-*"
    process_csv_file(file_location,file_pattern,excluded_etfs)
    db_update(file_location,file_pattern,excluded_etfs)

# Step 4: Process etf aum details files in the repository location
def process_etf_aum(excluded_etfs):
    file_location=r'D:\ETF_Data\ETFDataProcessing\ETFProcessedData\AUM_Returns'
    file_pattern="ETF_AUM_*-*"
    process_csv_file(file_location,file_pattern,excluded_etfs)
    db_update(file_location,file_pattern,excluded_etfs)

    
 

if __name__ == '__main__':
    excluded_etfs = [
    "Bandhan BSE Sensex ETF",
    "Kotak BSE Sensex ETF",
    "Nippon India ETF BSE Sensex",
    "Nippon India ETF BSE Sensex Next 50",
    "SBI BSE Sensex ETF",
    "SBI BSE Sensex Next 50 ETF"
    ]
    process_etf_return(excluded_etfs)
    #process_etf_aum(excluded_etfs)
    
