import pandas as pd
from pathlib import Path
import re
from openpyxl import load_workbook

def debug_etf_row(etf_name):
    matches = etf_df[etf_df['scheme_name'].str.contains(etf_name, case=False, na=False)]

    if matches.empty:
        print(f"\n No matching ETF found for: '{etf_name}'")
        return

    for idx, row in matches.iterrows():
        print(f"\n--- Debugging ETF: {row['scheme_name']} ---")
        print("\nFull row data:")
        print(row.to_string())

        print("\nTracking Difference Checks:")
        for period in time_periods:
            for variant in preferred_order:
                col_name = f"tracking_difference_{period}_{variant}"
                if col_name in etf_df.columns:
                    val = row.get(col_name)
                    status = f"{val}" if pd.notna(val) else " Missing"
                    print(f"  {col_name}: {status}")
                else:
                    print(f"Column not found: {col_name}")


# Load workbook and sheet
excel_path = r'D:\ETF_Data\ETFDataProcessing\ETFRawData\TrackingError\TrackingDifference_Mar_25.xlsx'
wb = load_workbook(excel_path, data_only=True)
ws = wb.active

# Find the row where "Tracking difference" appears
title_row = None
title_text = None
for row in ws.iter_rows(min_row=1, max_row=20):  # Search first 20 rows
    for cell in row:
        if cell.value and isinstance(cell.value, str) and cell.value.startswith('Tracking Difference for'):
            title_row = cell.row
            title_text = cell.value.strip()
            break
    if title_row:
        break

if title_row is None:
    raise ValueError("Header starting with 'Tracking Difference for' not found.")


# Extract month string
match = re.search(r'Tracking Difference for (\w{3}-\d{4})', title_text)
if match:
    month_str = match.group(1)
else:
    raise ValueError("Could not extract month string like 'Mar-2025'.")


# Step 2: Get the 3 header rows
header_1 = [str(cell.value).strip() if cell.value else '' for cell in ws[title_row + 1]]
header_2 = [str(cell.value).strip() if cell.value else '' for cell in ws[title_row + 2]]
header_3 = [str(cell.value).strip() if cell.value else '' for cell in ws[title_row + 3]]

# Step 3: Combine headers with forward fill for blanks
def clean_part(x):
    return re.sub(r'[^a-zA-Z0-9]+', '_', x.replace('(%)', '')).lower().strip('_')

# Forward fill blank cells in header rows to propagate values
def forward_fill(lst):
    last = ''
    out = []
    for val in lst:
        if val:
            last = val
        out.append(last)
    return out

header_1_filled = forward_fill(header_1)
header_2_filled = forward_fill(header_2)
header_3_filled = forward_fill(header_3)

combined_headers = []
for h1, h2, h3 in zip(header_1_filled, header_2_filled, header_3_filled):
    clean_h1 = clean_part(h1)
    clean_h2 = clean_part(h2)
    clean_h3 = clean_part(h3)
    
    # Special handling for scheme and benchmark
    if clean_h1.startswith("scheme_name") or clean_h1.startswith("benchmark"):
        combined_headers.append(clean_h1)
        continue

    # Construct the full header name
    if "since_launch" in clean_h2:
        full = f"tracking_difference_since_launch_{clean_h3}"
    else:
        parts = [clean_h1, clean_h2, clean_h3]
        full = "_".join(p for p in parts if p)
    
    combined_headers.append(full.strip('_'))


# Step 4: Read data below the headers
data_start_row = title_row + 4
df = pd.read_excel(excel_path, header=None, skiprows=data_start_row)
df.columns = combined_headers
df = df.dropna(how='all')  # Drop fully empty rows


# Filter ETF rows
etf_df = df[
    df['scheme_name'].str.contains('ETF', case=False, na=False) &
    ~df['scheme_name'].str.contains(r'\bFOF\b|Fund of Fund', case=False, na=False)
    ].copy()


# These are your preferred column suffixes
time_periods = ['1_year', '3_year', '5_year', '10_year', 'since_launch']
preferred_order = ['regular', 'direct']  # prefer regular, fallback to direct

# Always include scheme_name and benchmark
final_columns = {'scheme_name': 'scheme_name', 'benchmark': 'benchmark'}



# Always include scheme_name and benchmark
final_columns = {'scheme_name': 'scheme_name', 'benchmark': 'benchmark'}

# Dynamically choose the first available column with actual data (not NaN)
for period in time_periods:
    selected = False
    for variant in preferred_order:
        col_name = f"tracking_difference_{period}_{variant}"
        if col_name in etf_df.columns:
            # Check if this column has ANY non-null value across ETF rows
            if etf_df[col_name].notna().sum() > 0:
                label = period.replace('_', '-').title()
                final_columns[col_name] = f"{label} ({variant.title()})"
                selected = True
              
    if not selected:
        print(f"No usable tracking difference column for {period}")

#To debug the issues        
#debug_etf_row('Zerodha Nifty 1D Rate Liquid ETF')

# Filter and rename
#print("Final columns being extracted:")
#print(final_columns)

etf_rows = etf_df[list(final_columns.keys())].dropna(subset=['scheme_name'])
etf_final = etf_rows.rename(columns=final_columns)

#print(etf_final)

# Create output file names
destination_dir =Path(r'D:\ETF_Data\ETFDataProcessing\ETFProcessedData\TrackingError')

# Save ETF data with placeholder for header
etf_file = destination_dir / f'ETF_Data_{month_str}.xlsx'
etf_final.to_excel(etf_file, index=False, startrow=1)

# Add the month string at the top
wb = load_workbook(etf_file)
ws = wb.active
ws.insert_rows(1)
ws['A1'] = f"Tracking Difference for {month_str}"
wb.save(etf_file)

print(f"Files created:\n- {etf_file}\n")
