# NSE ETF Data Downloader using Selenium + undetected-chromedriver
import undetected_chromedriver as uc
import csv
import json
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Target URLs
home_url = 'https://www.nseindia.com/market-data/exchange-traded-funds-etf'
api_url = 'https://www.nseindia.com/api/etf'

def fetch_etf_data():
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    driver.get(home_url)

    # Let the cookies and headers load properly
    time.sleep(5)

    # Get cookies and headers
    selenium_cookies = driver.get_cookies()
    cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
        "Referer": home_url,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }

    # Now fetch the API using the cookies and headers
    import requests
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)

    try:
        response = session.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            print("Response:", response.text[:200])
            return None
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        driver.quit()

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

def main():
    json_data = fetch_etf_data()
    if json_data:
        csv_file_name = f'ETF_data_{time.strftime("%Y-%m-%d")}.csv'
        csv_file_path = os.path.join(os.getcwd(), csv_file_name)
        save_to_csv(json_data, csv_file_path)
        return csv_file_name

if __name__ == "__main__":
    main()
