#To extract the expense ratio of the ETF 
#Current process
#1.Download the data from the AMI website(Applying the filters)
#Future->Remove the manual process ,automate the whole flow
import pandas as pd
import os

# Load the Excel file
file_path =(r"D:\\ETF_Data\\ETFProcessData\\Downloaded\\ExpenseRatio\\Dec_ExpenseRatio.xlsx")
sheet_name = "Dec_ExpenseRatio1"

# Read the sheet
sheet_data = pd.read_excel(file_path, sheet_name=sheet_name)

# Filter rows where Scheme Name contains "ETF" but does not contain "FOF" or "Fund of Funds"
etf_data = sheet_data[
    sheet_data["Scheme Name"].str.contains("ETF|Exchange Traded Fund", case=False, na=False) &
    ~sheet_data["Scheme Name"].str.contains("FOF|Fund of Funds|Fund of Fund", case=False, na=False)
]

# Add a "Month" column extracted from the "TER Date"
etf_data["Month"] = pd.to_datetime(etf_data["TER Date"]).dt.to_period("M").astype(str)

# Calculate average TER values for Regular and Direct plans, grouped by Scheme Name and Month
average_ter = etf_data.groupby(["Scheme Name", "Month"]).agg(
    Regular=("Regular Plan - Base TER (%)", "mean"),
    Direct=("Direct Plan - Base TER (%)", "mean")
).reset_index()

# Perform addition if both Regular and Direct have values
average_ter["Total"] = average_ter[["Regular", "Direct"]].sum(axis=1, skipna=True)

# Rename columns for the final output
average_ter = average_ter.rename(columns={
    "Scheme Name": "Scheme Name",
    "Month": "Month",
    "Regular": "Regular",
    "Direct": "Direct"
})

# Save the result to an Excel file
file_name="Average_TER_ETFs_Updated.xlsx"
file_path =(r"D:\\ETF_Data\\ETFProcessData\\Processed\\ExpenseRatio")
output_file =os.path.join(file_path, file_name)	
average_ter.to_excel(output_file, index=False, header=["Scheme Name", "Month", "Regular", "Direct", "Total"])
print(f"Updated TER values saved to: {output_file}")
