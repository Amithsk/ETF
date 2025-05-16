import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import csv
import os

# NSE URLs
home_url = "https://www.nseindia.com/market-data/exchange-traded-funds-etf"
api_url = "https://www.nseindia.com/api/etf"

def get_etf_data():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    
    # Try to set binary location if running in GCP
    chromium_path = "/usr/bin/chromium"
    if os.path.exists(chromium_path):
        options.binary_location = chromium_path

    # Launch browser
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        print("User-Agent:", driver.execute_script("return navigator.userAgent"))

        # Step 1: Load homepage
        driver.get(home_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Homepage loaded, cookies set.")
        time.sleep(5)  # Wait for any bot checks to clear

        # Step 2: Fetch API data using browser context
        driver.execute_script("""
            window.apiResponse = null;
            fetch(arguments[0], {
                method: 'GET',
                headers: {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': arguments[1],
                    'User-Agent': navigator.userAgent
                },
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => { window.apiResponse = data; })
            .catch(err => { window.apiResponse = {error: err.toString()}; });
        """, api_url, home_url)

        # Wait for up to 15 seconds for response
        for i in range(15):
            time.sleep(1)
            api_response = driver.execute_script("return window.apiResponse;")
            if api_response is not None:
                break

        # Error handling
        if not api_response or 'error' in api_response:
            print(f"Failed to get API response or error: {api_response}")
            return None

        print("ETF data fetched successfully.")
        return api_response

    except Exception as e:
        print(f"Unexpected error while fetching ETF data: {e}")
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
            headers = etf_data[0].keys()
            writer.writerow(headers)
            for item in etf_data:
                writer.writerow(item.values())
        print(f"CSV file created successfully at {csv_file_path}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

def main():
    etf_json = get_etf_data()
    if etf_json:
        csv_file_name = f'ETF_data_{time.strftime("%Y-%m-%d")}.csv'
        csv_file_path = os.path.join(os.getcwd(), csv_file_name)
        save_to_csv(etf_json, csv_file_path)
        return csv_file_name
    else:
        print("ETF data not retrieved.")

if __name__ == "__main__":
    main()
