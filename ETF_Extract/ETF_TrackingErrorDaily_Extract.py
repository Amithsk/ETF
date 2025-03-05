#Extract the tracking error details from the website
#Tracking error  details are provided daily,so the code extrac the information daily basis
#The output of the code will be excel file with the date information
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Define the request details
BASE_URL = "https://www.amfiindia.com/modules/TrackingErrorDetails"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
PAYLOAD = {
    "strMfID": "-1",  # Fetch all mutual funds
    "strType": "1",   # Data type (Tracking Error)
    "strdt": "01-Sep-2023"  # Static date for debugging, can be updated dynamically
}

# Send the POST request
response = requests.post(BASE_URL, headers=HEADERS, data=PAYLOAD)

if response.status_code != 200:
    raise Exception(f"Failed to fetch data: {response.status_code}")

output_path =r"D:\\ETF_Data\\ETFProcessData\\Downloaded\\TrackingError"
output_file_name = "debug_processed_data.txt"
outputfinal = os.path.join(output_path, output_file_name)
# Save the response
with open(outputfinal, "w", encoding="utf-8") as file:
    file.write(response.text)
print(f"Response saved to {outputfinal} for inspection.")

# Parse the HTML response
soup = BeautifulSoup(response.text, "html.parser")

# Locate all tables in the HTML
tables = soup.find_all("table", style="width:100%;margin-top:0;")
if not tables or len(tables) < 2:
    raise ValueError("Expected at least two tables, but found fewer.")

# 1. Extract Date Information from the First Table
date_table = tables[0]
date_row = date_table.find("tr")
if not date_row:
    raise ValueError("Date table is empty or has an unexpected structure.")

date_text = date_row.get_text(strip=True)
if "Tracking Error for" in date_text:
    date_info = date_text.split("for")[-1].strip().replace("-", "_")  # Extract date
else:
    raise ValueError("Date format is unexpected in the first table.")

# 2. Extract Data from the Second Table
data_table = tables[1]
rows = data_table.find_all("tr")
if len(rows) < 2:
    raise ValueError("Mutual fund details table has an unexpected structure.")

# Extract first-level headers
first_level_headers = []
first_level_spans = []  # Track the colspan for each first-level header
for th in rows[0].find_all("th"):
    colspan = int(th.get("colspan", 1))  # Default colspan is 1
    first_level_headers.extend([th.text.strip()] * colspan)  # Repeat header based on colspan
    first_level_spans.append(colspan)

# Extract second-level headers
second_level_headers = [th.text.strip() for th in rows[1].find_all("th")]

# Combine first and second-level headers
final_headers = []
second_level_index = 0  # Track the position in the second-level headers

for header, span in zip(first_level_headers, first_level_spans):
    if span > 1:  # Combine first-level header with its sub-headers
        final_headers.extend([f"{header}_{second_level_headers[i]}" for i in range(second_level_index, second_level_index + span)])
        second_level_index += span
    else:  # No sub-header, use the first-level header as-is
        final_headers.append(header)


# Print the final headers for debugging
print(f"Final Headers: {final_headers}")

# Extract data rows from the second table
data = []
for row in rows[2:]:  # Skip the header row
    cells = [cell.text.strip() for cell in row.find_all(["td", "th"])]
    print("The values",cells)
    if len(cells) == len(final_headers):  # Ensure the row matches the header length
        data.append(cells)
        

# Create DataFrame from the extracted data
df = pd.DataFrame(data, columns=final_headers)

# Add the extracted date information to the DataFrame
print ("The date info",date_info)
df["Report Date"] = date_info

        
if df is not None:
     file_path = r"D:\\ETF_Data\\ETFProcessData\\Downloaded\\TrackingError"
     output_file = f"TrackingErrorData.xlsx"
     full_path = os.path.join(file_path, output_file)
     df.to_excel(full_path, index=False)
     print(f"Data saved to {output_file}")
    
else:
        print("No data was fetched.")
