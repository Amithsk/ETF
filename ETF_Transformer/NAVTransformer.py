#To extract the NAV values of the ETF from the data extracted from AMFI(Association of Mutual funds in India)
#The file will be .txt format
#Code will extract the values with ETF and transform into CSV file
import csv
import re

# Function to extract ETF data from the provided file and save it to a CSV
def extract_etf_data(input_file, output_file):
    # Initialize a list to store the extracted ETF values
    etf_data = []

    # Define a regular expression pattern to match dates in the format "27-Jun-2024"
    date_pattern = re.compile(r'\d{2}-[A-Za-z]{3}-\d{4}')
    current_date = None

    # Define a regular expression pattern to ignore lines starting with "Open Ended Schemes"
    ignore_pattern = re.compile(r'^Open Ended Schemes')

    # Read the input file

    with open(input_file, 'r') as file:
        for line in file:
            # Check if the line contains a date and update the current date
            if re.search(date_pattern, line):
                current_date = re.search(date_pattern, line).group()
            
            # Skip the line if it starts with "Open Ended Schemes"
            if ignore_pattern.match(line):
                continue

            # Check if the line contains information related to ETFs
            if 'ETF' in line and current_date:
                # Assuming the format is "ETF_NAME: NAV" or similar
                print(line.split(';', 8))
                etf_id,etf_name,etf_random1,etf_random2,nav,etf_random3,etf_random4,etf_date = line.split(';', 8)
                etf_data.append([current_date, etf_name.strip(), nav.strip()])

    # Write the extracted ETF data to a CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'ETF Name', 'NAV'])  # Write the header
        writer.writerows(etf_data)  # Write the ETF data rows

    print(f"ETF values with dates extracted and saved to {output_file}")

# Main script
if __name__ == "__main__":
    # Prompt the user to input the file name
    input_file = input("Please enter the name of the input file (including the extension): ")
    output_file = input("Please enter the name of the output CSV file (including the extension): ")

    # Run the function to extract ETF data and save it to the CSV
    extract_etf_data(input_file, output_file)
