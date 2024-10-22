import os
import subprocess
import pymysql
import pandas as pd

# GitHub repository details
REPO_PATH = '/Volumes/Project/ETFAnalyser/ETF'  # Local path to your repository
FILES_DIR = '/Volumes/Project/ETFAnalyser/ETF/ETF_Data/Download'  # Directory where the files are located inside the repo (if applicable)

# DB connection setup
def connect_db():
    connection = pymysql.connect(host='localhost', user='root', password='', db='ETF')
    return connection

# SQL Queries
retrieveetf_sql = "SELECT `idetf` FROM `etf` WHERE `etf_symbol` = %s"
insert_sql = """
    INSERT INTO `etf_daily_transaction`(
        `etf_id`, `etf_daily_traded_volume`, `etf_daily_traded_value`, `etf_last_traded_price`,
        `etf_prevclose_price`, `etf_trade_date`, `etf_traded_high`, `etf_traded_low`, 
        `etf_day_open`, `etf_daily_nooftrade`, `etf_52wh`, `etf_52wl`, 
        `etf_daily_deliverableqty`, `etf_daily_deliverablepercentageqty`
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Step 1: Pull latest changes from GitHub
def pull_latest_changes():
    os.chdir(REPO_PATH)
    subprocess.run(['git', 'pull'], check=True)
    print("Pulled latest changes from GitHub")

# Step 2: Process the CSV file and update the database
def process_csv_file(file_path):
    connection = connect_db()
    cursor = connection.cursor()
    
    # Load the CSV file
    dataDetails = pd.read_csv(file_path)
    
    missingETF = []
    
    # Iterate over each row in the CSV
    for rwCnt in dataDetails.index:
        etfTradeDate = dataDetails.iloc[rwCnt, 0]
        etfNav = dataDetails.iloc[rwCnt, 2]
        etfDateOpen = dataDetails.iloc[rwCnt, 3]
        etfHigh = dataDetails.iloc[rwCnt, 4]
        etfLow = dataDetails.iloc[rwCnt, 5]
        etfLTP = dataDetails.iloc[rwCnt, 6]
        etfPrevclose = dataDetails.iloc[rwCnt, 7]
        etfVwap = dataDetails.iloc[rwCnt, 8]
        etf52WH = dataDetails.iloc[rwCnt, 9]
        etf52WL = dataDetails.iloc[rwCnt, 10]
        etfVolume = dataDetails.iloc[rwCnt, 11]
        etfValue = dataDetails.iloc[rwCnt, 12]
        etfDayTrade = dataDetails.iloc[rwCnt, 13]
        etfsymboldetail = dataDetails.iloc[rwCnt, 14]
        etfDeliverableQty = dataDetails.iloc[rwCnt, 15]
        etfDeliverableQtyPercentage = dataDetails.iloc[rwCnt, 16]
        
        # Retrieve ETF details from the database
        cursor.execute(retrieveetf_sql, etfsymboldetail)
        etfInfo = cursor.fetchone()
        
        if etfInfo:
            etfID = etfInfo[0]
            Values = (
                etfID, etfVolume, etfValue, etfLTP, etfPrevclose, etfTradeDate, etfHigh, etfLow, 
                etfDateOpen, etfDayTrade, etf52WH, etf52WL, etfDeliverableQty, etfDeliverableQtyPercentage
            )
            print("Inserting values into ETF daily transaction:", Values)
            cursor.execute(insert_sql, Values)
        else:
            print(f"ETF symbol '{etfsymboldetail}' not found in the database.")
            missingETF.append(etfsymboldetail)
    
    # Write missing ETF symbols to an Excel file
    if missingETF:
        dateInfo = (pd.Timestamp.today()).strftime("%d-%b-%Y")
        missingETFDataFrame = pd.DataFrame(missingETF, columns=['ETF_Name'])
        error_file_path = os.path.join('/path_to_error_folder/', f'{dateInfo}_missing_etfs.xlsx')
        missingETFDataFrame.to_excel(error_file_path, index=False)
        print(f"Missing ETF data written to {error_file_path}")
    
    connection.commit()
    cursor.close()
    connection.close()

# Step 3: Delete the file locally and in GitHub
def delete_file(file_name):
    # Delete locally
    file_path = os.path.join(REPO_PATH, FILES_DIR, file_name)
    os.remove(file_path)
    print(f"Deleted local file: {file_name}")
    
    # Stage and push changes to GitHub
    subprocess.run(['git', 'add', file_path], check=True)
    subprocess.run(['git', 'commit', '-m', f"Deleted {file_name} after processing"], check=True)
    subprocess.run(['git', 'push'], check=True)
    print(f"Pushed file deletion to GitHub: {file_name}")

# Step 4: Process files in the repository
def process_files():
    pull_latest_changes()
    os.chdir(os.path.join(REPO_PATH, FILES_DIR))
    
    #for file_name in os.listdir('.'):
        #if file_name.endswith('.csv'):
            # Process CSV file
            #process_csv_file(file_name)
            
            # Delete file after processing
            #delete_file(file_name)

if __name__ == '__main__':
    process_files()
