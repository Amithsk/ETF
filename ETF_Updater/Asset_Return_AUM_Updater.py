#To update the Asset return details to the DB
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


# Step 1: Formatting function (Editable)
def format_asset_name(asset_name):
    if not asset_name:
        return asset_name

    # Rule1:Trim 
    asset_name = asset_name.strip()
    # Replace non-breaking space
    asset_name = str(asset_name).replace('\u00A0', ' ')
    
    #Rule 2:Replace 'TRI' at the end with 'Index'
    asset_name = re.sub(r'(?<!\bIndex)\s*\(?\s*(TRI|Total\s+Return\s+Index)\s*\)?\s*$',' Index',asset_name,flags=re.IGNORECASE)
    

    # Rule 3: Add 'Index' if it's not present
    if re.search(r'\bindex\b', asset_name, flags=re.IGNORECASE) is None:
        asset_name += ' Index'

    # Rule 4: Convert 'Weighted' to 'Weight'
    asset_name = asset_name.replace('Weighted', 'Weight')

    # Rule 5: Normalize whitespace
    asset_name = re.sub(r'\s+', ' ', asset_name).strip()

    # Rule 6: Add 'S&P' to BSE assets
    if asset_name.startswith("BSE"):
        asset_name = "S&P " + asset_name

    # Rule 7: Fix space after '400'
    asset_name = re.sub(r'(?<!\s)400(?!\s)', ' 400 ', asset_name)     # No space before or after
    asset_name = re.sub(r'(?<!\s)400(?=\s)', ' 400', asset_name)      # No space before, has space after
    asset_name = re.sub(r'(?<=\s)400(?!\s)', '400 ', asset_name)      # Has space before, no space after
    asset_name = re.sub(r'\s{2,}', ' ', asset_name).strip() 

    # Rule 8: Fix space after '200'
    asset_name = re.sub(r'(?<!\s)200(?!\s)', ' 200 ', asset_name)     # No space before or after
    asset_name = re.sub(r'(?<!\s)200(?=\s)', ' 200', asset_name)      # No space before, has space after
    asset_name = re.sub(r'(?<=\s)200(?!\s)', '200 ', asset_name)      # Has space before, no space after
    asset_name = re.sub(r'\s{2,}', ' ', asset_name).strip() 

    

    #Rule 9:Specific known pattern 
        #Replace NASDAQ-100 with NASDAQ 100
    asset_name = re.sub(r'^NASDAQ\-100\b', 'NASDAQ 100', asset_name, flags=re.IGNORECASE)
        #Replace NIFTY50 to  NIFTY 50 [Add space]
    asset_name = re.sub(r'(?i)\bNifty\s*50\b|Nifty50', 'Nifty 50', asset_name)
    
    # Rule 10: Replace 
        #Replace gold-related phrases with 'Gold Index'
    asset_name = re.sub(r'(?i)\b(Domestic\s+)?Prices?\s+of\s+(physical\s+)?Gold(\s+Index)?\b','Gold Index',asset_name)
    asset_name = re.sub(r'(?i)\bLBMA\s+AM\s+Gold\s+Prices?\s*-\s*IPru\b','Gold Index', asset_name)

    #Replace various silver-related phrases with 'Silver Index'
    asset_name = re.sub(
    r'(?i)\b((Domestic\s+)?Prices?\s+of\s+(physical\s+)?Silver|LBMA\s+AM\s+fixing\s+Prices)\s*(Index)?\b',
    'Silver Index', asset_name)

    #Replace  NYSE FANG -> NYSE FANG INDEX
    asset_name = re.sub(r'(?i)\bNYSE\s+FANG\+\s+Index\b', 'NYSE FANG INDEX', asset_name)
    #Replace  HANG SENG -> HANG SENG INDEX
    asset_name = re.sub(r'(?i)\bHang\s+Seng\s+TECH\s+Index\b', 'HANG SENG INDEX', asset_name)
    #Replace Nifty Alpha Low -Volatility 30 TRI ->Nifty Alpha Low-Volatility 30 TRI
    asset_name = re.sub(r'(?i)^Nifty Alpha Low\s*-\s*Volatility 30 Index$', 'NIFTY ALPHA LOW-VOLATILITY 30 INDEX', asset_name)

    #Replace NIFTY 500 Multicap 50:25:25 Total Return Index → NIFTY 500 MULTICAP 50:25:25 INDEX
    #asset_name = re.sub(r'(?i)\bNIFTY\s*500\s*MULTICAP\s*50:25:25\s*(Total\s+Return\s+Index|TRI)?\b',
    #'NIFTY 500 MULTICAP 50:25:25 INDEX',asset_name)

    #Replace  NIFTY500 Value 50 TRI → NIFTY500 VALUE 50 INDEX
    #asset_name = re.sub(r'(?i)\bNIFTY\s*500\s*VALUE\s*50\s*(TRI|Total\s+Return\s+Index)?\b',
    #'NIFTY500 VALUE 50 INDEX',asset_name)

    #Replace Nifty Capital Markets Index (TRI) → NIFTY CAPITAL MARKETS INDEX
    asset_name = re.sub(r'(?i)\bNIFTY\s*CAPITAL\s*MARKETS\s*INDEX\s*(\(TRI\)|TRI|Total\s+Return\s+Index)?\b',
    'NIFTY CAPITAL MARKETS INDEX',asset_name)
    
    #Replace Nifty India New Age Consumption TRI → NIFTY INDIA CONSUMPTION INDEX
    asset_name = re.sub(r'(?i)\bNIFTY\s*INDIA\s*(NEW\s*AGE\s*)?CONSUMPTION\s*(TRI|Total\s+Return\s+Index|INDEX)?\b',
    'NIFTY INDIA CONSUMPTION INDEX',asset_name)

    # Rule 9+: Specific mapping for Shariah
    if re.search(r'(?i)\bNifty\s*50\s*Shariah\s*Index\b', asset_name):
        return "SHARIAH INDEX"

    # Rule 11: Remove the extra 'Index' if present twice
    asset_name = re.sub(r'(Index)(\s*|\u00A0)+Index', r'\1', asset_name, flags=re.IGNORECASE)

    return asset_name

