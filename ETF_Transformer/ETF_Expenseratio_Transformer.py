import pandas as pd
from pathlib import Path
import magic

# === CONFIGURATION ===
# Paths to the two input Excel files
etf_file = r'D:\ETF_Data\ETFDataProcessing\ETFRawData\ExpenseRatio\ETF_Mar_25.xlsx'
gold_file = r'D:\ETF_Data\ETFDataProcessing\ETFRawData\ExpenseRatio\Gold_Mar_25.xlsx'

# Output directory
destination_dir = Path(r'D:\ETF_Data\ETFDataProcessing\ETFProcessedData\ExpenseRatio')
destination_dir.mkdir(parents=True, exist_ok=True)

# === COLUMNS TO EXTRACT ===
columns_required = [
    'Scheme Name',
    'TER Date',
    'Regular Plan - Total TER (%)',
    'Direct Plan - Total TER (%)'
]

def debug_etf_trace(df, etf_name, regular_col='Regular Plan - Total TER (%)', direct_col='Direct Plan - Total TER (%)'):
    import pandas as pd

    print(f"\n🔍 DEBUG TRACE for: {etf_name}\n{'-'*60}")
    
    # Step 1: Filter ETF rows
    etf_df = df[df['Scheme Name'].str.contains(etf_name, case=False, na=False)].copy()
    
    if etf_df.empty:
        print(f"ETF '{etf_name}' not found in raw data.")
        return

    print(f"✅ Found {len(etf_df)} rows for '{etf_name}' in raw data.")
    print(etf_df)


# === STEP 1: LOAD AND COMBINE FILES ===
print(etf_file,gold_file)
df1 = pd.read_excel(etf_file, usecols=columns_required)
df2 = pd.read_excel(gold_file, usecols=columns_required)

# Combine the two datasets
df = pd.concat([df1, df2], ignore_index=True)



# === STEP 2: CLEANING AND PREPROCESSING ===

# Check if both TER columns exist
regular_col = 'Regular Plan - Total TER (%)'
direct_col = 'Direct Plan - Total TER (%)'

if regular_col not in df.columns and direct_col not in df.columns:
    raise ValueError("Neither Regular nor Direct TER columns found in the files.")


# Coerce both TER columns to numeric
df[regular_col] = pd.to_numeric(df.get(regular_col), errors='coerce')
df[direct_col] = pd.to_numeric(df.get(direct_col), errors='coerce')

# Row-wise combine: prefer Regular if present, else Direct
df['TER (%)'] = df.apply(
    lambda row: row[direct_col] if pd.isna(row[regular_col]) or row[regular_col] == 0 else row[regular_col],
    axis=1
)

# Convert TER Date to Month period
df['Month'] = pd.to_datetime(df['TER Date']).dt.to_period('M')

# Keep only relevant data
df = df[['Scheme Name', 'Month', 'TER (%)']].dropna()
#To debug for any issue
#debug_etf_trace(df, "DSP Nifty Bank ETF")



# === STEP 3: MONTHLY AVERAGE CALCULATION ===
monthly_ter = (
    df.groupby(['Scheme Name', 'Month'])['TER (%)']
    .mean()
    .reset_index()
    .rename(columns={'TER (%)': 'Total TER (%)'})
)

# === STEP 4: SAVE OUTPUT ===
latest_month = monthly_ter['Month'].max().strftime('%b%y')
output_file = destination_dir / f'ETF_Data_{latest_month}.xlsx'


monthly_ter.to_excel(output_file, index=False)

print(f"✅ Combined monthly TER saved to {output_file}")
print(monthly_ter)
