#Code to download the ETF details from the NSE website
#Code needs to be adapted to Github action                                                
import requests
import csv
import time
import os

# Base URL to fetch ETF data in JSON format
api_url = 'https://www.nseindia.com/api/etf'
# Homepage URL to obtain cookies
home_url = 'https://www.nseindia.com/market-data/exchange-traded-funds-etf'

# Headers to simulate a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/market-data/exchange-traded-funds-etf",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

# Function to establish a session and fetch cookies
def establish_session():
    session = requests.Session()
    session.get(home_url, headers=headers)
    return session

# Function to fetch data using the session with cookies
def fetch_etf_data(session):
    try:
        response = session.get(api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to save JSON data to CSV
def save_to_csv(json_data, csv_file_path):
    if not json_data or "data" not in json_data:
        print("No valid JSON data to convert.")
        return

    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            etf_data = json_data["data"]

            # Write headers from the first item's keys
            headers = etf_data[0].keys()
            writer.writerow(headers)

            # Write rows
            for item in etf_data:
                writer.writerow(item.values())

        print(f"CSV file created successfully at {csv_file_path}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

# Main function to fetch the data and save it
def main():
    # Establish session
    session = establish_session()

    # Fetch ETF data using the session
    json_data = fetch_etf_data(session)

    # Save the JSON data to a CSV file in the current directory (for GitHub Actions)
    if json_data:
        csv_file_name = f'ETF_data_{time.strftime("%Y-%m-%d")}.csv'
        csv_file_path = os.path.join(os.getcwd(), csv_file_name)
        save_to_csv(json_data, csv_file_path)
        return csv_file_name  # Return the file name for committing

if __name__ == "__main__":
    main()
