import requests
import time
import csv
import os
from datetime import datetime
import random

home_url = 'https://www.nseindia.com/market-data/exchange-traded-funds-etf'
api_url = 'https://www.nseindia.com/api/etf'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": home_url,
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.nseindia.com"
}

def establish_session():
    session = requests.Session()
    session.headers.update(headers)
    try:
        resp = session.get(home_url, timeout=10)
        if resp.status_code == 200:
            time.sleep(2)  # mimic human-like delay
            return session
        else:
            print(f"Failed to access homepage, status code: {resp.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Session request failed: {e}")
        return None

def fetch_etf_data(session):
    # Add random wait 0–15 min after cutoff
    wait_seconds = random.randint(0,30)
    print(f"Waiting {wait_seconds} seconds before fetching today's data...")
    time.sleep(wait_seconds)
    if not session:
        return None
    try:
        response = session.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_to_csv(json_data, csv_file_path):
    if not json_data or "data" not in json_data or not json_data["data"]:
        print("No valid or non-empty JSON data to convert.")
        return

    try:
        etf_data = json_data["data"]
        headers = etf_data[0].keys()

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for item in etf_data:
                writer.writerow(item.values())

        print(f"CSV file created successfully at {csv_file_path}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

def main():
    session = establish_session()
    if not session:
        print("Session establishment failed")
        return
    wait_seconds = random.randint(30, 180)
    print(f"Waiting {wait_seconds} seconds before fetching today's data...")
    time.sleep(wait_seconds)

    json_data = fetch_etf_data(session)
    if json_data:

        today_str = datetime.now().strftime('%Y-%m-%d')
        csv_file_name = f'ETF_data_{today_str}.csv'
        csv_file_path = os.path.join(os.getcwd(), csv_file_name)
        save_to_csv(json_data, csv_file_path)
    else:
        print("Failed to fetch ETF data")

if __name__ == "__main__":
    main()
