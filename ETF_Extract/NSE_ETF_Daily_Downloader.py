import requests
import time
import csv
import os

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
    # hit the homepage first to get cookies
    resp = session.get(home_url)
    if resp.status_code != 200:
        print(f"Failed to get homepage, status: {resp.status_code}")
        return None
    time.sleep(5)  # wait to mimic real user browsing
    return session

def fetch_etf_data(session):
    if not session:
        return None
    try:
        response = session.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response content: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_to_csv(json_data, csv_file_path):
    if not json_data or "data" not in json_data:
        print("No valid JSON data to convert.")
        return

    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            etf_data = json_data["data"]
            headers = etf_data[0].keys()
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
    json_data = fetch_etf_data(session)
    if json_data:
        csv_file_name = f'ETF_data_{time.strftime("%Y-%m-%d")}.csv'
        csv_file_path = os.path.join(os.getcwd(), csv_file_name)
        save_to_csv(json_data, csv_file_path)
        print(f"Saved ETF data to {csv_file_path}")
    else:
        print("Failed to fetch ETF data")

if __name__ == "__main__":
    main()
