import pandas as pd
from openpyxl import load_workbook

# Load workbook and sheet
excel_path = r'D:\ETF_Data\ETFDataProcessing\ETFRawData\AUM_Returns\Fund-Performance-28-Feb-2025.xlsx'
wb = load_workbook(excel_path, data_only=True)
ws = wb['Fund_Performance']

# Find the row where "Fund Performance" appears
start_row = None
for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
    if row and "Fund Performance" in str(row[0]):
        start_row = i  # Data header is one row after this
        break

if start_row is None:
    raise ValueError("Could not find 'Fund Performance' in the sheet.")

# Load the Excel file using pandas from the detected header row
df = pd.read_excel(excel_path, sheet_name='Fund_Performance', header=start_row)

# Clean column names
def clean_column_name(col):
    return str(col).strip().replace('(%)', '').replace(' ', '_').replace('.', '').lower()

df.columns = [clean_column_name(col) for col in df.columns]
print(df.columns)

# Filter ETF rows
etf_df = df[
    df['scheme_name'].str.contains('ETF', case=False, na=False) &
    ~df['scheme_name'].str.contains(r'\bFOF\b|Fund of Fund', case=False, na=False)
    ].copy()

# Define columns for ETF and Benchmark
etf_columns_mapping = {
    'scheme_name': 'Scheme Name',
    'nav_date': 'NAV Date',
    'nav_regular': 'NAV Regular',
    'return_1_year__regular': 'Return 1 Year regular',
    'return_3_year__regular': 'Return 3 Year regular',
    'return_5_year__regular': 'Return 5 Year regular',
    'return_10_year__regular': 'Return 10 Year Regular',
    'return_since_launch_regular': 'Return Since launch Regular',
    'daily_aum_(cr)': 'Daily AUM(Cr)'
}

benchmark_columns_mapping = {
    'benchmark': 'Benchmark',
    'nav_date': 'Date',
    'return_1_year__benchmark': 'Return 1Year Benchmark',
    'return_3_year__benchmark': 'Return 3 year Benchmark',
    'return_5_year__benchmark': 'Return 5 year Benchmark',
    'return_10_year__benchmark': 'Return 10 Year Benchmark',
    'return_since_launch__benchmark': 'Return Since Launch Benchmark'
}

# Final ETF dataframe
etf_final = etf_df[list(etf_columns_mapping.keys())].rename(columns=etf_columns_mapping)

# Create output file names
from pathlib import Path
month_str = pd.to_datetime(etf_final['NAV Date'].iloc[0]).strftime('%b-%Y')
destination_dir = Path(r'D:\ETF_Data\ETFDataProcessing\ETFProcessedData\AUM_Returns')

# Save ETF data
etf_file = destination_dir / f'ETF_Data_{month_str}.xlsx'
etf_final.to_excel(etf_file, index=False)


# Define the fields to evaluate completeness
benchmark_fields = list(benchmark_columns_mapping.keys())
benchmark_rows = etf_df[benchmark_fields].dropna(subset=['benchmark'])

# Group by benchmark and select the most complete row
best_rows = []
for benchmark, group in benchmark_rows.groupby('benchmark'):
    best_row = None
    max_filled = -1
    for _, row in group.iterrows():
        filled_count = sum(
            pd.notna(row[field]) and str(row[field]).strip() != '' for field in benchmark_fields
        )
        if filled_count > max_filled:
            max_filled = filled_count
            best_row = row
    if best_row is not None:
        best_rows.append(best_row)

# Create final Benchmark DataFrame
benchmark_df = pd.DataFrame(best_rows).rename(columns=benchmark_columns_mapping)

# Save benchmark data
benchmark_file = destination_dir / f'Benchmark_Data_{month_str}.xlsx'
benchmark_df.to_excel(benchmark_file, index=False)
print(f"✅ Exported benchmark data for {len(benchmark_df)} unique benchmarks.")

# Get the AUM details
etf_aum_df = etf_final[['Scheme Name', 'NAV Date', 'Daily AUM(Cr)']].copy()
etf_aum_df['Month'] = pd.to_datetime(etf_aum_df['NAV Date']).dt.strftime('%b-%Y')
etf_aum_df = etf_aum_df[['Scheme Name', 'Month', 'Daily AUM(Cr)']]  # Reorder
etf_aum_df.rename(columns={'Daily AUM(Cr)': 'AUM'}, inplace=True)

# Save AUM data
etf_aum_file = destination_dir / f'ETF_AUM_{month_str}.xlsx'
etf_aum_df.to_excel(etf_aum_file, index=False)


print(f"Files created:\n- {etf_file}\n- {benchmark_file}")