# Load and normalize Benchmark Data into DataFrame
def load_and_format(file_location, file_pattern):
    search_path = os.path.join(file_location, file_pattern)
    files = glob.glob(search_path)
    
    #To display which file is getting processed
    print(f"Processing file: {files[0]}")
    if not files:
        raise FileNotFoundError(f"No files matching {search_path}")
    path = files[0]
    df = pd.read_excel(path)
    if 'Benchmark' not in df.columns:
        raise ValueError("Missing 'Benchmark' column in Excel.")
    # Extract month info from filename
    base = os.path.basename(path)
    m = re.search(r'Benchmark_Data_(.+?)\.', base)
    monthinfo = m.group(1) if m else 'UnknownMonth'
    # Create normalized column once
    df['FormattedBenchmark'] = df['Benchmark'].astype(str).apply(format_asset_name)
    return df, monthinfo

# Discovery: check which assets exist
def discovery_process(df, monthinfo, excluded_assets):
    conn = connect_db(); 
    cur = conn.cursor()
    missing = []
    for _, row in df.iterrows():
        raw = str(row['Benchmark']).strip()
        formatted = row['FormattedBenchmark']
        if raw in excluded_assets:
            continue
        cur.execute("SELECT idetf_asset FROM etf_asset WHERE asset_info = UPPER(%s)",(formatted,))
        if not cur.fetchone():
            missing.append(row)
    if missing:
        out = pd.DataFrame(missing)
        outfile = os.path.join(r'D:\ETF_Data\ETF_Error', f"MissingBenchmark_DATA_{monthinfo}.xlsx")
        out.to_excel(outfile, index=False)
        print(f"Saved missing to {outfile}")
    cur.close(); 
    conn.close()
#Function to ensure  that column names are dynamically identified and updated
def get_assetreturn_columns(columns):
    assetreturn_columns = {}
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
                assetreturn_columns[col] = time_period_map[key]
                break

    return assetreturn_columns


# Update DB with returns
def update_db(df, monthinfo, excluded_assets):
    connection = connect_db()
    cursor = connection.cursor()
    retrieve_sql = "SELECT `idetf_asset` FROM `etf_asset` WHERE `asset_info` = UPPER(%s)"

    insert_sql = (
        "INSERT INTO etf_asset_return_details"
        " (asset_id, asset_return_timeperiod, asset_returnsvalue, asset_returnsmonth, asset_returnsyear)"
        " VALUES (%s, %s, %s, %s, %s)"
    )
#To ensure that any change in the column header is handled dynamically 
    assetreturn_columns = get_assetreturn_columns(df.columns)
    if not assetreturn_columns:
        print("No valid return columns found in the file.")
        return
    
    # Step 1: Deduplicate by selecting the best row per asset
    best_rows = {}
    for _, row in df.iterrows():
        key = row['FormattedBenchmark']
        score = sum(not pd.isna(row.get(col)) for col in assetreturn_columns)  # Non-null count
        total = sum(float(row.get(col, 0)) if not pd.isna(row.get(col)) else 0 for col in assetreturn_columns)

        if key not in best_rows:
            best_rows[key] = (row, score, total)
        else:
            _, prev_score, prev_total = best_rows[key]
            if score > prev_score or (score == prev_score and total > prev_total):
                best_rows[key] = (row, score, total)

    # Step 2: Insert best row data into DB
    for asset_name, (row, _, _) in best_rows.items():
        if asset_name in excluded_assets:
            continue

        nav_date = pd.to_datetime(row["Date"])
        return_month = nav_date.strftime("%b")
        return_year = nav_date.year

        cursor.execute(retrieve_sql, (asset_name,))
        result = cursor.fetchone()

        if result:
            etf_id = result[0]
            for col, period_label in assetreturn_columns.items():
                value_raw = row.get(col)
                if pd.isna(value_raw):
                    print(f"Skipping {period_label} return for {asset_name} as it's missing.")
                    continue
                try:
                    value = float(value_raw)
                    #cursor.execute(insert_sql, (etf_id, period_label, value, return_month, return_year))
                except Exception as e:
                    print(f"Failed to insert {period_label} return for {asset_name}: {e}")
        else:
            print(f"Asset not found: {asset_name}")

    #connection.commit()
    cursor.close()
    connection.close()
           

if __name__ == '__main__':
    exclude = ['BSE PSU Bank TRI','Nifty MidSmall Healthcare TRI']
    loc = r'D:\ETF_Data\ETFDataProcessing\ETFProcessedData\AUM_Returns'
    pattern = 'Benchmark_Data_*-*'
    df, monthinfo = load_and_format(loc, pattern)
    discovery_process(df, monthinfo, exclude)
    update_db(df, monthinfo, exclude)
