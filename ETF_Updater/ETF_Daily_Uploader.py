import os
import subprocess
import pymysql
import pandas as pd
from datetime import datetime

# GitHub repository details
REPO_PATH = '/Volumes/Project/ETFAnalyser/ETF'  # Local path to your repository
FILES_DIR = '/Volumes/Project/ETFAnalyser/ETF/ETF_Data/Download'  # Directory where the files are located inside the repo 

# DB connection setup
def connect_db():
    password = os.getenv('MYSQL_PASSWORD')
    connection = pymysql.connect(host='localhost', user='root', password='', db='ETF')
    return connection

# SQL Queries
retrieveetf_sql = "SELECT `idetf` FROM `etf` WHERE `etf_symbol` = %s"
insert_sql="INSERT `etf_daily_transaction`(`etf_id`,`etf_daily_traded_volume`,`etf_daily_traded_value`,`etf_last_traded_price`,`etf_prevclose_price`,`etf_trade_date`,`etf_traded_high`,`etf_traded_low`,`etf_day_open`,`etf_daily_nooftrade`,`etf_52wh`,`etf_52wl`,`etf_daily_deliverableqty`,`etf_daily_deliverablepercentageqty`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

# Step 1: Pull latest changes from GitHub
def pull_latest_changes():
    os.chdir(REPO_PATH)
    subprocess.run(['git', 'pull'], check=True)
    print("Pulled latest changes from GitHub")

# Step 2: Process the CSV file and update the database
def process_csv_file(file_path, etf_trade_date):
    connection = connect_db()
    cursor = connection.cursor()

    # Load the CSV file
    dataDetails = pd.read_csv(file_path)

    missingETF = []

    # Iterate over each row in the CSV
    for rwCnt in dataDetails.index:
        etfsymboldetail = dataDetails.iloc[rwCnt, 0]
        etfDateOpen = dataDetails.iloc[rwCnt, 2]
        etfHigh = dataDetails.iloc[rwCnt, 3]
        etfLow = dataDetails.iloc[rwCnt, 4]
        etfLTP = dataDetails.iloc[rwCnt, 5]
        etfVolume = dataDetails.iloc[rwCnt, 8]
        etfValue = dataDetails.iloc[rwCnt, 9]
        etfNav = dataDetails.iloc[rwCnt, 10]
        etf52WH= dataDetails.iloc[rwCnt, 11]
        etf52WL= dataDetails.iloc[rwCnt, 12]
        etfPrevclose = dataDetails.iloc[rwCnt, 17]
        #Below values are not returned in the daily report,so assigning null values for now
        etfDayTrade=0
        etfDeliverableQtyPercentage=0
        etfDeliverableQty=0


        # Retrieve ETF details from the database
        cursor.execute(retrieveetf_sql, etfsymboldetail)
        etfInfo = cursor.fetchone()

        if etfInfo:
            etfID = etfInfo[0]
            Values = (
                etfInfo,etfVolume,etfValue,
                etfLTP,etfPrevclose,
                etf_trade_date,etfHigh,etfLow,etfDateOpen,
                etfDayTrade,
                etf52WH,etf52WL,
                etfDeliverableQty,
                etfDeliverableQtyPercentage
            )
            print("Inserting values into ETF daily transaction:", Values)
            #cursor.execute(insert_sql, Values)
        else:
            print(f"ETF symbol '{etfsymboldetail}' not found in the database.")
            missingETFdetails=[etfsymboldetail,etfVolume,etfValue,etfLTP,etfPrevclose,etf_trade_date,etfHigh,etfLow,etfDateOpen,etfDayTrade,etf52WH,etf52WL,etfDeliverableQty,etfDeliverableQtyPercentage]
            missingETF.append(missingETFdetails)

    # Write missing ETF symbols to an Excel file
    if missingETF:
        dateInfo = (pd.Timestamp.today()).strftime("%d-%b-%Y")
        missingETFcolumns = ['ETF_Symbol', 'Volume', 'Value', 'Last_Trade_Price', 'Previous_Close', 'Trade_Date','Day_High', 'Day_Low', 'Open_Price', 'Day_Trades', '52_Week_High', '52_Week_Low', 'Deliverable_Quantity', 'Deliverable_Quantity_Percentage']
        missingETFDataFrame = pd.DataFrame(missingETF, columns=missingETFcolumns)
        file_name ="MissingAsset_"+dateInfo+".xlsx"	
        file_path =os.path.join(r"D:\ETF_Data\ETF_Error\\", file_name)	
        missingETFDataFrame.to_excel(file_path, index=False)
        print(f"Missing ETF data written to {file_path}")

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

    # Iterate through each CSV file
    for file_name in os.listdir('.'):
        if file_name.endswith('.csv'):
            # Extract date from the file name, assuming it follows the format ETF_data_YYYY-MM-DD.csv
            date_str = file_name.split('_')[-1].replace('.csv', '')
            etf_trade_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            
            # Process CSV file with extracted date
            process_csv_file(file_name, etf_trade_date)

            # Delete file after processing
            #delete_file(file_name)

if __name__ == '__main__':
    process_files()
